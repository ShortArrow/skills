"""Wrap Markdown prose one sentence per line, in any language.

    python tests/reflow-prose.py [--check] <file>...

The rule is the same for every language: a sentence ends a line, a
sentence wider than LIMIT display columns also breaks after a clause
separator, and a line never breaks inside a word, a bracket or a quoted
phrase. Headings, tables, code, frontmatter and horizontal rules are left
alone. Inside a blockquote, lines are joined only when the previous line
is an unfinished sentence, so quoted headings, key: value lines and
deliberate breaks stay.

What differs by language is layered on per paragraph, decided by the
characters it contains: what counts as a sentence end (。 or . ? !), what
counts as a clause separator (、 or , ; :), and whether joining two lines
inserts a space (never between two Japanese characters, always between
two words). Both sets of marks are recognised in every paragraph, so a
paragraph that mixes the two languages is split at the sentence ends of
both.

Everything except whitespace and blockquote markers must be unchanged;
the script reports any other difference and refuses to write. With
--check it writes nothing and exits 1 when a file would change.
"""
import difflib
import io
import re
import sys
import unicodedata

LIMIT = 72
MIN_PIECE = 24
JA = re.compile('[\u3040-\u30ff\u4e00-\u9fff]')
ASCII = re.compile(r'[A-Za-z0-9`*_\-]')
KEYLINE = re.compile(r'^[A-Za-z_]+:')
ITEM = re.compile(r'^(\s*)([-*+] |\d+\. )')
QUOTE = re.compile(r'^(\s*)(> ?)')
RULE = re.compile(r'^\s*([-*_])(\s*\1){2,}\s*$')
ABBREV = {'e.g', 'i.e', 'etc', 'vs', 'cf', 'Mr', 'Mrs', 'Ms', 'Dr', 'No', 'St', 'Fig', 'approx'}
CLOSERS = '」』）)"”\')]*`_'
OPENERS = {'「': '」', '『': '』', '（': '）', '(': ')', '“': '”', '[': ']'}


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


# --- language layers -------------------------------------------------------

def wide(c):
    return unicodedata.east_asian_width(c) in 'WF'


def join_ja(a, b):
    if not a:
        return b
    pa, nb = a[-1], b[0]
    if pa in '（「『(' or nb in '）」』)、。，．,.':
        return a + b
    if wide(pa) and wide(nb):
        return a + b
    return a + ' ' + b


def join_en(a, b):
    return b if not a else a + ' ' + b


def sentence_end_ja(text, i):
    nxt = text[i + 1] if i + 1 < len(text) else ''
    return text[i] == '。' and nxt not in CLOSERS


def separator_ja(text, i):
    nxt = text[i + 1] if i + 1 < len(text) else ''
    return text[i] == '、' and nxt not in CLOSERS


def sentence_end_en(text, i):
    c = text[i]
    if c not in '.?!':
        return False
    j = i + 1
    if j < len(text) and text[j] == '*':
        return False
    while j < len(text) and text[j] in CLOSERS:
        j += 1
    if j >= len(text) or text[j] != ' ':
        return False
    k = j
    while k < len(text) and text[k] == ' ':
        k += 1
    if k >= len(text):
        return False
    if not (text[k].isupper() or text[k] in '"“(`[' or text[k].isdigit()):
        return False
    if c == '.':
        word = re.search(r'([A-Za-z][A-Za-z.]*)$', text[:i])
        if word:
            w = word.group(1)
            if w in ABBREV or w.rstrip('.') in ABBREV or (len(w) == 1 and w.isupper()):
                return False
        if re.search(r'\d$', text[:i]) and text[k].isdigit():
            return False
    return True


def separator_en(text, i):
    nxt = text[i + 1] if i + 1 < len(text) else ''
    return text[i] in ',;:' and nxt == ' '


def sentence_end(text, i):
    return sentence_end_ja(text, i) or sentence_end_en(text, i)


def separator(text, i):
    return separator_ja(text, i) or separator_en(text, i)


def join_for(text):
    return join_ja if JA.search(text) else join_en


# --- the language-neutral rule -------------------------------------------

