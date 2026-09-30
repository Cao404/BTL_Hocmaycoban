# Data dictionary

| Biến | Kiểu | Vai trò | Ý nghĩa và thời điểm có sẵn |
|---|---|---|---|
| age | số nguyên | feature | Tuổi khách hàng, có trước cuộc gọi |
| job | phân loại | feature | Nghề nghiệp, có trước cuộc gọi |
| marital | phân loại | feature | Tình trạng hôn nhân, có trước cuộc gọi |
| education | phân loại | feature | Trình độ học vấn, có trước cuộc gọi |
| default | nhị phân | feature | Có nợ quá hạn, có trước cuộc gọi |
| balance | số nguyên | feature | Số dư trung bình năm (EUR), có trước cuộc gọi |
| housing | nhị phân | feature | Có khoản vay nhà ở, có trước cuộc gọi |
| loan | nhị phân | feature | Có khoản vay cá nhân, có trước cuộc gọi |
| contact | phân loại | feature | Kênh liên hệ dự kiến/ghi nhận |
| day | số nguyên | feature | Ngày trong tháng của liên hệ |
| month | phân loại | feature | Tháng liên hệ |
| duration | số nguyên | loại bỏ | Thời lượng cuộc gọi, chỉ biết sau cuộc gọi; gây leakage |
| campaign | số nguyên | feature | Số lần liên hệ trong chiến dịch, gồm lần hiện tại |
| pdays | số nguyên | feature | Số ngày từ lần liên hệ trước; -1 là chưa từng liên hệ |
| previous | số nguyên | feature | Số lần liên hệ trước chiến dịch hiện tại |
| poutcome | phân loại | feature | Kết quả chiến dịch trước |
| y | nhị phân | target | Có đăng ký tiền gửi kỳ hạn (`yes`/`no`) |

Không có ID khách hàng ổn định trong bộ dữ liệu. Đơn vị quan sát là một lần liên hệ trong chiến dịch.

Vì không có định danh ổn định, project không thể xác minh hoặc thực hiện group split theo khách hàng. Split có phân tầng được sử dụng và giới hạn này phải được nêu khi diễn giải khả năng tổng quát hóa.
