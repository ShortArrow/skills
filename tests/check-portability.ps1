param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$skillsRoot = Join-Path $RepositoryRoot 'skills'

foreach ($directory in Get-ChildItem -LiteralPath $skillsRoot -Directory) {
    $skillFile = Join-Path $directory.FullName 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillFile)) {
        $failures.Add("$($directory.Name): missing SKILL.md")
        continue
    }

    $content = Get-Content -Raw -LiteralPath $skillFile
    if ($content -notmatch '(?s)^---\r?\n(?<frontmatter>.*?)\r?\n---') {
        $failures.Add("$($directory.Name): invalid frontmatter fence")
        continue
    }

    $frontmatter = $Matches.frontmatter
    if ($frontmatter -notmatch '(?m)^name:\s*(?<name>[^\r\n]+)') {
        $failures.Add("$($directory.Name): missing name")
    } elseif ($Matches.name.Trim() -ne $directory.Name) {
        $failures.Add("$($directory.Name): frontmatter name does not match directory")
    }
    if ($frontmatter -notmatch '(?m)^description:\s*(\||[^\r\n]+)') {
        $failures.Add("$($directory.Name): missing description")
    }

    $resourceMatches = [regex]::Matches(
        $content,
        '(?:`|\()(?<path>(?:scripts|references|assets)/[^`)\s]+)'
    )
    foreach ($match in $resourceMatches) {
        $relative = $match.Groups['path'].Value.TrimEnd('.', ',', ':', ';')
        $target = Join-Path $directory.FullName ($relative -replace '/', '\')
        if (-not (Test-Path -LiteralPath $target)) {
            $failures.Add("$($directory.Name): missing referenced resource $relative")
        }
    }
}

$hostBranchSkills = @(
    'any-screenshot',
    'codex',
    'grill-me',
    'pdf-transcribe',
    'peer-sessions',
    'plan-delegate-verify',
    'request-approval',
    'tool-call-syntax'
)

foreach ($name in $hostBranchSkills) {
    $content = Get-Content -Raw -LiteralPath (Join-Path $skillsRoot "$name\SKILL.md")
    foreach ($hostName in @('Claude', 'Codex', 'Copilot', 'Cursor', 'Gemini CLI', 'Any other host')) {
        if ($content -notmatch [regex]::Escape($hostName)) {
            $failures.Add("${name}: missing $hostName host route")
        }
    }
}

$claudeInvariants = @(
    @{ Skill = 'request-approval'; Text = 'AskUserQuestion' }
    @{ Skill = 'plan-delegate-verify'; Text = 'Agent(prompt: "...", model: "opus")' }
    @{ Skill = 'tool-call-syntax'; Text = 'antml:function_calls' }
    @{ Skill = 'peer-sessions'; Text = 'scripts/peer-sessions.sh' }
    @{ Skill = 'pdf-transcribe'; Text = 'Read(file_path="spec.pdf", pages="1-5")' }
    @{ Skill = 'any-screenshot'; Text = 'Claude in Chrome' }
    @{ Skill = 'codex'; Text = 'codex exec --full-auto --sandbox read-only' }
    @{ Skill = 'grill-me'; Text = 'Prefer choices over open-ended questions' }
    @{ Skill = 'plan-delegate-verify'; Text = 'only the user explicitly invoking' }
    @{ Skill = 'plan-delegate-verify'; Text = 'automatic activation from the' }
)

foreach ($entry in $claudeInvariants) {
    $content = Get-Content -Raw -LiteralPath (Join-Path $skillsRoot "$($entry.Skill)\SKILL.md")
    if ($content -notmatch [regex]::Escape($entry.Text)) {
        $failures.Add("$($entry.Skill): lost Claude Code invariant $($entry.Text)")
    }
}

$codexInvariants = @(
    @{ Skill = 'request-approval'; Text = 'Use the approval request attached to the blocked or escalated tool call' }
    @{ Skill = 'plan-delegate-verify'; Text = 'do not pretend a subagent ran' }
    @{ Skill = 'tool-call-syntax'; Text = 'Never print `antml` tags, XML wrappers, or a guessed JSON envelope' }
    @{ Skill = 'peer-sessions'; Text = 'Do not fall back to the Claude script' }
    @{ Skill = 'pdf-transcribe'; Text = 'Do not emit it as a Codex tool call' }
    @{ Skill = 'grill-me'; Text = 'a dedicated user-input tool when' }
)

foreach ($entry in $codexInvariants) {
    $content = Get-Content -Raw -LiteralPath (Join-Path $skillsRoot "$($entry.Skill)\SKILL.md")
    if ($content -notmatch [regex]::Escape($entry.Text)) {
        $failures.Add("$($entry.Skill): lost Codex invariant $($entry.Text)")
    }
}

