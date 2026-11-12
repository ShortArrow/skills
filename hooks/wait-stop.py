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
# A gate only the user can open — an approval, a review, a manual trigger — with machine
# work behind it. The gate itself is timed-wait's blocked-on-input, but what it releases is
# a deployment nobody is watching, so the turn still owes what will report it and when.
GATE = r'(?:承認|approval|approve|review deployments?)'
RELEASED = (r'(?:公開|配信|配布|デプロイ|リリース|反映|publish(?:es|ed|ing)?|deploy(?:s|ed|ing|ment)?|'
            r'release[ds]?|crates\.io|registry|レジストリ)')
GATED = [
    GATE + r'(?:待ち|を待|が必要|を求めら|されるまで)',
    GATE + r'\s*(?:して|をして|をお願い|してください|を押して|すると|したら|されると|され次第)',
    r'\bwaiting (?:for|on) (?:an? |the )?' + GATE,
    # The gate and the machine work it releases in one breath, either order.
    GATE + r'\b[^.\n]{0,60}?' + RELEASED,
    RELEASED + r'[^.\n]{0,60}?\b' + GATE,
]
WAIT = re.compile('|'.join(WAITS + GATED), re.IGNORECASE)
ON_USER = re.compile(r'教えて|知らせて|お返事|返事を|指示を|あなたが|let me know|tell me|your (?:reply|answer|go-ahead)', re.IGNORECASE)
QUOTED = re.compile(r'「[^」]*」|『[^』]*』|"[^"]*"|“[^”]*”|`[^`]*`')
REPORTED = re.compile(r'<(?:tool-use-id|task-id)>([^<]+)</|<agent-message from="([^"]+)"')
NOTIFICATION = re.compile(r'<task-notification>.*?(?:</task-notification>|$)|<agent-message[^>]*>', re.DOTALL)
STILL_RUNNING = 'waiting on its own background work'
# A notification arriving is not the job succeeding. Claude Code reports completed,
# failed or killed, and this repository's history holds a watcher named "Push, open
# draft PR and wait for CI" that ended failed with exit code 1: read as "a notice came
# back", a dead watcher becomes a green CI.
BROKE = re.compile(r'<status>\s*(?:failed|killed|error|cancell?ed|timed[_ -]?out)\s*</status>|'
                   r'\b(?:failed with exit code|exit code [1-9])', re.IGNORECASE)
# Work running somewhere this session cannot see: no background command holds it, so
# pending() finds nothing to wait on and the turn ends on a promise nobody keeps.
REMOTE = (r'(?:workflow run|デプロイ|deploy(?:s|ing|ed|ment)?|レジストリ|registry|'
          r'crates\.io|ワークフロー|workflow|パイプライン|pipeline)')
UNDER_WAY = (r'(?:(?<!完了)中|が進行|を開始|されます|はず|予定|待ち|'
             r'in progress|under way|running|queued|pending|will (?:be|pick|appear)|'
             r'picks? (?:it )?up|triggered|kicked off|dispatch(?:ed)?|起動しました|取り込(?:む|まれる|み)?)')
# A closing that reports the remote work as already observed is a report, not a wait.
OBSERVED = re.compile(r'完了しました|済みです|済みました|確認しました|反映されたこと|'
                      r'finished|completed|succeeded|confirmed|verified', re.IGNORECASE)
ELSEWHERE = re.compile(REMOTE + r'[^.\n]{0,40}?' + UNDER_WAY + r'|'
                       + UNDER_WAY + r'[^.\n]{0,40}?' + REMOTE, re.IGNORECASE)
# The closing asks the user to run something. With `!` the output lands in the
# conversation and the next turn continues on it; without, the user runs it in another
# window and the agent either gets the output pasted by hand or gets only "done", and
# then assumes a result it never saw. Measured here: 53 of 159 such requests came
# without the form.
HANDS_A_COMMAND = re.compile(
    r'(?:コマンド|以下|次(?:の|を)|これ)?\s*[^\n]{0,30}?(?:実行|打って|走らせて|叩いて)\s*(?:して)?(?:ください|ほしい|もらえ|下さい)'
    r'|\bplease run\b|\brun (?:this|the following|these)\b|\bexecute (?:this|the following)\b', re.IGNORECASE)
