"""Characterisation tests for tests/reflow-prose.py.

    python -m pytest tests/test_reflow_prose.py
"""
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    'reflow_prose', os.path.join(os.path.dirname(__file__), 'reflow-prose.py'))
reflow_prose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reflow_prose)
split = reflow_prose.split_sentences
reflow = reflow_prose.reflow


def test_japanese_sentence_ends_a_line():
    assert split('一文目。二文目。') == ['一文目。', '二文目。']


FIRST = '読点までの前半で一行にしてから'
MIDDLE = '長い文なら間に読点までの行を挟んでから'
LAST = '句点までの後半で一行にするという規則を当てる'


def pad(s, n):
    return s + 'ー' * (n - len(s))


def test_japanese_sentence_within_120_characters_stays_on_one_line():
    text = pad(FIRST, 50) + '、' + pad(LAST, 68) + '。'
    assert len(text) == 120
    assert split(text) == [text]


def test_japanese_sentence_over_120_characters_breaks_at_every_touten():
    first, last = pad(FIRST, 50) + '、', pad(LAST, 69) + '。'
    text = first + last
    assert len(text) == 121
    assert split(text) == [first, last]


def test_long_japanese_sentence_gets_a_middle_line_per_touten():
    first, middle, last = pad(FIRST, 40) + '、', pad(MIDDLE, 40) + '、', pad(LAST, 40) + '。'
    assert split(first + middle + last) == [first, middle, last]


def test_short_leading_fragment_stays_on_the_line():
    tail = pad(LAST, 120) + '。'
    assert split('また、' + tail) == ['また、' + tail]
    assert split('したがって、' + tail) == ['したがって、' + tail]


def test_touten_inside_brackets_or_code_does_not_split():
    text = '「前半で一行にして、後半で一行にする」という規則を`a、b`に当てる。'
    assert split(text) == [text]


def test_english_breaks_only_when_wide():
    short = 'The cache is invalidated on write, and readers take the lock.'
    assert split(short) == [short]
    wide = ('A sentence wider than seventy-two columns breaks after a clause separator, '
            'and this one is wide enough to do so.')
    assert split(wide) == [
        'A sentence wider than seventy-two columns breaks after a clause separator,',
        'and this one is wide enough to do so.',
    ]


def test_reflow_rejoins_a_japanese_clause_split_below_the_limit():
    lines = ['読点までの前半で一行にして、', '句点までの後半で一行にする。', '二文目。']
    assert reflow(lines) == ['読点までの前半で一行にして、句点までの後半で一行にする。', '二文目。']
