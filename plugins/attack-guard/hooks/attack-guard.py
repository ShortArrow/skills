"""PreToolUse on Bash and PowerShell: stop a command shaped like a MITRE ATT&CK technique.

An agent's ssh, port probe or key read looks the same to an endpoint detector as an
intruder's, so these shapes are left to a person at their own terminal. Which shapes, and
under which technique id, is the table attack-techniques.json beside this file, which
other hooks may read as well. Its semantics:

  techniques   id -> ATT&CK name, as attack.mitre.org gives it today.
  prefixes     words skipped before the command name, with the options and numbers after them.
  rules        a match is the first technique of every rule a command meets; regexes are
               searched case-insensitively unless "case_sensitive" is true, and use no
               lookaround or backreference, so a Rust or Go reader can compile them.
    A rule without "scope" is met by one simple command when all of these hold:
      commands           its name, lower-cased, without directory or .exe, is in the list;
      shells, or_exe     the shell is listed ("bash", "powershell"), or or_exe and .exe was written;
      stop_at            arguments from the first one matching are not read;
      first_argument     the first argument matches; not_first_argument: it does not;
      arguments          each regex matches some argument;
      flag_then_value    some argument matches the first regex and the next one the second.
    "always_deny": true refuses whatever the machine's setting is (the canary).
  runners      commands that run another command line, read with the same rules, up to three deep:
      commands, parse_as   the runner's names, and whether the line inside is read as bash or PowerShell;
      script_after         the line is the arguments after the first one matching (cmd /c, bash -c, pwsh -Command);
      file_flag, arguments_flag, switches   Start-Process's form: the file and its argument list, by flag
                           or by position, past flags that take a value unless they are switches.
    A rule with "scope": "line" is met by the whole command line when all of these hold:
      any_command        some simple command's name is in the list;
      any_piped_command  some simple command after a | has its name in the list;
      line               the line matches.

Each word counts only where a shell runs it as a command: at the start of the line or
after &&, ||, ;, |, &, a newline, `$(`, a bash backtick, or the opening of a subshell,
group or block, past VAR=value, $var =, sudo, env, if, then and the like. The same word
in a quoted string, a heredoc, a here-string, a comment or an argument is text, and ssh
in a git URL or GIT_SSH_COMMAND is git's transport.

Whether a match is refused or asked about is the machine's, never the repository's:
  ATTACK_GUARD=deny|ask       decides outright;
  otherwise the JSON file at ATTACK_GUARD_CONFIG (default ~/.claude/attack-guard.json),
  {"deny_hosts": [glob...], "deny_remotes": [glob...]}, refuses on a host whose name
  matches, or in a clone with a remote URL that matches (case-insensitive globs);
  anything else asks. ATTACK_GUARD_HOSTNAME replaces the host name (tests).

Reads the hook input on stdin. Prints a deny or ask verdict, or nothing to allow.
"""
import fnmatch
import json
import os
import re
import socket
import subprocess
import sys

TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attack-techniques.json')
ASSIGNMENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
SEPARATORS = set(';|&(){}\n')


def commands(text, powershell):
    """(separator before it, words) for each simple command in text, as the shell would split them."""
    escape = '`' if powershell else '\\'
    found, words, word, heredocs = [], [], [], []
    state = {'sep': ''}
    i, n = 0, len(text)

    def end_word():
        if word:
            words.append(''.join(word))
            word.clear()

    def end_command(sep):
        end_word()
        if words:
            found.append((state['sep'], list(words)))
            words.clear()
        state['sep'] = sep

    while i < n:
        c = text[i]
        if c == escape and i + 1 < n:
            if text[i + 1] != '\n':
                word.append(text[i + 1])
            i += 2
        elif c == "'":
            close = text.find("'", i + 1)
            close = n if close < 0 else close
            word.append(text[i + 1:close])
            i = close + 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == escape else 1
            word.append(text[i + 1:j])
            i = j + 1
        elif powershell and text.startswith(("@'", '@"'), i):
            close = text.find('\n' + text[i + 1] + '@', i + 2)
            i = n if close < 0 else close + 3
        elif c == '#' and not word:
            newline = text.find('\n', i)
            i = n if newline < 0 else newline
        elif not powershell and text.startswith('<<', i) and not text.startswith('<<<', i):
            end_word()
            m = re.compile(r'<<(-?)\s*([\'"]?)([^\s\'";|&<>()]+)\2').match(text, i)
            if m:
                heredocs.append((m.group(3), m.group(1) == '-'))
                i = m.end()
            else:
                i += 2
        elif c == '\n':
            end_command('\n')
            i += 1
            for delimiter, dash in heredocs:
                while i < n:
                    newline = text.find('\n', i)
                    line = text[i:n if newline < 0 else newline]
                    i = n if newline < 0 else newline + 1
                    if (line.lstrip('\t') if dash else line) == delimiter:
                        break
            heredocs.clear()
        elif c in SEPARATORS or (c == '`' and not powershell):
            end_command(c)
            i += 1
        elif c == '$' and text.startswith('$(', i):
            end_command('(')
            i += 2
        elif c in ' \t\r':
            end_word()
            i += 1
        else:
            word.append(c)
            i += 1
    end_command('')
    return found


