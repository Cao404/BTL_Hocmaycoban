# Project 07 - Dự đoán khách hàng đăng ký tiền gửi có kỳ hạn

Project xây dựng mô hình hỗ trợ ưu tiên cuộc gọi trước khi liên hệ khách hàng. Hệ thống dự đoán xác suất đăng ký tiền gửi có kỳ hạn từ các thuộc tính có sẵn trước cuộc gọi, loại bỏ `duration` để tránh rò rỉ thông tin.

## Kết quả cần tái tạo

Quy trình được tách thành bốn bước độc lập:

1. tải và kiểm tra dữ liệu UCI Bank Marketing;
2. chia train/validation/test có phân tầng trước mọi bước học từ dữ liệu;
3. chọn Logistic Regression và ngưỡng chỉ trên validation, đồng thời báo độ biến thiên bằng cross-validation trên train;
4. mở test một lần để lập báo cáo cuối, sau đó chạy web/API bằng pipeline đã lưu.

## Tiến độ 06 tuần

Project được chia đúng theo kế hoạch trong đề bài. Mỗi thư mục tuần có README và `run_week.ps1` riêng:

| Tuần | Nội dung | Lệnh chạy |
|---|---|---|
| 01 | Chốt bài toán, timing, nguồn, giấy phép và schema | `.\tuan_01\run_week.ps1` |
| 02 | Tải/làm sạch, split, EDA trên train và baseline | `.\tuan_02\run_week.ps1` |
| 03 | Pipeline, Logistic Regression và validation | `.\tuan_03\run_week.ps1` |
| 04 | Test cuối, nhiều ngưỡng và phân tích lỗi | `.\tuan_04\run_week.ps1` |
| 05 | Flask web, API, validation và test tích hợp | `.\tuan_05\run_week.ps1` |
| 06 | Kiểm thử toàn bộ và kiểm tra bàn giao | `.\tuan_06\run_week.ps1` |

## Cài đặt trên Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Chạy toàn bộ pipeline

```powershell
python -m src.data --download
python -m src.train
python -m src.evaluate
python -m app.app
```

Mở `http://127.0.0.1:5000`. Không chạy lại `src.evaluate` sau khi đã xem kết quả test. Nếu cần kiểm thử quy trình từ đầu, xóa toàn bộ artifact đã tạo và ghi rõ đây là một vòng thực nghiệm mới; tùy chọn `--force` chỉ dùng khi giảng viên yêu cầu tái tạo.

`scripts/run_pipeline.ps1` dùng cho môi trường sạch. Nếu file khóa test đã tồn tại, script chỉ chạy test và release check, không huấn luyện hoặc mở test lại.

## Kiểm thử

```powershell
pytest -q
```

## Cấu trúc

```text
app/                  Flask web, API và giao diện
config/               seed, tỷ lệ split, không gian tham số/ngưỡng
data/                  hướng dẫn nguồn; raw/processed được tạo tự động
docs/                  data dictionary, model card, nhật ký và phân công
models/                pipeline và metadata được tạo tự động
reports/               kết quả đánh giá và biểu đồ do Python sinh ra
src/                   tải dữ liệu, huấn luyện, đánh giá
tests/                 kiểm thử schema, leakage và API
tuan_01/ ... tuan_06/  công việc và script chạy theo từng tuần
```

## API

`POST /api/score` nhận một bản ghi JSON gồm 15 biến (không có `duration`) và trả về xác suất, ngưỡng đang dùng, nhãn ưu tiên cùng cảnh báo sử dụng. Ví dụ:

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

## Nguồn và giấy phép

Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing*. UCI Machine Learning Repository. DOI: 10.24432/C5K306. Dữ liệu phát hành theo CC BY 4.0. Xem chi tiết tại `data/README.md`.
