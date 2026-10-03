$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    throw 'Chưa có .venv. Hãy tạo môi trường và cài requirements.txt trước.'
}

$Python = Resolve-Path -LiteralPath '.venv\Scripts\python.exe'
$env:PYTHONIOENCODING = 'utf-8'
if (Test-Path -LiteralPath 'reports\results\final_test.lock') {
    Write-Host 'Test đã được mở; giữ nguyên model/ngưỡng và không chạy lại data, train hoặc evaluate.'
} else {
    & $Python -m src.data --download
    & $Python -m src.train
    & $Python -m src.evaluate
}
& $Python -m pytest -q
& $Python -m src.release_check

Write-Host 'Pipeline hoàn tất. Chạy web bằng: .venv\Scripts\python.exe -m app.app'
