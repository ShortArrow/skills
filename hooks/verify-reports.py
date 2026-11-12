"""Gate: a subagent's report is verified by another subagent before it is relayed or published.

adversarial-verify names the moment a subagent's "done" is about to pass as fact, and a
skill listing is consulted when a turn begins, so the moment is missed whenever the
report arrives later, which is how a background subagent's report always arrives. This
hook reads the session transcript at the two places the claim leaves the session.

    verify-reports.py publish   PreToolUse on a shell tool: refuse git push, gh pr create,
                                gh pr ready and gh issue create while any report in
                                the session has no verification after it.
    verify-reports.py stop      Stop: send the turn back once when a report that
                                arrived since the user last spoke has none.

A report is a completed Agent or Workflow call, synchronous or announced by a
task-notification. A verification is a report from an Agent call whose description
starts with "Verify" or "Re-verify", or names it skeptic, adversarial, refute,
fact-check or cross-check: the names sessions have given their verifiers, and the
ones adversarial-verify asks for. A report is
verified when a verification completed after it. An unreadable transcript lets the
call through: the gate is a check on the agent, not a lock on the user.

A consultation of another vendor's model through the shell counts as a report too,
after consultation-path. The host has no tool for "ask a different model", so such a
reading arrives as a shell call and was invisible here while the gate read only Agent,
Task and Workflow: the one kind of claim nobody in the session observed was the one
kind that left it unopposed.

Recognising one is a text match, and three narrower rules were each broken by an
adversarial verifier. Matching the invocation (`codex exec` at the start of a segment)
missed 21 real shapes. Matching the name minus a list of what runs no model drew 56
false positives, because that list has no end, and two of its rules read the prompt, so
the prompt could switch them off. An allowlist of documented answer-returning
subcommands missed about forty more — decisively, a verifier ran `echo "..." | copilot`
with no flag at all and got an answer, so no rule keyed on flags or subcommands can be
right. Each of the three had passed its own tests and scored well on real data first.

So the rule is the consultee's name as a word in the command, and nothing else. Shell
text cannot be classified reliably: a command reaches a binary through a variable, a
quoted path, a pipe, an interpreter, a line continuation, a PowerShell argument array or
an alias. The only question left is which way to be wrong, and the costs are not close —
a false flag costs one Verify: subagent that finds nothing, a miss lets a claim nobody
observed leave the session. Three structural exclusions remain, each text no shell would
run: a heredoc body (keeping the opener's line, since `cat <<EOF | codex exec -`
consults on it), the text after an unquoted `#`, and a path segment after the name.

Two automated security reviews then found parser differentials, all in the only step
that can hide a call: a `<<` inside quotes or after a `#` read as a heredoc opener, and
an unterminated heredoc discarding the rest of the command, plus an unhandled backslash
desynchronising the quote walk. Both are fixed by failing toward flagging, as below. One
of its examples was refuted at the shell, where the `#` it relied on does open a
comment: a security finding is a claim too. The second review found Bash escape rules
being applied to PowerShell commands, where a backslash is literal and a backtick
escapes; two of its three findings did not reproduce. A third found PowerShell's block
comment, where `<# ... #>` ends and the code after it runs; its other finding, that
curly quotes shelter a `#`, was refuted by running it.

Measured against one session's transcript, 1004 shell calls, each candidate judged by
its output rather than its command: 5 of 5 readings a model actually answered were
caught, 0 missed, with 21 further calls flagged that asked no model. Two earlier counts
here, 5 of 5 and then 7 of 7, were computed from commands that looked like
consultations; two of that seven never reached a model, and `| tail` had hidden the
non-zero exit. A command that looks like a consultation is no evidence that one
answered.
"""
import json
import re
import sys

PUBLISH = re.compile(
    r'\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--?[\w-]+(?:=\S+)?))*\s+push\b'
    r'|\bgh\s+pr\s+(?:create|ready)\b'
    r'|\bgh\s+issue\s+create\b'
)
VERIFIER = re.compile(
    r'^\s*(?:re-?)?verif(?:y|ication)\b|\bskeptic\b|\badversarial(?:ly)?\b|\brefute\b|\bfact-?check|\bcross-?check',
    re.IGNORECASE)
NOTIFIED = re.compile(r'<tool-use-id>([^<]+)</tool-use-id>.*?<status>([^<]+)</status>', re.DOTALL)
DELEGATING_TOOLS = ('Agent', 'Task', 'Workflow')

