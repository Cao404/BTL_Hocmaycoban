# Hồ sơ dữ liệu

## Nguồn

- Tên: Bank Marketing.
- Nhà cung cấp: UCI Machine Learning Repository.
- Tác giả: Sérgio Moro, Paulo Rita và Paulo Cortez.
- DOI: https://doi.org/10.24432/C5K306
- Trang dữ liệu: https://archive.ics.uci.edu/dataset/222/bank%2Bmarketing
- Tệp sử dụng: `bank-full.csv` trong `bank.zip`, 45.211 dòng.
- Giấy phép: Creative Commons Attribution 4.0 International (CC BY 4.0).

Script `python -m src.data --download` tải tệp ZIP từ UCI, kiểm tra checksum SHA-256, giải nén đúng `bank-full.csv`, kiểm tra schema và tạo manifest. Không commit dữ liệu gốc hoặc các tệp split.

## Chất lượng và quy ước missing

UCI ghi nhận không có giá trị null theo định dạng CSV. Tuy nhiên nhiều biến phân loại dùng giá trị chuỗi `unknown`; đây là một mức dữ liệu quan sát được, không tự động thay bằng mode. Script báo cáo riêng số lượng `unknown`, trùng lặp hoàn toàn, phân bố target và các kiểm tra miền.

Không có dòng nào bị loại. Các giá trị số hiếm được giữ nguyên và báo min/max thay vì tự động coi là ngoại lệ sai. Manifest ghi rõ `rows_removed = 0` và danh sách lý do loại rỗng.

`duration` là thời lượng của cuộc gọi hiện tại và chỉ có sau khi cuộc gọi kết thúc. Vì mục tiêu là chấm điểm trước cuộc gọi, biến này bị loại trước khi chia X/y và không xuất hiện trong schema serving.

Dữ liệu chỉ có tháng/ngày liên hệ nhưng không có năm hoặc timestamp đầy đủ, nên không thể thiết lập thứ tự thời gian tin cậy. Project dùng split 60/20/20 có phân tầng và ghi nhận đây là giới hạn. Bộ dữ liệu cũng không có mã khách hàng ổn định để group split theo người.

## Tái tạo

```powershell
python -m src.data --download
```

Ngày tải, URL, checksum ZIP/CSV, phiên bản thư viện và số dòng được ghi vào `data/processed/data_manifest.json`.
