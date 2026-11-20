"""Tests for hooks/own-the-call-judge.py, with a fake claude in place of the model.

    python -m pytest tests/test_own_the_call_judge.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import textwrap

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'own-the-call-judge.py')
spec = importlib.util.spec_from_file_location('own_the_call_judge', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def stop(message, active=False):
    return {'hook_event_name': 'Stop', 'stop_hook_active': active, 'last_assistant_message': message}


def fake_claude(tmp_path, body):
    """A claude stand-in: a python script that logs its stdin and does what body says."""
    script = tmp_path / 'fake_claude.py'
    script.write_text(textwrap.dedent(f'''
        import sys, pathlib
        prompt = sys.stdin.buffer.read().decode('utf-8')
        pathlib.Path(r'{tmp_path}', 'prompt.txt').write_text(prompt, encoding='utf-8')
        pathlib.Path(r'{tmp_path}', 'argv.txt').write_text('\\n'.join(sys.argv[1:]), encoding='utf-8')
    ''') + textwrap.dedent(body), encoding='utf-8')
    return [sys.executable, str(script)]


def run(tmp_path, payload, body):
    env = dict(os.environ, OWN_THE_CALL_JUDGE_CLAUDE=json.dumps(fake_claude(tmp_path, body)))
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                       capture_output=True, env=env, timeout=60)
    return p.returncode, p.stdout.decode('utf-8'), p.stderr.decode('utf-8')


def answer(result, is_error=False):
    return f"print({json.dumps(json.dumps({'result': result, 'is_error': is_error}))})\n"


def test_closing_keeps_only_the_trailing_paragraphs_that_fit():
    head = 'あ' * 2000
    message = f'{head}\n\n**次の一手**\n- やること：x\n- 根拠：y\n\ngo をください。'
    closing = hook.closing(message)
    assert closing.startswith('**次の一手**')
    assert closing.endswith('go をください。')
    assert head not in closing


def test_closing_keeps_one_paragraph_even_when_it_is_long():
    long = 'い' * 3000
    assert hook.closing(f'前置き\n\n{long}') == long


def test_sends_only_the_closing_to_the_model(tmp_path):
    message = '秘密の前置き\n\n' + 'う' * 2000 + '\n\nマージはお任せします。'
    code, out, err = run(tmp_path, stop(message), answer('{"ok": true}'))
    prompt = (tmp_path / 'prompt.txt').read_text(encoding='utf-8')
    assert 'マージはお任せします。' in prompt
    assert '秘密の前置き' not in prompt
    argv = (tmp_path / 'argv.txt').read_text(encoding='utf-8').split('\n')
    assert '--tools' in argv and argv[argv.index('--tools') + 1] == ''
    assert 'disableAllHooks' in argv[argv.index('--settings') + 1]
    assert (code, out) == (0, '')


def test_blocks_when_the_model_says_not_ok(tmp_path):
    code, out, err = run(tmp_path, stop('どれにしますか？'), answer('{"ok": false, "reason": "pick one"}'))
    assert code == 0
    assert json.loads(out) == {'decision': 'block', 'reason': 'pick one'}


def test_reads_a_verdict_wrapped_in_prose_or_a_fence(tmp_path):
    code, out, err = run(tmp_path, stop('x'), answer('```json\n{"ok": false, "reason": "r"}\n```'))
    assert json.loads(out)['decision'] == 'block'


def test_an_impossible_verdict_reaches_the_user_without_blocking(tmp_path):
    code, out, err = run(tmp_path, stop('x'), answer('{"ok": false, "impossible": true, "reason": "r"}'))
    assert code == 0
    assert json.loads(out) == {'systemMessage': 'r'}


def test_skips_a_turn_already_sent_back(tmp_path):
    code, out, err = run(tmp_path, stop('どれにしますか？', active=True), answer('{"ok": false, "reason": "r"}'))
    assert (code, out) == (0, '')
    assert not (tmp_path / 'prompt.txt').exists()


def test_passes_silently_when_claude_fails(tmp_path):
    cases = {
        'nonzero exit': 'sys.exit(1)\n',
        'refusal': answer("API Error: Haiku 5.5 can't help with this.", is_error=True),
        'not json': 'print("garbage")\n',
        'no verdict': answer('I think it is fine.'),
        'crash': 'raise RuntimeError("boom")\n',
    }
    for name, body in cases.items():
        code, out, err = run(tmp_path, stop('どれにしますか？'), body)
        assert (code, out) == (0, ''), name
        assert 'no verdict' in err, name


def test_passes_silently_when_claude_is_missing(tmp_path):
    env = dict(os.environ, OWN_THE_CALL_JUDGE_CLAUDE=json.dumps([str(tmp_path / 'no-such-claude')]))
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(stop('x')).encode('utf-8'),
                       capture_output=True, env=env, timeout=60)
    assert (p.returncode, p.stdout) == (0, b'')


def test_passes_silently_when_claude_times_out(tmp_path):
    env = dict(os.environ, OWN_THE_CALL_JUDGE_CLAUDE=json.dumps(fake_claude(tmp_path, 'import time; time.sleep(30)\n')),
               OWN_THE_CALL_JUDGE_TIMEOUT='1')
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(stop('x')).encode('utf-8'),
                       capture_output=True, env=env, timeout=60)
    assert (p.returncode, p.stdout) == (0, b'')


def test_passes_silently_on_unreadable_input():
    p = subprocess.run([sys.executable, HOOK], input=b'not json', capture_output=True, timeout=60)
    assert (p.returncode, p.stdout) == (0, b'')
