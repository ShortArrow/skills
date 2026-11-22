"""Tests for skills/windows-sandbox/scripts/Invoke-SandboxRun.ps1's liveness check and cleanup.

    python -m pytest tests/test_sandbox_run.py

The machine has one sandbox slot, and the runner must never stop a sandbox it did
not start. The script's functions are loaded alone from its syntax tree, with a
fake wsb and with Get-Process and Stop-Process replaced, so no sandbox is touched.
"""
import os
import shutil
import subprocess

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'skills', 'windows-sandbox', 'scripts',
                      'Invoke-SandboxRun.ps1')
PWSH = shutil.which('pwsh')

LOAD = r'''
$ast = [System.Management.Automation.Language.Parser]::ParseFile($env:SANDBOX_SCRIPT, [ref]$null, [ref]$null)
$defs = $ast.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)
foreach ($d in $defs) { . ([scriptblock]::Create($d.Extent.Text)) }
$sandboxProcessNames = 'WindowsSandbox', 'WindowsSandboxClient'
$killableProcessNames = $sandboxProcessNames
$wsbCli = Get-Command $env:FAKE_WSB -CommandType Application
'''

pytestmark = pytest.mark.skipif(not PWSH, reason='pwsh not installed')


def run(tmp_path, wsb_body, body):
    wsb = tmp_path / 'wsb.cmd'
    wsb.write_text(wsb_body, encoding='ascii')
    env = dict(os.environ, SANDBOX_SCRIPT=os.path.abspath(SCRIPT), FAKE_WSB=str(wsb))
    proc = subprocess.run([PWSH, '-NoProfile', '-NonInteractive', '-Command', LOAD + body],
                          capture_output=True, text=True, env=env, timeout=60)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def test_a_failing_wsb_list_does_not_read_as_no_sandbox(tmp_path):
    """wsb list failing while a hand-started sandbox runs: the slot is taken."""
    out = run(tmp_path, '@exit /b 1\r\n', 'function Get-SandboxPids { @(4242) }\nTest-SandboxRunning')
    assert out == 'True'


def test_an_empty_wsb_list_with_no_process_is_a_free_slot(tmp_path):
    out = run(tmp_path, '@echo {"WindowsSandboxEnvironments": []}\r\n',
              'function Get-SandboxPids { @() }\nTest-SandboxRunning')
    assert out == 'False'


def test_cleanup_stops_only_environments_that_appeared_after_the_launch(tmp_path):
    log = tmp_path / 'stopped.txt'
    wsb = ('@if "%1"=="list" echo {"WindowsSandboxEnvironments": [{"Id": "old"}, {"Id": "new"}]}\r\n'
           f'@if "%1"=="stop" echo %3>>"{log}"\r\n')
    body = r'''
function Get-Process { param($Name, $ErrorAction) @() }
Stop-SandboxStartedHere -PriorIds @('old') -PriorPids @()
'''
    run(tmp_path, wsb, body)
    assert log.read_text().split() == ['new']


def test_cleanup_stops_only_processes_that_appeared_after_the_launch(tmp_path):
    body = r'''
function Get-Process { param($Name, $ErrorAction) @([pscustomobject]@{ Id = 1 }, [pscustomobject]@{ Id = 2 }) }
$script:stopped = @()
function Stop-Process { param($Id, [switch]$Force, $ErrorAction) $script:stopped += $Id }
Stop-SandboxStartedHere -PriorIds @() -PriorPids @(1)
$script:stopped -join ','
'''
    assert run(tmp_path, '@echo {"WindowsSandboxEnvironments": []}\r\n', body) == '2'
