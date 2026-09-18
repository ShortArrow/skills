# temp

Drafts, not installed skills.
Nothing here is listed in `.claude-plugin/marketplace.json`,
so no host loads it until it is moved into `skills/` and added there.

## Where this came from

Three skills generalised out of one private repository's Hyper-V setup:
a Windows 11 guest kept running as the fixture for an Avalonia application's UI Automation suite,
driven from the host over SSH, with a runner,
a deployment script and a provisioning script behind it.
Product names, the application's own paths and its mock hardware gateway have been stripped;
what is left is the part that holds for any Windows guest.

| Draft | What it owns |
|---|---|
| `windows-interactive-session` | Session 0 against the logged-on session: autologon, the interactive scheduled task, the marker-file handoff, where the screen may be measured |
| `windows-ssh-commands` | The command channel: file-plus-`-File` over `-EncodedCommand`, BOMs, CLIXML, exit codes, the two ssh clients' path rules |
| `hyperv-persistent-vm` | The long-lived guest: staged checkpoints, dynamic memory, finding the address, the VMConnect console, what persistence costs |

## The scripts

Seven files, generalised from the same repository and following `windows-sandbox`'s framing:
a reference implementation to copy into a project,
never a runtime dependency,
because a project's runner has to work for a person and for a CI runner and neither has a skill installed.

| File | From |
|---|---|
| `windows-ssh-commands/scripts/GuestSsh.ps1` | the helper functions the runner, the deployer and the provisioner each had their own copy of |
| `windows-interactive-session/scripts/Invoke-GuestInteractiveRun.ps1` | the host side of the UI runner, with the product's staging and its mock gateway removed |
| `windows-interactive-session/scripts/guest-run-template.ps1` | the guest side of the same runner, reduced to the part that is the same every time |
| `windows-interactive-session/scripts/Test-GuestReadiness.ps1` | its readiness check |
| `hyperv-persistent-vm/scripts/New-HyperVFixtureVM.ps1` | the provisioning script; its .NET 10 stage became `-WingetPackage` plus a verification expression |
| `hyperv-persistent-vm/scripts/Get-HyperVGuestAddress.ps1` | the address lookup that was copied into four scripts |
| `hyperv-persistent-vm/scripts/Show-HyperVConsole.ps1` | unchanged but for the language of its help |

They parse (`[System.Management.Automation.Language.Parser]::ParseFile`) and are ASCII-only,
deliberately: a BOM-less non-ASCII `.ps1` is read as ANSI by the Windows PowerShell on the far end. **None of them has been run end to end since being generalised** — that needs a Hyper-V host with a guest on it,
and it is the first thing to do before any of this moves into `skills/`.

## Before moving any of them into `skills/`

- **Run them against a real guest.** The originals worked;
  these have had names, stages and parameters changed,
  and the here-strings that build guest-side scripts are exactly where that breaks quietly.
- **Decide the cross-skill dependency.** Two scripts dot-source `GuestSsh.ps1` from a sibling skill,
  defaulting to `../../windows-ssh-commands/scripts/GuestSsh.ps1` and taking `-GuestSshPath` otherwise.
  That default holds only when both skills are installed.
  Either accept it (the copy-it-in framing means it rarely matters),
  or give each skill its own copy and accept the duplication.
- **Decide the boundary with `hyperv-clean-vm`.** It already carries the Hyper-V Administrators group,
  the password-before-the-first-checkpoint rule,
  the administrators' key file and checkpoint chaining.
  `hyperv-persistent-vm` cross-references it rather than repeating it,
  but the two descriptions have to say which one owns which case,
  or whichever fires first wins.
  Merging the two is a live option;
  so is keeping `hyperv-persistent-vm` as the runner-side companion.
- **`windows-ssh-commands` overlaps `hyperv-clean-vm`'s "Facts that bite" table** on quoting and on `schtasks` for long jobs.
  Whatever lands in `skills/` should hold each fact once.
- **`windows-interactive-session` is the one with no sibling.** Nothing in the catalogue currently says that UI Automation cannot reach across sessions,
  which is the failure that costs the most time and names itself the least.
  `flaui-screenshot` and `windows-screenshot` are its neighbours and should link to it.
- Add `tests/<name>/firing-tests.md` for each,
  three firing scenarios and two that must not fire,
  and a fixture under `tests/fixtures/<name>/`.
- Run `pwsh -File tests/check-portability.ps1` and `python tests/skill-doctor.py --strict` after adding them to the marketplace manifest.

## Not yet carried over

Material from the source repository that is real but not yet general enough to write down here:

- Staging a newer shared framework into a guest's dotnet root so that a tool built on a later runtime can run beside an older suite.
  The mechanism is general — read the required frameworks out of the tool's `runtimeconfig.json`,
  match on the major version only,
  carry `hostfxr` along — but it was only ever exercised against one tool.
- Seeding an application's profile and rewriting a config file section-aware,
  where two sections hold the same key name.
  `windows-ssh-commands` carries the read-back rule;
  the editing itself was too tied to one file format.