$hostInvariants = @(
    @{ Skill = 'request-approval'; Text = 'askQuestions' }
    @{ Skill = 'request-approval'; Text = 'ask_user' }
    @{ Skill = 'request-approval'; Text = '"Ask questions"' }
    @{ Skill = 'grill-me'; Text = 'askQuestions' }
    @{ Skill = 'grill-me'; Text = 'ask_user' }
    @{ Skill = 'plan-delegate-verify'; Text = 'runSubagent' }
    @{ Skill = 'plan-delegate-verify'; Text = '@name' }
    @{ Skill = 'peer-sessions'; Text = 'not documented (checked 2026-08-28)' }
    @{ Skill = 'pdf-transcribe'; Text = 'read_file' }
    @{ Skill = 'any-screenshot'; Text = 'browser_agent' }
    @{ Skill = 'any-screenshot'; Text = 'screenshotPage' }
    @{ Skill = 'find-skills'; Text = '~/.agents/skills/' }
)

foreach ($entry in $hostInvariants) {
    $content = Get-Content -Raw -LiteralPath (Join-Path $skillsRoot "$($entry.Skill)\SKILL.md")
    if ($content -notmatch [regex]::Escape($entry.Text)) {
        $failures.Add("$($entry.Skill): missing host row $($entry.Text)")
    }
}

# A skill that names a public standard rests on it, so it carries a
# Sources block saying which version was read and when. The pattern is
# case-sensitive and word-bounded on purpose: "Administrators" contains
# "nist", and a match there would demand a citation for nothing.
$standardPattern = 'ISTQB|ISO/IEC|\bIEC 6\d{4}|\bRFC \d{4}|BCP 47|Semantic Versioning|\bSemVer\b|\bSLSA\b|OpenSSF|\bScorecard\b|GSN Community|Diátaxis|文化庁|\bJTF\b|消費者庁|厚生労働省|DO-178|arXiv|docs\.github\.com|github-linguist|developers\.google\.com/style|Microsoft Writing Style Guide|plainlanguage\.gov|digital\.gov'
foreach ($directory in Get-ChildItem -LiteralPath $skillsRoot -Directory) {
    $content = Get-Content -Raw -LiteralPath (Join-Path $directory.FullName 'SKILL.md')
    if ($content -notmatch $standardPattern) { continue }
    if ($content -notmatch '(?m)^## Sources\s*$') {
        $failures.Add("$($directory.Name): names a standard but has no '## Sources' block")
    } elseif ($content -notmatch '(?sm)^## Sources\s*$.*?20\d\d-\d\d-\d\d') {
        $failures.Add("$($directory.Name): '## Sources' block carries no check date (YYYY-MM-DD)")
    }
}

$claudeRunner = Get-Content -Raw -LiteralPath (Join-Path $RepositoryRoot 'tests\run-firing-tests.sh')
if ($claudeRunner -notmatch 'claude -p') {
    $failures.Add('Claude firing-test runner no longer invokes claude -p')
}

$marketplace = Get-Content -Raw -LiteralPath (Join-Path $RepositoryRoot '.claude-plugin\marketplace.json')
foreach ($directory in Get-ChildItem -LiteralPath $skillsRoot -Directory) {
    if ($marketplace -notmatch [regex]::Escape("./skills/$($directory.Name)")) {
        $failures.Add("$($directory.Name): missing from Claude marketplace groups")
    }
}

$readme = Get-Content -Raw -LiteralPath (Join-Path $RepositoryRoot 'README.md')
foreach ($heading in @('Install in Claude Code', 'Install in Codex', 'Install anywhere')) {
    if ($readme -notmatch [regex]::Escape($heading)) {
        $failures.Add("README: missing $heading")
    }
}

if ($readme -notmatch [regex]::Escape('npx skills add ShortArrow/skills -g')) {
    $failures.Add('README: missing the agent-neutral user-level install command')
}

if ($readme -match 'skills/<name>/agents/openai\.yaml') {
    $failures.Add('README layout lists optional openai.yaml files that do not exist')
}
if ($readme -notmatch 'official OpenAI documentation' -or $readme -notmatch 'on \d{4}-\d{2}-\d{2}\.') {
    $failures.Add('README: Codex discovery claim lacks its source or check date')
}

$toolSyntax = Get-Content -Raw -LiteralPath (Join-Path $skillsRoot 'tool-call-syntax\SKILL.md')
if ($toolSyntax -notmatch '## Claude Code\r?\n\r?\n### Write this') {
    $failures.Add('tool-call-syntax: Claude Code details are not nested under the host heading')
}

if ($failures.Count -gt 0) {
    # Every failure, not the first: Write-Error under ErrorActionPreference
    # Stop would end the run at the first line.
    $failures | ForEach-Object { [Console]::Error.WriteLine($_) }
    exit 1
}

Write-Output "Portable skill checks passed for $((Get-ChildItem -LiteralPath $skillsRoot -Directory).Count) skills."
