"""Characterisation tests for hooks/verify-reports.py.

    python -m pytest tests/test_verify_reports.py
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'verify-reports.py')
spec = importlib.util.spec_from_file_location('verify_reports', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def prompt(text):
    return {'type': 'user', 'message': {'role': 'user', 'content': text}}


def launch(use_id, description, name='Agent'):
    return {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': use_id, 'name': name, 'input': {'description': description, 'prompt': '...'}}]}}


def launched(use_id):
    return {'type': 'user', 'toolUseResult': {'isAsync': True, 'status': 'async_launched'},
            'message': {'role': 'user', 'content': [
                {'type': 'tool_result', 'tool_use_id': use_id, 'content': 'Async agent launched successfully.'}]}}


def returned(use_id):
    return {'type': 'user', 'toolUseResult': {'status': 'completed', 'content': []},
            'message': {'role': 'user', 'content': [
                {'type': 'tool_result', 'tool_use_id': use_id, 'content': 'All 12 tests pass.'}]}}


def notified(use_id, status='completed'):
    return {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': (
        f'<task-notification>\n<task-id>a1</task-id>\n<tool-use-id>{use_id}</tool-use-id>\n'
        f'<status>{status}</status>\n<summary>Agent finished</summary>\n</task-notification>')}}


def background(use_id, description):
    return [launch(use_id, description), launched(use_id), notified(use_id)]


def publish(command, entries):
    return hook.publish_verdict({'tool_input': {'command': command}}, entries)


def stop(entries, active=False):
    return hook.stop_verdict({'stop_hook_active': active}, entries)


REPORTED = [prompt('fix it'), *background('t1', 'Fix the parser')]
VERIFIED = [*REPORTED, *background('t2', 'Verify: parser fix')]


def test_publishing_with_an_unverified_report_is_refused():
    for command in ['git push', 'git -C repo push origin main', 'cd x && git push -u origin b',
                    'gh pr create --draft --title t', 'gh pr ready 63', 'gh issue create -t t']:
        out = publish(command, REPORTED)
        assert out['hookSpecificOutput']['permissionDecision'] == 'deny', command
        assert '"Fix the parser"' in out['hookSpecificOutput']['permissionDecisionReason']


def test_publishing_after_a_verification_is_allowed():
    assert publish('git push', VERIFIED) is None


def test_a_verifier_is_known_by_the_names_sessions_give_it():
    for name in ['Verify PR #250 code', 'Re-verify ADR 0052', 'Skeptic: blast radius of fix',
                 'Adversarially verify PR 251', '#65 adversarial review 1', 'Refute-by-default review of PR 137',
                 'Fact-check ADR 0051 claims', 'Cross-check P/Invoke signatures']:
        assert publish('git push', [*REPORTED, *background('v', name)]) is None, name
    for name in ['Structure review of USERGUIDE', '#74 merge main and verify', 'Fix #60 review 2 findings']:
        assert publish('git push', [*REPORTED, *background('v', name)]), name


def test_a_report_after_the_last_verification_is_unverified_again():
    later = [*VERIFIED, *background('t3', 'Add the CLI flag')]
    reason = publish('gh pr ready', later)['hookSpecificOutput']['permissionDecisionReason']
    assert '"Add the CLI flag"' in reason and 'Fix the parser' not in reason


def test_other_commands_and_sessions_without_subagents_pass():
    assert publish('git status', REPORTED) is None
    assert publish('gh pr view 63', REPORTED) is None
    assert publish('git commit -m "push the fix"', REPORTED) is None
    assert publish('git push', [prompt('push it')]) is None


def test_a_launch_or_a_failure_is_not_a_report():
    assert publish('git push', [launch('t1', 'Fix the parser'), launched('t1')]) is None
    assert publish('git push', [launch('t1', 'Fix'), launched('t1'), notified('t1', 'failed')]) is None


def test_a_synchronous_result_is_a_report():
    assert publish('git push', [launch('t1', 'Fix the parser'), returned('t1')])


def test_a_workflow_counts_on_its_notification_only():
    started = [launch('w1', 'review-changes', name='Workflow'), returned('w1')]
    assert publish('git push', started) is None
    assert publish('git push', [*started, notified('w1')])


def test_stop_sends_back_a_report_of_this_turn_once():
    out = stop(REPORTED)
    assert out['decision'] == 'block' and '"Fix the parser"' in out['reason']
    assert stop(REPORTED, active=True) is None
    assert stop(VERIFIED) is None


def test_stop_leaves_reports_from_earlier_turns_to_the_publish_gate():
    assert stop([*REPORTED, prompt('ok, next')]) is None
    assert publish('git push', [*REPORTED, prompt('ok, next')])


def test_process_reads_the_transcript_and_fails_open(tmp_path):
    transcript = tmp_path / 's.jsonl'
    transcript.write_text('\n'.join(json.dumps(e) for e in REPORTED), encoding='utf-8')
    payload = {'transcript_path': str(transcript), 'tool_input': {'command': 'git push'}}
    run = subprocess.run([sys.executable, HOOK, 'publish'], input=json.dumps(payload),
                         capture_output=True, text=True, encoding='utf-8')
    assert run.returncode == 0
    assert json.loads(run.stdout)['hookSpecificOutput']['permissionDecision'] == 'deny'
    missing = {'transcript_path': str(tmp_path / 'none.jsonl'), 'tool_input': {'command': 'git push'}}
    quiet = subprocess.run([sys.executable, HOOK, 'publish'], input=json.dumps(missing), capture_output=True, text=True)
    assert quiet.returncode == 0 and quiet.stdout == ''
