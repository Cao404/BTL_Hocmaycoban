$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Chưa có .venv.' }
Set-Location -LiteralPath $Root
if (Test-Path -LiteralPath 'reports\results\final_test.lock') {
    Write-Host 'Project đã qua tuần 04; không tạo lại split. Chỉ tái tạo EDA/baseline từ train và validation hiện có.'
    & $Python -m src.eda
    & $Python -m src.baseline
} else {
    & $Python -m src.data --download
    & $Python -m src.eda
    & $Python -m src.baseline
}
