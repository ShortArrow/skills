"""PreToolUse on `gh pr create` and `gh pr edit`: refuse a body that breaks pull-request's mechanical rules.

Refused in every repository, because each is wrong at either scale:
  - a github.com `blob/` link whose ref is not a full commit hash, since its line moves;
  - a line broken with two trailing spaces or a backslash, outside fenced code;
  - a heading named verified, confirmed or 検証, unless the repository's own
    pull request template has that heading.

The 120-character first body (pull-request's procedure, step 1) belongs to the small
scale only, so it is refused only on `gh pr create` when the scale is known:
small when the receiving repository's owner is the signed-in gh user and the clone
has no pull request template; large when the owner is someone else and there is a
template. Any other combination, an owner or user that cannot be read, or a body the
shell builds (`$(...)`, a heredoc) gets context instead of a refusal, because the
cues do not settle it: an own repository with a template may be a team's, and
someone else's without one may be small or large.

Reads the hook input on stdin. Prints a deny verdict, a context, or nothing.
Environment: PR_BODY_CHECK_GH_USER replaces `gh config get user` (tests).
"""
import json
import os
import re
import shlex
import subprocess
import sys

FIRST_BODY_LIMIT = 120
UNPINNED = re.compile(r'https://github\.com/[^/\s]+/[^/\s]+/blob/(?![0-9a-f]{40}/)[^\s)>\]]+')
HARD_BREAK = re.compile(r'( {2,}|\\)$')
VERIFIED = re.compile(r'^#{1,6}\s*(.*\b(?:verified|verification|confirmed)\b.*|.*(?:検証|確認済み).*)$', re.I)
HEADING = re.compile(r'^#{1,6}\s*(.+?)\s*#*\s*$')
TEMPLATES = ('.github/pull_request_template.md', 'pull_request_template.md', 'docs/pull_request_template.md')
TEMPLATE_DIRS = ('.github/PULL_REQUEST_TEMPLATE', 'PULL_REQUEST_TEMPLATE', 'docs/PULL_REQUEST_TEMPLATE')
REMOTE = re.compile(r'github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?/?$')


def gh_pr_call(command):
    """(subcommand, arguments) of the first `gh pr create|edit` in command, or None.

    Raises ValueError when the shell builds the command in a way shlex cannot split."""
    if not re.search(r'\bgh\s+pr\s+(create|edit)\b', command):
        return None
    if '$(' in command or '`' in command or '<<' in command:
        raise ValueError('the shell builds this command')
    tokens = shlex.split(command)
    for i in range(len(tokens) - 2):
        if tokens[i] == 'gh' and tokens[i + 1] == 'pr' and tokens[i + 2] in ('create', 'edit'):
            rest = []
            for token in tokens[i + 3:]:
                if token in ('&&', '||', ';', '|'):
                    break
                rest.append(token)
            return tokens[i + 2], rest
    return None


def option(args, *names):
    """The value of the first of names in args, in `--x v`, `--x=v` or `-x v` form, or None."""
    for i, arg in enumerate(args):
        for name in names:
            if arg == name and i + 1 < len(args):
                return args[i + 1]
            if name.startswith('--') and arg.startswith(name + '='):
                return arg[len(name) + 1:]
    return None


def body_of(args, cwd):
    """The body the call carries, or None when it carries none."""
    text = option(args, '--body', '-b')
    if text is not None:
        return text
    path = option(args, '--body-file', '-F')
    if path is None:
        return None
    if path == '-':
        raise ValueError('the body comes from standard input')
    with open(os.path.join(cwd, path), encoding='utf-8') as handle:
        return handle.read()


def git(cwd, *args):
    proc = subprocess.run(['git', '-C', cwd, *args], capture_output=True, text=True, timeout=10)
    return proc.stdout.strip() if proc.returncode == 0 else ''


def owner_of(args, cwd):
    """The receiving repository's owner: -R/--repo, else the upstream remote, else origin."""
    named = option(args, '--repo', '-R')
    if named:
        return named.split('/')[-2] if '/' in named else None
    for remote in ('upstream', 'origin'):
        found = REMOTE.search(git(cwd, 'remote', 'get-url', remote))
        if found:
            return found.group(1)
    return None


