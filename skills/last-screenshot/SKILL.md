---
name: last-screenshot
description: Read the screenshot the user took most recently, triggered by the moments the user points at their screen in words alone ("this", "which one?", これ, どれ?, "look at this error") or types /last-screenshot. Finds the newest image in the folder the platform's own screenshot tool saves to (Windows Pictures\Screenshots, the macOS screencapture location, XDG Pictures/Screenshots on Linux), reads it, and answers the message before it. Not for taking a screenshot of an app or a page; that is any-screenshot's.
---

# Last screenshot

**"This" on the user's screen is a picture the agent has not seen.** The user took it a moment ago,
and it is already on disk in the folder their screenshot key saves to.
Reading the newest image there answers the question about it;
asking which one they mean costs them the moment they meant it in.

## Procedure

1. Run `python <this skill>/scripts/last-screenshot.py`.
   It prints the path of the newest image and exits 0,
   or prints why there is none and exits 1.
2. On exit 1, say what it printed — the folder does not exist,
   or holds no image — and stop.
   Do not search other folders for it:
   a picture found elsewhere is a guess at what the user meant.
3. On exit 0, read the path with the file-reading tool,
   which shows an image to the model.
4. Answer the user's message before the command with the picture in hand.
   Say which file was read, by its name and time,
   so a stale or wrong capture is caught at once.

## Where each platform saves

| Platform | Folder read | Set by |
|---|---|---|
| Windows | `%USERPROFILE%\Pictures\Screenshots` | Win+PrtScn and the Snipping Tool's automatic save |
| macOS | the `com.apple.screencapture` `location` default, else `~/Desktop` | `defaults write com.apple.screencapture location`, or Options in the Screenshot app |
| Linux | `$(xdg-user-dir PICTURES)/Screenshots`, then `$(xdg-user-dir PICTURES)` | GNOME 42 and later, and Spectacle since late 2023, use the first; older Spectacle the second |

Only those folders are read, not their subfolders,
and only image files count; the newest by modification time is the last.

Two cases the script cannot see:
GNOME translates the `Screenshots` folder name into the user's language,
so a non-English desktop saves to a folder it does not look in;
and a Windows Pictures folder moved into OneDrive saves under the OneDrive path.
Either one ends at step 2 with "no screenshot folder",
and the user can say where theirs go.

A screenshot can hold anything that was on the screen.
This skill reads one, the newest,
and only when the user has pointed at it.

## How this connects

`any-screenshot` takes a capture of a window, a page or a desktop;
this skill reads the one the user already took.

## Sources

Read on 2026-11-22.

- macOS: the Desktop default and `defaults write com.apple.screencapture location`,
  macrumors.com/how-to/change-screenshots-folder.
- GNOME: screenshots are stored to (xdg-)Pictures/Screenshots from GNOME 42,
  gnome-shell commit "screenshot-ui: Store screenshots to files" (commits-list, January 2022),
  and the localised folder name,
  gitlab.gnome.org/GNOME/gnome-shell/-/issues/5454.
- KDE Spectacle: the default moved to `~/Pictures/Screenshots` in November 2023,
  bugs.kde.org/show_bug.cgi?id=474594.
