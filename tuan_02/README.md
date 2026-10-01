# Tuần 02 - Dữ liệu, EDA và baseline

## Công việc

- Tải dữ liệu bằng script và ghi checksum/manifest.
- Kiểm tra schema, missing, trùng lặp, `unknown` và phân bố target.
- Chia train/validation/test trước EDA và preprocessing.
- Chỉ thực hiện EDA trên train.
- Tạo baseline tất cả âm tính và baseline ngẫu nhiên theo prevalence train.

## Minh chứng đầu ra

- `data/processed/data_manifest.json`
- `data/processed/train.csv`, `validation.csv`, `test.csv` (không commit)
- `reports/figures/train_*.png`
- `reports/results/week2_validation_baselines.csv`

## Chạy tuần 02

```powershell
.\tuan_02\run_week.ps1
```
