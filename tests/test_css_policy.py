"""Tests for skills/interface-design/scripts/css/, written before the configuration exists.

    npm ci && python -m pytest tests/test_css_policy.py

stylelint.config.mjs is the shared configuration a project extends. It refuses
text-align: justify, a fixed height or block-size on a rule that can hold text, and a
color and background pair under 7:1, as far as the stylesheet alone settles it.
Each case lints a few lines of CSS with the configuration and reads stylelint's JSON.
"""
import json
import os
import subprocess

import pytest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CONFIG = os.path.join(ROOT, 'skills', 'interface-design', 'scripts', 'css', 'stylelint.config.mjs')
STYLELINT = os.path.join(ROOT, 'node_modules', 'stylelint', 'bin', 'stylelint.mjs')


def lint(tmp_path, css):
    """(rule, line) for every warning the configuration raises on css."""
    assert os.path.exists(STYLELINT), 'stylelint is not installed; run npm ci at the repository root'
    sheet = tmp_path / 'sheet.css'
    sheet.write_text(css, encoding='utf-8')
    proc = subprocess.run(['node', STYLELINT, '--config', CONFIG, '--formatter', 'json', str(sheet)],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 2), proc.stderr
    report = json.loads(proc.stdout or proc.stderr)
    return [(w['rule'], w['line']) for result in report for w in result['warnings']]


def rules(found):
    return sorted({rule for rule, _ in found})


# --- text-align: justify -------------------------------------------------------

def test_justified_text_is_refused(tmp_path):
    found = lint(tmp_path, 'p { text-align: justify; }\n.a { text-align-last: justify; }\n.b { text-align: left; }\n')
    assert found == [('declaration-property-value-disallowed-list', 1), ('declaration-property-value-disallowed-list', 2)]


# --- a fixed height on what holds text -------------------------------------------

def test_a_fixed_height_or_block_size_on_a_text_rule_is_refused(tmp_path):
    css = '.label { height: 40px; }\n.title { block-size: 2rem; }\n.row { height: calc(1em + 4px); }\n'
    assert lint(tmp_path, css) == [('shortarrow/no-fixed-text-height', n) for n in (1, 2, 3)]


def test_heights_that_follow_their_content_pass(tmp_path):
    css = ('.a { height: auto; }\n.b { height: 100%; }\n.c { min-height: 40px; }\n'
           '.d { height: fit-content; }\n.e { height: 0; }\n.f { height: var(--h); }\n')
    assert lint(tmp_path, css) == []


def test_media_scrolling_boxes_and_decorations_may_have_a_fixed_height(tmp_path):
    css = ('img { height: 40px; }\n.logo svg { height: 1em; }\nvideo, canvas { height: 200px; }\n'
           '.log { height: 200px; overflow-y: auto; }\n.dot::before { content: ""; height: 8px; }\n')
    assert lint(tmp_path, css) == []


# --- contrast ------------------------------------------------------------------------

def test_a_pair_under_seven_to_one_is_refused_and_the_boundary_passes(tmp_path):
    css = ('.weak { color: #777; background: #fff; }\n'
           '.edge-fail { color: #5a5a5a; background-color: white; }\n'
           '.edge-pass { color: #595959; background-color: #ffffff; }\n'
           '.strong { color: rgb(0 0 0); background: hsl(0 0% 100%); }\n')
    assert lint(tmp_path, css) == [('shortarrow/text-contrast', 1), ('shortarrow/text-contrast', 2)]


def test_custom_properties_are_resolved_from_the_root(tmp_path):
    css = (':root { --fg: #767676; --bg: #fff; }\n'
           '.a { color: var(--fg); background: var(--bg); }\n'
           '.b { color: var(--missing); background: #fff; }\n')
    assert lint(tmp_path, css) == [('shortarrow/text-contrast', 2)]


def test_each_theme_is_judged_with_its_own_values(tmp_path):
    """Light passes; the dark theme's values fail, and only that is reported."""
    css = (':root { --fg: #000; --bg: #fff; }\n'
           '@media (prefers-color-scheme: dark) { :root { --fg: #444; --bg: #000; } }\n'
           '.a { color: var(--fg); background: var(--bg); }\n')
    found = lint(tmp_path, css)
    assert found == [('shortarrow/text-contrast', 3)]


def test_what_the_stylesheet_alone_cannot_settle_is_not_judged(tmp_path):
    """Translucency, currentColor, transparency, images, mixes, and a pair split across rules."""
    css = ('.a { color: rgba(0, 0, 0, 0.5); background: #fff; }\n'
           '.b { color: currentColor; background: #fff; }\n'
           '.c { color: #777; background: transparent; }\n'
           '.d { color: #777; background: linear-gradient(#fff, #eee); }\n'
           '.e { color: color-mix(in srgb, #777, #fff); background: #fff; }\n'
           '.f { color: #777; }\n.f > span { background: #fff; }\n')
    assert lint(tmp_path, css) == []
