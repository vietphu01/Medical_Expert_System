# Báo cáo tiến độ Tuần 1

**18/11/2026 · Hoàn thành 5/5 mục Tuần 1 (T01–T05) · Tiếp theo T06**

Medical Expert System là đồ án kết hợp mô hình học máy tự viết bằng NumPy với logic mờ và luật chuyên gia. Ứng dụng Flask có biểu mẫu cho bốn nhóm bệnh và lưu lịch sử bằng SQLite. Mục tiêu thực nghiệm là so sánh mô hình trên dữ liệu thật của cả bốn nhóm, rồi dùng Cleveland và Pima để đo khi nào luật đưa ra kết luận và việc gộp luật với ML làm thay đổi dự đoán ra sao. [Đặc tả dự án](../SPEC.md)

Ở thời điểm này, **ứng dụng đã kiểm tra đầu vào và giữ lịch sử qua lần khởi động lại. Pipeline ngoại tuyến đã sẵn sàng cho huấn luyện trên bốn bộ dữ liệu thật.** Điểm trên giao diện hiện vẫn đến từ mô hình của bản nguyên mẫu, huấn luyện bằng dữ liệu tổng hợp. Kết quả CV trên dữ liệu thật và điểm đánh giá holdout cuối sẽ lần lượt có ở T06 và T10.

## Tuần 1 đã bàn giao gì?

| Mục | Kết quả |
|---|---|
| T01 · Lịch sử | Bản ghi còn nguyên sau hai lần khởi tạo SQLite. Có thể dùng DB tạm khi kiểm thử. |
| T02 · Đầu vào | API báo lỗi theo từng trường, biểu mẫu đánh dấu ô cần sửa. Yêu cầu lỗi và fact ngoài danh sách cho phép bị từ chối trước khi ghi lịch sử. |
| T03 · Tim mạch và tiểu đường | Nạp Cleveland và Pima từ tệp nguồn đã đối chiếu, chuẩn hóa nhãn và ghi thống kê dữ liệu thiếu. |
| T04 · Chia tập và tiền xử lý | Lưu ID cho holdout khoảng 20% và 5 fold trên phần train, phân tầng theo nhãn với seed 42. Mỗi fold chỉ học cách điền thiếu và chuẩn hóa từ train của fold đó. |
| T05 · Gan và thận | Đưa ILPD và CKD vào cùng pipeline, lưu metadata và manifest như hai bộ đầu. |

## Dữ liệu sẵn sàng cho T06

| Nhóm bệnh · Bộ dữ liệu | Mẫu âm / dương | Train / Holdout | Điểm cần biết |
|---|---:|---:|---|
| Tim mạch · Cleveland | 164 / 139 | 242 / 61 | Ba đặc trưng được chọn đều đủ dữ liệu. Mã nguồn 1–4 cùng thuộc lớp dương. |
| Tiểu đường · Pima | 500 / 268 | 614 / 154 | Có 5 giá trị glucose và 11 giá trị BMI bằng 0 được quy về thiếu. |
| Gan · ILPD | 164 / 406 | 456 / 114 | Còn 570 mẫu sau khi loại 13 bản ghi trùng toàn bộ. Ba đặc trưng được chọn đều đủ dữ liệu. |
| Thận · CKD | 150 / 250 | 320 / 80 | Thiếu 17 giá trị creatinine, 12 huyết áp và 9 tuổi. |

Khi viết luật, cần xác minh đơn vị glucose Pima, bilirubin và albumin ILPD, cùng loại huyết áp trong CKD (tâm thu hay tâm trương). Quyền tái phân phối tệp Pima gốc vẫn chưa được xác nhận. Các điểm này đã có trong hồ sơ nguồn. [Cleveland/Pima](../tasks/T03_DATA_SOURCES.md) · [ILPD/CKD](../tasks/T05_DATA_SOURCES.md)

## Kết quả rà soát lại

- **25/25 kiểm thử đạt**, gồm kiểm tra DB tạm, đầu vào của cả bốn nhóm, bộ nạp dữ liệu và test phát hiện rò rỉ khi tiền xử lý.
- Tái tạo metadata và manifest từ bốn tệp nguồn khớp từng byte với bản đã lưu. Cả **20 fold** có đủ hai lớp trong train và validation. Mỗi ID train xuất hiện đúng một lần ở validation, mọi ID holdout đều nằm ngoài các fold.
- Ở checkout hiện tại, `requirements.txt` có danh sách thư viện trong bản làm việc, còn bản đã commit vẫn rỗng. Kết quả rà soát dùng môi trường Python 3.12 hiện có. Việc tái lập từ checkout sạch còn cần kiểm tra khi bàn giao. [Nhật ký nghiệm thu và commit](../STATUS.md)

**Mốc tiếp theo là T06.** Chạy bốn mô hình tự viết, ensemble và baseline theo các fold đã lưu. Chọn mô hình cho từng bộ bằng F1 trung bình trên validation, xuất metric và dự đoán theo ID, rồi nối ứng dụng với mô hình đã fit trên train. T07–T09 hoàn thiện và thử các đối chứng ML–luật trước khi khóa cấu hình để đánh giá holdout ở T10. [Danh sách công việc](../TASKS.md)