def name_and_arguments(words, prefixes):
    """The command a simple command runs, lower-cased without path or .exe, whether .exe was written, and its arguments."""
    rest = list(words)
    while rest:
        head = rest[0]
        if ASSIGNMENT.match(head):
            rest.pop(0)
        elif head.startswith('$') and (head.endswith('=') or rest[1:2] == ['=']):
            rest = rest[1:] if head.endswith('=') else rest[2:]
        elif head.lower() in prefixes:
            rest.pop(0)
            while rest and (rest[0].startswith('-') or rest[0].isdigit()):
                rest.pop(0)
        else:
            break
    if not rest:
        return '', False, []
    name = re.split(r'[\\/]', rest[0])[-1].lower()
    exe = name.endswith('.exe')
    return (name[:-4] if exe else name), exe, rest[1:]


def load_table():
    with open(TABLE, encoding='utf-8') as f:
        table = json.load(f)
    flags = lambda rule: 0 if rule.get('case_sensitive') else re.I
    for rule in table['rules']:
        f = flags(rule)
        rule['_arguments'] = [re.compile(p, f) for p in rule.get('arguments', [])]
        for key in ('first_argument', 'not_first_argument', 'stop_at', 'line'):
            if key in rule:
                rule['_' + key] = re.compile(rule[key], f)
        if 'flag_then_value' in rule:
            rule['_flag_then_value'] = [re.compile(p, f) for p in rule['flag_then_value']]
    return table


def command_matches(rule, name, exe, arguments, powershell):
    """Whether one simple command meets a command rule."""
    if name not in rule['commands']:
        return False
    if 'shells' in rule and ('powershell' if powershell else 'bash') not in rule['shells']             and not (rule.get('or_exe') and exe):
        return False
    if '_stop_at' in rule:
        cut = next((i for i, a in enumerate(arguments) if rule['_stop_at'].search(a)), len(arguments))
        arguments = arguments[:cut]
    first = arguments[0] if arguments else None
    if '_first_argument' in rule and (first is None or not rule['_first_argument'].search(first)):
        return False
    if '_not_first_argument' in rule and first is not None and rule['_not_first_argument'].search(first):
        return False
    if not all(any(p.search(a) for a in arguments) for p in rule['_arguments']):
        return False
    if '_flag_then_value' in rule:
        flag, value = rule['_flag_then_value']
        if not any(flag.search(a) and value.search(b) for a, b in zip(arguments, arguments[1:])):
            return False
    return True


def line_matches(rule, command, parsed):
    """Whether a whole command line meets a line rule."""
    names = [name for _, _, (name, _, _) in parsed]
    if 'any_command' in rule and not set(rule['any_command']) & set(names):
        return False
    if 'any_piped_command' in rule and not any(sep == '|' and name in rule['any_piped_command']
                                               for sep, _, (name, _, _) in parsed):
        return False
    return '_line' not in rule or bool(rule['_line'].search(command))


def inner_command(runner, arguments):
    """The command line a runner such as cmd /c, pwsh -Command or Start-Process is handed, or None."""
    if 'script_after' in runner:
        flag = re.compile(runner['script_after'], re.I)
        at = next((i for i, a in enumerate(arguments) if flag.search(a)), None)
        return None if at is None else ' '.join(arguments[at + 1:]) or None
    file_flag, list_flag = re.compile(runner['file_flag'], re.I), re.compile(runner['arguments_flag'], re.I)
    switch = re.compile(runner['switches'], re.I)
    file, listed, positional, i = None, [], [], 0
    while i < len(arguments):
        a = arguments[i]
        if file_flag.search(a) and i + 1 < len(arguments):
            file, i = arguments[i + 1], i + 2
        elif list_flag.search(a) and i + 1 < len(arguments):
            listed.append(arguments[i + 1].replace(',', ' ')); i += 2
        elif a.startswith('-'):
            i += 1 if switch.search(a) else 2
        else:
            positional.append(a); i += 1
    if file is None and positional:
        file = positional.pop(0)
    listed += [p.replace(',', ' ') for p in positional[:1]]
    return None if file is None else ' '.join([file] + listed)


