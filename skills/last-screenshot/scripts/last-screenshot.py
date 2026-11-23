"""Print the path of the user's most recent screenshot, or why there is none.

    python last-screenshot.py

Exit 0 with the path on stdout, or exit 1 with the reason on stdout. Only the
folders the platform's own screenshot tool saves to are read, not their
subfolders, and only image files count:

  Windows  %USERPROFILE%\\Pictures\\Screenshots (Win+PrtScn, Snipping Tool)
  macOS    `defaults read com.apple.screencapture location`, else ~/Desktop
  Linux    $(xdg-user-dir PICTURES)/Screenshots (GNOME 42 and later, Spectacle
           since late 2023), then $(xdg-user-dir PICTURES) itself (older
           Spectacle); ~/Pictures when xdg-user-dir has no answer
"""
import os
import platform
import subprocess
import sys

IMAGES = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.heic')


def run(argv):
    """stdout of a command, or '' when it is missing or fails."""
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return ''
    return proc.stdout if proc.returncode == 0 else ''


def expand(path, home):
    if path == '~':
        return home
    return os.path.join(home, path[2:]) if path.startswith(('~/', '~\\')) else path


def folders(system, home, env, run=run):
    """The folders to look in, in order, for the platform named by platform.system()."""
    if system == 'Windows':
        return [os.path.join(env.get('USERPROFILE') or home, 'Pictures', 'Screenshots')]
    if system == 'Darwin':
        location = run(['defaults', 'read', 'com.apple.screencapture', 'location']).strip()
        return [expand(location, home) if location else os.path.join(home, 'Desktop')]
    pictures = run(['xdg-user-dir', 'PICTURES']).strip()
    if not pictures or os.path.normpath(pictures) == os.path.normpath(home):
        pictures = os.path.join(home, 'Pictures')
    return [os.path.join(pictures, 'Screenshots'), pictures]


def newest(dirs):
    """(path, None) for the most recently modified image in dirs, or (None, the reason)."""
    present = [d for d in dirs if os.path.isdir(d)]
    if not present:
        return None, 'no screenshot folder: ' + ', '.join(dirs) + ' does not exist'
    images = []
    for folder in present:
        for entry in os.scandir(folder):
            if entry.is_file() and entry.name.lower().endswith(IMAGES):
                images.append((entry.stat().st_mtime, entry.path))
    if not images:
        return None, 'no screenshot in ' + ', '.join(present)
    return max(images)[1], None


def main():
    home = os.path.expanduser('~')
    path, reason = newest(folders(platform.system(), home, os.environ))
    print(path or reason)
    return 0 if path else 1


if __name__ == '__main__':
    sys.exit(main())