BANG_FORM = re.compile(r'(?:^|\n|`|\s)!\s*\S|`!`|先頭に\s*`?!')
# The closing claims a finished, good outcome.
CLAIMS_DONE = re.compile(
    r'(?:通りました|成功しました|完了(?:しました|です|したもの)|終わりました|済みました|マージ(?:しました|できます)|'
    r'(?:all )?(?:checks? )?(?:are |is )?green|passed|succeeded|merged it|went through)', re.IGNORECASE)
# A commitment carried across a compaction by a bare label. The summary preserves the
# reference and drops what it referred to, so the obligation outlives the record of what it
# was. Measured here on 2026-11-10: after a compaction this session carried "situations
# 5/7/10/12" through four consecutive closings while unable to reconstruct the enumeration,
# because only references to it survived. The boundary is not inferred — Claude Code writes
# a system entry carrying compactMetadata, then a user entry with isCompactSummary.
BARE_LABEL = re.compile(
    r'(?:situations?|items?|項目|シナリオ|ケース|case)\s*#?\d+(?:\s*(?:[/,、と]|and|,)\s*#?\d+)*'
    r'|#\d+(?:\s*[/,、]\s*#\d+)+',
    re.IGNORECASE)
# A label is defined only where the text immediately following it says what it is: a
# parenthetical gloss, or an apposition. Any comma or dash plus text was far too loose — it
# read a neighbouring list item and a trailing remark about the label as definitions, which
# is how three of this session's four real closings passed when they should not have. The
# gloss must follow the label: text before it belongs to whatever preceded it.
#
# Japanese `は、` is deliberately not a definition here. It marks a topic, so it introduces
# any remark about the label as readily as a gloss of it, and no pattern separates "X は、
# [what X is]" from "X は、[something true of X]". Treating it as a definition passed a
# closing that only said the items were related to the day's work; leaving it out costs a
# miss on a genuine `X は、[definition]`, and a miss is the cheaper error for a check that
# sends turns back.
DEFINES = re.compile(
    r'^\s*[（(][^）)]{4,}[）)]'
    r'|^\s*とは\s*[^。\n]{6,}'
    r'|^\s*(?:,\s*(?:the|a|an)\b|which is|that is)\s*\S{3,}'
    r'|^\s*[—–]\s*[^、。\n]{6,}')

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

COMMAND_REASON = (
    'The reply asks the user to run a command but does not offer the `!` form, so its output lands in '
    'their terminal and not in this conversation. They then pay for it twice — running it, then pasting '
    'the output or just saying it is done — and a turn that continues on "done" assumes a result it '
    'never saw. Prefix each command with `! ` so the output comes back here, and say what in that output '
    'decides the next step. If the command genuinely cannot run through this session (an interactive '
    'login, another machine), say so, say what to look for in its output, and ask for that rather than '
    'for confirmation that it ran.'
)

BROKE_REASON = (
    'The reply reports the work as finished and good, but the notification that came back carried '
    'failed, killed or a non-zero exit code, so the watcher died without a result and the outcome it '
    'claims was never observed. A notification arriving is not the job succeeding. Read the status and '
    'the output file before reporting: say what the exit code was, whether the underlying job is still '
    'running, finished or never started, and restart the watch (`gh run watch <id> --exit-status`) or '
    'report plainly that the result is unknown. Reporting an unobserved success is the one failure here '
    'that gets believed.'
)

ELSEWHERE_REASON = (
    'The reply ends on work running somewhere this session cannot see — a dispatched workflow, a deploy, '
    'a registry pickup — and nothing here holds it: no background command, subagent or wakeup, so no '
    'notification will arrive and the promise has no keeper. Apply timed-wait (read its SKILL.md if it is '
    'not loaded): poll the external state at a cadence matched to how fast it changes, with a watcher '
    'started in the background (`gh run watch <id> --exit-status`, `gh run list -R <repo>`, or the '
    'provider\'s status command) or a wakeup past the expected finish; state the deadline as a wall-clock '
    'time. If this session genuinely cannot reach that state, say so, name who can, and say what is '
    'unverified rather than what is expected.'
)

