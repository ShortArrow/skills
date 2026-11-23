"""Tests for hooks/pr-body-check.py, written before the hook exists.

    python -m pytest tests/test_pr_body_check.py

The hook refuses a pull request body that breaks pull-request's mechanical rules,
and the 120-character first body only where the receiving repository is known to
be small. Each case fixes one decision; the expected values come from
skills/pull-request/SKILL.md, not from the hook.
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'pr-body-check.py')
SHA = 'c' * 40
LONG = 'This body explains every file the diff touches, one by one, and then repeats it again for good measure, padding past the limit.'


def load():
    spec = importlib.util.spec_from_file_location('pr_body_check', HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repo(tmp_path, url='https://github.com/me/tool.git', template=None):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    subprocess.run(['git', '-C', str(tmp_path), 'remote', 'add', 'origin', url], check=True)
    if template is not None:
        (tmp_path / '.github').mkdir()
        (tmp_path / '.github' / 'pull_request_template.md').write_text(template, encoding='utf-8')
    return tmp_path


def run(command, cwd, user='me'):
    """The hook's output for a Bash call, as the client runs it."""
    payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': command}, 'cwd': str(cwd)})
    env = {**os.environ, 'PR_BODY_CHECK_GH_USER': user}
    proc = subprocess.run([sys.executable, HOOK], input=payload.encode('utf-8'), capture_output=True, env=env)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def decision(out):
    return out.get('hookSpecificOutput', {}).get('permissionDecision')


def context(out):
    return out.get('hookSpecificOutput', {}).get('additionalContext', '')


# --- refused in every repository -------------------------------------------

def test_an_unpinned_blob_link_is_refused_and_a_pinned_one_passes(tmp_path):
    r = repo(tmp_path)
    bad = run("gh pr edit 3 --body 'See https://github.com/me/tool/blob/main/src/a.py#L4'", r)
    assert decision(bad) == 'deny' and 'pinned' in bad['hookSpecificOutput']['permissionDecisionReason']
    good = run(f"gh pr edit 3 --body 'See https://github.com/me/tool/blob/{SHA}/src/a.py#L4'", r)
    assert decision(good) is None


def test_a_line_broken_with_two_spaces_or_a_backslash_is_refused_outside_code(tmp_path):
    r = repo(tmp_path)
    (r / 'body.md').write_text('First line  \nsecond line\\\nthird\n', encoding='utf-8')
    assert decision(run('gh pr edit 3 --body-file body.md', r)) == 'deny'
    (r / 'code.md').write_text('Run:\n\n```sh\nmake \\\n  test\n```\n', encoding='utf-8')
    assert decision(run('gh pr edit 3 --body-file code.md', r)) is None


def test_a_verified_heading_is_refused_unless_the_template_asks_for_it(tmp_path):
    r = repo(tmp_path)
    for heading in ('## Verified', '### Confirmed', '## 検証'):
        (r / 'body.md').write_text(f'Why.\n\n{heading}\n\nIt works.\n', encoding='utf-8')
        assert decision(run('gh pr edit 3 --body-file body.md', r)) == 'deny', heading


def test_a_heading_the_repositorys_template_has_is_allowed(tmp_path):
    r = repo(tmp_path, url='https://github.com/bigorg/project.git', template='## Verification\n\n- [ ] tests\n')
    (r / 'body.md').write_text('## Verification\n\nRan the suite.\n', encoding='utf-8')
    assert decision(run('gh pr edit 3 --body-file body.md', r)) is None


# --- the 120-character first body --------------------------------------------

def test_scale_is_small_for_the_users_own_repository_without_a_template():
    hook = load()
    assert hook.scale(owner='me', login='me', template=None) == 'small'
    assert hook.scale(owner='Me', login='me', template=None) == 'small'


def test_scale_is_large_for_someone_elses_repository_with_a_template():
    assert load().scale(owner='bigorg', login='me', template='## Summary\n') == 'large'


def test_scale_is_unknown_when_the_cues_disagree_or_are_missing():
    hook = load()
    assert hook.scale(owner='me', login='me', template='## Summary\n') is None
    assert hook.scale(owner='someone', login='me', template=None) is None
    assert hook.scale(owner=None, login='me', template=None) is None
    assert hook.scale(owner='me', login=None, template=None) is None


def test_a_long_first_body_is_refused_on_a_small_repository(tmp_path):
    out = run(f"gh pr create --draft --title t --body '{LONG}'", repo(tmp_path))
    assert decision(out) == 'deny' and '120' in out['hookSpecificOutput']['permissionDecisionReason']


def test_a_short_first_body_passes_on_a_small_repository(tmp_path):
    assert decision(run("gh pr create --draft --title t --body 'Closes #12.'", repo(tmp_path))) is None


def test_a_long_first_body_passes_on_a_large_repository(tmp_path):
    r = repo(tmp_path, url='git@github.com:bigorg/project.git', template='## Summary\n\n## Testing\n')
    assert decision(run(f"gh pr create --title t --body '{LONG}'", r)) is None


def test_when_the_scale_is_unknown_a_long_first_body_gets_context_not_a_refusal(tmp_path):
    r = repo(tmp_path, url='https://github.com/someone/small.git')
    out = run(f"gh pr create --draft --title t --body '{LONG}'", r)
    assert decision(out) is None
    assert '120' in context(out)


def test_the_full_body_put_in_with_edit_has_no_length_limit(tmp_path):
    r = repo(tmp_path)
    (r / 'body.md').write_text(LONG * 4 + '\n', encoding='utf-8')
    assert decision(run('gh pr edit 3 --body-file body.md', r)) is None


def test_the_repo_flag_names_the_receiving_repository(tmp_path):
    r = repo(tmp_path, url='https://github.com/me/tool.git')
    out = run(f"gh pr create -R someone/else --title t --body '{LONG}'", r)
    assert decision(out) is None


# --- what the hook cannot read -----------------------------------------------

def test_a_body_built_by_the_shell_gets_context_not_a_refusal(tmp_path):
    r = repo(tmp_path)
    command = "gh pr create --title t --body \"$(cat <<'EOF'\nSee https://github.com/me/tool/blob/main/a.py\nEOF\n)\""
    out = run(command, r)
    assert decision(out) is None
    assert context(out)


def test_other_commands_are_left_alone(tmp_path):
    r = repo(tmp_path)
    for command in ('gh pr view 3', 'gh pr list', 'git push', "echo 'gh pr create --body x  '"):
        assert run(command, r) == {}, command
