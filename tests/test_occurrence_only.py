"""Tests for skills/test-design/scripts/occurrence-only.py, written before the script exists.

    python -m pytest tests/test_occurrence_only.py

The script reports a Python test whose every assertion says only that a call
happened, or how many times: it passes while the result is wrong, and passes as
well when a different path makes the same call.
"""
import os
import subprocess
import sys

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'skills', 'test-design', 'scripts', 'occurrence-only.py')


def scan(tmp_path, source, name='test_view.py'):
    path = tmp_path / name
    path.write_text(source, encoding='utf-8')
    proc = subprocess.run([sys.executable, SCRIPT, str(tmp_path)], capture_output=True, text=True, timeout=60)
    return proc.returncode, [line.split(': ', 1)[1] for line in proc.stdout.splitlines() if ': ' in line]


def test_a_test_that_only_checks_a_call_happened_is_reported(tmp_path):
    code, found = scan(tmp_path, (
        'def test_edit_redraws(view, renderer):\n'
        '    view.type("a")\n'
        '    renderer.redraw.assert_called_once()\n'))
    assert code == 1
    assert found == ['test_edit_redraws asserts only that a call happened, not what it carried or produced']


def test_counting_calls_or_reading_called_is_occurrence_too(tmp_path):
    code, found = scan(tmp_path, (
        'def test_a(m):\n    assert m.called\n    assert m.call_count == 1\n\n'
        'class TestB:\n    def test_b(self, m):\n        self.assertTrue(m.called)\n        self.assertEqual(m.call_count, 2)\n'))
    assert code == 1
    assert [f.split()[0] for f in found] == ['test_a', 'test_b']


def test_a_test_that_checks_what_was_carried_or_produced_passes(tmp_path):
    code, found = scan(tmp_path, (
        'def test_a(renderer):\n    renderer.redraw.assert_called_once_with(line=3)\n\n'
        'def test_b(view, m):\n    m.assert_called_once()\n    assert view.text == "a"\n\n'
        'class TestC:\n    def test_c(self, calc):\n        self.assertEqual(calc.add(1, 2), 3)\n\n'
        'def test_d(m):\n    assert m.call_args.kwargs["line"] == 3\n'))
    assert (code, found) == (0, [])


def test_checking_that_nothing_happened_is_not_occurrence(tmp_path):
    code, found = scan(tmp_path, 'def test_scroll_does_not_save(saver):\n    saver.save.assert_not_called()\n')
    assert (code, found) == (0, [])


def test_a_test_with_no_assertion_is_left_to_other_checks(tmp_path):
    code, found = scan(tmp_path, 'def test_smoke(app):\n    app.start()\n')
    assert (code, found) == (0, [])


def test_only_test_files_are_read_and_the_place_is_named(tmp_path):
    (tmp_path / 'helpers.py').write_text('def test_x(m):\n    m.assert_called()\n', encoding='utf-8')
    path = tmp_path / 'sub' / 'view_test.py'
    path.parent.mkdir()
    path.write_text('\n\ndef test_x(m):\n    m.assert_called()\n', encoding='utf-8')
    proc = subprocess.run([sys.executable, SCRIPT, str(tmp_path)], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 1
    assert [line.split(': ', 1)[0] for line in proc.stdout.splitlines()] == [f'{path}:3']