LOST_LABEL_REASON = (
    'The reply carries a commitment by a bare label ("{phrase}") across a compaction that dropped what '
    'the label referred to. A summary preserves the reference and not its content, so the obligation '
    'outlives the record of what it was, and neither this session nor the user can act on it. Either say '
    'what the label means in the same sentence — one clause naming the actual work — or drop it from the '
    'list and say it is unrecoverable. Do not carry it forward as a live item on the strength of its '
    'number: a to-do nobody can reconstruct is not a to-do, and repeating it reads as tracked work that '
    'is not tracked. Where the defining content may still exist, the transcript under '
    '~/.claude/projects is the place to look before citing it again.'
)

GATED_REASON = (
    'The reply hands back a gate only the user can open ("{phrase}") and ends there, but machine work '
    'runs behind it and nothing in this session will report that: no background command, subagent or '
    'wakeup is still pending. timed-wait calls this blocked-on-input, and it is the one class with no '
    'liveness signal, so the fallback is declared when the wait begins, not after. Do not start a '
    'watcher that polls the gate itself — it would spin until the user acts. Instead end the turn with '
    'the three things the user needs to act once: what to click and where, what starts after it and how '
    'long that takes, and who watches that result — either a wakeup past the expected finish, or a '
    'stated handover that the next turn resumes the watch on being told it is approved. '
    'Which of those two it is depends on where the work runs, and this hook cannot tell: if what the '
    'approval releases is one command this session runs itself, the handover is the whole answer and a '
    'watcher would have nothing to watch, because the reply is the resume — say what will run and what '
    'in its output decides the next step, and add no wakeup. Only work that proceeds without this '
    'session owes a watcher.'
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
    """(live, broke): whether something will still resume the session, and whether a watcher died.

    `live` is the original question — a background call, a messaged subagent or a wakeup
    still due. `broke` is separate: a notification came back carrying failed, killed or a
    non-zero exit code, so the work it was watching has no result, whatever the turn says
    about it.

    A call is known by its tool-use id and by the task or agent id its result names,
    and is done once a notification or a hand-back names either, unless the notification
    says the subagent is still waiting on work of its own. A call started more than
    STALE_HOURS before the last entry is taken as gone: a restarted client leaves the
    ids of the tasks it lost in the transcript with no notification.
    """
    waiting, woken, broke = {}, False, set()
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
                    if BROKE.search(one):
                        broke.add(a or b)
    last = next((e['timestamp'] for e in reversed(entries) if e.get('timestamp')), '')
    live = woken or any(not hours_between(at, last) > STALE_HOURS for at in waiting.values())
    return live, bool(broke)


def compaction_dropped(entries):
    """Whether a compaction has condensed this session, dropping what it summarised.

    Claude Code marks the boundary explicitly: a system entry carrying compactMetadata,
    followed by a user entry with isCompactSummary. Nothing here is inferred, so a session
    that was never compacted is never suspected.
    """
    return any(entry.get('compactMetadata') or entry.get('isCompactSummary') for entry in entries)


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
    whole = payload.get('last_assistant_message') or ''
    closing = QUOTED.sub('', closing_paragraph(whole))
    live, broke = pending(entries)
    if broke and CLAIMS_DONE.search(closing) and not ON_USER.search(closing):
        return {'decision': 'block', 'reason': BROKE_REASON}
    # Unlike the wait classes, this one reads the whole reply: measured here, the request
    # sits in the closing only 45 times out of 167, the rest inside numbered steps. The
    # `!` is read from the whole reply too, unquoted — QUOTED strips the backticks that
    # carry it — so a reply that offers the form anywhere passes.
    if HANDS_A_COMMAND.search(QUOTED.sub('', whole)) and not BANG_FORM.search(whole):
        return {'decision': 'block', 'reason': COMMAND_REASON}
    label = BARE_LABEL.search(closing)
    if label and compaction_dropped(entries):
        if not DEFINES.search(closing[label.end():label.end() + 80]):
            return {'decision': 'block', 'reason': LOST_LABEL_REASON.format(phrase=label.group(0))}
    found = WAIT.search(closing)
    if (not found and ELSEWHERE.search(closing) and not OBSERVED.search(closing)
            and not live and not ON_USER.search(closing)):
        return {'decision': 'block', 'reason': ELSEWHERE_REASON}
    if not found or ON_USER.search(closing) or live:
        return None
    gated = re.search('|'.join(GATED), closing, re.IGNORECASE)
    reason = GATED_REASON if gated and gated.start() == found.start() else REASON
    return {'decision': 'block', 'reason': reason.format(phrase=found.group(0))}


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