# A consultation is recognised by the consultee's name appearing as a word in a
# shell command. That is all: the looseness is the design, and the module
# docstring above holds why — three narrower rules were each broken, shell text
# cannot be classified reliably, and a false flag costs one verification while a
# miss costs the guarantee. The only exclusions are structural, below.
CONSULT = re.compile(r'\b(codex|copilot|gemini)(?:\.exe|\.cmd)?\b(?![\w.-]*[/\\])',
                     re.IGNORECASE)
# A heredoc body is text being written, not commands to run, so a fixture or a
# skill body quoting `codex exec` is not a call. Only the body is dropped, never
# the opener's own line, because `cat <<EOF | codex exec -` consults on it.
# `<<` must be a redirection, not arithmetic: in `x=$((a<<b))` the shift is not
# an opener, and reading it as one swallowed every line after it. A redirection's
# `<<` is preceded by whitespace or the start of the line, and `<<<` is a
# here-string, which has no terminator line.
HEREDOC_OPENS = re.compile(r"(?:^|\s)<<(?!<)-?\s*\\?['\"]?([\w-]+)['\"]?")
# `<<'EOF'`, `<< "END"` and `<<\EOF` quote the delimiter, which is syntax rather
# than a quoted string, so the quotes come off before the quote-aware blanking
# in runnable_part would mistake the delimiter for text.
DELIMITER_QUOTES = re.compile(r"""<<(-?\s*)(?:\\|['"])\s*([\w-]+)['"]?""")
# PowerShell is this machine's primary shell and the push side of this gate
# already matches it, so reading only Bash left one unwatched route.
# A backslash, a backtick or a doubled single quote: each escapes in one of the
# two shells and is literal in the other, so a `#` alongside one cannot be
# classified without knowing which grammar applies. Bash escape rules were
# applied to PowerShell commands until a security review pointed this out.
AMBIGUOUS_ESCAPE = re.compile(r"\\|`|''")
# PowerShell's block comment ends, and the code after `#>` runs: a verifier's
# `Write-Output x <# a #> ; codex exec q` really does reach the consultation.
# A `#` inside one would otherwise be read as starting a line comment and take
# the rest of the command with it, so the cut is abandoned when either
# delimiter appears.
BLOCK_COMMENT = re.compile(r'<#|#>')
SHELL_TOOLS = ('Bash', 'PowerShell')
PUBLISH_REASON = (
    'Not yet: {count} subagent report(s) in this session have no adversarial verification after them '
    '({names}). Apply adversarial-verify: launch a separate subagent with a description starting '
    '"Verify:", give it each claim and how to try to break it (the commands to rerun, the files to '
    'read), not the conclusion; act on what survives, then run this command again.'
)
STOP_REASON = (
    'Subagent report(s) arrived this turn with no adversarial verification after them ({names}). '
    'Before relaying them as fact, apply adversarial-verify: launch a separate subagent with a '
    'description starting "Verify:" that tries to break each claim; or, if the turn ends before it '
    'returns, say plainly that the report is unverified.'
)


