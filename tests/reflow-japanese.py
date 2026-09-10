"""Rewrap Japanese Markdown prose at sentence boundaries.

Paragraphs, list items and blockquotes that contain Japanese are joined
and split again: one sentence per line (at 。), and a sentence wider than
LIMIT display columns is also split after a 、. Headings, tables, code,
frontmatter and lines without Japanese are left as they are. Inside a
blockquote, lines are joined only when the previous line is an unfinished
sentence, so quoted headings, key: value lines and deliberate breaks stay.
Everything except whitespace and blockquote markers must be unchanged;
the script reports any other difference.
"""
import difflib
import io
import re
import sys
import unicodedata

LIMIT = 72
JA = re.compile(r'[぀-ヿ一-鿿]')
ASCII = re.compile(r'[A-Za-z0-9`*_\-]')
KEYLINE = re.compile(r'^[A-Za-z_]+:')
PREFIX = re.compile(r'^(> ?|[-*] |\d+\. )')
NOSPLIT_AFTER = '」』）)*'


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


def join(a, b):
    if not a:
        return b
    pa, nb = a[-1], b[0]
    if pa in '（「『(' or nb in '）」』)、。，．,.':
        return a + b
    if ASCII.match(pa) or ASCII.match(nb):
        return a + ' ' + b
    return a + b


def split_sentences(text):
    out, cur = [], ''
    for i, c in enumerate(text):
        cur += c
        nxt = text[i + 1] if i + 1 < len(text) else ''
        if c == '。' and nxt not in NOSPLIT_AFTER:
            out.append(cur)
            cur = ''
        elif c == '、' and width(cur) > LIMIT and nxt not in NOSPLIT_AFTER:
            out.append(cur)
            cur = ''
    if cur.strip():
        out.append(cur)
    return [s.strip() for s in out if s.strip()]


def quote_continues(body, nb):
    if nb == '' or nb.startswith('#') or KEYLINE.match(nb):
        return False
    if body.startswith('#') or KEYLINE.match(body):
        return False
    if body.rstrip().endswith(('。', '」', '）')):
        return False
    return True


def reflow(lines):
    out, i, infence = [], 0, False
    while i < len(lines):
        l = lines[i]
        if l.startswith('```'):
            infence = not infence
            out.append(l)
            i += 1
            continue
        if infence or not l.strip() or l.startswith(('#', '|', '---', '    ')) or l.strip() == '>':
            out.append(l)
            i += 1
            continue
        m = PREFIX.match(l)
        prefix = m.group(1) if m else ''
        if prefix.startswith('>'):
            cont = '> '
        else:
            cont = ' ' * len(prefix)
        body = l[len(prefix):]
        j = i + 1
        while j < len(lines):
            n = lines[j]
            if not n.strip() or n.startswith(('#', '|', '```')):
                break
            if prefix.startswith('>'):
                if not n.startswith('>'):
                    break
                nb = n[1:].lstrip(' ')
                if not quote_continues(body, nb):
                    break
                body = join(body, nb.strip())
            elif prefix:
                if not n.startswith(' '):
                    break
                body = join(body, n.strip())
            else:
                if PREFIX.match(n) or n.startswith(' '):
                    break
                body = join(body, n.strip())
            j += 1
        if not JA.search(body):
            out.extend(lines[i:j])
            i = j
            continue
        for k, s in enumerate(split_sentences(body)):
            out.append((prefix if k == 0 else cont) + s)
        i = j
    return out


def strip_markers(s):
    return re.sub(r'[\s>]', '', s)


for path in sys.argv[1:]:
    src = io.open(path, encoding='utf-8').read()
    if src.startswith('---\n'):
        k = src.index('\n---\n', 4) + 5
        fm, body = src[:k], src[k:]
    else:
        fm, body = '', src
    new = fm + '\n'.join(reflow(body.split('\n')))
    a, b = strip_markers(src), strip_markers(new)
    print(path, 'content-equal (ignoring whitespace and >):', a == b)
    if a != b:
        for op in difflib.SequenceMatcher(None, a, b).get_opcodes():
            if op[0] != 'equal':
                print('   ', op[0], repr(a[op[1] - 15:op[2] + 15]), '->', repr(b[op[3] - 15:op[4] + 15]))
    io.open(path, 'w', encoding='utf-8', newline='\n').write(new)
