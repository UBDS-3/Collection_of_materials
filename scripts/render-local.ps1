<#
.SYNOPSIS
Build the Quarto site locally on Windows.

.DESCRIPTION
Uses the project's virtual environment, keeps temporary caches inside the
repository, validates publishable datasets, generates live pages/navigation,
and passes any remaining arguments to `quarto render`.
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$QuartoArgs
)

$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Python = Join-Path $ProjectDir '.venv\Scripts\python.exe'
$OriginalLocalAppData = $env:LOCALAPPDATA

if (-not (Test-Path -LiteralPath $Python)) {
    throw @"
Missing .venv. Create it and install requirements first:
  uv venv .venv
  uv pip install --python .venv\Scripts\python.exe -r requirements.txt
"@
}

if (-not (Get-Command quarto -ErrorAction SilentlyContinue)) {
    throw 'Quarto is not on PATH. Install it from https://quarto.org/docs/get-started/.'
}

$QuartoVersionText = (& quarto --version | Select-Object -First 1).Trim()
if ($LASTEXITCODE -ne 0 -or $QuartoVersionText -notmatch '(\d+\.\d+(?:\.\d+)?)') {
    throw "Could not determine the installed Quarto version (received: '$QuartoVersionText')."
}
$QuartoVersion = [Version]$Matches[1]
if ($QuartoVersion -lt [Version]'1.4.0') {
    throw "Quarto Live requires Quarto 1.4.0 or newer; found $QuartoVersionText. Update Quarto from https://quarto.org/docs/get-started/."
}

Set-Location $ProjectDir

# Keep user-installed R packages visible even though Quarto's cache is moved
# into the repository below. R on Windows stores packages under LOCALAPPDATA.
if ($OriginalLocalAppData) {
    $RUserLibraryRoot = Join-Path $OriginalLocalAppData 'R\win-library'
    if (Test-Path -LiteralPath $RUserLibraryRoot) {
        $RUserLibraries = Get-ChildItem -LiteralPath $RUserLibraryRoot -Directory |
            Select-Object -ExpandProperty FullName
        if ($RUserLibraries) {
            $env:R_LIBS_USER = $RUserLibraries -join [IO.Path]::PathSeparator
        }
    }
}

@(
    '.cache\ipython',
    '.cache\jupyter',
    '.cache\matplotlib',
    '.cache\quarto',
    '.local\share\quarto\logs',
    '.local\appdata',
    '.tmp\jupyter-runtime',
    '.tmp\runtime'
) | ForEach-Object {
    New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir $_) | Out-Null
}

$env:XDG_CACHE_HOME = Join-Path $ProjectDir '.cache'
$env:XDG_DATA_HOME = Join-Path $ProjectDir '.local\share'
$env:LOCALAPPDATA = Join-Path $ProjectDir '.local\appdata'
$env:XDG_RUNTIME_DIR = Join-Path $ProjectDir '.tmp\runtime'
$env:IPYTHONDIR = Join-Path $ProjectDir '.cache\ipython'
$env:JUPYTER_CONFIG_DIR = Join-Path $ProjectDir '.cache\jupyter'
$env:JUPYTER_RUNTIME_DIR = Join-Path $ProjectDir '.tmp\jupyter-runtime'
$env:MPLCONFIGDIR = Join-Path $ProjectDir '.cache\matplotlib'
$env:QUARTO_CACHE_DIR = Join-Path $ProjectDir '.cache\quarto'
$env:QUARTO_PYTHON = $Python

function Invoke-Checked([string]$Program, [string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Program $($Arguments -join ' ')"
    }
}

Invoke-Checked $Python @('scripts/validate-datasets.py')
Invoke-Checked $Python @('scripts/generate-live-pages.py')
Invoke-Checked $Python @('scripts/generate-navigation.py')
Invoke-Checked 'quarto' (@('render') + $QuartoArgs)
