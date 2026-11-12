"""pre-push: refuse a push whose commits name a repository the user keeps private.

    python repo-names.py --explain ID  in your own terminal, to see a name

The guard-private-names skill installs it; its SKILL.md says how.

The names come from two places: the repositories `gh` lists for the signed-in
account that are not public, and the clones `ghq list` finds, less those GitHub
confirms are public. Each name is split into words at case changes, separators
and digits, and the words are looked up in `words.txt` (an English word list):
a name with a word outside the list is matched however its words are joined and
cased; a name of two or more listed words is matched only exactly as written; a
name that is one listed word is not checked, being an ordinary word. Matches are
whole words, in the tree of every pushed tip and in the lines every other pushed
commit adds.

A refusal prints where each hit is and an 8-character id, never the name: the
message lands in terminals, agent transcripts and CI logs, and printing the name
there would be the leak it exists to stop. `--explain` maps an id back to its name
for the person at the keyboard. A name that is an ordinary word goes in the clone's
untracked `info/repo-names-allowed` (one per line), which is never pushed, because
an allow list of private names published would be the same leak.

When `gh` cannot list the names, the push is refused: a check that passes because
it could not look is not a check.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ZERO = '0' * 40
ALLOWED = 'info/repo-names-allowed'
OWNED = 'user/repos?affiliation=owner,collaborator,organization_member&per_page=100'
MIN_LENGTH = 3
SHOWN = 60
WORDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.txt')
SEPARATOR = '[-_. ]?'


class NamesUnknown(Exception):
    """The private names could not be listed, so nothing can be passed."""

    def __init__(self, message, stdout=''):
        super().__init__(message)
        self.stdout = stdout


def run(*args):
    """stdout of a command; NamesUnknown when it fails, carrying what it printed."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise NamesUnknown(f'{args[0]}: {error}')
    if proc.returncode != 0:
        raise NamesUnknown(f'{" ".join(args[:3])}: {proc.stderr.strip()[:200]}', proc.stdout)
    return proc.stdout


def ident(name):
    return hashlib.sha256(name.lower().encode('utf-8')).hexdigest()[:8]


def words_of(name):
    """The lowercase words of a name: split at case changes, separators and digits."""
    return [w.lower() for w in re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+', name)]


def load_words(path=WORDS):
    """The dictionary: the words after the license header's `---` line."""
    try:
        with open(path, encoding='utf-8') as handle:
            text = handle.read()
    except OSError:
        return set()
    _, separator, body = text.partition('\n---\n')
    return {w.lower() for w in (body if separator else text).split()}


def parse_pushes(text):
    """git's pre-push stdin: local ref, local sha, remote ref, remote sha per line."""
    return [tuple(line.split()) for line in text.splitlines() if len(line.split()) == 4]


def _public_on_github(clones, run):
    """The subset of (owner, name) that GitHub reports as public; unknown counts as not public."""
    public = set()
    for start in range(0, len(clones), 100):
        batch = clones[start:start + 100]
        fields = ' '.join(f'r{i}: repository(owner: {json.dumps(o)}, name: {json.dumps(n)}) {{ isPrivate }}'
                          for i, (o, n) in enumerate(batch))
        try:
            out = run('gh', 'api', 'graphql', '-f', f'query={{ {fields} }}')
        except NamesUnknown as error:
            out = error.stdout
        try:
            data = (json.loads(out) or {}).get('data') or {}
        except ValueError:
            continue
        for i, pair in enumerate(batch):
            if (data.get(f'r{i}') or {}).get('isPrivate') is False:
                public.add(pair)
    return public


def load_names(run=run):
    """name -> 'private' or 'ghq'. Raises NamesUnknown when gh cannot list the account's repositories."""
    names, public = {}, set()
    for line in run('gh', 'api', '--paginate', OWNED, '--jq', '.[] | [.name, .visibility] | @tsv').splitlines():
        name, _, visibility = line.strip().partition('\t')
        if not name:
            continue
        if visibility == 'public':
            public.add(name.lower())
        else:
            names[name] = 'private'
    try:
        listed = run('ghq', 'list')
    except NamesUnknown:
        listed = ''
    clones, others = [], []
    for line in listed.splitlines():
        parts = line.strip().replace('\\', '/').strip('/').split('/')
        if not parts or not parts[-1]:
            continue
        if len(parts) == 3 and parts[0] == 'github.com':
            clones.append((parts[1], parts[2]))
        else:
            others.append(parts[-1])
    confirmed = _public_on_github(clones, run) if clones else set()
    for owner, name in clones:
        if (owner, name) not in confirmed:
            names.setdefault(name, 'ghq')
    for name in others:
        names.setdefault(name, 'ghq')
    return {n: k for n, k in names.items() if len(n) >= MIN_LENGTH and n.lower() not in public}


def drop(names, allowed, own):
    """names less the allowed ones and the name of the repository being pushed to."""
    own_name = re.sub(r'\.git$', '', (own or '').rstrip('/').replace('\\', '/').split('/')[-1].split(':')[-1]).lower()
    allowed = {a.lower() for a in allowed}
    return {n: k for n, k in names.items() if n.lower() not in allowed and n.lower() != own_name}


def _git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                          encoding='utf-8', errors='replace').stdout


def _target(name, words):
    """(pattern, needle) for a name, or None when the name is one dictionary word.

    The needle is a string every match contains, case-insensitively, for git grep."""
    parts = words_of(name)
    unknown = [w for w in parts if not w.isdigit() and w not in words]
    if unknown:
        return '(?i:' + SEPARATOR.join(map(re.escape, parts)) + ')', max(unknown, key=len)
    if len(parts) >= 2:
        return re.escape(name), name
    return None


