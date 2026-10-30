"""Stop hook: a turn that ends waiting on an event nothing in the session will report.

timed-wait's moment is the last sentence of a turn that says "waiting for CI" or
"once CI passes I will merge": a session only resumes on a user message or a
notification, so a wait with no background command, subagent or wakeup still
pending is a wait that ends when the user asks. Transcripts showed it as a user
asking whether CI had finished, whether the runner was alive, or to resume a
monitor that had stopped; and as a watcher that exited on "pending" or was killed,
after which the session kept saying it was waiting.

Reads the Stop input on stdin and the transcript it names, and prints a block
verdict or nothing. Only the closing paragraph is read, quoted spans are skipped,
a wait on the user is grill-me's and passes, and a stop already continued by a
Stop hook is let through. An unreadable transcript lets the turn end.
"""
import json
import re
import sys
from datetime import datetime

EVENT = r'(?:CI|ビルド|ジョブ|ワークフロー|チェック|e2e|E2E|テスト|デプロイ|リリース|ランナー|サブエージェント|エージェント|run|checks?|build|job|workflow|deploy|tests?)'
WAITS = [
    EVENT + r'\s*(?:の結果|の完了|が(?:終わる|通る|揃う|そろう)の)?\s*を?\s*(?:待っています|待っている(?!なら)|待ちます|待つ|待ちです|待ちのまま)',
    EVENT + r'\s*(?:の実行)?\s*(?:が|は)?\s*(?:通ったら|終わったら|完了したら|揃ったら|そろったら|成功したら|落ちたら)',
    r'\bwaiting (?:for|on) (?:the )?' + EVENT,
    r'\bonce (?:the )?' + EVENT + r'\b[^.\n]{0,20}?\b(?:pass|passes|finish|finishes|complete|completes|is green)\b',
]
WAIT = re.compile('|'.join(WAITS), re.IGNORECASE)
ON_USER = re.compile(r'教えて|知らせて|お返事|返事を|指示を|あなたが|let me know|tell me|your (?:reply|answer|go-ahead)', re.IGNORECASE)
QUOTED = re.compile(r'「[^」]*」|『[^』]*』|"[^"]*"|“[^”]*”|`[^`]*`')
REPORTED = re.compile(r'<(?:tool-use-id|task-id)>([^<]+)</|<agent-message from="([^"]+)"')
NOTIFICATION = re.compile(r'<task-notification>.*?(?:</task-notification>|$)|<agent-message[^>]*>', re.DOTALL)
STILL_RUNNING = 'waiting on its own background work'
STALE_HOURS = 6
BACKGROUND_ID = re.compile(r'background (?:with )?\(?ID: (\w+)|agentId: (\w+)')
ASYNC_TOOLS = ('Agent', 'Task', 'Workflow', 'Monitor')
WAKE_TOOLS = ('ScheduleWakeup', 'CronCreate')

REASON = (
    'The reply ends waiting on an event ("{phrase}"), but nothing in this session will report it: '
    'no background command, subagent or wakeup is still pending, and a session resumes only on a user '
    'message or a notification. Apply timed-wait (read its SKILL.md if it is not loaded): start a watcher '
    'in the background that exits only when the state is final (for CI, `gh pr checks <n> --watch` or '
    '`gh run watch <id> --exit-status`, with run_in_background), or schedule a wakeup at the expected '
    'duration; then end the turn saying what will report and when. If nothing can watch it, say so and '
    'who resumes it.'
)


def closing_paragraph(message):
    paragraphs = [p for p in re.split(r'\n\s*\n', message.strip()) if p.strip()]
    return paragraphs[-1] if paragraphs else ''


def texts(content):
    if isinstance(content, str):
        return [content]
    return [b.get('text', '') for b in content or [] if isinstance(b, dict) and b.get('type') == 'text']


def is_user_prompt(entry):
    if entry.get('type') != 'user' or entry.get('isMeta') or 'toolUseResult' in entry:
        return False
    body = ' '.join(texts((entry.get('message') or {}).get('content')))
    return bool(body.strip()) and '<task-notification>' not in body


def pending(entries):
    """Whether a background call, a messaged subagent or a wakeup is still due to resume the session.

    A call is known by its tool-use id and by the task or agent id its result names,
    and is done once a notification or a hand-back names either, unless the notification
    says the subagent is still waiting on work of its own. A call started more than
    STALE_HOURS before the last entry is taken as gone: a restarted client leaves the
    ids of the tasks it lost in the transcript with no notification.
    """
    waiting, woken = {}, False
    for entry in entries:
        if is_user_prompt(entry):
            woken = False
        at = entry.get('timestamp') or ''
        content = (entry.get('message') or {}).get('content')
        for block in content if isinstance(content, list) else []:
            inp = block.get('input') or {}
            if block.get('type') == 'tool_use':
                if inp.get('run_in_background') or block.get('name') in ASYNC_TOOLS:
                    waiting[block.get('id')] = at
                if block.get('name') == 'SendMessage' and inp.get('to'):
                    waiting[inp['to']] = at
                if block.get('name') in WAKE_TOOLS:
                    woken = True
            if block.get('type') == 'tool_result':
                body = block.get('content')
                body = body if isinstance(body, str) else ' '.join(texts(body))
                waiting.update({a or b: at for a, b in BACKGROUND_ID.findall(body)})
        notice = ' '.join(texts(content)) + ' ' + str((entry.get('attachment') or {}).get('prompt') or '')
        for one in NOTIFICATION.findall(notice):
            if STILL_RUNNING not in one:
                for a, b in REPORTED.findall(one):
                    waiting.pop(a or b, None)
    last = next((e['timestamp'] for e in reversed(entries) if e.get('timestamp')), '')
    return woken or any(not hours_between(at, last) > STALE_HOURS for at in waiting.values())


def hours_between(start, end):
    """Hours from one ISO timestamp to another, or 0 when either is missing or unreadable."""
    try:
        parse = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
        return (parse(end) - parse(start)).total_seconds() / 3600
    except ValueError:
        return 0


def verdict(payload, entries):
    """The block verdict for a Stop input and its transcript, or None to let the turn end."""
    if payload.get('stop_hook_active'):
        return None
    closing = QUOTED.sub('', closing_paragraph(payload.get('last_assistant_message') or ''))
    found = WAIT.search(closing)
    if not found or ON_USER.search(closing) or pending(entries):
        return None
    return {'decision': 'block', 'reason': REASON.format(phrase=found.group(0))}


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
        if not isinstance(payload, dict) or payload.get('stop_hook_active'):
            return
        with open(payload['transcript_path'], encoding='utf-8') as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except (ValueError, KeyError, TypeError, OSError):
        return
    out = verdict(payload, entries)
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
