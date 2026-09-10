"""Refuse a SKILL.md whose frontmatter the host cannot read, and report the listing budget.

    python tests/check-frontmatter.py [skills-dir]

The host parses the frontmatter as YAML and loads name and description
into every session. A description written as a plain scalar that contains
": " is not YAML ("mapping values are not allowed here"), and the host then
loads no description at all: the skill costs nothing always-on and never
fires on its description. That failure is silent in every listing, so it is
checked here with a real parser. Exits 1 on the first file that fails.

The host also sends Claude one listing of every loaded skill, capped at
skillListingBudgetFraction of the context window in characters (default
0.01: 8,000 characters at a 200k window). Over the cap, the skills with the
fewest recorded uses lose their descriptions first and are listed by name
only, so a new skill can never fire on its description. The report at the
end gives the per-plugin totals and the fraction that holds the whole
catalogue; it does not fail.
"""
import glob
import io
import json
import os
import sys

import yaml

FENCE = '\n---\n'
DEFAULT_BUDGET_CHARS = 200000 * 4 * 0.01


def frontmatter_of(text):
    if not text.startswith('---\n') or FENCE not in text[4:]:
        return None
    return text[4:text.index(FENCE, 4)]


def main(argv):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = argv[0] if argv else os.path.join(repo, 'skills')
    failures = []
    descriptions = {}
    for path in sorted(glob.glob(os.path.join(root, '*', 'SKILL.md'))):
        name = os.path.basename(os.path.dirname(path))
        text = io.open(path, encoding='utf-8').read()
        frontmatter = frontmatter_of(text)
        if frontmatter is None:
            failures.append(f'{name}: no frontmatter fence')
            continue
        try:
            data = yaml.safe_load(frontmatter)
        except yaml.YAMLError as error:
            failures.append(f'{name}: frontmatter is not YAML: {str(error).splitlines()[0]}')
            continue
        if not isinstance(data, dict):
            failures.append(f'{name}: frontmatter is not a mapping')
            continue
        if data.get('name') != name:
            failures.append(f'{name}: name is {data.get("name")!r}, not the directory name')
        description = data.get('description')
        if not isinstance(description, str) or not description.strip():
            failures.append(f'{name}: description is missing or empty after parsing')
            continue
        descriptions[name] = description.strip()

    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        print('  Fix: write the description as a block scalar (description: |) so ": " and quotes are literal.', file=sys.stderr)
        return 1

    print(f'Frontmatter parses for {len(descriptions)} skills.')
    marketplace = os.path.join(repo, '.claude-plugin', 'marketplace.json')
    if os.path.exists(marketplace):
        totals = {}
        for plugin in json.load(io.open(marketplace, encoding='utf-8'))['plugins']:
            names = [os.path.basename(rel) for rel in plugin['skills']]
            totals[plugin['name']] = sum(len(descriptions.get(n, '')) + len(n) + 4 for n in names)
        grand = sum(totals.values())
        print(f'Skill-listing characters per plugin (default budget {int(DEFAULT_BUDGET_CHARS)} at a 200k context):')
        for name, chars in totals.items():
            print(f'  {name:<20} {chars:6}')
        print(f'  {"all plugins":<20} {grand:6}  whole catalogue needs skillListingBudgetFraction >= {grand / (200000 * 4):.3f}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
