# Tuần 05 - Web, API và kiểm thử tích hợp

## Công việc

- Tích hợp pipeline đã lưu vào Flask; không train trong request.
- Hoàn thiện màn hình phạm vi, chấm điểm, dashboard và model card.
- Cung cấp `POST /api/score` và `GET /api/health`.
- Kiểm tra trường hợp hợp lệ, trường thiếu/thừa, category sai, số ngoài miền và `duration`.
- Chạy test API và luồng web cơ bản.

## Minh chứng đầu ra

- `app/app.py`
- `app/templates/`
- `app/static/`
- `docs/api.md`
- `tests/test_api.py`

## Chạy tuần 05

```powershell
.\tuan_05\run_week.ps1
```

Sau khi test đạt, chạy web bằng `python -m app.app`.
