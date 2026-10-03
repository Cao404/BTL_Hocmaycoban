$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Chưa có .venv.' }
Set-Location -LiteralPath $Root
if (Test-Path -LiteralPath 'reports\results\final_test.lock') {
    Write-Host 'Test đã được mở ở tuần 04; không huấn luyện/chọn lại mô hình.'
    Import-Csv 'reports\results\validation_candidates.csv' | Select-Object candidate,pr_auc,average_precision,precision,recall,f1 | Format-Table -AutoSize
    Get-Content -Raw 'reports\results\validation_cross_validation_summary.json'
    Get-Content -Raw 'models\model_metadata.json'
} else {
    & $Python -m src.train
}