def matches(tool, command, table=None, depth=0):
    """[(technique id, the simple command or the line)] for every rule command meets, in order;
    a command a runner is handed (cmd /c, bash -c, pwsh -Command, Start-Process) is read as well."""
    table = table or TABLE_RULES
    powershell = tool == 'PowerShell'
    parsed = [(sep, words, name_and_arguments(words, table['prefixes']))
              for sep, words in commands(command, powershell)]
    found = []
    for _, words, (name, exe, arguments) in parsed:
        for rule in table['rules']:
            if rule.get('scope') != 'line' and command_matches(rule, name, exe, arguments, powershell):
                found.append((rule['technique'], ' '.join(words)))
                if rule.get('always_deny'):
                    found.append(('!deny', ''))
        for runner in table.get('runners', []) if depth < 3 else []:
            if name in runner['commands']:
                inner = inner_command(runner, arguments)
                if inner:
                    tool_inside = 'PowerShell' if runner['parse_as'] == 'powershell' else 'Bash'
                    found += matches(tool_inside, inner, table, depth + 1)
    for rule in table['rules']:
        if rule.get('scope') == 'line' and line_matches(rule, command, parsed):
            found.append((rule['technique'], command.strip()))
    return found


def host_name():
    return (os.environ.get('ATTACK_GUARD_HOSTNAME') or os.environ.get('COMPUTERNAME')
            or os.environ.get('HOSTNAME') or socket.gethostname())


def remotes(cwd):
    try:
        out = subprocess.run(['git', '-C', cwd, 'remote', '-v'], capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return []
    return [line.split()[1] for line in out.stdout.decode('utf-8', 'replace').splitlines() if len(line.split()) > 1]


def mode(cwd):
    """'deny' or 'ask' for this machine and this clone."""
    setting = os.environ.get('ATTACK_GUARD', '').strip().lower()
    if setting in ('deny', 'ask'):
        return setting
    path = os.environ.get('ATTACK_GUARD_CONFIG') or os.path.join(os.path.expanduser('~'), '.claude', 'attack-guard.json')
    try:
        with open(path, encoding='utf-8') as f:
            config = json.load(f)
    except (OSError, ValueError):
        return 'ask'

    def matching(value, patterns):
        return any(fnmatch.fnmatch(value.lower(), p.lower()) for p in patterns or [])

    if matching(host_name(), config.get('deny_hosts')):
        return 'deny'
    if config.get('deny_remotes') and any(matching(url, config['deny_remotes']) for url in remotes(cwd)):
        return 'deny'
    return 'ask'


def reason(found, command, decision):
    seen = []
    for technique, words in found:
        if technique not in [t for t, _ in seen]:
            seen.append((technique, words))
    listed = '、'.join(f'{t}（{TABLE_RULES["techniques"][t]}）：{w}' for t, w in seen)
    head = f'MITRE ATT&CK の技術に当てはまる形のコマンド。{listed}。'
    if decision == 'deny':
        return (head + 'このマシンでは、エージェントからは実行しない。要るなら、ユーザーに頼んで、'
                f'ユーザー自身の端末で手で打ってもらう：{command.strip()}')
    return head + '実行してよいか、ユーザーに確かめる。'


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode('utf-8', 'replace'))
        tool, command = data.get('tool_name', ''), data['tool_input']['command']
    except (ValueError, KeyError, TypeError, AttributeError):
        return
    found = matches(tool, command)
    if not found:
        return
    decision = 'deny' if ('!deny', '') in found else mode(data.get('cwd') or os.getcwd())
    found = [f for f in found if f[0] != '!deny']
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': decision,
                                             'permissionDecisionReason': reason(found, command, decision)}},
                     ensure_ascii=False))


TABLE_RULES = load_table()

if __name__ == '__main__':
    main()
