"""Characterisation tests for skills/repair-skill/scripts/session-steps.py.

    python tests/test_session_steps.py
"""
import importlib.util
import os

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location(
    'session_steps', os.path.join(ROOT, 'skills', 'repair-skill', 'scripts', 'session-steps.py'))
session_steps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_steps)
FIXTURE = os.path.join(HERE, 'fixtures', 'brokenskill', 'session.jsonl')


def steps():
    return session_steps.read_steps(FIXTURE)


def test_every_step_carries_its_transcript_line():
    lines = [s.line for s in steps()]
    assert lines == sorted(lines) and lines[0] >= 1


def test_the_skill_invocation_is_named():
    assert any(s.kind == 'Skill' and s.detail == 'daily-summary' for s in steps())


def test_the_command_and_its_result_are_paired():
    seq = steps()
    i = next(k for k, s in enumerate(seq) if s.kind == 'Bash' and 'fetch.py' in s.detail)
    assert seq[i + 1].kind == 'result' and seq[i + 1].detail.startswith('ok:')


def test_an_error_result_is_flagged():
    assert any(s.kind == 'result' and s.detail.startswith('error:') for s in steps())


def test_a_later_user_message_is_a_correction():
    corrections = [s for s in steps() if s.kind == 'correction']
    assert len(corrections) == 1 and '100' in corrections[0].detail


def test_summary_lists_skill_files_and_corrections():
    summary = session_steps.summarise(steps())
    assert summary['skills'] == ['daily-summary']
    assert any(p.endswith('daily-summary/SKILL.md') for p in summary['skill_files'])
    assert len(summary['errors']) == 1 and len(summary['corrections']) == 1


def test_a_session_id_resolves_under_the_projects_directory(tmp_path=None):
    import tempfile, shutil
    with tempfile.TemporaryDirectory() as home:
        proj = os.path.join(home, 'projects', 'V--some-repo')
        os.makedirs(proj)
        shutil.copy(FIXTURE, os.path.join(proj, 'abc-123.jsonl'))
        assert session_steps.locate('abc-123', home) == os.path.join(proj, 'abc-123.jsonl')
        assert session_steps.locate(FIXTURE, home) == FIXTURE


if __name__ == '__main__':
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            try:
                fn()
                print('PASS', name)
            except Exception as error:
                failed += 1
                print('FAIL', name, repr(error))
    raise SystemExit(1 if failed else 0)