def _targets(names, words):
    return {n: t for n in sorted(names, key=len, reverse=True) if (t := _target(n, words))}


def _matcher(targets):
    """One regex with a group per name; `lastgroup` says which name matched."""
    groups = '|'.join(f'(?P<n{i}>{pattern})' for i, (pattern, _) in enumerate(targets.values()))
    return re.compile(rf'(?<![A-Za-z0-9_])(?:{groups})(?![A-Za-z0-9_])')


def _hits(matcher, ordered, text):
    for match in matcher.finditer(text):
        yield match.start(), ordered[int(match.lastgroup[1:])]


def _scan_tree(repo, sha, names, targets, matcher):
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', suffix='.txt') as handle:
        handle.write('\n'.join(needle for _, needle in targets.values()) + '\n')
        patterns = handle.name
    ordered = list(targets)
    try:
        out = _git(repo, 'grep', '-n', '-I', '-i', '-F', '-f', patterns, sha, '--')
    finally:
        os.unlink(patterns)
    found = []
    for line in out.splitlines():
        rest = line[len(sha) + 1:] if line.startswith(sha + ':') else line
        path, _, rest = rest.partition(':')
        number, _, text = rest.partition(':')
        for start, name in _hits(matcher, ordered, text):
            found.append({'commit': sha[:7], 'path': path, 'line': int(number),
                          'col': start + 1, 'id': ident(name), 'kind': names[name]})
    return found


def _scan_added_lines(repo, commit, names, targets, matcher):
    found, seen, path, ordered = [], set(), None, list(targets)
    for line in _git(repo, 'show', '--format=', '--no-color', '--no-renames', '-U0', commit).splitlines():
        if line.startswith('+++ '):
            path = line[6:] if line.startswith('+++ b/') else None
        elif line.startswith('+') and path:
            for _, name in _hits(matcher, ordered, line[1:]):
                key = (path, name)
                if key not in seen:
                    seen.add(key)
                    found.append({'commit': commit[:7], 'path': path, 'line': None, 'col': None,
                                  'id': ident(name), 'kind': names[name]})
    return found


def scan(repo, pushes, names, remote, words=frozenset()):
    """Every hit in what the pushes would send: each tip's tree, and the lines other new commits add."""
    targets = _targets(names, words)
    if not targets:
        return []
    matcher = _matcher(targets)
    found = []
    for _, local, _, remote_sha in pushes:
        if local == ZERO:
            continue
        found += _scan_tree(repo, local, names, targets, matcher)
        if remote_sha == ZERO:
            commits = _git(repo, 'rev-list', local, '--not', f'--remotes={remote}').split()
        else:
            commits = _git(repo, 'rev-list', f'{remote_sha}..{local}').split()
        for commit in commits:
            if commit != local:
                found += _scan_added_lines(repo, commit, names, targets, matcher)
    return found


def report(found, allowed_path, script):
    lines = [f'pre-push: refused. {len(found)} place(s) carry the name of a repository you keep private',
             'or a clone ghq found. Names are not printed; each is shown as an 8-character id.',
             'By id, with the number of places:']
    counts, kinds = {}, {}
    for f in found:
        counts[f['id']] = counts.get(f['id'], 0) + 1
        kinds[f['id']] = f['kind']
    for an_id in sorted(counts, key=lambda i: (-counts[i], i)):
        lines.append(f'  {an_id}  {kinds[an_id]}  {counts[an_id]}')
    lines.append('Places:')
    for f in found[:SHOWN]:
        where = f'{f["path"]}:{f["line"]}:{f["col"]}' if f['line'] else f'{f["path"]} (added in {f["commit"]})'
        lines.append(f'  {where}  {f["id"]}  {f["kind"]}')
    if len(found) > SHOWN:
        lines.append(f'  ... and {len(found) - SHOWN} more')
    lines.append(f'See a name, in your own terminal: python {script} --explain ID')
    lines.append(f'If it is an ordinary word and not a leak, add it on its own line to {allowed_path}')
    return '\n'.join(lines)


def shown_path(path, cwd):
    """path relative to cwd for the message; absolute when on another drive."""
    try:
        return os.path.relpath(path, cwd).replace(os.sep, '/')
    except ValueError:
        return path


def explain(an_id, names):
    return sorted(n for n in names if ident(n) == an_id)


def _allowed(repo):
    path = _git(repo, 'rev-parse', '--git-path', ALLOWED).strip()
    path = path if os.path.isabs(path) else os.path.join(repo, path)
    try:
        with open(path, encoding='utf-8') as handle:
            entries = {l.strip() for l in handle if l.strip() and not l.startswith('#')}
    except OSError:
        entries = set()
    return entries, path


def main(argv):
    repo = os.getcwd()
    if len(argv) >= 3 and argv[1] == '--explain':
        for name in explain(argv[2], load_names()):
            print(name)
        return 0
    remote, url = (argv[1:3] + ['', ''])[:2]
    try:
        names = load_names()
    except NamesUnknown as error:
        print(f'pre-push: refused. The private repository names could not be listed ({error}).\n'
              'Sign in with gh and push again; nothing is passed unchecked.', file=sys.stderr)
        return 1
    allowed, allowed_path = _allowed(repo)
    found = scan(repo, parse_pushes(sys.stdin.read()), drop(names, allowed, url), remote or 'origin', load_words())
    if found:
        print(report(found, allowed_path, shown_path(os.path.abspath(__file__), repo)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
