"""Stop hook: a turn that closes by leaving a decision with the user.

own-the-call's moment is the last sentence of a turn, and a skill listing is
consulted when a turn begins, not when it ends; the closing 「お任せします」
was seen in three sessions whose agent had the evidence to decide. With the
skill's body in context the same closing became a proposal in every sample,
so this hook supplies the body's rule at the moment the listing cannot reach.

Reads the Stop input on stdin and prints a block verdict, or nothing. Only the
closing paragraph is read, quoted spans in it are skipped (a reply that talks
about the phrase is not using it), and a stop already continued by a Stop hook
is let through, so a reply is sent back at most once.
"""
import json
import re
import sys

HAND_BACKS = [
    r'お任せ(?:いた)?します',
    r'ご判断(?:ください|をお願い)',
    r'(?:指示|お知らせ)(?:して)?ください',
    r'(?:どちら|どれ)(?:が|に)(?:よい|いい|しますか)',
    r'どうしますか',
    r'しましょうか',
    r"\bup to you\b",
    r"\byour call\b",
    r"\bshall I\b",
    r"\b(?:do|would) you (?:want|like) me to\b",
    r"\bwhich (?:one )?do you prefer\b",
    r"\blet me know (?:if|whether|how) you(?:'d| would)? (?:like|want)\b",
]
PATTERN = re.compile('|'.join(HAND_BACKS), re.IGNORECASE)
QUOTED = re.compile(r'「[^」]*」|『[^』]*』|"[^"]*"|“[^”]*”|`[^`]*`')

REASON = (
    'The reply closes by leaving a decision with the user ("{phrase}"). '
    'Apply own-the-call (read its SKILL.md if it is not loaded): '
    'if the step is inside what the request asked for, do it and report; '
    'otherwise rewrite the closing as a proposal: what will be done, the evidence that decided it, '
    'what it costs and how it is undone, and one go-ahead naming the fact that would change the plan. '
    'A question for a fact only the user holds stays, in the form grill-me gives it.'
)


def closing_paragraph(message):
    paragraphs = [p for p in re.split(r'\n\s*\n', message.strip()) if p.strip()]
    return paragraphs[-1] if paragraphs else ''


def verdict(payload):
    """The block verdict for a Stop input, or None to let the turn end."""
    if payload.get('stop_hook_active'):
        return None
    closing = QUOTED.sub('', closing_paragraph(payload.get('last_assistant_message') or ''))
    found = PATTERN.search(closing)
    if not found:
        return None
    return {'decision': 'block', 'reason': REASON.format(phrase=found.group(0))}


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode('utf-8'))
    except ValueError:
        return
    out = verdict(payload) if isinstance(payload, dict) else None
    if out:
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
