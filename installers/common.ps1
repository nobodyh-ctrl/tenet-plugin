# Shared helpers for the PowerShell entry points (Windows PowerShell 5.1+ and PowerShell 7).

function Find-Python {
  # The Microsoft Store alias "python.exe" exists even when Python is not installed; probing with
  # a version check (instead of Get-Command alone) rejects it.
  $candidates = @(@('py', '-3'), @('python'), @('python3'))
  foreach ($candidate in $candidates) {
    $exe = $candidate[0]
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    $prefix = @()
    if ($candidate.Count -gt 1) { $prefix = $candidate[1..($candidate.Count - 1)] }
    try {
      & $exe @prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>$null | Out-Null
      if ($LASTEXITCODE -eq 0) { return @{ Exe = $exe; Prefix = $prefix } }
    } catch { continue }
  }
  Write-Host 'error: Python 3.9+ not found. Install it from https://www.python.org/downloads/ or with "winget install Python.Python.3.12", then re-run.' -ForegroundColor Red
  exit 1
}

function Invoke-Python {
  param([hashtable]$Python, [string[]]$Arguments)
  $all = @($Python.Prefix) + $Arguments
  & $Python.Exe @all
  exit $LASTEXITCODE
}
