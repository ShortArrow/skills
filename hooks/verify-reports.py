"""Gate: a subagent's report is verified by another subagent before it is relayed or published.

adversarial-verify names the moment a subagent's "done" is about to pass as fact, and a
skill listing is consulted when a turn begins, so the moment is missed whenever the
report arrives later, which is how a background subagent's report always arrives. This
hook reads the session transcript at the two places the claim leaves the session.

    verify-reports.py publish   PreToolUse on Bash: refuse git push, gh pr create,
                                gh pr ready and gh issue create while any report in
                                the session has no verification after it.
    verify-reports.py stop      Stop: send the turn back once when a report that
                                arrived since the user last spoke has none.

A report is a completed Agent or Workflow call, synchronous or announced by a
task-notification. A verification is a report from an Agent call whose description
starts with "Verify" or "Re-verify", or names it skeptic, adversarial, refute,
fact-check or cross-check: the names sessions have given their verifiers, and the
ones adversarial-verify asks for. A report is
verified when a verification completed after it. An unreadable transcript lets the
call through: the gate is a check on the agent, not a lock on the user.
"""
import json
import re
import sys

PUBLISH = re.compile(
    r'\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--?[\w-]+(?:=\S+)?))*\s+push\b'
    r'|\bgh\s+pr\s+(?:create|ready)\b'
    r'|\bgh\s+issue\s+create\b'
)
VERIFIER = re.compile(
    r'^\s*(?:re-?)?verif(?:y|ication)\b|\bskeptic\b|\badversarial(?:ly)?\b|\brefute\b|\bfact-?check|\bcross-?check',
    re.IGNORECASE)
NOTIFIED = re.compile(r'<tool-use-id>([^<]+)</tool-use-id>.*?<status>([^<]+)</status>', re.DOTALL)
DELEGATING_TOOLS = ('Agent', 'Task', 'Workflow')

PUBLISH_REASON = (
    'Not yet: {count} subagent report(s) in this session have no adversarial verification after them '
    '({names}). Apply adversarial-verify: launch a separate subagent with a description starting '
    '"Verify:", give it each claim and how to try to break it (the commands to rerun, the files to '
    'read), not the conclusion; act on what survives, then run this command again.'
)
STOP_REASON = (
    'Subagent report(s) arrived this turn with no adversarial verification after them ({names}). '
    'Before relaying them as fact, apply adversarial-verify: launch a separate subagent with a '
    'description starting "Verify:" that tries to break each claim; or, if the turn ends before it '
    'returns, say plainly that the report is unverified.'
)


def read_transcript(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def is_user_prompt(entry):
    if entry.get('type') != 'user' or entry.get('isMeta') or 'toolUseResult' in entry:
        return False
    content = (entry.get('message') or {}).get('content')
    if isinstance(content, str):
        return True
    return isinstance(content, list) and any(b.get('type') == 'text' for b in content)


def reports(entries):
    """(index, description, is_verification) for every completed delegated call, in order."""
    calls = {}
    synchronous = set()
    found = []
    for i, entry in enumerate(entries):
        content = (entry.get('message') or {}).get('content')
        for block in content if isinstance(content, list) else []:
            if block.get('type') == 'tool_use' and block.get('name') in DELEGATING_TOOLS:
                calls[block['id']] = (block.get('input') or {}).get('description') or block['name']
                if block.get('name') != 'Workflow':
                    synchronous.add(block['id'])
            if block.get('type') == 'tool_result' and block.get('tool_use_id') in synchronous:
                result = entry.get('toolUseResult')
                if not (isinstance(result, dict) and result.get('isAsync')) and not block.get('is_error'):
                    found.append(i_report(i, calls[block['tool_use_id']]))
        prompt = (entry.get('attachment') or {}).get('prompt')
        if isinstance(prompt, str) and '<task-notification>' in prompt:
            for use_id, status in NOTIFIED.findall(prompt):
                if use_id in calls and status.strip() == 'completed':
                    found.append(i_report(i, calls[use_id]))
    return found


def i_report(index, description):
    return index, description, bool(VERIFIER.search(description))


def unverified(found, since=0):
    last_check = max((i for i, _, check in found if check), default=-1)
    return [d for i, d, check in found if not check and i > last_check and i >= since]


def names(descriptions):
    shown = ', '.join(f'"{d}"' for d in descriptions[:5])
    return shown + (f' and {len(descriptions) - 5} more' if len(descriptions) > 5 else '')


def publish_verdict(payload, entries):
    command = (payload.get('tool_input') or {}).get('command') or ''
    if not PUBLISH.search(command):
        return None
    left = unverified(reports(entries))
    if not left:
        return None
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': PUBLISH_REASON.format(count=len(left), names=names(left)),
    }}


def stop_verdict(payload, entries):
    if payload.get('stop_hook_active'):
        return None
    since = max((i for i, e in enumerate(entries) if is_user_prompt(e)), default=0)
    left = unverified(reports(entries), since)
    if not left:
        return None
    return {'decision': 'block', 'reason': STOP_REASON.format(names=names(left))}


VERDICTS = {'publish': publish_verdict, 'stop': stop_verdict}
CONCERNS = {
    'publish': lambda payload: bool(PUBLISH.search((payload.get('tool_input') or {}).get('command') or '')),
    'stop': lambda payload: not payload.get('stop_hook_active'),
}


def main(argv):
    """Read the transcript only when the call is one the gate concerns; every Bash call passes here."""
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
        if not (isinstance(payload, dict) and CONCERNS[argv[0]](payload)):
            return
        entries = read_transcript(payload['transcript_path'])
    except (ValueError, KeyError, TypeError, OSError):
        return
    out = VERDICTS[argv[0]](payload, entries)
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main(sys.argv[1:])
