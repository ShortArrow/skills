"""Stop hook: a model judges whether the reply's closing owns its call.

The prompt-type hook that did this judged the whole hook input, and in some
sessions every evaluation of a stretch of the conversation was refused by the
evaluator's safety check, while the same replies sent alone passed. This hook
sends only the closing, the trailing paragraphs that fit in CLOSING_CHARS,
to `claude -p` with no tools and no hooks, and fails open: a missing claude,
a timeout, a refusal or an answer that is not a verdict lets the turn end.

Reads the Stop input on stdin. Prints a block verdict, a systemMessage for a
closing the model calls impossible to fix, or nothing.

Environment:
  OWN_THE_CALL_JUDGE_MODEL    model alias for claude -p (default: haiku)
  OWN_THE_CALL_JUDGE_TIMEOUT  seconds to wait for claude (default: 60)
  OWN_THE_CALL_JUDGE_CLAUDE   JSON argv list replacing `claude` (tests)
"""
import json
import os
import re
import shutil
import subprocess
import sys

CLOSING_CHARS = 1200
PROMPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'own-the-call-judge.prompt.txt')
VERDICT = re.compile(r'\{[^{}]*"ok"[^{}]*\}', re.DOTALL)


def closing(message):
    """The trailing paragraphs whose total fits CLOSING_CHARS; always at least the last one."""
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', message.strip()) if p.strip()]
    kept = []
    for p in reversed(paragraphs):
        if kept and sum(len(k) for k in kept) + len(p) > CLOSING_CHARS:
            break
        kept.insert(0, p)
    return '\n\n'.join(kept)


def claude_argv():
    override = os.environ.get('OWN_THE_CALL_JUDGE_CLAUDE')
    if override:
        return json.loads(override)
    found = shutil.which('claude')
    return [found] if found else None


def fail_open(why):
    """Note why no verdict was reached; the turn ends as if the closing passed."""
    sys.stderr.write(f'own-the-call-judge: no verdict ({why}); letting the turn end\n')
    return None


def ask_model(text):
    """The model's verdict dict, or None when anything goes wrong."""
    argv = claude_argv()
    if not argv:
        return fail_open('claude not found')
    with open(PROMPT_FILE, encoding='utf-8') as f:
        prompt = f.read().replace('$CLOSING', text)
    model = os.environ.get('OWN_THE_CALL_JUDGE_MODEL', 'haiku')
    timeout = float(os.environ.get('OWN_THE_CALL_JUDGE_TIMEOUT', '60'))
    try:
        p = subprocess.run(argv + ['-p', '--model', model, '--tools', '',
                                   '--settings', '{"disableAllHooks": true}',
                                   '--no-session-persistence', '--output-format', 'json'],
                           input=prompt.encode('utf-8'), capture_output=True, timeout=timeout)
        if p.returncode != 0:
            return fail_open(f'claude exited {p.returncode}')
        out = json.loads(p.stdout.decode('utf-8', errors='replace'))
        if out.get('is_error'):
            return fail_open(f"claude error: {str(out.get('result'))[:200]}")
        found = VERDICT.search(out.get('result') or '')
        verdict = json.loads(found.group(0)) if found else None
    except (OSError, ValueError, subprocess.TimeoutExpired, AttributeError) as e:
        return fail_open(type(e).__name__)
    if not (isinstance(verdict, dict) and 'ok' in verdict):
        return fail_open('no verdict in the answer')
    return verdict


def decide(payload):
    """The hook output for a Stop input, or None to let the turn end."""
    if payload.get('stop_hook_active'):
        return None
    text = closing(payload.get('last_assistant_message') or '')
    if not text:
        return None
    verdict = ask_model(text)
    if not verdict or verdict.get('ok') is not False:
        return None
    reason = str(verdict.get('reason') or 'The closing does not own its call; see own-the-call.')
    if verdict.get('impossible'):
        return {'systemMessage': reason}
    return {'decision': 'block', 'reason': reason}


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
    except ValueError:
        return
    out = decide(payload) if isinstance(payload, dict) else None
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