def read_transcript(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def is_user_prompt(entry):
    if entry.get('type') != 'user' or entry.get('isMeta') or 'toolUseResult' in entry:
        return False
    content = (entry.get('message') or {}).get('content')
    if isinstance(content, str):
        return True
    return isinstance(content, list) and any(b.get('type') == 'text' for b in content)


def consultation(block):
    """The label for a shell call that asks another model, or None.

    A consultation returns a claim exactly as a subagent does — a reading nobody
    in this session observed — so consultation-path routes it to the same gate.
    What distinguishes it from any other shell call is only the command, since
    the host has no tool of its own for "ask a different vendor's model".

    The name alone decides, for the reasons set out above CONSULT. A command
    that merely mentions a consultee is flagged and costs one verification; that
    is the cheaper error. Only the two structural cases are dropped: a heredoc
    body, which is text being written, and the text after an unquoted `#`.
    """
    if block.get('name') not in SHELL_TOOLS:
        return None
    command = (block.get('input') or {}).get('command') or ''
    for part in segments(without_heredoc_bodies(command)):
        found = CONSULT.search(part)
        if found:
            return f'consultation: {found.group(1).lower()}'
    return None


def without_heredoc_bodies(command):
    """The command with every heredoc body dropped, keeping the opener's line.

    A heredoc body is text being written, not commands to run, so a fixture or a
    skill body quoting `codex exec` is not a call. The opener's own line stays,
    because `cat <<EOF | codex exec -` consults on that line; removing the line
    with the body hid exactly that. A terminator may be indented by `<<-` or
    carry trailing spaces, and both left the body in place until handled here.

    Dropping lines is the one thing here that can hide a call, so it fails
    toward flagging in two ways. A `<<` inside quotes or after a `#` opens
    nothing — `echo "a <<EOF b"` and `# <<EOF` are text — so the opener is
    looked for only in what the quote-aware walk leaves outside them. And a
    terminator that never arrives means the guess was wrong, so the lines are
    restored rather than discarded; otherwise `cat <<EOF > f` with no `EOF`
    swallowed every command after it, which is a one-line way past the gate.
    """
    lines = command.split('\n')
    out, awaiting, held = [], None, []
    for line in lines:
        if awaiting is not None:
            held.append(line)
            if line.strip() == awaiting:
                awaiting, held = None, []
            continue
        out.append(line)
        opened = HEREDOC_OPENS.search(runnable_part(line))
        if opened:
            awaiting = opened.group(1)
    # An unterminated heredoc: the opener was quoted, commented or mistaken, so
    # give back what was held instead of trusting the guess.
    return '\n'.join(out + held)


def runnable_part(line):
    """The line with quoted text and any trailing comment blanked out.

    Used only to decide whether a `<<` is a real heredoc opener. Quoted text is
    replaced by spaces rather than removed so that positions, and therefore the
    `(?:^|\\s)` before `<<`, still behave.

    A delimiter's own quoting is syntax, not a quoted string: `<<'EOF'`,
    `<< "END"` and `<<\\EOF` all open a heredoc, so the delimiter after a `<<`
    is passed through rather than blanked.
    """
    out, quote, escaped = [], None, False
    for ch in DELIMITER_QUOTES.sub(r'<<\1\2', line):
        if escaped:
            out.append(' ')
            escaped = False
            continue
        if ch == '\\' and quote != "'":
            escaped = True
            out.append(' ')
            continue
        if quote:
            out.append(' ')
            if ch == quote:
                quote = None
            continue
        if ch in '\'"':
            quote = ch
            out.append(' ')
            continue
        if ch == '#':
            out.extend(' ' * (len(line) - len(out)))
            break
        out.append(ch)
    return ''.join(out)



def segments(command):
    """The command split at every separator that can begin a new command.

    A separator inside quotes begins nothing — `sed "s|a|b|"` is one command
    with three bars in an argument — so the walk tracks the quote it is inside.
    A substitution is the exception: `$(…)` and a backtick open a command even
    within double quotes, which is how `R="$(codex exec …)"` hides one, so a
    double quote does not suppress them.

    An unquoted `#` ends the line and takes the separators after it with it:
    nothing after the `#` in `echo hi # ; codex exec "q"` runs. Tracking quotes
    is what separates that from `git commit -m "fix #12" && codex exec`, where
    the `#` is inside a string and the call behind it is real.

    A backslash escapes the next character everywhere but inside single quotes.
    Without that, an escaped quote desynchronised the walk and the rest of the
    command was read as quoted: `echo "he said \\"hi\\"" # ; codex exec q` lost
    its call, which is a way past the gate rather than a cosmetic slip.

    Those are Bash's rules, and PowerShell's differ: there a backslash is an
    ordinary character, a backtick escapes, and `''` inside a single-quoted
    string is one escaped quote. Rather than carry two grammars, the one place
    the difference could hide a call is given up: where a command mixes an
    escape character with a `#`, the comment is not cut and the text after it is
    kept. That costs a flag on a command whose `#` really was a comment, and the
    module's choice above says which way to spend that.
    """
    # Where an escape character and a `#` appear together, which of the two
    # grammars applies decides whether that `#` is a comment, so the cut is
    # abandoned and everything is kept.
    cut_comments = '#' in command and not (
        AMBIGUOUS_ESCAPE.search(command) or BLOCK_COMMENT.search(command))
    out, current, quote = [], [], None
    skipping_comment = False
    escaped = False
    for i, ch in enumerate(command):
        if skipping_comment:
            if ch == '\n':
                skipping_comment = False
            continue
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == '\\' and quote != "'":
            current.append(ch)
            escaped = True
            continue
        opens_run = ch == '`' or (ch == '(' and i and command[i - 1] == '$')
        if quote and not (opens_run and quote == '"'):
            current.append(ch)
            if ch == quote:
                quote = None
        elif ch == '#' and cut_comments and (i == 0 or command[i - 1] in ' \t\n|&;('):
            skipping_comment = True
            out.append(''.join(current))
            current = []
        elif ch in '\'"':
            quote = ch
            current.append(ch)
        elif ch in '|&;\n()`':
            out.append(''.join(current))
            current = []
        else:
            current.append(ch)
    out.append(''.join(current))
    return out


def reports(entries):
    """(index, description, is_verification) for every completed delegated call, in order."""
    calls = {}
    synchronous = set()
    found = []
    for i, entry in enumerate(entries):
        content = (entry.get('message') or {}).get('content')
        for block in content if isinstance(content, list) else []:
            consulted = consultation(block)
            if consulted:
                calls[block['id']] = consulted
                synchronous.add(block['id'])
            if block.get('type') == 'tool_use' and block.get('name') in DELEGATING_TOOLS:
                calls[block['id']] = (block.get('input') or {}).get('description') or block['name']
                if block.get('name') != 'Workflow':
                    synchronous.add(block['id'])
            if block.get('type') == 'tool_result' and block.get('tool_use_id') in synchronous:
                result = entry.get('toolUseResult')
                if not (isinstance(result, dict) and result.get('isAsync')) and not block.get('is_error'):
                    found.append(i_report(i, calls[block['tool_use_id']]))
        prompt = (entry.get('attachment') or {}).get('prompt')
        if isinstance(prompt, str) and '<task-notification>' in prompt:
            for use_id, status in NOTIFIED.findall(prompt):
                if use_id in calls and status.strip() == 'completed':
                    found.append(i_report(i, calls[use_id]))
    return found


def i_report(index, description):
    return index, description, bool(VERIFIER.search(description))


def unverified(found, since=0):
    last_check = max((i for i, _, check in found if check), default=-1)
    return [d for i, d, check in found if not check and i > last_check and i >= since]


def names(descriptions):
    shown = ', '.join(f'"{d}"' for d in descriptions[:5])
    return shown + (f' and {len(descriptions) - 5} more' if len(descriptions) > 5 else '')


def publishes(command):
    """Whether the command publishes. Deliberately matches a mere mention too.

    An attempt to narrow this was reverted. The gate matches the publish text
    anywhere in the command, so writing about a push — a heredoc, a grep, a
    commit message — is refused as though it were one, which a verifier hit in
    practice on a command whose only `gh pr create` sat inside a heredoc string.

    The narrowing judged a publish as what a segment runs, the same walk the
    consultation check uses. It fixed the mention cases and broke seven real
    publishes that this regex catches: `eval "git push"`, `bash -c 'git push'`,
    `sh -c`, `pwsh -c`, `cmd /c`, `Invoke-Expression` and `iex`, because the
    command to run sits inside the quoted argument that the narrowing blanked.

    Those two error classes are not equal. A false refusal costs one rewritten
    command and says why. A missed publish lets an unverified report leave the
    session, which is the single thing this file exists to prevent. So the
    over-matching stays, and the annoyance is the price of the guarantee.
    """
    return bool(PUBLISH.search(command))


def publish_verdict(payload, entries):
    command = (payload.get('tool_input') or {}).get('command') or ''
    if not publishes(command):
        return None
    left = unverified(reports(entries))
    if not left:
        return None
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': PUBLISH_REASON.format(count=len(left), names=names(left)),
    }}


def stop_verdict(payload, entries):
    if payload.get('stop_hook_active'):
        return None
    since = max((i for i, e in enumerate(entries) if is_user_prompt(e)), default=0)
    left = unverified(reports(entries), since)
    if not left:
        return None
    return {'decision': 'block', 'reason': STOP_REASON.format(names=names(left))}


VERDICTS = {'publish': publish_verdict, 'stop': stop_verdict}
CONCERNS = {
    'publish': lambda payload: publishes((payload.get('tool_input') or {}).get('command') or ''),
    'stop': lambda payload: not payload.get('stop_hook_active'),
}


def main(argv):
    """Read the transcript only when the call is one the gate concerns; every Bash call passes here."""
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
        if not (isinstance(payload, dict) and CONCERNS[argv[0]](payload)):
            return
        entries = read_transcript(payload['transcript_path'])
    except (ValueError, KeyError, TypeError, OSError):
        return
    out = VERDICTS[argv[0]](payload, entries)
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main(sys.argv[1:])
