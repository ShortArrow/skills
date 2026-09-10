"""Refuse a SKILL.md whose frontmatter the host cannot read.

    python tests/check-frontmatter.py [skills-dir]

The host parses the frontmatter as YAML and loads name and description
into every session. A description written as a plain scalar that contains
": " is not YAML ("mapping values are not allowed here"), and the host then
loads no description at all: the skill costs nothing always-on and never
fires on its description. That failure is silent in every listing, so it is
checked here with a real parser. Exits 1 on the first file that fails.
"""
import glob
import io
import os
import sys

import yaml

root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills')
failures = []
for path in sorted(glob.glob(os.path.join(root, '*', 'SKILL.md'))):
    name = os.path.basename(os.path.dirname(path))
    text = io.open(path, encoding='utf-8').read()
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        failures.append(f'{name}: no frontmatter fence')
        continue
    frontmatter = text[4:text.index('\n---\n', 4)]
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
for failure in failures:
    print(failure, file=sys.stderr)
    print('  Fix: write the description as a block scalar (description: |) so ": " and quotes are literal.', file=sys.stderr)
if not failures:
    print(f'Frontmatter parses for {len(glob.glob(os.path.join(root, "*", "SKILL.md")))} skills.')
sys.exit(1 if failures else 0)
