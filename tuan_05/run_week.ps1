$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Chưa có .venv.' }
Set-Location -LiteralPath $Root
& $Python -m pytest tests\test_api.py -q
& $Python -c "from app.app import create_app; c=create_app({'TESTING':True}).test_client(); assert all(c.get(p).status_code==200 for p in ['/','/score','/dashboard','/model-card','/api/health']); print('Web smoke test: ĐẠT')"
Write-Host 'Chạy demo: .\.venv\Scripts\python.exe -m app.app'
