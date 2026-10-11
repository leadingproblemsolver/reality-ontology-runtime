<#
.SYNOPSIS
Bootstrap this repository as a local Claude Code operating workspace on Windows.
.DESCRIPTION
Installs existing Python package, initializes ONLY local SQLite state,
runs core tests/invariants, then launches Claude Code. It does not sync
external apps, approve outbound writes, seed fabricated missions or deploy jobs.
#>
[CmdletBinding()]
param(
    [switch]$NoLaunch,
    [switch]$SkipInstall,
    [switch]$VerifyTypeScript
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

function Assert-Exit([string]$step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$step failed with exit code $LASTEXITCODE. Local cutover is BLOCKED."
    }
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv .venv
    } else {
        throw "Python 3.11+ missing. Install Python and rerun."
    }
    Assert-Exit "venv creation"
}

$env:PATH = (Join-Path $root ".venv\Scripts") + ";" + $env:PATH
& $venvPython -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ is required'"
Assert-Exit "Python version"

if (-not $SkipInstall) {
    & $venvPython -m pip install -e ".[dev]"
    Assert-Exit "Python package install"
}

$db = if ($env:RO_DB) { $env:RO_DB } else { ".runtime/reality.db" }
if ($db -eq ".runtime/reality.db") {
    New-Item -ItemType Directory -Force -Path (Join-Path $root ".runtime") | Out-Null
}
& $venvPython -m reality_ontology.cli --db $db init
Assert-Exit "canonical SQLite init"
& $venvPython -m reality_ontology.cli --db $db verify-invariants
Assert-Exit "invariant report"
& $venvPython -m pytest
Assert-Exit "Python test suite"
& $venvPython scripts/claude_session_context.py
Assert-Exit "read-only SessionStart snapshot"

if ($VerifyTypeScript) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm missing; TypeScript verification BLOCKED."
    }
    Push-Location (Join-Path $root "logistinfra-runtime")
    try {
        & npm ci
        Assert-Exit "npm ci"
        & npm run build
        Assert-Exit "TypeScript build"
        & npm test
        Assert-Exit "TypeScript tests"
    } finally {
        Pop-Location
    }
}

Write-Host "LOCAL_CLAUDE_ENTRYPOINT_READY; live external pipeline bindings remain UNVERIFIED."
if ($NoLaunch) { exit 0 }
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    throw "Claude Code CLI missing. Install Claude Code, then rerun this script."
}
& claude
Assert-Exit "Claude Code"
