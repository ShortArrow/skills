"""Fetch issues from the tracker (here: data/issues.json, paged) and print them as JSON."""
import argparse
import json
import os

DATA = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'issues.json')


def page(offset, limit):
    with open(DATA, encoding='utf-8') as fh:
        issues = json.load(fh)
    return issues[offset:offset + limit], len(issues)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=100)
    args = parser.parse_args()
    records, total = page(0, args.limit)
    print(json.dumps(records, ensure_ascii=False))
    print(f'fetched {len(records)} records', file=__import__('sys').stderr)


if __name__ == '__main__':
    main()
