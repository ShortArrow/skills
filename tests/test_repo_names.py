"""Tests for skills/guard-private-names/scripts/repo-names.py, written before the hook exists.

The pre-push hook refuses a push whose commits carry the name of a repository
the user belongs to privately or keeps a clone of. Each case fixes one decision:
what counts as a hit, what is never printed, and when not knowing the names
must stop the push rather than let it through.
"""
import hashlib
import importlib.util
import os
import subprocess

HOOK = os.path.join(os.path.dirname(__file__), '..', 'skills', 'guard-private-names', 'scripts', 'repo-names.py')
spec = importlib.util.spec_from_file_location('repo_names', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

ZERO = '0' * 40


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com',
                           '-c', 'commit.gpgsign=false', *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def commit(path, files, message='c'):
    for name, text in files.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            target.unlink()
        else:
            target.write_text(text, encoding='utf-8')
    git(path, 'add', '-A')
    git(path, 'commit', '-q', '-m', message)
    return git(path, 'rev-parse', 'HEAD')


def repo(path):
    git(path, 'init', '-q', '-b', 'main')
    return path


def ident(name):
    return hashlib.sha256(name.lower().encode('utf-8')).hexdigest()[:8]


# --- what reaches the check ------------------------------------------------

def test_stdin_lines_become_pushes():
    pushes = hook.parse_pushes('refs/heads/a 1111 refs/heads/main 2222\n\n')
    assert pushes == [('refs/heads/a', '1111', 'refs/heads/main', '2222')]


def test_a_deleted_ref_is_not_scanned(tmp_path):
    r = repo(tmp_path)
    commit(r, {'a.md': 'secretproj\n'})
    found = hook.scan(str(r), [('(delete)', ZERO, 'refs/heads/x', '1' * 40)], {'secretproj': 'private'}, 'origin')
    assert found == []


# --- what counts as a hit --------------------------------------------------

def test_a_private_name_in_the_pushed_tree_is_found_at_its_line(tmp_path):
    r = repo(tmp_path)
    tip = commit(r, {'docs/a.md': 'one\ntwo SecretProj three\n'})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], {'secretproj': 'private'}, 'origin')
    assert [(f['path'], f['line'], f['id']) for f in found] == [('docs/a.md', 2, ident('secretproj'))]


def test_a_name_inside_a_longer_word_is_not_a_hit(tmp_path):
    r = repo(tmp_path)
    tip = commit(r, {'a.md': 'profiles and filesystem\n'})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], {'files': 'private'}, 'origin')
    assert found == []


def test_a_name_joined_by_a_hyphen_is_a_hit(tmp_path):
    r = repo(tmp_path)
    tip = commit(r, {'a.md': 'session files-5b\n'})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], {'files': 'private'}, 'origin')
    assert len(found) == 1


def test_a_name_added_then_removed_in_pushed_history_is_found(tmp_path):
    r = repo(tmp_path)
    commit(r, {'a.md': 'clean\n'})
    commit(r, {'b.md': 'secretproj leaked\n'})
    tip = commit(r, {'b.md': None})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], {'secretproj': 'private'}, 'origin')
    assert [(f['path'], f['line']) for f in found] == [('b.md', None)]
    assert found[0]['commit'] != tip[:7]


def test_a_name_inside_a_longer_word_in_pushed_history_is_not_a_hit(tmp_path):
    r = repo(tmp_path)
    commit(r, {'a.md': 'clean\n'})
    commit(r, {'b.md': 'profiles and filesystem\n'})
    tip = commit(r, {'b.md': None})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], {'files': 'private'}, 'origin')
    assert found == []


def test_history_already_on_the_remote_is_not_scanned_again(tmp_path):
    r = repo(tmp_path)
    old = commit(r, {'b.md': 'secretproj leaked\n'})
    commit(r, {'b.md': None})
    tip = commit(r, {'a.md': 'clean\n'})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', old)], {'secretproj': 'private'}, 'origin')
    assert found == []


# --- how a name is matched, by whether its words are in the dictionary ------

def test_a_name_splits_into_words_at_case_changes_separators_and_digits():
    assert hook.words_of('SampleRepoName') == ['sample', 'repo', 'name']
    assert hook.words_of('sample-repo_name') == ['sample', 'repo', 'name']
    assert hook.words_of('HTTPServer2') == ['http', 'server', '2']


def scan_text(tmp_path, text, names, words):
    r = repo(tmp_path)
    tip = commit(r, {'a.md': text})
    return hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], names, 'origin', words)


def test_a_name_with_a_word_outside_the_dictionary_is_found_however_it_is_joined(tmp_path):
    text = 'my-qzx-tool\nmy_qzx_tool\nMy Qzx Tool\nMyQzxTool\nmyqzxtool\n'
    found = scan_text(tmp_path, text, {'MyQzxTool': 'private'}, {'my', 'tool'})
    assert [f['line'] for f in found] == [1, 2, 3, 4, 5]


