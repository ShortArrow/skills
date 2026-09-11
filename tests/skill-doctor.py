"""Report the health of every skill in a directory, the way the host will see it.

    python tests/skill-doctor.py [skills-dir] [--strict] [--json] [--host]

Claude Code's own /skill-doctor reports usage and context cost, and
`claude plugin validate` checks manifests; neither reads a SKILL.md the way
the runtime does, and on 2026-09-10 both passed a skill whose description
the runtime could not parse. This does, for each skill:

  yaml      the frontmatter parses with a YAML parser, name matches the
            directory, description is a non-empty string (a plain scalar
            containing ": " is not YAML, and the runtime then loads no
            description at all)
  desc      description length: warn over 1,000 characters; error over
            1,024, where Copilot CLI rejects the skill outright, and over
            1,536, where Claude Code truncates
  layers    every references/*.md is named in the body, every references/
            scripts/ assets/ path the body names exists, and a skill with
            references/japanese.md carries a "Language layers" section
  wrap      SKILL.md and its references follow the one-sentence-per-line
            rule (tests/reflow-prose.py --check)

then the marketplace beside the skills directory:

  member    every skill is in exactly one plugin and every listed path
            exists
  hooks     a plugin's hooks are the inline object a marketplace entry
            accepts (a file path is silently ignored), and every script
            they run under ${CLAUDE_PLUGIN_ROOT} exists
  listing   the characters each plugin adds to the skill listing against
            the runtime default (1% of a 200k context, 8,000 characters),
            and the skillListingBudgetFraction that holds them all; over
            budget, the least-used skills are listed by name only

and, with --host, what this machine's Claude Code actually loaded:

  cache     the installed plugin cache is at the current commit; if it is
            behind, the host is describing an older tree
  loaded    `claude plugin details` lists every skill with an always-on
            cost; a skill at "< 20" tokens loaded with no description

Exit 1 on any error; with --strict, on any warning too. --json prints the
report as one object.
"""
import glob
import importlib.util
import io
import json
import os
import re
import subprocess
import sys

import yaml

FENCE = '\n---\n'
DESC_WARN = 1000
DESC_COPILOT = 1024
DESC_CAP = 1536
CONTEXT_CHARS = 200000 * 4
DEFAULT_FRACTION = 0.01
RESOURCE = re.compile(r'(?:`|\()((?:scripts|references|assets)/[^`)\s]+)')
PLUGIN_ROOT_SCRIPT = re.compile(r'CLAUDE_PLUGIN_ROOT\}/([^"\' ]+)')

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
            report['errors'].append(f'desc: {n} characters, Claude Code truncates at {DESC_CAP} and Copilot CLI rejects the skill over {DESC_COPILOT}')
        elif n > DESC_COPILOT:
            report['errors'].append(f'desc: {n} characters, Copilot CLI rejects a skill whose description exceeds {DESC_COPILOT} and never lists it')
        elif n > DESC_WARN:
            report['warnings'].append(f'desc: {n} characters, over the {DESC_WARN} house cap (Copilot CLI rejects at {DESC_COPILOT})')

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


def examine_marketplace(repo, reports):
    out = {'errors': [], 'warnings': [], 'plugins': {}, 'total': 0, 'fraction_needed': 0.0, 'name': None}
    path = os.path.join(repo, '.claude-plugin', 'marketplace.json')
    chars = {r['name']: r['description_chars'] + len(r['name']) + 4 for r in reports}
    if not os.path.exists(path):
        out['total'] = sum(chars.values())
        out['fraction_needed'] = out['total'] / CONTEXT_CHARS
        return out
    try:
        data = json.load(io.open(path, encoding='utf-8'))
    except ValueError as error:
        out['errors'].append(f'member: marketplace.json is not JSON: {error}')
        return out
    out['name'] = data.get('name')
    seen = {}
    for plugin in data.get('plugins', []):
        pname = plugin.get('name', '?')
        total = 0
        for rel in plugin.get('skills', []):
            skill = os.path.basename(rel)
            if not os.path.isdir(os.path.join(repo, *rel.strip('./').split('/'))):
                out['errors'].append(f'member: {pname} lists {rel}, which does not exist')
                continue
            seen.setdefault(skill, []).append(pname)
            total += chars.get(skill, 0)
        out['plugins'][pname] = total
        hooks = plugin.get('hooks')
        if isinstance(hooks, str):
            out['errors'].append(f'hooks: {pname} gives hooks as a file path ({hooks}); a marketplace entry only accepts the inline object, and this form is silently ignored')
        elif isinstance(hooks, dict):
            for event, groups in hooks.items():
                for group in groups:
                    for hook in group.get('hooks', []):
                        for script in PLUGIN_ROOT_SCRIPT.findall(hook.get('command', '')):
                            if not os.path.exists(os.path.join(repo, *script.split('/'))):
                                out['errors'].append(f'hooks: {pname} {event} runs {script}, which does not exist')
        elif hooks is not None:
            out['errors'].append(f'hooks: {pname} hooks has an unexpected type {type(hooks).__name__}')
    for r in reports:
        owners = seen.get(r['name'], [])
        if not owners:
            out['errors'].append(f'member: {r["name"]} is in no plugin, so no install carries it')
        elif len(owners) > 1:
            out['warnings'].append(f'member: {r["name"]} is in {len(owners)} plugins ({", ".join(owners)})')
    out['total'] = sum(out['plugins'].values())
    out['fraction_needed'] = out['total'] / CONTEXT_CHARS
    return out


