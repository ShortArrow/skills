"""Characterisation tests for hooks/verify-reports.py.

    python -m pytest tests/test_verify_reports.py
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'verify-reports.py')
spec = importlib.util.spec_from_file_location('verify_reports', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def prompt(text):
    return {'type': 'user', 'message': {'role': 'user', 'content': text}}


def launch(use_id, description, name='Agent'):
    return {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': use_id, 'name': name, 'input': {'description': description, 'prompt': '...'}}]}}


def launched(use_id):
    return {'type': 'user', 'toolUseResult': {'isAsync': True, 'status': 'async_launched'},
            'message': {'role': 'user', 'content': [
                {'type': 'tool_result', 'tool_use_id': use_id, 'content': 'Async agent launched successfully.'}]}}


def returned(use_id):
    return {'type': 'user', 'toolUseResult': {'status': 'completed', 'content': []},
            'message': {'role': 'user', 'content': [
                {'type': 'tool_result', 'tool_use_id': use_id, 'content': 'All 12 tests pass.'}]}}


def notified(use_id, status='completed'):
    return {'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': (
        f'<task-notification>\n<task-id>a1</task-id>\n<tool-use-id>{use_id}</tool-use-id>\n'
        f'<status>{status}</status>\n<summary>Agent finished</summary>\n</task-notification>')}}


def background(use_id, description):
    return [launch(use_id, description), launched(use_id), notified(use_id)]


def publish(command, entries):
    return hook.publish_verdict({'tool_input': {'command': command}}, entries)


def stop(entries, active=False):
    return hook.stop_verdict({'stop_hook_active': active}, entries)


REPORTED = [prompt('fix it'), *background('t1', 'Fix the parser')]
VERIFIED = [*REPORTED, *background('t2', 'Verify: parser fix')]


def test_publishing_with_an_unverified_report_is_refused():
    for command in ['git push', 'git -C repo push origin main', 'cd x && git push -u origin b',
                    'gh pr create --draft --title t', 'gh pr ready 63', 'gh issue create -t t']:
        out = publish(command, REPORTED)
        assert out['hookSpecificOutput']['permissionDecision'] == 'deny', command
        assert '"Fix the parser"' in out['hookSpecificOutput']['permissionDecisionReason']


def test_publishing_after_a_verification_is_allowed():
    assert publish('git push', VERIFIED) is None


def test_a_verifier_is_known_by_the_names_sessions_give_it():
    for name in ['Verify PR #250 code', 'Re-verify ADR 0052', 'Skeptic: blast radius of fix',
                 'Adversarially verify PR 251', '#65 adversarial review 1', 'Refute-by-default review of PR 137',
                 'Fact-check ADR 0051 claims', 'Cross-check P/Invoke signatures']:
        assert publish('git push', [*REPORTED, *background('v', name)]) is None, name
    for name in ['Structure review of USERGUIDE', '#74 merge main and verify', 'Fix #60 review 2 findings']:
        assert publish('git push', [*REPORTED, *background('v', name)]), name


def test_a_report_after_the_last_verification_is_unverified_again():
    later = [*VERIFIED, *background('t3', 'Add the CLI flag')]
    reason = publish('gh pr ready', later)['hookSpecificOutput']['permissionDecisionReason']
    assert '"Add the CLI flag"' in reason and 'Fix the parser' not in reason


def test_other_commands_and_sessions_without_subagents_pass():
    assert publish('git status', REPORTED) is None
    assert publish('gh pr view 63', REPORTED) is None
    assert publish('git commit -m "push the fix"', REPORTED) is None
    assert publish('git push', [prompt('push it')]) is None


def test_a_launch_or_a_failure_is_not_a_report():
    assert publish('git push', [launch('t1', 'Fix the parser'), launched('t1')]) is None
    assert publish('git push', [launch('t1', 'Fix'), launched('t1'), notified('t1', 'failed')]) is None


def test_a_synchronous_result_is_a_report():
    assert publish('git push', [launch('t1', 'Fix the parser'), returned('t1')])


def test_a_workflow_counts_on_its_notification_only():
    started = [launch('w1', 'review-changes', name='Workflow'), returned('w1')]
    assert publish('git push', started) is None
    assert publish('git push', [*started, notified('w1')])


def test_stop_sends_back_a_report_of_this_turn_once():
    out = stop(REPORTED)
    assert out['decision'] == 'block' and '"Fix the parser"' in out['reason']
    assert stop(REPORTED, active=True) is None
    assert stop(VERIFIED) is None


def test_stop_leaves_reports_from_earlier_turns_to_the_publish_gate():
    assert stop([*REPORTED, prompt('ok, next')]) is None
    assert publish('git push', [*REPORTED, prompt('ok, next')])


def test_process_reads_the_transcript_and_fails_open(tmp_path):
    transcript = tmp_path / 's.jsonl'
    transcript.write_text('\n'.join(json.dumps(e) for e in REPORTED), encoding='utf-8')
    payload = {'transcript_path': str(transcript), 'tool_input': {'command': 'git push'}}
    run = subprocess.run([sys.executable, HOOK, 'publish'], input=json.dumps(payload),
                         capture_output=True, text=True, encoding='utf-8')
    assert run.returncode == 0
    assert json.loads(run.stdout)['hookSpecificOutput']['permissionDecision'] == 'deny'
    missing = {'transcript_path': str(tmp_path / 'none.jsonl'), 'tool_input': {'command': 'git push'}}
    quiet = subprocess.run([sys.executable, HOOK, 'publish'], input=json.dumps(missing), capture_output=True, text=True)
    assert quiet.returncode == 0 and quiet.stdout == ''


def bash(use_id, command):
    return {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': use_id, 'name': 'Bash',
         'input': {'command': command, 'description': 'Consult'}}]}}


def consulted(use_id, command, text='The implementation hits an N+1 query.'):
    return [bash(use_id, command),
            {'type': 'user', 'toolUseResult': {'status': 'completed', 'content': []},
             'message': {'role': 'user', 'content': [
                 {'type': 'tool_result', 'tool_use_id': use_id, 'content': text}]}}]


# Every shape below is a real consultation. The first four are the tidy forms a
# skill documents; the rest were found by an adversarial verifier that broke an
# earlier detector keyed on `codex exec` at the start of a segment — 21 misses,
# each one a reading that would have left the session unopposed.
CONSULT_COMMANDS = [
    'codex exec --sandbox read-only --cd . "review this"',
    'codex exec --sandbox read-only -C . "review" < /dev/null',
    'copilot -p "review this" --silent --allow-all-tools --available-tools view glob grep',
    'cd repo && codex exec --sandbox read-only "review"',
    # The shape consultations actually arrive in: a directory in a variable,
    # chained with `;`, then cd'd and wrapped in timeout before the binary.
    'T="/tmp/p"; cd "$T" && timeout 300 copilot -p "review" --silent'
    " --allow-all-tools --available-tools 'view' 'glob' 'grep' -C \"$T\" 2>&1 | tail -25",
    'T="/tmp/p"; cd "$T" && timeout 420 codex exec --sandbox read-only --cd "$T" "review" 2>&1 | tail -18',
    'T="/tmp/p"; rm -rf "$T"; mkdir -p "$T"; cd "$T" && git init -q .'
    ' && timeout 420 codex exec --sandbox read-only --cd "$T" "review" < /dev/null',
    # A substitution inside double quotes: the capture idiom, and the one a
    # quote-tracking splitter hides unless `$(` overrides the quote.
    'R="$(codex exec "q" < /dev/null)"',
    'echo "$(copilot -p q)"',
    # The binary reached by path, quoted, or through the PowerShell call operator.
    '"C:/Program Files/OpenAI/codex.exe" exec "q"',
    '& "C:\\Users\\me\\codex.exe" exec "q"',
    'npx @openai/codex exec "q"',
    # A wrapper in front of it. `timeout 5m` is why a `timeout \\d+` prefix list
    # is not enough, and a fixed list is why the match no longer uses one.
    'xargs codex exec < prompts.txt',
    'nice -n 19 codex exec "q"',
    'timeout 5m codex exec "q"',
    'timeout -k 10 300 codex exec "q"',
    'bash -c "codex exec q"',
    'pwsh -NoProfile -Command "codex exec q"',
    'Start-Process codex -ArgumentList "exec","q" -Wait',
    # Global options before the subcommand, the documented `exec` alias, and the
    # other non-interactive subcommand codex --help lists.
    'codex -m o3 exec "q"',
    'codex -c model=o3 exec "q"',
    'codex e "q"',
    'codex review --uncommitted',
    # A prompt on stdin with no flag at all, and combined short flags. Both were
    # confirmed to answer: `echo "..." | copilot -s` and `copilot -sp "q"`.
    'cat prompt.txt | copilot -s --allow-all-tools',
    'copilot -sp "q"',
    # gemini is unusable on this machine today, which is a fact about today.
    'gemini -p "q"',
    'mise exec npm:@google/gemini-cli -- gemini -p "q"',
    # The prompt is quoted and may say anything, including what looks like a
    # flag or a managing subcommand. Scanning the whole segment for `--help`
    # suppressed exactly these, which are consultations about those topics.
    'codex exec "explain what --help does"',
    'codex exec --sandbox read-only "why does login fail?"',
    'copilot -p "show me --version output" -s',
    'codex exec "review skills/codex/SKILL.md"',
    # Each of these a verifier confirmed by running the binary and getting an
    # answer back. The first two are why no flag requirement can be correct:
    # a bare `copilot` reads its prompt from a pipe.
    'echo "Reply with exactly PONG" | timeout 120 copilot',
    'echo "q" | timeout 120 copilot --silent',
    'copilot --yolo < p.txt',
    'Get-Content p.md | copilot',
    # `timeout -v`: the wrapper's own flag was read as a version request.
    'timeout -v 180 codex exec --sandbox read-only "q" < /dev/null',
    # `--help` passed after `--` is the prompt, not a usage request.
    'timeout 180 codex exec --sandbox read-only -- --help < /dev/null',
    # `codex review` has no subcommands, so `help` here is the prompt.
    'codex review help',
    # Shapes that follow from shell semantics rather than a run.
    'codex "exec" q',
    'codex --cd "C:/a b" exec q',
    'npx -y @openai/codex@latest exec q',
    "Start-Process codex -ArgumentList 'exec q' -Wait",
    "$a = @('exec','q'); codex @a",
    'c=codex; "$c" exec q',
    'ssh -v host codex exec q',
    # An interpreter that really does run it, not one printing its name.
    "python -c 'import subprocess; subprocess.run([codex, exec, q])'",
    # A heredoc whose opener line itself runs the consultation: only the body
    # is dropped, never the opener's own line.
    'cat <<EOF | codex exec -\nreview this\nEOF',
    # A terminator containing a dash, which a bare \w+ did not capture.
    'cat <<END-MARK\nx\nEND-MARK\ncodex exec q',
    # An arithmetic shift is not a heredoc opener; reading it as one swallowed
    # every line after it.
    'x=$((a<<b))\ncodex exec q',
    'echo "a\\"b"; codex exec q',
    # A pipeline whose earlier segment is a text tool still consults in its last.
    'git log | codex exec "summarise"',
    'cat p.txt | codex exec',
    # A loop that genuinely runs it, as against one that only lists the names.
    'for f in a.py b.py; do codex exec "review $f"; done',
    'env FOO=1 codex exec "q"',
    './codex exec "q"',
    'codex.exe exec "q"',
    'copilot --prompt "q" --silent',
]


def test_a_consultation_through_bash_is_a_report():
    """codex and copilot return a claim the same way a subagent does.

    The gate read only Agent, Task and Workflow, so a reading obtained through
    Bash left the session unopposed — the exact claim adversarial-verify exists
    to stop.
    """
    for command in CONSULT_COMMANDS:
        entries = [prompt('ask codex'), *consulted('b1', command)]
        out = publish('git push', entries)
        assert out is not None, command
        assert out['hookSpecificOutput']['permissionDecision'] == 'deny', command


def test_a_consultation_is_satisfied_by_a_verifier():
    entries = [prompt('ask codex'), *consulted('b1', CONSULT_COMMANDS[0]),
               *background('t2', 'Verify: the N+1 claim')]
    assert publish('git push', entries) is None


def test_a_call_that_names_no_consultee_is_not_a_report():
    for command in ['ls', 'git status', 'python tests/x.py', 'git push',
                    'pytest tests/', 'npm install', 'gh pr list']:
        entries = [prompt('check'), *consulted('b1', command)]
        assert publish('git push', entries) is None, command


def test_the_three_structural_exclusions_hold():
    """Only text that no shell would run is dropped from the match.

    Three narrower rule sets were each broken by a verifier, so the name alone
    now triggers and these are the only exceptions: a heredoc body, the text
    after an unquoted `#`, and a path segment following the name.
    """
    for command in [
            # A heredoc body is text being written. The terminator may be
            # indented by `<<-`, carry trailing spaces, or be backslash-escaped.
            "cat >> t.py <<'EOF'\nCMD = 'codex exec --sandbox read-only'\nEOF",
            'cat <<-EOF > f\n\tcodex exec "q"\n\tEOF',
            'cat > f <<\\EOF\ncodex exec q\nEOF',
            'cat <<END-MARK > f\ncodex exec q\nEND-MARK',
            # The text after an unquoted `#` runs nothing, separators included.
            'echo hi # ; codex exec "q"',
            'ls; # codex exec "q"',
            'ls;# codex exec "q"',
            'python tests/x.py # copilot -p is documented here',
            # A path in this repository, which documents these tools.
            'python tests/reflow-prose.py --check skills/codex/SKILL.md',
            'python -m pytest tests/consultation-path/']:
        entries = [prompt('check'), *consulted('b1', command)]
        assert publish('git push', entries) is None, command


def test_a_quoted_hash_is_not_a_comment():
    """`git commit -m "fix #12" && codex exec` consults, and did not.

    Treating a `#` inside a string as a comment swallowed the `&&` and the real
    call behind it — a verifier's finding, and the reason the cut tracks quotes.
    """
    for command in ['git commit -m "fix #12" && codex exec "review"',
                    'echo "a #b"; codex exec q',
                    "echo 'see #3'; codex exec q"]:
        entries = [prompt('ask'), *consulted('b1', command)]
        assert publish('git push', entries) is not None, command


def test_a_mention_is_flagged_and_that_is_the_cheaper_error():
    """The looseness is the design, so it is asserted rather than tolerated.

    Each of these asks no model, and each costs one verification that finds
    nothing. Three attempts to exclude them cost real misses instead: 21, then
    56 false positives with two rules a prompt could switch off, then about
    forty — among them a bare `copilot` reading its prompt from a pipe.
    """
    for command in ['codex --version', 'codex login', 'echo codex exec',
                    'grep -rn "codex exec" skills/', 'pkill codex',
                    'npm i -g @openai/codex', 'find . -name codex',
                    'command -v codex', 'Get-Process copilot']:
        entries = [prompt('check'), *consulted('b1', command)]
        assert publish('git push', entries) is not None, command


def test_a_failed_consultation_is_not_a_report():
    """A run that errored produced no reading, so there is nothing to verify."""
    entries = [prompt('ask codex'), bash('b1', CONSULT_COMMANDS[0]),
               {'type': 'user', 'toolUseResult': {'status': 'failed'},
                'message': {'role': 'user', 'content': [
                    {'type': 'tool_result', 'tool_use_id': 'b1', 'is_error': True,
                     'content': "error: unexpected argument '--full-auto' found"}]}}]
    assert publish('git push', entries) is None


def test_stop_sends_back_a_consultation_of_this_turn():
    entries = [prompt('ask codex'), *consulted('b1', CONSULT_COMMANDS[0])]
    out = stop(entries)
    assert out['decision'] == 'block'
    assert stop(entries, active=True) is None

def test_a_consultation_through_powershell_is_a_report():
    """PowerShell is this machine's primary shell and the push gate matches it.

    Reading only Bash left one unwatched route to the same claim.
    """
    entries = [prompt('ask codex'),
               *consulted('b1', 'codex exec --sandbox read-only --cd . "review"')]
    entries[1]['message']['content'][0]['name'] = 'PowerShell'
    assert publish('git push', entries) is not None


def test_a_consultation_inside_a_substitution_is_a_report():
    for command in ['OUT=$(codex exec --sandbox read-only --cd . "review")',
                    'REVIEW=`codex exec --sandbox read-only --cd . "review"`']:
        entries = [prompt('ask'), *consulted('b1', command)]
        assert publish('git push', entries) is not None, command


def test_a_publish_through_an_interpreter_is_still_refused():
    """A narrowing of this check was reverted, and these are why.

    Judging a publish as what a segment runs fixed the mention cases and broke
    these seven, because the command to run sits inside the quoted argument the
    narrowing blanked. A missed publish lets an unverified report out, which is
    the one thing this file prevents, so the over-matching stays.
    """
    for command in ['eval "git push"', "eval 'git push'", "bash -c 'git push'",
                    'sh -c "git push origin main"', "pwsh -c 'git push'",
                    'cmd /c "git push"', "Invoke-Expression 'git push'",
                    'iex "git push"']:
        assert publish(command, REPORTED) is not None, command


def test_a_real_publish_is_refused():
    for command in ['git push', 'git -C repo push origin main', 'git push && echo done',
                    'cd x && git push -u origin b', 'gh pr create --draft --title t',
                    'gh pr ready 63', 'gh issue create -t t', 'xargs git push']:
        assert publish(command, REPORTED) is not None, command


def test_a_publish_only_named_is_refused_too_and_that_is_accepted():
    """The cost of the line above: writing about a push is refused as one.

    A verifier hit this on a command whose only `gh pr create` sat in a heredoc
    string. The refusal names the reason and costs one rewritten command, which
    is the cheaper side of a choice that has no clean option.
    """
    for command in ["cat > note.md <<'EOF'\nrun gh pr create when ready\nEOF",
                    'echo "gh pr create"', 'grep -rn "git push" hooks/']:
        assert publish(command, REPORTED) is not None, command


def test_a_tool_that_is_not_a_shell_is_never_a_report():
    entries = [prompt('read it'), *consulted('b1', 'codex exec --sandbox read-only "x"')]
    entries[1]['message']['content'][0]['name'] = 'Read'
    assert publish('git push', entries) is None

def test_a_quoted_or_commented_heredoc_opener_opens_nothing():
    """Dropping lines is the one step here that can hide a call.

    A `<<` inside quotes or after a `#` is text, not an opener. Treating it as
    one dropped every line that followed, which a security review found as a
    one-line way past the gate.
    """
    # Each ends with a line equal to the fake delimiter, so the terminator
    # matches and the unterminated-heredoc restore below cannot mask the bug.
    for command in ['# <<EOF\ncodex exec q\nEOF',
                    'echo "a <<EOF b"\ncodex exec q\nEOF',
                    'echo "<<END" > f\ncodex exec q\nEND']:
        entries = [prompt('ask'), *consulted('b1', command)]
        assert publish('git push', entries) is not None, command


def test_an_unterminated_heredoc_restores_what_it_held():
    """No terminator means the opener was misread, so the lines come back.

    Discarding them let `cat <<EOF > f` with no closing `EOF` swallow every
    command behind it.
    """
    for command in ['cat <<EOF > f\nsome text\ncodex exec q',
                    'cat <<MISSING\nx\ncodex exec q']:
        entries = [prompt('ask'), *consulted('b1', command)]
        assert publish('git push', entries) is not None, command


def test_a_quoted_heredoc_delimiter_still_opens_one():
    """The delimiter's own quoting is syntax, not a quoted string."""
    for command in ["cat >> t.py <<'EOF'\nCMD = 'codex exec'\nEOF",
                    'cat > f <<\\EOF\ncodex exec q\nEOF',
                    'cat << "END-MARK" > f\ncodex exec q\nEND-MARK']:
        entries = [prompt('check'), *consulted('b1', command)]
        assert publish('git push', entries) is None, command


