# Model card - Bank Marketing Prioritization

## Mục đích

Mô hình xếp hạng khả năng khách hàng quan tâm tới tiền gửi có kỳ hạn trước cuộc gọi. Đầu ra là xác suất và một nhãn ưu tiên theo ngưỡng đã chốt trên validation. Đây không phải quyết định bắt buộc và không được dùng để loại trừ khách hàng khỏi dịch vụ.

## Dữ liệu và mô hình

- UCI Bank Marketing, `bank-full.csv`, CC BY 4.0.
- Logistic Regression với one-hot encoding cho biến phân loại và chuẩn hóa biến số.
- `duration` bị loại vì chỉ biết sau khi cuộc gọi kết thúc.
- Split 60/20/20 có phân tầng; preprocessing chỉ fit trên train.
- Chọn mô hình theo PR-AUC trên validation; báo riêng Average Precision; chọn ngưỡng theo F1 với ràng buộc recall tối thiểu.
- Đo độ biến thiên bằng Stratified 5-fold cross-validation chỉ trên train; test không tham gia chọn mô hình.

## Giới hạn

Dữ liệu đến từ một ngân hàng Bồ Đào Nha và một bối cảnh chiến dịch lịch sử nên có thể lệch miền khi áp dụng nơi khác. Các nhóm tuổi/nghề có quy mô và sai số khác nhau. Xác suất không chứng minh quan hệ nhân quả, không phản ánh ý chí hiện tại của khách hàng và không thay thế đánh giá nghiệp vụ.

Dữ liệu không cung cấp mã khách hàng ổn định, vì vậy không thể xác minh hoặc group split theo khách hàng. Đây là giới hạn cần xem xét nếu nguồn dữ liệu mới có nhiều bản ghi cho cùng một người.

## Sử dụng có trách nhiệm

Không dùng tuổi, nghề hoặc dự đoán để từ chối dịch vụ. Theo dõi precision/recall theo nhóm, bảo vệ dữ liệu cá nhân, cho phép nhân viên bỏ qua đề xuất, ghi log phiên bản model và kiểm tra drift trước khi tái sử dụng.
