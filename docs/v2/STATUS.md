# Trạng thái giai đoạn 2

**Ngày 25/11/2026, nhóm chốt bàn giao website demo vào cuối ngày 3.** Ngày 4 dành cho trợ lý hội thoại nếu có thêm thời gian và luồng trực tiếp đã chạy đạt. Sản phẩm phục vụ ba học phần bằng một kịch bản chung gồm đọc chỉ số, giải thích suy luận, xem bằng chứng thực nghiệm và đặt lịch mẫu. “Ngày 1” là ngày nhóm bắt đầu triển khai. [Kế hoạch đã duyệt](../reports/KE_HOACH_PHAT_TRIEN_3_4_NGAY.md)

| Hạng mục | Trạng thái tại lúc chốt | Bằng chứng hoặc việc tiếp theo |
|---|---|---|
| Website và suy luận V1 | Đã kiểm tra lại. Bốn nhóm chạy ML, Cleveland và Pima có luật đích. Có lịch sử SQLite và sáu ca demo tự tạo | Bộ kiểm thử đạt 50/50 trên DB tạm. [Ca demo](../tasks/T13_DEMO.md) |
| Kết quả nghiên cứu V1 | Đã có mô hình và bảng CV cục bộ. Đối chiếu SHA-256 khớp 17/17 tệp phương pháp và tệp mô hình với khóa T10 | [Khóa V1](../../manifests/t10_lock.json) · [Kết quả CV](../tasks/T06_TRAINING.md) · [Kết quả holdout đã công bố](../REVIEW.md) |
| Dữ liệu và thư viện cho V2 | Môi trường hiện có Flask và NumPy, còn thiếu pandas và Matplotlib. Chưa tìm thấy tệp nguồn Cleveland và Pima trong repo | Partner kiểm tra bản nguồn cục bộ hoặc lấy đúng bản ở hồ sơ T03 rồi xác minh SHA-256. [Hồ sơ nguồn](../tasks/T03_DATA_SOURCES.md) |
| Thực nghiệm Cleveland V2 | Đã chốt phép so sánh 3 và 4 biến. Chưa chạy, chưa có điểm V2 | Dùng đúng 242 ID train, 5 fold cũ và cùng Gaussian NB. [Giao thức](SPEC.md#thực-nghiệm-cleveland) |
| Trang giới thiệu, kiến thức, đồ thị và đặt lịch | Đã chốt phạm vi ngày 3. Chờ triển khai và kiểm tra trên website | [Công việc](TASKS.md) · [Phiếu nghiệm thu](REVIEW.md) |
| Trợ lý hội thoại | Tùy chọn ngày 4 | Dùng chung hai luồng suy luận và đặt lịch đã kiểm tra |

## Nhân lực và quyết định

- **Bạn** phụ trách hệ chuyên gia, giao diện, lịch hẹn và tích hợp. **Partner** phụ trách dữ liệu, phân tích bằng pandas, mô hình và biểu đồ Matplotlib. Hai người đổi vai một lượt khi tập vấn đáp.
- Ngân sách là **ước lượng** 5–6 giờ/người/ngày, tương ứng 30–36 giờ công cho ba ngày, 40–48 giờ công nếu làm đủ bốn ngày. Giờ thực tế sẽ ghi cuối từng ngày.
- Dùng Flask, SQLite và NumPy hiện có. Chuyên gia, ca nhập và lịch hẹn dùng dữ liệu minh họa. Kết quả hiệu năng lấy từ dữ liệu nghiên cứu thật. MySQL và kết nối lịch phòng khám thật để sau đợt demo. Bài socket của Chapter 6 là phần điểm khuyến khích nếu còn thời gian. [Phạm vi đã duyệt](../reports/KE_HOACH_PHAT_TRIEN_3_4_NGAY.md)
- Nếu hết ngày 1 vẫn thiếu đúng nguồn Cleveland, ghi rõ đầu vào còn thiếu, tiếp tục phần Python và vấn đáp bằng bảng CV V1. Giữ thí nghiệm Cleveland ở trạng thái chờ nguồn cho đến khi tái lập được mốc A.

## Sổ bàn giao

| Mốc | Kiểm tra và bằng chứng | Kết quả | Bước tiếp |
|---|---|---|---|
| 25/11, đối chiếu nền V1 tại `f189b3e` | Chạy `.venv/bin/python -B -m unittest discover -s tests -q` với `MEDICAL_HISTORY_DB` trỏ vào thư mục tạm. Đối chiếu SHA-256 theo `docs/t10_lock.json` | 50/50 đạt và các mã kiểm tra nêu trên khớp | Bắt đầu phần dữ liệu và luồng website theo [TASKS](TASKS.md) |
| 25/11, V2-00 tại `6ebd587` | Đọc thay đổi của kế hoạch và bốn tệp SSTR, đối chiếu bảng, mốc, mã task và 44 liên kết nội bộ bằng Python. Chạy `git diff --cached --check` trước commit | Đạt nghiệm thu tài liệu. Các task triển khai V2-01 đến V2-07 còn mở | Partner bắt đầu V2-01. Bạn bắt đầu V2-02 và thiết kế lịch hẹn cho V2-03 |

Mỗi task hoàn thành thêm một dòng với mã task, commit, lệnh đã chạy, kết quả và đường dẫn bằng chứng. Ghi số giờ thực tế khi tổng kết ngày. Bất kỳ kết quả V2 nào bị mất hiệu lực cần được ghi ở đây cùng lý do và các bảng hoặc hình bị ảnh hưởng trước khi sửa.
