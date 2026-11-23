"""Report Python tests whose every assertion is that a call happened.

    python occurrence-only.py <file or folder>...

A test that checks only that `redraw` was called, or how many times, passes while
what was drawn is wrong, and passes as well when another path makes the same call.
Read with the syntax tree, from test_*.py and *_test.py files: a test function is
reported when it asserts at least once and every assertion is one of
`m.assert_called()`, `m.assert_called_once()`, `assert m.called`,
`assert m.call_count == n`, or their unittest forms (`assertTrue(m.called)`,
`assertEqual(m.call_count, n)`). An assertion on the arguments, on a value, or that
a call did not happen is not occurrence-only. A test with no assertion is not
reported here.

Prints `path:line: name ...` per test and exits 1 when any is found, else 0.
"""
import ast
import os
import sys

OCCURRENCE_METHODS = {'assert_called', 'assert_called_once'}
OCCURRENCE_ATTRIBUTES = {'called', 'call_count'}
UNITTEST_ASSERTS = {'assertTrue', 'assertFalse', 'assertEqual', 'assertEquals', 'assertGreater',
                    'assertGreaterEqual', 'assertLess', 'assertLessEqual', 'assertNotEqual', 'assertIs',
                    'assertIsNot', 'assertIsNone', 'assertIsNotNone', 'assertIn', 'assertNotIn'}
MESSAGE = 'asserts only that a call happened, not what it carried or produced'


def reads_only_occurrence(node):
    """Whether every value the expression reads is a mock's called or call_count, and it reads one."""
    attributes = [n for n in ast.walk(node) if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Load)]
    names = [n for n in ast.walk(node) if isinstance(n, ast.Name)]
    occurrence = [a for a in attributes if a.attr in OCCURRENCE_ATTRIBUTES]
    if not occurrence:
        return False
    inside = {id(n) for a in occurrence for n in ast.walk(a.value)}
    other = [a for a in attributes if a.attr not in OCCURRENCE_ATTRIBUTES and id(a) not in inside]
    loose = [n for n in names if id(n) not in inside]
    return not other and not loose


def assertions(function):
    """('occurrence' | 'content') for each assertion in the function body, nested functions excluded."""
    kinds = []
    stack = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Assert):
            kinds.append('occurrence' if reads_only_occurrence(node.test) else 'content')
            continue
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in OCCURRENCE_METHODS and not node.args and not node.keywords:
                kinds.append('occurrence')
                continue
            if method in UNITTEST_ASSERTS:
                values = list(node.args[:2])
                occurrence = values and all(reads_only_occurrence(v) or isinstance(v, ast.Constant) for v in values) \
                    and any(reads_only_occurrence(v) for v in values)
                kinds.append('occurrence' if occurrence else 'content')
                continue
            if method.startswith('assert') or method in ('raises', 'warns'):
                kinds.append('content')
        stack.extend(ast.iter_child_nodes(node))
    return kinds


def tests_in(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test'):
            yield node


def findings(path):
    with open(path, encoding='utf-8') as handle:
        tree = ast.parse(handle.read(), filename=path)
    for test in tests_in(tree):
        kinds = assertions(test)
        if kinds and all(k == 'occurrence' for k in kinds):
            yield f'{path}:{test.lineno}: {test.name} {MESSAGE}'


def test_files(paths):
    for path in paths:
        if os.path.isfile(path):
            yield path
            continue
        for folder, _, names in sorted(os.walk(path)):
            for name in sorted(names):
                if name.endswith('.py') and (name.startswith('test_') or name.endswith('_test.py')):
                    yield os.path.join(folder, name)


def main(argv):
    found = [line for path in test_files(argv[1:] or ['.']) for line in findings(path)]
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