def login():
    """The signed-in gh user, read from gh's own configuration, or None."""
    if 'PR_BODY_CHECK_GH_USER' in os.environ:
        return os.environ['PR_BODY_CHECK_GH_USER'] or None
    try:
        proc = subprocess.run(['gh', 'config', 'get', 'user', '-h', 'github.com'],
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() or None if proc.returncode == 0 else None


def template_of(cwd):
    """The text of the clone's pull request template(s), or None when it has none."""
    texts = []
    for path in TEMPLATES:
        for candidate in (path, path.upper(), path.replace('pull_request_template', 'PULL_REQUEST_TEMPLATE')):
            full = os.path.join(cwd, candidate)
            if os.path.isfile(full):
                with open(full, encoding='utf-8', errors='replace') as handle:
                    texts.append(handle.read())
                break
    for folder in TEMPLATE_DIRS:
        full = os.path.join(cwd, folder)
        if os.path.isdir(full):
            for name in sorted(os.listdir(full)):
                with open(os.path.join(full, name), encoding='utf-8', errors='replace') as handle:
                    texts.append(handle.read())
    return '\n'.join(texts) if texts else None


def scale(owner, login, template):
    """'small', 'large', or None when the two cues do not settle it."""
    if not owner or not login:
        return None
    own = owner.lower() == login.lower()
    if own and template is None:
        return 'small'
    if not own and template is not None:
        return 'large'
    return None


def outside_code(body):
    """(line number, line) for each line outside fenced code blocks."""
    fenced = False
    for number, line in enumerate(body.splitlines(), 1):
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def problems(body, template):
    allowed = {h.group(1).lower() for h in map(HEADING.match, (template or '').splitlines()) if h}
    found = []
    for number, line in outside_code(body):
        link = UNPINNED.search(line)
        if link:
            found.append(f'line {number}: {link.group(0)} is not pinned to a full commit hash; '
                         'link the line at the commit it was read at (press y on the file view)')
        if HARD_BREAK.search(line):
            found.append(f'line {number}: ends in two spaces or a backslash; '
                         'a newline already breaks the line in a pull request body')
        heading = HEADING.match(line)
        if heading and VERIFIED.match(line) and heading.group(1).lower() not in allowed:
            found.append(f'line {number}: a "{heading.group(1)}" section; '
                         'one line naming the condition and the result, the evidence in the commit, the test or a linked run')
    return found


def deny(reasons):
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
        'permissionDecisionReason': 'pull-request: ' + ' '.join(reasons)}}


def note(text):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': 'pull-request: ' + text}}


def verdict(payload):
    command = (payload.get('tool_input') or {}).get('command') or ''
    cwd = payload.get('cwd') or os.getcwd()
    try:
        call = gh_pr_call(command)
        if call is None:
            return None
        subcommand, args = call
        body = body_of(args, cwd)
    except (ValueError, OSError) as error:
        return note(f'the body could not be read ({error}), so its links, line breaks and headings were not checked; '
                    'write it to a file and pass it with --body-file.')
    if body is None:
        return None
    template = template_of(cwd)
    found = problems(body, template)
    if subcommand == 'create' and len(body.strip()) > FIRST_BODY_LIMIT:
        size = scale(owner_of(args, cwd), login(), template)
        if size == 'small':
            found.append(f'the first body is {len(body.strip())} characters; on a small repository open the draft '
                         f'with at most {FIRST_BODY_LIMIT} (the one thing the diff cannot say, or the issue it closes), '
                         'then put the full body in with gh pr edit --body-file')
        elif size is None and not found:
            return note(f'the first body is over {FIRST_BODY_LIMIT} characters and the scale could not be told '
                        'from the owner and the template; on a small repository open the draft with a short body, '
                        "on a large one fill the project's template in full.")
    return deny(found) if found else None


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
    except ValueError:
        return
    out = verdict(payload) if isinstance(payload, dict) else None
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
