$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Chưa có .venv.' }
Set-Location -LiteralPath $Root
& $Python -c "from src.features import FEATURES, LEAKAGE_FEATURES; assert len(FEATURES)==15; assert LEAKAGE_FEATURES==['duration']; print('Tuần 01 ĐẠT: 15 features, duration đã loại.')"
Get-Item README.md,data\README.md,docs\data_dictionary.md,config\config.json | Select-Object Name,Length
