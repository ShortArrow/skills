"""Characterisation tests for hooks/own-the-call-stop.py.

    python -m pytest tests/test_own_the_call_stop.py
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'own-the-call-stop.py')
spec = importlib.util.spec_from_file_location('own_the_call_stop', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
verdict = hook.verdict


def stop(message, active=False):
    return {'hook_event_name': 'Stop', 'stop_hook_active': active, 'last_assistant_message': message}


def test_blocks_a_decision_left_with_the_user():
    out = verdict(stop('PR #63 の本文を更新しました。\n\nマージするかどうかはお任せします。'))
    assert out['decision'] == 'block'
    assert 'お任せします' in out['reason']
    assert 'own-the-call' in out['reason']


def test_blocks_a_bare_request_for_instructions():
    assert verdict(stop('マージはまだしていません。進めてよければ指示してください。'))


def test_blocks_english_hand_backs():
    assert verdict(stop('The body is updated.\n\nWhether to merge is up to you.'))
    assert verdict(stop('Tests pass.\n\nShall I push the branch?'))
    assert verdict(stop('Two options remain.\n\nWhich do you prefer?'))


def test_allows_a_proposal_with_one_go_ahead():
    assert verdict(stop('**提案:** squash でマージします。\n\nマージしてよければ「ok」と返してください。')) is None


def test_allows_a_plain_report():
    assert verdict(stop('repair-skill の変更をコミットして push しました。')) is None


def test_reads_only_the_closing_paragraph():
    message = '前のセッションは「お任せします」で終わっていました。\n\nこの言い回しを止めるフックを足しました。'
    assert verdict(stop(message)) is None
    assert verdict(stop('判断はお任せします。\n\n以上です。')) is None


def test_ignores_a_quoted_phrase():
    assert verdict(stop('止める言い回しは「お任せします」と "up to you" です。')) is None
    assert verdict(stop('止める言い回しは `shall I` です。')) is None


def test_blocks_once_per_stop():
    assert verdict(stop('お任せします。', active=True)) is None


def test_allows_input_without_a_message():
    assert verdict({'hook_event_name': 'Stop'}) is None


def test_process_prints_the_verdict_and_exits_zero():
    run = subprocess.run([sys.executable, HOOK], input=json.dumps(stop('どうするかはお任せします。')),
                         capture_output=True, text=True, encoding='utf-8')
    assert run.returncode == 0
    assert json.loads(run.stdout)['decision'] == 'block'
    quiet = subprocess.run([sys.executable, HOOK], input='not json', capture_output=True, text=True)
    assert quiet.returncode == 0 and quiet.stdout == ''
