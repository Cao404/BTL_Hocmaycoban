# Tuần 04 - Test cuối và phân tích lỗi

## Công việc

- Giữ nguyên mô hình và ngưỡng đã chọn ở tuần 03.
- Mở test đúng một lần để kết luận.
- Báo accuracy, PR-AUC, precision, recall, F1 và confusion matrix.
- So sánh ít nhất ba ngưỡng.
- Phân tích lỗi theo nhóm tuổi và nghề nghiệp.
- So sánh random baseline tại đúng cùng tỷ lệ liên hệ của mô hình.

## Minh chứng đầu ra

- `reports/results/final_test_metrics.json`
- `reports/results/test_model_comparison.csv`
- `reports/results/test_thresholds.csv`
- `reports/results/test_error_analysis.csv`
- `reports/figures/test_precision_recall.png`
- `reports/figures/test_confusion_matrix.png`

`run_week.ps1` không đánh giá lại nếu đã tồn tại file khóa test.

## Chạy tuần 04

```powershell
.\tuan_04\run_week.ps1
```