def test_an_escaped_quote_does_not_desynchronise_the_walk():
    """A backslash escapes the next character outside single quotes.

    Without that, one escaped quote made the rest of the command read as
    quoted, and the call inside it was lost.
    """
    # The escaped quote keeps the `#` inside the string, so it opens no comment
    # and the call behind it is real. Drop the escape handling and the walk
    # reads the `#` as unquoted, discards the rest, and loses the call.
    command = 'echo "x\\" # ; codex exec q"'
    entries = [prompt('ask'), *consulted('b1', command)]
    assert publish('git push', entries) is not None, command

def test_an_ambiguous_escape_beside_a_hash_keeps_the_text():
    """Bash escape rules were being applied to PowerShell commands.

    A backslash is literal in PowerShell, a backtick escapes, and `''` inside a
    single-quoted string is one escaped quote. Which grammar applies decides
    whether a given `#` opens a comment, so where an escape character and a `#`
    meet, the comment is not cut and the call behind it survives.
    """
    for command in ['Write-Output "a`" # ; codex exec q"',
                    "Write-Output 'it''s' # ; codex exec q",
                    'Write-Output "C:\\" # ; codex exec q']:
        entries = [prompt('ask'), *consulted('b1', command)]
        entries[1]['message']['content'][0]['name'] = 'PowerShell'
        assert publish('git push', entries) is not None, command


def test_an_unambiguous_hash_is_still_a_comment():
    """The guard above is narrow: with no escape character present, the cut stands."""
    for command in ['echo hi # ; codex exec "q"', 'ls; # codex exec "q"',
                    'ls;# codex exec q', 'python x.py # copilot -p is documented']:
        entries = [prompt('check'), *consulted('b1', command)]
        assert publish('git push', entries) is None, command

def test_a_powershell_block_comment_does_not_hide_what_follows_it():
    """`<# ... #>` ends, and the code after it runs.

    Confirmed in pwsh: `Write-Output x <# a #> ; Write-Output RAN` prints RAN.
    The `#` inside the delimiters was being read as starting a line comment,
    which took the rest of the command and the consultation with it.
    """
    for command in ['<# note #> codex exec q',
                    'Write-Output x <# a #> ; codex exec q',
                    'Write-Output "x" <# ; nothing #> ; codex exec q']:
        entries = [prompt('ask'), *consulted('b1', command)]
        entries[1]['message']['content'][0]['name'] = 'PowerShell'
        assert publish('git push', entries) is not None, command
