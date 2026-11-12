"""Gate: a living document follows the surface it describes, in the same commit.

clean-docs sets the rule this enforces — a living document follows its source, a
record freezes when written — and the moment it is missed is the push, because a
surface change and its documentation are correct separately and wrong together.

    docs-follow.py   PreToolUse on Bash: refuse git push while an outgoing commit
                     changes a surface (a skill body, a hook, a script, the
                     marketplace) and no living document changed with it.

A surface is code or configuration a reader depends on. A document is a living
document that can follow one: a README, a skill, anything under docs/. A record
(CHANGELOG, release notes) is frozen when written, so touching one never
satisfies the gate. Tests and fixtures are neither: they follow the code by
being run, not by being read.

Staleness is judged from commits rather than mtime, after i18n-parity: a
checkout does not preserve modification times, so an mtime comparison passes on
a fresh clone whatever the state. For the same reason the exception is declared
as a full commit sha in docs-follow-exceptions.txt, never as a path — a path
would be a permanent hole, while a sha stops matching as soon as the next commit
touches the file.

An unreadable repository lets the call through. The gate is a check on the agent,
not a lock on the user.
"""
import json
import os
import re
import subprocess
import sys

PUSH = re.compile(r'\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--?[\w-]+(?:=\S+)?))*\s+push\b')
FULL_SHA = re.compile(r'^([0-9a-f]{40})\s+(\S.*)$')

SURFACE = ('hooks/', 'scripts/', '.claude-plugin/')
DOCUMENT = ('readme', 'docs/')
RECORDS = ('changelog.md', 'release-notes.md')

REASON = (
    'Not yet: {count} outgoing commit(s) change a surface with no living document following in the '
    'same commit ({names}). clean-docs: a living document follows its source, so the skill body, '
    'README or docs/ page that describes the changed behaviour belongs in the commit that changes '
    'it. Amend the commit to carry the document, or, when nothing needs to follow (an internal '
    'rename, wiring only), add the full 40-character sha and the reason to '
    'hooks/docs-follow-exceptions.txt and push again.'
)


SPENT = (
    ' Spent entries in hooks/docs-follow-exceptions.txt, matching no outgoing commit ({names}): '
    'delete them, since an expired entry reads exactly like a working one.'
)


def classify(path):
    """Surface, document, record, or neither. Order matters: a record looks like a document."""
    p = path.replace('\\', '/').lower()
    if os.path.basename(p) in RECORDS:
        return 'record'
    if p.startswith('tests/'):
        return None
    if p.startswith(SURFACE):
        return 'surface'
    if p.startswith('skills/') and p.endswith('.md'):
        return 'document'
    if any(k in p for k in DOCUMENT) and p.endswith('.md'):
        return 'document'
    if p.endswith(('.py', '.sh', '.ps1', '.json')):
        return 'surface'
    return None


def parse_exceptions(text):
    """Full shas only, each with a reason beside it. An entry with no reason is a silenced check."""
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = FULL_SHA.match(line)
        if m:
            out.add(m.group(1))
    return out


def unfollowed(commits, excused=frozenset()):
    """The commits that change a surface with no living document in the same commit."""
    left = []
    for commit in commits:
        if commit['sha'] in excused:
            continue
        kinds = {classify(p) for p in commit['paths']}
        if 'surface' in kinds and 'document' not in kinds:
            left.append(commit)
    return left


def spent(commits, excused):
    """Entries that match no outgoing commit, so the reader can delete them.

    An expired entry does nothing and reads exactly like a working one, so every
    refusal names the ones no longer in use.
    """
    outgoing_shas = {c['sha'] for c in commits}
    return {sha for sha in excused if sha not in outgoing_shas}


def paths_of(name_only):
    """The paths in a `git show --name-only` output, dropping what is not one.

    git writes the signature banner for a signed commit to stdout on some
    platforms, so the output of a verified commit begins with `gpg:` lines. They
    classify as neither surface nor document and are harmless on their own, but a
    line that is not a path has no business being counted as one.
    """
    out = []
    for line in name_only.split('\n'):
        line = line.strip()
        if not line or line.startswith('gpg:') or line.startswith('Primary key fingerprint'):
            continue
        out.append(line)
    return out


def git(cwd, *args):
    proc = subprocess.run(('git',) + args, cwd=cwd, capture_output=True, text=True, timeout=20)
    if proc.returncode != 0:
        raise OSError(proc.stderr.strip() or 'git failed')
    return proc.stdout


def outgoing(cwd):
    """The commits a push would send, newest first, each with the paths it touched."""
    upstream = git(cwd, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}').strip()
    shas = git(cwd, 'rev-list', f'{upstream}..HEAD').split()
    commits = []
    for sha in shas:
        raw = git(cwd, 'show', '--no-show-signature', '--pretty=format:', '--name-only', sha)
        commits.append({'sha': sha, 'paths': paths_of(raw)})
    return commits


def exceptions(cwd):
    path = os.path.join(cwd, 'hooks', 'docs-follow-exceptions.txt')
    try:
        with open(path, encoding='utf-8') as f:
            return parse_exceptions(f.read())
    except OSError:
        return set()


def push_verdict(payload, commits, excused=frozenset()):
    command = (payload.get('tool_input') or {}).get('command') or ''
    if not PUSH.search(command):
        return None
    left = unfollowed(commits, excused)
    if not left:
        return None
    names = ', '.join(c['sha'][:7] for c in left)
    reason = REASON.format(count=len(left), names=names)
    stale = spent(commits, excused)
    if stale:
        reason += SPENT.format(names=', '.join(sorted(s[:7] for s in stale)))
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': reason,
    }}


def main():
    """Read git only when the call is a push; every other Bash call passes here."""
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
        if not isinstance(payload, dict):
            return
        if not PUSH.search((payload.get('tool_input') or {}).get('command') or ''):
            return
        cwd = payload.get('cwd') or os.getcwd()
        commits = outgoing(cwd)
        excused = exceptions(cwd)
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        return
    out = push_verdict(payload, commits, excused)
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
