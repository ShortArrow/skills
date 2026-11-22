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
whole words, in the tree of every pushed tip, in the lines every other pushed
commit adds, and in the message of every pushed commit and annotated tag.

The private Host and HostName values of ~/.ssh/config join the names: an alias
with no dot, a name ending in .local, .lan, .internal, .home or .ts.net, or an
address; lines with * or ? are skipped. Every IPv4 address is refused too,
except 127.0.0.0/8, 0.0.0.0, a netmask from 255.0.0.0 up, and the
documentation ranges of RFC 5737. Four numbers joined to a letter, a dot or a
`~` in front are a version, as in `OpenSSH.Server~~~~0.0.1.0`, not an address.

A refusal prints where each hit is and an 8-character id, never the name: the
message lands in terminals, agent transcripts and CI logs, and printing the name
there would be the leak it exists to stop. `--explain` maps an id back to its name
for the person at the keyboard. A value that is not a leak goes in the clone's
untracked `info/repo-names-allowed` (one per line), which is never pushed, because
an allow list of private names published would be the same leak.

When `gh` cannot list the names, or git cannot read what the push would send,
the push is refused: a check that passes because it could not look is not a check.
"""
import hashlib
import ipaddress
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
SSH_CONFIG = os.path.join(os.path.expanduser('~'), '.ssh', 'config')
IPV4 = re.compile(r'(?<![\w.~])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?!\w|\.[0-9])')
IPV4_GREP = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
PASSED_NETWORKS = [ipaddress.ip_network(n) for n in
                   ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24', '127.0.0.0/8')]
INTERNAL_SUFFIXES = ('.local', '.lan', '.internal', '.home', '.ts.net')


class ScanFailed(Exception):
    """git could not read what the push would send, so nothing can be passed."""


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


def load_ssh_names(path=SSH_CONFIG):
    """The private Host and HostName values of an ssh config, less every line with * or ?.

    Private means an alias with no dot, a name ending in an internal suffix, or
    an IPv4 address; a public name such as github.com would stop every push that
    mentions it."""
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            lines = handle.read().splitlines()
    except OSError:
        return set()
    names = set()
    for line in lines:
        match = re.match(r'\s*(host|hostname)\s*(?:=\s*|\s+)(.*)', line, re.IGNORECASE)
        if not match or '*' in line or '?' in line:
            continue
        for value in match.group(2).split('#')[0].split():
            value = value.strip('"')
            if value and not value.startswith('!') and _is_private_host(value):
                names.add(value)
    return names


def _is_private_host(value):
    name = value.rstrip('.').lower()
    return '.' not in name or name.endswith(INTERNAL_SUFFIXES) or _is_ipv4(name)


def _is_ipv4(text):
    try:
        ipaddress.IPv4Address(text)
    except ValueError:
        return False
    return True


def _says_nothing(address):
    """True for an address that names no machine: documentation, loopback, any, or a netmask."""
    if any(address in n for n in PASSED_NETWORKS) or int(address) == 0:
        return True
    host_bits = ~int(address) & 0xFFFFFFFF
    return address.packed[0] == 255 and host_bits & (host_bits + 1) == 0


def _addresses(text, skipped):
    """(start, address) for each IPv4 address in text that says something and is not skipped."""
    for match in IPV4.finditer(text):
        try:
            address = ipaddress.IPv4Address(match.group())
        except ValueError:
            continue
        if _says_nothing(address) or str(address) in skipped:
            continue
        yield match.start(), str(address)


def drop(names, allowed, own):
    """names less the allowed ones and the name of the repository being pushed to."""
    own_name = re.sub(r'\.git$', '', (own or '').rstrip('/').replace('\\', '/').split('/')[-1].split(':')[-1]).lower()
    allowed = {a.lower() for a in allowed}
    return {n: k for n, k in names.items() if n.lower() not in allowed and n.lower() != own_name}


def _git(repo, *args, ok=(0,)):
    """stdout of git in repo; ScanFailed when it exits with a code outside ok."""
    proc = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                          encoding='utf-8', errors='replace')
    if proc.returncode not in ok:
        raise ScanFailed(f'git {args[0]} exited {proc.returncode}: {proc.stderr.strip()[:200]}')
    return proc.stdout


def _is_commit(repo, sha):
    return subprocess.run(['git', '-C', repo, 'cat-file', '-e', f'{sha}^{{commit}}'],
                          capture_output=True).returncode == 0


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


def _scan_tree(repo, sha, finders):
    """Hits in the tree at sha: each finder is (git grep options, patterns, text -> (start, value, kind))."""
    found = []
    for options, patterns, find in finders:
        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', suffix='.txt') as handle:
            handle.write(patterns + '\n')
            pattern_file = handle.name
        try:
            out = _git(repo, 'grep', '-n', '-I', *options, '-f', pattern_file, sha, '--', ok=(0, 1))
        finally:
            os.unlink(pattern_file)
        for line in out.splitlines():
            rest = line[len(sha) + 1:] if line.startswith(sha + ':') else line
            path, _, rest = rest.partition(':')
            number, _, text = rest.partition(':')
            for start, value, kind in find(text):
                found.append({'commit': sha[:7], 'path': path, 'line': int(number),
                              'col': start + 1, 'id': ident(value), 'kind': kind})
    return found


def _scan_added_lines(repo, commit, finders):
    found, seen, path = [], set(), None
    for line in _git(repo, 'show', '--format=', '--no-color', '--no-renames', '-U0', commit).splitlines():
        if line.startswith('+++ '):
            path = line[6:] if line.startswith('+++ b/') else None
        elif line.startswith('+') and path:
            for _, _, find in finders:
                for _, value, kind in find(line[1:]):
                    key = (path, value.lower())
                    if key not in seen:
                        seen.add(key)
                        found.append({'commit': commit[:7], 'path': path, 'line': None, 'col': None,
                                      'id': ident(value), 'kind': kind})
    return found


def _finders(names, words, allowed):
    """The finders for the names, by the dictionary rule, and for IPv4 addresses."""
    finders = []
    targets = _targets(names, words)
    if targets:
        matcher, ordered = _matcher(targets), list(targets)
        finders.append((('-i', '-F'), '\n'.join(needle for _, needle in targets.values()),
                        lambda text: ((s, n, names[n]) for s, n in _hits(matcher, ordered, text))))
    skipped = {a.lower() for a in allowed} | {n.lower() for n in names}
    finders.append((('-E',), IPV4_GREP,
                    lambda text: ((s, a, 'ipv4') for s, a in _addresses(text, skipped))))
    return finders


def scan(repo, pushes, names, remote, words=frozenset(), allowed=frozenset()):
    """Every hit in what the pushes would send: each tip's tree, and the lines other new commits add.

    IPv4 addresses are checked beside the names, less those that name no
    machine, the allowed ones and those already among the names."""
    finders = _finders(names, words, allowed)
    found = []
    for _, local, _, remote_sha in pushes:
        if local == ZERO:
            continue
        found += _scan_tree(repo, local, finders)
        if remote_sha == ZERO or not _is_commit(repo, remote_sha):
            commits = _git(repo, 'rev-list', local, '--not', f'--remotes={remote}').split()
        else:
            commits = _git(repo, 'rev-list', f'{remote_sha}..{local}').split()
        if _git(repo, 'cat-file', '-t', local).strip() == 'tag':
            body = _git(repo, 'cat-file', 'tag', local).partition('\n\n')[2]
            found += _scan_message(body, local, '(tag message)', finders)
        for commit in commits:
            if commit != local:
                found += _scan_added_lines(repo, commit, finders)
            body = _git(repo, 'show', '-s', '--no-show-signature', '--format=%B', commit)
            found += _scan_message(body, commit, '(commit message)', finders)
    return found


def _scan_message(text, sha, label, finders):
    """Hits in a commit or tag message, one per value; the label stands where a path would."""
    seen = set()
    for _, _, find in finders:
        for _, value, kind in find(text):
            if value.lower() not in seen:
                seen.add(value.lower())
                yield {'commit': sha[:7], 'path': label, 'line': None, 'col': None,
                       'id': ident(value), 'kind': kind}


def report(found, allowed_path, script):
    lines = [f'pre-push: refused. {len(found)} place(s) carry the name of a repository you keep private,',
             'a clone ghq found, a host from ~/.ssh/config or an IPv4 address.',
             'Values are not printed; each is shown as an 8-character id.',
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
    lines.append(f'If it is not a leak, its owner adds it on its own line to {allowed_path}')
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


def _ssh_kinds():
    return {name: 'ssh' for name in load_ssh_names()}


def main(argv):
    repo = os.getcwd()
    if len(argv) >= 3 and argv[1] == '--explain':
        for name in explain(argv[2], {**_ssh_kinds(), **load_names()}):
            print(name)
        return 0
    remote, url = (argv[1:3] + ['', ''])[:2]
    try:
        names = load_names()
    except NamesUnknown as error:
        print(f'pre-push: refused. The private repository names could not be listed ({error}).\n'
              'Sign in with gh and push again; nothing is passed unchecked.', file=sys.stderr)
        return 1
    names = {**_ssh_kinds(), **names}
    try:
        allowed, allowed_path = _allowed(repo)
        found = scan(repo, parse_pushes(sys.stdin.read()), drop(names, allowed, url), remote or 'origin',
                     load_words(), allowed)
    except ScanFailed as error:
        print(f'pre-push: refused. What the push would send could not be read ({error}).\n'
              'Nothing is passed unchecked.', file=sys.stderr)
        return 1
    if found:
        print(report(found, allowed_path, shown_path(os.path.abspath(__file__), repo)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
