# Công việc giai đoạn 2

Mốc nộp chính là cuối ngày 3. Bạn phụ trách sản phẩm và hệ chuyên gia, partner phụ trách học máy. Các mã cùng ngày có thể làm song song theo cột phụ thuộc. Mỗi dấu kiểm ứng với kết quả đã chạy và được người còn lại kiểm tra. Đọc [đặc tả](SPEC.md), đối chiếu [phiếu nghiệm thu](REVIEW.md) rồi ghi commit, lệnh, kết quả và bước tiếp vào [trạng thái](STATUS.md).

## Chốt trước triển khai

- [x] **V2-00 · Hai người · Chốt SSTR.** Đủ bốn tài liệu, mốc ngày 3 và ngày 4 phân biệt rõ, giao thức Cleveland đã ghi trước thí nghiệm, mọi task có người phụ trách và tiêu chí kiểm tra.

## Mốc bàn giao cuối ngày 3

| Mã | Ngày và người | Phụ thuộc | Hoàn thành khi |
|---|---|---|---|
| V2-01 | 1 · Partner | V2-00 | **Chuẩn bị dữ liệu và môi trường.** Xác minh checksum nguồn, xác định ID train theo manifest, cài và ghi phiên bản pandas, Matplotlib vào môi trường tái lập của repo. Có bảng nhãn và missing của train trước điền thiếu với nguồn, mẫu số. Ghi rõ phần chờ nếu thiếu tệp. |
| V2-02 | 1–2 · Bạn | V2-00 | **Trang chủ và kiến thức.** Hai lối vào ca minh họa và chuyên gia đi được từ trang chủ. Hai mục kiến thức ngắn có nguồn. Mở lại được bốn form, kết quả động và lịch sử. Có ca tự tạo kiểm tra luồng điều hướng. |
| V2-03 | 1–2 · Bạn | V2-00 | **Lịch hẹn trực tiếp.** Chuyên gia và khung giờ mẫu đọc từ SQLite. Người dùng đặt và tra được lịch bằng mã, kể cả sau khi khởi động lại. Hai yêu cầu đồng thời cho một giờ trả một 201, một 409 và chỉ có một bản ghi. Chạy trên DB tạm. |
| V2-04 | 2 · Partner | Phần Cleveland của V2-01 có tệp nguồn và ID train đã xác minh | **Đối chứng A/B.** Chạy lại A khớp mốc T06, thêm đúng một cột vào B, xuất run riêng đủ CSV/JSON. Hai cấu hình dùng cùng 242 ID ngoài fold. Có bảng 5 cặp F1, độ lệch chuẩn, recall, số FP/FN và kết luận kể cả chiều bất lợi. |
| V2-05 | 2–3 · Partner và bạn | V2-00, pandas và Matplotlib đã cài. Hình A/B dùng kết quả V2-04 | **Đồ thị trên website.** Partner cung cấp lệnh tái tạo các hình và bảng nguồn, bạn nối chúng vào mục thực nghiệm. Mỗi hình ghi tập chia và phiên bản. Đối chiếu ít nhất một giá trị trên mỗi hình với bảng nguồn. Khi thiếu Cleveland, phần V1 và trang web vẫn bàn giao được. |
| V2-06 | 3 · Hai người | V2-02, V2-03, phần V1 của V2-05. Kiểm riêng V2-04 nếu đã chạy | **Tích hợp và vấn đáp.** Bộ kiểm thử hiện có và các ca mới đạt với DB tạm. Chạy demo 5–7 phút từ trang chủ qua ca Pima số 5 đến đặt lịch, đổi vai trả lời. Ghi tình trạng thực nghiệm, kết quả kiểm tra và phần còn mở vào SSTR. |

### Theo dõi hoàn thành

- [ ] V2-01 · Môi trường và dữ liệu train.
- [ ] V2-02 · Trang chủ, điều hướng và kiến thức.
- [ ] V2-03 · Đặt lịch trực tiếp.
- [ ] V2-04 · Thí nghiệm Cleveland 3 và 4 đặc trưng.
- [ ] V2-05 · Hình và bảng số trên website. Nếu V2-04 còn chờ, ghi rõ đã giao phần hình V1 và để mở phần hình A/B.
- [ ] V2-06 · Tích hợp, kịch bản và vấn đáp.

**Nhánh thiếu nguồn.** Hết ngày 1, nếu thiếu Cleveland đúng phiên bản, partner ghi tên tệp và trở ngại vào STATUS, chuyển sang hình V1 và luyện giải thích. Có thể dùng số đếm train đã công bố với dẫn nguồn, ghi rõ phần missing chưa đo nếu thiếu dữ liệu gốc. Khi đánh giá mốc ngày 3, ghi riêng “đã bàn giao demo” và “thực nghiệm chờ nguồn” nếu đúng thực tế.

## Phần thêm ngày 4

- [ ] **V2-07 · Bạn triển khai, partner kiểm tra · Trợ lý có hướng dẫn.** Bắt đầu sau khi luồng suy luận và đặt lịch trực tiếp đạt kiểm tra ngày 3. Nhập ca 5 qua trợ lý cho cùng trace với form. Chọn chưa biết hoặc sửa được chỉ số, hỏi lại khi nhập lỗi. Tra lịch, đổi ý trước xác nhận, xác nhận đặt, rồi thử tình huống giờ vừa bị lấy. Đối chiếu số lịch được ghi và tập lại demo có trợ lý.
