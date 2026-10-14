<#
.SYNOPSIS
  Removes only the components that tenet installed (per its manifest).
.DESCRIPTION
  Foreign rules, settings, MCP servers and Engram data are preserved. The private profile is kept
  unless -Purge is given. Every removal is backed up and can be undone with install.ps1 -Restore <id>.
.EXAMPLE
  .\installers\uninstall.ps1 -DryRun
#>
[CmdletBinding()]
param(
  [switch]$DryRun,
  [switch]$Purge,
  [string]$ConfigDir
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

$python = Find-Python
$cli = Join-Path (Split-Path $PSScriptRoot -Parent) 'scripts\agentcfg.py'
$arguments = @($cli, 'uninstall')
if ($DryRun) { $arguments += '--dry-run' }
if ($Purge) { $arguments += '--purge' }
if ($ConfigDir) { $arguments += @('--config-dir', $ConfigDir) }

Invoke-Python -Python $python -Arguments $arguments
