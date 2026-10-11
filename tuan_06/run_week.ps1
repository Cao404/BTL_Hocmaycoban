$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Chưa có .venv.' }
Set-Location -LiteralPath $Root
& $Python -m pytest -q
& $Python -m src.release_check
Write-Host 'Tuần 06 hoàn tất. Các thay đổi chỉ ở Git local, chưa push.'
