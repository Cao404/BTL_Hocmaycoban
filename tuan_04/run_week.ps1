$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Chưa có .venv.' }
Set-Location -LiteralPath $Root
if (Test-Path -LiteralPath 'reports\results\final_test.lock') {
    Write-Host 'Test đã được mở trước đó; chỉ hiển thị kết quả đã đóng băng.'
    Get-Content -Raw 'reports\results\final_test_metrics.json'
    Import-Csv 'reports\results\test_model_comparison.csv' | Select-Object candidate,contact_rate,precision,recall,f1,pr_auc | Format-Table -AutoSize
} else {
    & $Python -m src.evaluate
}
