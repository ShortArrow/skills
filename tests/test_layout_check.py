"""Tests for skills/interface-design/scripts/layout/, written before the scripts exist.

    python -m pytest tests/test_layout_check.py

layout-check.mjs opens each page of a served folder in headless Chrome at each
width and reports what leaves its box: an element outside its parent, content a
box cannot hold, a page that scrolls sideways. layout.test.mjs is the file a
project copies in, driven by its layout.config.json. The fixtures under
tests/fixtures/layout-check/site each make one of those happen, or none.
Needs Node 22 or later and Chrome (CHROME_PATH overrides where it is looked for).
"""
import json
import os
import shutil
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', 'skills', 'interface-design', 'scripts', 'layout')
CHECK = os.path.join(SCRIPTS, 'layout-check.mjs')
TEMPLATE = os.path.join(SCRIPTS, 'layout.test.mjs')
SITE = os.path.join(HERE, 'fixtures', 'layout-check', 'site')
WIDTHS = [375, 601, 1040, 1280]
CHROMES = ['C:/Program Files/Google/Chrome/Application/chrome.exe', '/usr/bin/google-chrome', '/usr/bin/chromium',
           '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']

pytestmark = pytest.mark.skipif(
    not shutil.which('node') or not (os.environ.get('CHROME_PATH') or any(map(os.path.exists, CHROMES))),
    reason='needs node and Chrome')


def check(pages, widths=WIDTHS):
    """checkLayout's result for pages of the fixture site: one entry per page and width."""
    script = ("const m = await import(process.argv[1]);"
              "const r = await m.checkLayout({ dir: process.argv[2], pages: JSON.parse(process.argv[3]),"
              " widths: JSON.parse(process.argv[4]) });"
              "console.log(JSON.stringify(r));")
    url = 'file:///' + os.path.abspath(CHECK).replace('\\', '/').lstrip('/')
    proc = subprocess.run(['node', '--input-type=module', '-e', script, url, SITE, json.dumps(pages), json.dumps(widths)],
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def problems_by_width(result, page):
    return {r['width']: r['problems'] for r in result if r['page'] == page}


def test_a_clean_page_passes_at_every_width():
    result = check(['/clean.html'])
    assert problems_by_width(result, '/clean.html') == {w: [] for w in WIDTHS}
    assert all(r['inspected'] > 0 for r in result)


def test_a_page_that_overflows_only_when_narrow_is_reported_only_there():
    found = problems_by_width(check(['/narrow.html']), '/narrow.html')
    assert found[375], found
    assert any('sideways' in p for p in found[375])
    assert any('outside its parent' in p for p in found[375])
    assert found[601] == found[1040] == found[1280] == []


def test_text_a_fixed_height_cannot_hold_is_reported_at_every_width():
    found = problems_by_width(check(['/clipped.html']), '/clipped.html')
    for width in WIDTHS:
        assert any('.label' in p and 'cannot hold' in p for p in found[width]), (width, found[width])
        assert any('.note' in p and 'cannot hold' in p for p in found[width]), (width, found[width])


def test_what_leaves_a_box_on_purpose_is_not_reported():
    """An absolutely placed badge, a scrolling box and an empty collapsed box."""
    assert problems_by_width(check(['/allowed.html']), '/allowed.html') == {w: [] for w in WIDTHS}


def test_the_copied_template_passes_a_clean_site_and_fails_a_broken_one(tmp_path):
    project = tmp_path / 'project'
    shutil.copytree(SITE, project / 'site')
    (project / 'tests').mkdir()
    shutil.copy(CHECK, project / 'tests' / 'layout-check.mjs')
    shutil.copy(TEMPLATE, project / 'tests' / 'layout.test.mjs')

    def run(pages):
        (project / 'layout.config.json').write_text(json.dumps({'dir': 'site', 'pages': pages}), encoding='utf-8')
        return subprocess.run(['node', '--test', '--test-concurrency=1', 'tests/'], cwd=project,
                              capture_output=True, text=True, timeout=300)

    clean = run(['/clean.html'])
    assert clean.returncode == 0, clean.stdout[-2000:]
    assert 'tests 4' in clean.stdout, 'one test per default width'
    broken = run(['/clipped.html'])
    assert broken.returncode != 0
    assert 'cannot hold' in broken.stdout