def test_a_name_of_dictionary_words_is_found_only_as_written(tmp_path):
    text = 'sample-repo-name\nSample Repo Name\nSample-Repo-Name\nsamplereponame\n'
    found = scan_text(tmp_path, text, {'sample-repo-name': 'private'}, {'sample', 'repo', 'name'})
    assert [f['line'] for f in found] == [1]


def test_a_name_of_one_dictionary_word_is_not_checked(tmp_path):
    assert scan_text(tmp_path, 'see the docs\n', {'docs': 'private'}, {'docs'}) == []


def test_a_number_counts_as_a_word_of_the_name(tmp_path):
    found = scan_text(tmp_path, 'project-01\nproject\nproject01\n', {'project-01': 'private'}, {'project'})
    assert [f['line'] for f in found] == [1]


def test_the_dictionary_is_read_after_its_license_header(tmp_path):
    path = tmp_path / 'words.txt'
    path.write_text('Copyright notice\nwith words in it\n---\nalpha\nbeta\n', encoding='utf-8')
    assert hook.load_words(str(path)) == {'alpha', 'beta'}


# --- which names are checked -----------------------------------------------

def run_returning(outputs):
    def run(*args):
        for prefix, out in outputs.items():
            if ' '.join(args).startswith(prefix):
                if isinstance(out, Exception):
                    raise out
                return out
        return ''
    return run


def test_public_names_are_dropped_and_private_ones_kept():
    run = run_returning({
        'gh api --paginate': 'secretproj\tprivate\nopenproj\tpublic\nworkthing\tinternal\n',
        'ghq list': '',
    })
    assert hook.load_names(run) == {'secretproj': 'private', 'workthing': 'private'}


def test_a_ghq_clone_confirmed_public_on_github_is_dropped():
    run = run_returning({
        'gh api --paginate': '',
        'ghq list': 'github.com/someone/openclone\ngithub.com/other/hidden\nexample.org/x/selfhosted\n',
        'gh api graphql': '{"data":{"r0":{"isPrivate":false},"r1":null}}',
    })
    assert hook.load_names(run) == {'hidden': 'ghq', 'selfhosted': 'ghq'}


def test_names_shorter_than_three_characters_are_ignored():
    run = run_returning({'gh api --paginate': 'ab\tprivate\nabc\tprivate\n', 'ghq list': ''})
    assert hook.load_names(run) == {'abc': 'private'}


def test_when_gh_cannot_list_the_names_the_push_is_refused():
    run = run_returning({'gh api --paginate': hook.NamesUnknown('gh: not logged in')})
    try:
        hook.load_names(run)
    except hook.NamesUnknown:
        return
    raise AssertionError('load_names returned while gh had failed')


def test_a_failing_command_raises_and_keeps_what_it_printed():
    import sys
    try:
        hook.run(sys.executable, '-c', 'print("partial"); raise SystemExit(1)')
    except hook.NamesUnknown as error:
        assert error.stdout.strip() == 'partial'
        return
    raise AssertionError('run returned for a command that exited 1')


def test_the_pushed_repositorys_own_name_and_allowed_names_are_dropped():
    names = {'skills': 'ghq', 'docs': 'private', 'secretproj': 'private'}
    kept = hook.drop(names, allowed={'docs'}, own='https://github.com/ShortArrow/skills.git')
    assert kept == {'secretproj': 'private'}


# --- what is printed -------------------------------------------------------

def test_the_report_never_prints_a_name(tmp_path):
    r = repo(tmp_path)
    tip = commit(r, {'a.md': 'SecretProj here\n'})
    found = hook.scan(str(r), [('refs/heads/main', tip, 'refs/heads/main', ZERO)], {'secretproj': 'private'}, 'origin')
    text = hook.report(found, allowed_path='.git/info/repo-names-allowed', script='x')
    assert 'secretproj' not in text.lower()
    assert 'a.md:1:' in text and ident('secretproj') in text


def test_the_report_counts_every_id_even_past_the_shown_places():
    found = [{'commit': 'c', 'path': f'f{i}.md', 'line': 1, 'col': 1, 'id': 'aaaaaaaa', 'kind': 'private'}
             for i in range(hook.SHOWN + 5)]
    found.append({'commit': 'c', 'path': 'z.md', 'line': 1, 'col': 1, 'id': 'bbbbbbbb', 'kind': 'ghq'})
    text = hook.report(found, allowed_path='x', script='x')
    assert f'aaaaaaaa  private  {hook.SHOWN + 5}' in text
    assert 'bbbbbbbb  ghq  1' in text


def test_the_report_names_the_script_where_it_was_installed():
    found = [{'commit': 'c', 'path': 'a.md', 'line': 1, 'col': 1, 'id': 'aaaaaaaa', 'kind': 'private'}]
    text = hook.report(found, allowed_path='x', script='.git/hooks/repo-names.py')
    assert 'python .git/hooks/repo-names.py --explain ID' in text


def test_explain_maps_an_id_back_to_its_name():
    assert hook.explain(ident('secretproj'), {'secretproj': 'private', 'other': 'ghq'}) == ['secretproj']
