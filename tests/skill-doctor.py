"""Report the health of every skill in a directory, the way the host will see it.

    python tests/skill-doctor.py [skills-dir] [--strict] [--json]

Claude Code's own /skill-doctor reports usage and context cost, and
`claude plugin validate` checks manifests; neither reads a SKILL.md the way
the runtime does. This does, for each skill:

  yaml      the frontmatter parses with a YAML parser, name matches the
            directory, description is a non-empty string (a plain scalar
            containing ": " is not YAML, and the runtime then loads no
            description at all)
  desc      description length: warn over 1,200 characters, error over
            1,536, which is where the runtime truncates
  layers    every references/*.md is named in the body, every references/
            scripts/ assets/ path the body names exists, and a skill with
            references/japanese.md carries a "Language layers" section
  wrap      SKILL.md and its references follow the one-sentence-per-line
            rule (tests/reflow-prose.py --check)

and then the listing budget: the characters each plugin adds to the skill
listing against the runtime default (1% of a 200k context, 8,000
characters), and the skillListingBudgetFraction that holds them all. Over
budget, the least-used skills are listed by name only and never fire on
their description.

Exit 1 on any error; with --strict, on any warning too. --json prints the
report as one object.
"""
import glob
import importlib.util
import io
import json
import os
import re
import sys

import yaml

FENCE = '\n---\n'
DESC_WARN = 1200
DESC_CAP = 1536
CONTEXT_CHARS = 200000 * 4
DEFAULT_FRACTION = 0.01
RESOURCE = re.compile(r'(?:`|\()((?:scripts|references|assets)/[^`)\s]+)')

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('reflow_prose', os.path.join(here, 'reflow-prose.py'))
reflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reflow)


def would_rewrap(path):
    src = io.open(path, encoding='utf-8').read()
    if src.startswith('---\n') and FENCE in src[4:]:
        k = src.index(FENCE, 4) + 5
        fm, body = src[:k], src[k:]
    else:
        fm, body = '', src
    return fm + '\n'.join(reflow.reflow(body.split('\n'))) != src


def examine(skill_dir):
    name = os.path.basename(skill_dir)
    path = os.path.join(skill_dir, 'SKILL.md')
    report = {'name': name, 'errors': [], 'warnings': [], 'description_chars': 0}
    if not os.path.exists(path):
        report['errors'].append('no SKILL.md')
        return report
    text = io.open(path, encoding='utf-8').read()
    if not text.startswith('---\n') or FENCE not in text[4:]:
        report['errors'].append('yaml: no frontmatter fence')
        return report
    frontmatter, body = text[4:text.index(FENCE, 4)], text[text.index(FENCE, 4) + 5:]
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as error:
        report['errors'].append('yaml: ' + str(error).splitlines()[0] + ' (write the description as a block scalar, description: |)')
        return report
    if not isinstance(data, dict):
        report['errors'].append('yaml: frontmatter is not a mapping')
        return report
    if data.get('name') != name:
        report['errors'].append(f'yaml: name is {data.get("name")!r}, directory is {name!r}')
    description = data.get('description')
    if not isinstance(description, str) or not description.strip():
        report['errors'].append('yaml: description missing or empty after parsing')
    else:
        n = len(description.strip())
        report['description_chars'] = n
        if n > DESC_CAP:
            report['errors'].append(f'desc: {n} characters, the runtime truncates at {DESC_CAP}')
        elif n > DESC_WARN:
            report['warnings'].append(f'desc: {n} characters, over the {DESC_WARN} house cap; the "Use when" tail is what truncation removes')

    for rel in RESOURCE.findall(text):
        rel = rel.rstrip('.,:;')
        if not os.path.exists(os.path.join(skill_dir, *rel.split('/'))):
            report['errors'].append(f'layers: body names {rel}, which does not exist')
    references = glob.glob(os.path.join(skill_dir, 'references', '*.md'))
    for ref in references:
        rel = 'references/' + os.path.basename(ref)
        if rel not in text:
            report['errors'].append(f'layers: {rel} exists but the body never names it, so it is never read')
    if any(os.path.basename(r) == 'japanese.md' for r in references) and not re.search(r'^#+ Language layers\s*$', body, re.M):
        report['warnings'].append('layers: has references/japanese.md but no "Language layers" section')

    for f in [path] + references:
        try:
            if would_rewrap(f):
                report['warnings'].append(f'wrap: {os.path.relpath(f, skill_dir)} is not wrapped one sentence per line (tests/reflow-prose.py)')
        except Exception as error:
            report['warnings'].append(f'wrap: could not check {os.path.relpath(f, skill_dir)}: {error}')
    return report


def listing_budget(repo, reports):
    marketplace = os.path.join(repo, '.claude-plugin', 'marketplace.json')
    chars = {r['name']: r['description_chars'] + len(r['name']) + 4 for r in reports}
    if not os.path.exists(marketplace):
        total = sum(chars.values())
        return {'plugins': {}, 'total': total, 'fraction_needed': total / CONTEXT_CHARS}
    plugins = {}
    for plugin in json.load(io.open(marketplace, encoding='utf-8'))['plugins']:
        plugins[plugin['name']] = sum(chars.get(os.path.basename(rel), 0) for rel in plugin['skills'])
    total = sum(plugins.values())
    return {'plugins': plugins, 'total': total, 'fraction_needed': total / CONTEXT_CHARS}


def main(argv):
    strict = '--strict' in argv
    as_json = '--json' in argv
    args = [a for a in argv if not a.startswith('--')]
    root = os.path.abspath(args[0]) if args else os.path.join(os.path.dirname(here), 'skills')
    repo = os.path.dirname(root)
    dirs = sorted(d for d in glob.glob(os.path.join(root, '*')) if os.path.isdir(d))
    reports = [examine(d) for d in dirs]
    budget = listing_budget(repo, reports)
    errors = sum(len(r['errors']) for r in reports)
    warnings = sum(len(r['warnings']) for r in reports)
    default_budget = int(CONTEXT_CHARS * DEFAULT_FRACTION)

    if as_json:
        print(json.dumps({'skills': reports, 'listing': budget, 'errors': errors, 'warnings': warnings}, ensure_ascii=False, indent=2))
    else:
        width = max(len(r['name']) for r in reports) if reports else 5
        print(f'{"skill":<{width}}  desc  status')
        for r in reports:
            status = 'ok'
            if r['errors']:
                status = 'ERROR'
            elif r['warnings']:
                status = 'warn'
            print(f'{r["name"]:<{width}}  {r["description_chars"]:>4}  {status}')
            for e in r['errors']:
                print(f'{"":<{width}}        ! {e}')
            for w in r['warnings']:
                print(f'{"":<{width}}        ~ {w}')
        print()
        print(f'Skill listing: default budget {default_budget} characters (1% of a 200k context); over it, the least-used skills are listed by name only.')
        for plugin, chars in budget['plugins'].items():
            mark = 'over' if chars > default_budget else 'fits'
            print(f'  {plugin:<20} {chars:>6}  {mark}')
        print(f'  {"all":<20} {budget["total"]:>6}  needs skillListingBudgetFraction >= {budget["fraction_needed"]:.3f}')
        print()
        print(f'{len(reports)} skills, {errors} errors, {warnings} warnings')
    return 1 if errors or (strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
