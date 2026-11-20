"""Tests for hooks/docs-follow.py, written before the hook exists.

    python tests/test_docs_follow.py

The gate refuses a push whose outgoing commits change a surface — a skill's
frontmatter, a hook, the marketplace — while no living document followed in the
same commit. Each case below fixes one decision the hook has to make, and the
expected values come from clean-docs and i18n-parity, not from the hook.
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'docs-follow.py')
spec = importlib.util.spec_from_file_location('docs_follow', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

PASS, FAIL = [], []


def check(name, got, want):
    """Record a comparison, and under a runner that collects test_* also raise.

    Run as a script the checks are counted and reported together, so one
    failure does not hide the rest.  A collecting runner calls each test_*
    itself and reads an exception as the failure, so a silent list would let
    it report green while FAIL filled up.
    """
    (PASS if got == want else FAIL).append(name)
    if got != want:
        print(f'FAIL {name}\n  want {want!r}\n  got  {got!r}')
        if __name__ != '__main__':
            raise AssertionError(f'{name}: want {want!r}, got {got!r}')


# --- what counts as a surface, and what follows it -------------------------

def test_classify():
    """A surface is code or configuration a reader depends on; a document follows it."""
    check('skill body is a document', hook.classify('skills/own-the-call/SKILL.md'), 'document')
    check('README is a document', hook.classify('README.md'), 'document')
    check('docs/ is a document', hook.classify('docs/design-intent.md'), 'document')
    check('hook is a surface', hook.classify('hooks/verify-reports.py'), 'surface')
    check('marketplace is a surface', hook.classify('.claude-plugin/marketplace.json'), 'surface')
    check('script is a surface', hook.classify('scripts/peer-sessions.sh'), 'surface')
    check('test is neither', hook.classify('tests/test_wait_stop.py'), None)
    check('fixture is neither', hook.classify('tests/fixtures/sweep/kilo.py'), None)
    check('CHANGELOG is a record, not a document',
          hook.classify('CHANGELOG.md'), 'record')
    check('the exceptions file is neither, or excusing a commit needs another excuse',
          hook.classify('hooks/docs-follow-exceptions.txt'), None)


def test_records_are_never_required_to_follow():
    """clean-docs: a record freezes when written. Touching one does not satisfy the gate."""
    commit = {'sha': 'a' * 40, 'paths': ['hooks/verify-reports.py', 'CHANGELOG.md']}
    check('a record does not count as following', hook.unfollowed([commit]), [commit])


# --- the core judgement ----------------------------------------------------

def test_surface_with_a_document_passes():
    commit = {'sha': 'b' * 40,
              'paths': ['hooks/verify-reports.py', 'skills/adversarial-verify/SKILL.md']}
    check('surface followed by a document', hook.unfollowed([commit]), [])


def test_surface_alone_is_refused():
    commit = {'sha': 'c' * 40, 'paths': ['hooks/verify-reports.py']}
    check('surface with nothing following', hook.unfollowed([commit]), [commit])


def test_document_alone_passes():
    """A prose edit has no surface to follow. i18n-parity: a check that forbids
    legitimate one-sided edits gets switched off."""
    commit = {'sha': 'd' * 40, 'paths': ['README.md']}
    check('document alone', hook.unfollowed([commit]), [])


def test_tests_alone_pass():
    commit = {'sha': 'e' * 40, 'paths': ['tests/test_wait_stop.py']}
    check('tests alone', hook.unfollowed([commit]), [])


def test_each_commit_is_judged_alone():
    """A document in a later commit does not excuse an earlier commit's surface:
    the push is refused on the commit that lacks it."""
    bare = {'sha': 'f' * 40, 'paths': ['hooks/verify-reports.py']}
    doc = {'sha': '0' * 40, 'paths': ['README.md']}
    check('one bare commit among two', hook.unfollowed([bare, doc]), [bare])


# --- the exception, copied from i18n-parity --------------------------------

def test_exception_is_declared_as_a_commit():
    """Pinning a path would be a permanent hole. The exception names a sha, so the
    next commit to touch the file leaves it matching nothing."""
    commit = {'sha': '1' * 40, 'paths': ['hooks/verify-reports.py']}
    check('declared commit is excused',
          hook.unfollowed([commit], excused={'1' * 40}), [])
    check('a different commit is not excused',
          hook.unfollowed([commit], excused={'2' * 40}), [commit])


def test_exception_file_parses_reasons_and_full_hashes():
    text = (
        '# a renamed internal symbol, no public surface changed\n'
        f'{"3" * 40}  internal rename of _walk\n'
        '\n'
        f'{"4" * 40}  wiring only\n'
    )
    check('two shas parsed', hook.parse_exceptions(text), {'3' * 40, '4' * 40})
    check('abbreviated sha refused', hook.parse_exceptions('3fa9c2b  too short\n'), set())
    check('a sha with no reason is a silenced check',
          hook.parse_exceptions(f'{"5" * 40}\n'), set())


def test_spent_exceptions_are_named_so_the_file_can_be_pruned():
    """i18n-parity: an expired entry is indistinguishable from a working one by
    reading, so every run reports which entries no longer match an outgoing commit."""
    commits = [{'sha': '8' * 40, 'paths': ['hooks/verify-reports.py']}]
    excused = {'8' * 40, '9' * 40}
    check('the entry still in use is not reported spent',
          hook.spent(commits, excused), {'9' * 40})
    check('nothing outgoing means every entry is spent',
          hook.spent([], {'9' * 40}), {'9' * 40})


def test_signature_banner_is_not_mistaken_for_a_path():
    """git show writes the gpg banner to stdout on this machine, so a signed
    commit's --name-only output carries lines that are not paths. A junk line
    classifies as neither and is harmless today, but it would mask a real path."""
    raw = '\n'.join([
        'gpg: Signature made 11/10/26 17:07:04 Tokyo Standard Time',
        'gpg:                using EDDSA key 2F300FD08BFAE8C282',
        'gpg: Good signature from "ShortArrow (hi!) <a@b.c>" [ultimate]',
        'hooks/docs-follow.py',
        '',
    ])
    check('only the real path survives', hook.paths_of(raw), ['hooks/docs-follow.py'])
    check('a banner-only output yields nothing',
          hook.paths_of('gpg: Good signature from "x" [ultimate]\n'), [])
    check('a path with spaces is kept',
          hook.paths_of('docs/a b.md\n'), ['docs/a b.md'])


# --- the verdict the host acts on -----------------------------------------

def test_verdict_is_a_deny_on_push_only():
    def verdict(command, commits):
        payload = {'tool_input': {'command': command}}
        return hook.push_verdict(payload, commits)

    bare = [{'sha': '6' * 40, 'paths': ['hooks/verify-reports.py']}]
    out = verdict('git push origin main', bare)
    check('push is denied', (out or {}).get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')
    check('the reason names the commit',
          '6' * 7 in ((out or {}).get('hookSpecificOutput', {}) or {}).get('permissionDecisionReason', ''),
          True)
    check('a non-push command is untouched', verdict('git status', bare), None)
    check('a clean push passes',
          verdict('git push', [{'sha': '7' * 40, 'paths': ['README.md']}]), None)


# --- which repository the push runs in -----------------------------------

def test_push_target_follows_cd_and_dash_c():
    """The hook's cwd is the session's, not the push's. A `cd` before the push
    and git's -C both move the repository the push sends from, and the outgoing
    commits are read there."""
    def target(command, cwd='/a', windows=False):
        got = hook.push_target(command, cwd, windows=windows)
        return None if got is None else got.replace('\\', '/')

    check('a bare push runs in cwd', target('git push origin main'), '/a')
    check('cd to an absolute path', target('cd /b && git push'), '/b')
    check('cd to a relative path', target('cd sub && git push'), '/a/sub')
    check('cd then ; then push', target('cd /b; git push'), '/b')
    check('a quoted path with a space', target('cd "/b c" && git push'), '/b c')
    check('a command between cd and push', target('cd /b && git status && git push'), '/b')
    check('a cd after the push does not count', target('git push && cd /b'), '/a')
    check('two cds compose', target('cd /b && cd c && git push'), '/b/c')
    check('git -C absolute', target('git -C /b push'), '/b')
    check('git -C relative', target('git -C sub push'), '/a/sub')
    check('cd then git -C relative', target('cd /b && git -C c push'), '/b/c')
    check('two -C compose', target('git -C /b -C c push'), '/b/c')
    check('-c before -C is skipped', target('git -c x.y=1 -C /b push'), '/b')
    check('an env prefix before git', target('cd /b && GIT_TRACE=0 git push'), '/b')
    check('newline separates commands', target('cd /b\ngit push'), '/b')
    check('PowerShell Set-Location', target('Set-Location /b; git push'), '/b')
    check('PowerShell Set-Location -Path', target('Set-Location -Path /b; git push'), '/b')
    check('cd - cannot be followed', target('cd - && git push'), None)
    check('Git Bash drive path on Windows',
          target('cd /v/github.com/x && git push', cwd='C:/w', windows=True), 'V:/github.com/x')
    check('a single-letter root is not a drive off Windows',
          target('cd /v/x && git push'), '/v/x')
    check('no push, no target', target('cd /b && git status'), None)


def _git(cwd, *args):
    subprocess.run(['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=' + _NO_HOOKS]
                   + list(args), cwd=cwd, check=True, capture_output=True)


_NO_HOOKS = None


def _clone_with(tmp, name, path):
    """A clone of its own bare remote, one commit ahead that touches `path`."""
    bare = os.path.join(tmp, name + '.git')
    work = os.path.join(tmp, name)
    _git(tmp, 'init', '--bare', '-b', 'main', bare)
    _git(tmp, 'clone', bare, work)
    _git(work, 'config', 'user.email', 'x@example.invalid')
    _git(work, 'config', 'user.name', 'x')
    with open(os.path.join(work, 'README.md'), 'w') as f:
        f.write('x\n')
    _git(work, 'add', '.')
    _git(work, 'commit', '-m', 'base')
    _git(work, 'push', 'origin', 'main')
    os.makedirs(os.path.dirname(os.path.join(work, path)), exist_ok=True)
    with open(os.path.join(work, path), 'w') as f:
        f.write('y\n')
    _git(work, 'add', '.')
    _git(work, 'commit', '-m', 'ahead')
    return work


def test_the_pushed_repository_is_the_one_checked():
    """End to end: the session sits in a clean clone and pushes another one whose
    outgoing commit changes a hook alone. The other clone is the one judged."""
    import tempfile
    global _NO_HOOKS
    with tempfile.TemporaryDirectory() as tmp:
        _NO_HOOKS = os.path.join(tmp, 'no-hooks')
        os.makedirs(_NO_HOOKS)
        clean = _clone_with(tmp, 'clean', 'README.md')
        bare = _clone_with(tmp, 'bare', 'hooks/x.py')

        def run(command, cwd):
            payload = json.dumps({'tool_input': {'command': command}, 'cwd': cwd})
            proc = subprocess.run([sys.executable, HOOK], input=payload.encode(),
                                  capture_output=True)
            return b'"deny"' in proc.stdout

        fwd = bare.replace('\\', '/')
        check('cd into the bare clone is refused', run(f'cd "{fwd}" && git push', clean), True)
        check('git -C the bare clone is refused', run(f'git -C "{fwd}" push', clean), True)
        check('pushing the clean clone from the bare one passes',
              run(f'cd "{clean.replace(chr(92), "/")}" && git push', bare), False)
        check('a bare push from the bare clone is still refused', run('git push', bare), True)


def test_unreadable_input_lets_the_call_through():
    """verify-reports.py's rule: the gate is a check on the agent, not a lock on
    the user. A git failure must not strand the push."""
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=b'{"tool_input": {"command": "git push"}, "cwd": "/nonexistent-xyz"}',
        capture_output=True)
    check('no verdict on an unreadable repository', proc.stdout, b'')
    check('exit 0 on an unreadable repository', proc.returncode, 0)


def test_non_json_stdin_is_survived():
    proc = subprocess.run([sys.executable, HOOK], input=b'not json', capture_output=True)
    check('no verdict on junk stdin', proc.stdout, b'')
    check('exit 0 on junk stdin', proc.returncode, 0)


def main():
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, '__name__', '').startswith('test_'):
            fn()
    print(f'\n{len(PASS)} passed, {len(FAIL)} failed')
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
