# SPDX-License-Identifier: MIT
param(
    [string]$OutputDirectory = 'downloads',
    [switch]$Offline
)
$ErrorActionPreference = 'Stop'
$scriptFile = Join-Path $PSScriptRoot 'download.py'
$arguments = @($scriptFile, '--output', $OutputDirectory)
if ($Offline) { $arguments += '--offline' }
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @arguments
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 @arguments
} else {
    throw 'Install Python 3.10 or newer, then rerun this helper.'
}
exit $LASTEXITCODE
