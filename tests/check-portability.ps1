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

$dualHostSkills = @(
    'any-screenshot',
    'codex',
    'grill-me',
    'pdf-transcribe',
    'peer-sessions',
    'plan-delegate-verify',
    'request-approval',
    'tool-call-syntax'
)

foreach ($name in $dualHostSkills) {
    $content = Get-Content -Raw -LiteralPath (Join-Path $skillsRoot "$name\SKILL.md")
    foreach ($hostName in @('Claude', 'Codex')) {
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
foreach ($heading in @('Install in Claude Code', 'Install in Codex')) {
    if ($readme -notmatch [regex]::Escape($heading)) {
        $failures.Add("README: missing $heading")
    }
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
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "Portable skill checks passed for $((Get-ChildItem -LiteralPath $skillsRoot -Directory).Count) skills."
