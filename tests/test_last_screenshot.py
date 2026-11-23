"""Tests for skills/last-screenshot/scripts/last-screenshot.py, written before the script exists.

    python -m pytest tests/test_last_screenshot.py

The script prints the path of the user's most recent screenshot, or says why there is
none. Where each platform saves a screenshot comes from the platform's own tools:
Windows' Pictures\\Screenshots, macOS's `com.apple.screencapture location` (the
Desktop when unset), and XDG Pictures/Screenshots then Pictures on Linux (GNOME 42
and Spectacle since 2023 use the first, older Spectacle the second).
"""
import importlib.util
import os
import subprocess
import sys

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'skills', 'last-screenshot', 'scripts', 'last-screenshot.py')


def script():
    spec = importlib.util.spec_from_file_location('last_screenshot', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def answers(mapping):
    """A run(argv) stand-in that answers by the command's first word, '' when unknown."""
    return lambda argv: mapping.get(argv[0], '')


def touch(path, mtime):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG')
    os.utime(path, (mtime, mtime))
    return path


# --- where each platform keeps them -----------------------------------------

def test_windows_looks_in_pictures_screenshots_under_the_user_profile(tmp_path):
    found = script().folders('Windows', home='C:/ignored', env={'USERPROFILE': str(tmp_path)}, run=answers({}))
    assert found == [os.path.join(str(tmp_path), 'Pictures', 'Screenshots')]


def test_macos_reads_the_screencapture_location_and_expands_the_home(tmp_path):
    home = str(tmp_path)
    found = script().folders('Darwin', home=home, env={}, run=answers({'defaults': '~/Shots\n'}))
    assert found == [os.path.join(home, 'Shots')]
    found = script().folders('Darwin', home=home, env={}, run=answers({'defaults': '/Volumes/x/caps\n'}))
    assert found == ['/Volumes/x/caps']


def test_macos_falls_back_to_the_desktop_when_no_location_is_set(tmp_path):
    found = script().folders('Darwin', home=str(tmp_path), env={}, run=answers({}))
    assert found == [os.path.join(str(tmp_path), 'Desktop')]


def test_linux_looks_in_xdg_pictures_screenshots_then_pictures(tmp_path):
    pictures = os.path.join(str(tmp_path), 'Bilder')
    found = script().folders('Linux', home=str(tmp_path), env={}, run=answers({'xdg-user-dir': pictures + '\n'}))
    assert found == [os.path.join(pictures, 'Screenshots'), pictures]


def test_linux_uses_home_pictures_when_xdg_has_no_answer_or_answers_the_home(tmp_path):
    home = str(tmp_path)
    expected = [os.path.join(home, 'Pictures', 'Screenshots'), os.path.join(home, 'Pictures')]
    assert script().folders('Linux', home=home, env={}, run=answers({})) == expected
    assert script().folders('Linux', home=home, env={}, run=answers({'xdg-user-dir': home + '\n'})) == expected


# --- which one is the last ---------------------------------------------------

def test_the_newest_image_across_the_folders_is_the_last(tmp_path):
    first, second = tmp_path / 'Screenshots', tmp_path / 'Pictures'
    touch(first / 'old.png', 1_000)
    newest = touch(second / 'new.jpg', 3_000)
    touch(first / 'notes.txt', 9_000)
    touch(first / 'clip.mov', 9_000)
    touch(first / 'nested' / 'deep.png', 9_000)
    path, reason = script().newest([str(first), str(second)])
    assert (path, reason) == (str(newest), None)


def test_no_folder_says_so(tmp_path):
    path, reason = script().newest([str(tmp_path / 'absent')])
    assert path is None and 'no screenshot folder' in reason and 'absent' in reason


def test_an_empty_folder_says_so(tmp_path):
    (tmp_path / 'Screenshots').mkdir()
    (tmp_path / 'Screenshots' / 'readme.txt').write_text('x')
    path, reason = script().newest([str(tmp_path / 'Screenshots')])
    assert path is None and 'no screenshot in' in reason


# --- as the skill runs it ----------------------------------------------------

@pytest.mark.skipif(sys.platform == 'darwin', reason='macOS reads the real screencapture setting')
def test_the_script_prints_the_path_or_the_reason(tmp_path):
    env = {**os.environ, 'USERPROFILE': str(tmp_path), 'HOME': str(tmp_path), 'XDG_CONFIG_HOME': str(tmp_path / 'cfg')}
    run = lambda: subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, env=env)
    empty = run()
    assert empty.returncode == 1 and 'no screenshot folder' in empty.stdout
    shot = touch(tmp_path / 'Pictures' / 'Screenshots' / 'Screenshot 2026-11-22 141500.png', 5_000)
    found = run()
    assert found.returncode == 0 and found.stdout.strip() == str(shot)