def examine_host(repo, market, reports):
    """What the installed Claude Code plugins actually loaded."""
    out = {'errors': [], 'warnings': [], 'notes': []}
    if not market.get('name'):
        out['warnings'].append('host: no marketplace name, cannot look up installed plugins')
        return out
    head = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    installed_path = os.path.join(os.path.expanduser('~'), '.claude', 'plugins', 'installed_plugins.json')
    installed = {}
    if os.path.exists(installed_path):
        installed = json.load(io.open(installed_path, encoding='utf-8')).get('plugins', {})
    env = dict(os.environ)
    env.pop('CLAUDECODE', None)
    for pname in market['plugins']:
        key = f'{pname}@{market["name"]}'
        entries = installed.get(key)
        if not entries:
            out['notes'].append(f'host: {key} is not installed here')
            continue
        sha = entries[0].get('gitCommitSha', '')
        if head and sha and not head.startswith(sha) and not sha.startswith(head[:len(sha)]):
            out['warnings'].append(f'cache: {key} is at {sha[:12]}, HEAD is {head[:12]}; the host is describing an older tree (claude plugin update {key})')
        try:
            proc = subprocess.run(['claude', 'plugin', 'details', key], capture_output=True, text=True, env=env, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as error:
            out['warnings'].append(f'host: could not run claude plugin details for {key}: {error}')
            continue
        listed = {}
        for line in proc.stdout.splitlines():
            m = re.match(r'^\s+([a-z0-9-]+)\s+(<\s*\d+|~[\d,]+k?)\s+', line)
            if m:
                listed[m.group(1)] = m.group(2).replace(' ', '')
        if not listed:
            out['warnings'].append(f'host: could not read the component table for {key}')
            continue
        for r in reports:
            if r['name'] in listed and listed[r['name']].startswith('<'):
                out['errors'].append(f'loaded: {key} loaded {r["name"]} with no description (always-on {listed[r["name"]]} tokens)')
    return out


def main(argv):
    strict = '--strict' in argv
    as_json = '--json' in argv
    host = '--host' in argv
    args = [a for a in argv if not a.startswith('--')]
    root = os.path.abspath(args[0]) if args else os.path.join(os.path.dirname(here), 'skills')
    repo = os.path.dirname(root)
    dirs = sorted(d for d in glob.glob(os.path.join(root, '*')) if os.path.isdir(d))
    reports = [examine(d) for d in dirs]
    market = examine_marketplace(repo, reports)
    hostinfo = examine_host(repo, market, reports) if host else {'errors': [], 'warnings': [], 'notes': []}
    errors = sum(len(r['errors']) for r in reports) + len(market['errors']) + len(hostinfo['errors'])
    warnings = sum(len(r['warnings']) for r in reports) + len(market['warnings']) + len(hostinfo['warnings'])
    default_budget = int(CONTEXT_CHARS * DEFAULT_FRACTION)

    if as_json:
        print(json.dumps({'skills': reports, 'marketplace': market, 'host': hostinfo, 'errors': errors, 'warnings': warnings}, ensure_ascii=False, indent=2))
    else:
        width = max(len(r['name']) for r in reports) if reports else 5
        print(f'{"skill":<{width}}  desc  status')
        for r in reports:
            status = 'ERROR' if r['errors'] else ('warn' if r['warnings'] else 'ok')
            print(f'{r["name"]:<{width}}  {r["description_chars"]:>4}  {status}')
            for e in r['errors']:
                print(f'{"":<{width}}        ! {e}')
            for w in r['warnings']:
                print(f'{"":<{width}}        ~ {w}')
        print()
        print('Marketplace')
        for e in market['errors']:
            print(f'  ! {e}')
        for w in market['warnings']:
            print(f'  ~ {w}')
        if not market['errors'] and not market['warnings']:
            print('  every skill in one plugin, every path present, hooks in the inline form')
        print()
        print(f'Skill listing: default budget {default_budget} characters (1% of a 200k context); over it, the least-used skills are listed by name only.')
        for plugin, chars in market['plugins'].items():
            print(f'  {plugin:<20} {chars:>6}  {"over" if chars > default_budget else "fits"}')
        print(f'  {"all":<20} {market["total"]:>6}  needs skillListingBudgetFraction >= {market["fraction_needed"]:.3f} for this catalogue alone')
        print('  Other plugins and the bundled skills share the same budget; `claude --debug` logs "Skill listing over budget" with the real totals.')
        if host:
            print()
            print('Host (installed Claude Code plugins)')
            for e in hostinfo['errors']:
                print(f'  ! {e}')
            for w in hostinfo['warnings']:
                print(f'  ~ {w}')
            for n in hostinfo['notes']:
                print(f'  - {n}')
            if not hostinfo['errors'] and not hostinfo['warnings']:
                print('  every installed plugin is at HEAD and every skill loaded with a description')
        print()
        print(f'{len(reports)} skills, {errors} errors, {warnings} warnings')
    return 1 if errors or (strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
