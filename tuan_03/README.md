# Tuần 03 - Pipeline mô hình và validation

## Công việc

- Đóng gói imputer, scaler, one-hot encoder và classifier trong Pipeline.
- So sánh Logistic Regression theo `C` và `class_weight`.
- So sánh thêm cây quyết định nông.
- Chọn mô hình bằng PR-AUC trên validation và báo riêng Average Precision.
- Đo độ biến thiên của mô hình đã chọn bằng Stratified 5-fold cross-validation chỉ trên train.
- Chọn ngưỡng bằng validation, chưa đọc test.

## Minh chứng đầu ra

- `models/bank_marketing_pipeline.joblib`
- `models/model_metadata.json`
- `reports/results/validation_candidates.csv`
- `reports/results/validation_thresholds.csv`
- `reports/results/validation_cross_validation.csv`
- `reports/results/validation_cross_validation_summary.json`

## Chạy tuần 03

```powershell
.\tuan_03\run_week.ps1
```