def split_sentences(text):
    out, cur, last_sep = [], '', -1
    stack = []
    straight = 0
    i = 0
    while i < len(text):
        c = text[i]
        cur += c
        if c == '"':
            straight ^= 1
        elif c in OPENERS:
            stack.append(OPENERS[c])
        elif stack and c == stack[-1]:
            stack.pop()
        enclosed = bool(stack) or straight
        if not enclosed and sentence_end(text, i):
            j = i + 1
            while j < len(text) and text[j] in CLOSERS and text[j] != '*':
                cur += text[j]
                j += 1
            if width(cur) > LIMIT and last_sep > 0:
                out.append(cur[:last_sep])
                cur = cur[last_sep:].lstrip()
            out.append(cur)
            cur, last_sep = '', -1
            i = j
            continue
        if not enclosed and separator(text, i) and width(cur) >= MIN_PIECE:
            if width(cur) > LIMIT and last_sep > 0:
                out.append(cur[:last_sep])
                cur = cur[last_sep:].lstrip()
            if width(cur) > LIMIT:
                out.append(cur)
                cur, last_sep = '', -1
            else:
                last_sep = len(cur)
        i += 1
    if cur.strip():
        if width(cur) > LIMIT and last_sep > 0:
            out.append(cur[:last_sep])
            cur = cur[last_sep:].lstrip()
        out.append(cur)
    return [s.strip() for s in out if s.strip()]


def quote_continues(body, nb):
    if nb == '' or nb.startswith('#') or KEYLINE.match(nb) or ITEM.match(nb):
        return False
    if body.startswith('#') or KEYLINE.match(body):
        return False
    t = body.rstrip()
    if t and t[-1] in '。.?!」』）)"”\')]':
        return False
    return True


def reflow(lines):
    out, i, fence = [], 0, None
    in_list = False
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if fence is not None:
            out.append(l)
            if s.startswith(fence):
                fence = None
            i += 1
            continue
        if s.startswith(('```', '~~~')):
            fence = s[:3]
            out.append(l)
            i += 1
            continue
        if not s:
            in_list = False
            out.append(l)
            i += 1
            continue
        if s.startswith(('#', '|', '<')) or s == '>' or RULE.match(l):
            out.append(l)
            i += 1
            continue
        indent = len(l) - len(l.lstrip(' '))
        if indent >= 4 and not in_list:
            out.append(l)
            i += 1
            continue
        qm = QUOTE.match(l)
        im = ITEM.match(l)
        if qm:
            prefix, cont, kind = qm.group(0), qm.group(1) + '> ', 'quote'
        elif im:
            prefix, cont, kind = im.group(0), ' ' * len(im.group(0)), 'item'
            in_list = True
        else:
            prefix, cont, kind = ' ' * indent, ' ' * indent, 'para'
        body = l[len(prefix):]
        j = i + 1
        while j < len(lines):
            n = lines[j]
            ns = n.strip()
            if not ns or ns == '>' or ns.startswith(('#', '|', '```', '~~~', '<')) or RULE.match(n):
                break
            if kind == 'quote':
                if not QUOTE.match(n):
                    break
                nb = n[QUOTE.match(n).end():]
                if not quote_continues(body, nb):
                    break
                body = join_for(body + nb)(body, nb.strip())
            elif kind == 'item':
                nindent = len(n) - len(n.lstrip(' '))
                if ITEM.match(n) or QUOTE.match(n) or nindent <= len(im.group(1)):
                    break
                body = join_for(body + ns)(body, ns)
            else:
                nindent = len(n) - len(n.lstrip(' '))
                if ITEM.match(n) or QUOTE.match(n) or nindent != indent:
                    break
                body = join_for(body + ns)(body, ns)
            j += 1
        pieces = split_sentences(body)
        if len(pieces) == 1 and j == i + 1:
            out.append(l)
        else:
            for k, piece in enumerate(pieces):
                out.append((prefix if k == 0 else cont) + piece)
        i = j
    return out


def strip_markers(s):
    return re.sub(r'[\s>]', '', s)


def main(argv):
    check = '--check' in argv
    paths = [a for a in argv if a != '--check']
    changed = refused = 0
    for path in paths:
        src = io.open(path, encoding='utf-8').read()
        if src.startswith('---\n') and '\n---\n' in src[4:]:
            k = src.index('\n---\n', 4) + 5
            fm, body = src[:k], src[k:]
        else:
            fm, body = '', src
        new = fm + '\n'.join(reflow(body.split('\n')))
        a, b = strip_markers(src), strip_markers(new)
        if a != b:
            print(path, 'REFUSED: content would change')
            for op in difflib.SequenceMatcher(None, a, b).get_opcodes():
                if op[0] != 'equal':
                    print('   ', op[0], repr(a[op[1] - 20:op[2] + 20]), '->', repr(b[op[3] - 20:op[4] + 20]))
            refused += 1
            continue
        if new != src:
            changed += 1
            if check:
                print(path, 'would change')
            else:
                io.open(path, 'w', encoding='utf-8', newline='\n').write(new)
                print(path, 'rewrapped')
    return 1 if refused or (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
