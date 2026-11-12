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
