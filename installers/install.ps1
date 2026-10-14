<#
.SYNOPSIS
  Installs the forge complementary configuration on Windows.
.DESCRIPTION
  Detects the environment, locates Python 3.9+ and delegates to scripts/agentcfg.py.
  Never installs third-party tools. Run with -DryRun first to preview every change.
.EXAMPLE
  .\installers\install.ps1 -DryRun -WithPlugin -WithEngram
#>
[CmdletBinding()]
param(
  [switch]$DryRun,
  [switch]$WithPermissions,
  [switch]$WithPlugin,
  [switch]$WithEngram,
  [string]$ConfigDir,
  [string]$Restore
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

Write-Host ("forge installer - {0} / PowerShell {1}" -f [Environment]::OSVersion.VersionString, $PSVersionTable.PSVersion)
$python = Find-Python
$cli = Join-Path (Split-Path $PSScriptRoot -Parent) 'scripts\agentcfg.py'

if ($Restore) {
  $arguments = @($cli, 'restore', $Restore)
} else {
  $arguments = @($cli, 'install')
  if ($WithPermissions) { $arguments += '--with-permissions' }
  if ($WithPlugin) { $arguments += '--with-plugin' }
  if ($WithEngram) { $arguments += '--with-engram' }
}
if ($DryRun) { $arguments += '--dry-run' }
if ($ConfigDir) { $arguments += @('--config-dir', $ConfigDir) }

Invoke-Python -Python $python -Arguments $arguments
