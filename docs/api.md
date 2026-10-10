# Tài liệu API

## POST /api/score

Chấm điểm một lần liên hệ trước cuộc gọi. Header `Content-Type: application/json`.

### Request hợp lệ

```json
{
  "age": 35,
  "job": "technician",
  "marital": "married",
  "education": "secondary",
  "default": "no",
  "balance": 1200,
  "housing": "yes",
  "loan": "no",
  "contact": "cellular",
  "day": 15,
  "month": "may",
  "campaign": 1,
  "pdays": -1,
  "previous": 0,
  "poutcome": "unknown"
}
```

### Response 200

```json
{
  "model": "logistic_C=10.0_weight=none",
  "priority_label": "ưu tiên liên hệ",
  "probability": 0.327451,
  "threshold": 0.1,
  "warning": "Đây là hỗ trợ xếp hạng, không phải mệnh lệnh hoặc căn cứ loại trừ dịch vụ."
}
```

### Lỗi

- `422`: thiếu/thừa trường, sai kiểu, sai category, ngoài miền quan sát hoặc gửi `duration`.
- `503`: chưa có model đã huấn luyện.

Tên model và ngưỡng trong response được đọc trực tiếp từ artifact đã đóng băng. Xác suất trong ví dụ có tính minh họa; kết quả thực tế phụ thuộc dữ liệu request và phiên bản artifact.

## GET /api/health

Trả trạng thái ứng dụng và cờ `model_ready`.
