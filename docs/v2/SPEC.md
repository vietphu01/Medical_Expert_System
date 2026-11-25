# Đặc tả website và thí nghiệm giai đoạn 2

Mốc ngày 3 phục vụ người đã có một số chỉ số trên phiếu khám. Họ có thể xem cách hệ thống diễn giải một ca, đối chiếu kết quả học máy hoặc đặt một lịch trao đổi mẫu ngay từ trang chủ. Website chạy cục bộ bằng Flask và SQLite. Mô hình NumPy V1 tiếp tục phục vụ bốn nhóm bệnh. Phiên bản nghiên cứu Cleveland có thêm một đầu vào chỉ xuất hiện ở mục thực nghiệm. [Trạng thái](STATUS.md) · [Hợp đồng V1](../SPEC.md)

## Luồng trên website

| Điểm vào | Hành vi người dùng cần thấy |
|---|---|
| Trang chủ | Hai lựa chọn nổi bật “Xem ca minh họa” và “Xem lịch chuyên gia”. Ghi rõ đây là sản phẩm học tập, danh sách và lịch hẹn là dữ liệu demo. |
| Kiến thức | Hai mục ngắn về cách nhận biết tên phép đo trên phiếu và cách đọc điểm hỗ trợ cùng giới hạn quần thể. Mỗi nội dung sức khỏe ghi nguồn. Với Pima gọi đúng glucose hai giờ OGTT và giữ chú thích đơn vị nguồn chưa xác minh. |
| Suy luận | Truy cập được cả bốn form, lịch sử và ca mẫu. Sau khi chạy, hiện điểm ML, luật khớp hoặc trạng thái thiếu bằng chứng, điểm kết hợp và chi tiết tính. Khi dữ kiện thiếu, ML dùng trung vị từ train, luật nhận giá trị chưa biết. |
| Thực nghiệm | Đọc được biểu đồ trên web, tên bộ dữ liệu, phiên bản, tập chia, trục và chú giải. Mỗi hình chỉ nguồn bảng và quy trình tái tạo. |
| Chuyên gia và lịch | Chọn chuyên gia, xem chuyên khoa và giờ trống theo giờ Việt Nam, kiểm tra lại người và giờ, xác nhận, nhận mã hẹn. Mở lại lịch bằng mã sau khi khởi động lại ứng dụng. Có thể đi thẳng từ trang chủ. |

## Hợp đồng dữ liệu ứng dụng

**Suy luận.** Dùng `GET /api/diseases` để đọc schema và `POST /api/diagnose` với `disease`, `inputs`, tùy chọn `extra_facts` theo [API hiện có](../../medical_expert/web/app.py). Ví dụ hợp lệ là `{"disease":"diabetes","inputs":{"glucose":90,"bmi":26,"age":45}}`. Truyền đủ khóa, dùng `null` cho trường chủ động để trống. Form và trợ lý đọc `trace.ml`, `trace.facts`, `trace.fired_rules`, `trace.result` trên thang 0–1. Đầu vào lỗi trả 400 và lỗi theo trường, thiếu mô hình trả 503. Đồ thị và lời giải thích dùng cùng trace.

**Đặt lịch.** Giờ bắt đầu dùng ISO 8601 kèm múi giờ. Cơ sở dữ liệu lưu chuyên gia mẫu, khung giờ và lịch hẹn. Mỗi cặp chuyên gia và giờ bắt đầu là duy nhất, mỗi khung giờ có nhiều nhất một lịch hẹn. Bản demo chỉ cần mã hẹn để tra cứu, không cần thu thông tin sức khỏe hay thông tin liên lạc cho việc đặt lịch.

| API của giai đoạn 2 | Đầu vào và kết quả |
|---|---|
| `GET /api/experts` | 200, danh sách chuyên gia mẫu với `id`, `name`, `specialty`. |
| `GET /api/experts/<id>/slots` | 200, danh sách giờ còn trống với `id`, `starts_at`. Hết giờ trả danh sách rỗng. Chuyên gia chưa có trả 404. |
| `POST /api/appointments` | Sau khi người dùng xác nhận, gửi `{"slot_id":7}` với ID do danh sách giờ cung cấp. 201 trả `code`, `expert_id`, `starts_at`. Thiếu hoặc sai kiểu trả 400, giờ chưa có trả 404, giờ vừa bị đặt trả 409 và giao diện tải lại giờ trống. |
| `GET /api/appointments/<code>` | 200 trả thông tin xác nhận của mã đã đặt, 404 nếu mã chưa có. |

Mã hẹn được tạo ở máy chủ và là duy nhất. Ghi lịch trong một giao dịch SQLite có ràng buộc duy nhất trên `slot_id`. Hai yêu cầu cùng đến cho một giờ phải cho đúng một mã hẹn và một hàng trong DB. Khởi tạo lại ứng dụng giữ lịch và lịch sử suy luận đã có. Kiểm thử dùng SQLite tạm.

## Thực nghiệm Cleveland

**Câu hỏi đã chốt trước khi chạy.** Trên cùng các ca Cleveland, việc thêm nhịp tim cao nhất đạt được trong nghiệm pháp gắng sức (`thalach`) làm F1 lớp dương của Gaussian Naive Bayes thay đổi thế nào? Người sử dụng thực tế cần có kết quả nghiệm pháp mới cung cấp được chỉ số này. [Từ điển nguồn UCI](https://archive.ics.uci.edu/dataset/45/heart+disease)

| Thành phần | Quy ước dùng cho cả hai cấu hình |
|---|---|
| Nguồn và nhãn | Tệp `processed.cleveland.data` đúng SHA-256 ghi trong [khóa T10](../../manifests/t10_lock.json). Cột đích `num` bằng 0 cho nhãn âm, 1–4 cho nhãn dương. Bảo toàn ID dòng nguồn theo loader V1. |
| Đầu vào | A gồm `age, bp, chol` theo đúng thứ tự V1. B gồm `age, bp, chol, thalach`. Chỉ khác cột cuối. `bp` lấy từ `trestbps`. |
| Tập phát triển | Chỉ 242 ID trong `cleveland.train_ids` của [manifest T04](../../manifests/t04_split_manifest.json), seed 42, cùng 5 fold đã lưu. Giới hạn EDA, fit và dự đoán vào phần train này. Holdout T10 dành cho kết quả đã công bố của V1. |
| Tiền xử lý và mô hình | Trong từng fold, học trung vị và chuẩn hóa trên phần huấn luyện rồi áp dụng lên validation. Dùng cùng Gaussian NB NumPy và ngưỡng nhãn ≥ 0,5. Đánh giá riêng điểm ML để đo tác động của đặc trưng. |
| Chỉ tiêu | Chính là F1 lớp dương trung bình qua 5 fold. Báo F1 của A và B trong từng fold, độ lệch chuẩn theo quy ước V1, chênh lệch B trừ A theo cặp, recall, FP và FN. FP/FN toàn bộ là tổng trên các dự đoán ngoài fold, mỗi ID xuất hiện đúng một lần cho mỗi cấu hình. |

Đầu tiên đối chiếu F1 từng fold của A với CSV của V1 và mốc trung bình **0,5868464868** (0,5868 khi trình bày). Nếu lệch quá sai số làm tròn, kiểm tra ID, thứ tự cột và tiền xử lý trước khi diễn giải B. Chấp nhận kết quả tăng, giảm hoặc khác chiều giữa các fold. Kết luận chỉ áp dụng cho đánh giá phát triển trên train/CV. Muốn đưa ứng viên vào luồng suy luận cần đánh giá độc lập ở vòng sau. [Kết quả tham chiếu](../tasks/T06_TRAINING.md)

Ghi run riêng trong `results/<run_id_v2>/` với `metadata.json`, `metrics.csv`, `predictions.csv` theo [định dạng V1](../SPEC.md). Metadata ghi hai schema, cấu hình, ngưỡng, seed, phiên bản nguồn, checksum, manifest và cách tái tạo. CSV phân biệt A/B qua `variant` và ghi số fold trong `split`. Bảng dự đoán có 484 dòng dữ liệu ngoài fold (242 × 2). Số này là tiêu chí nghiệm thu.

## Phân tích bằng Python

Partner dùng pandas lập bảng số mẫu theo nhãn và số giá trị thiếu theo đặc trưng trên train, trước điền thiếu, ghi rõ mẫu số. Dùng Matplotlib tạo các hình sau bằng một lệnh chạy lại được từ gốc repo. Lưu bảng nguồn và đường dẫn hình khi nghiệm thu.

| Hình | Nguồn và cách đọc |
|---|---|
| Chọn mô hình V1 | F1 lớp dương trung bình và độ lệch chuẩn của mô hình cùng baseline trên cùng 5 fold, ít nhất cho Pima. Đọc từ CSV T06. |
| Tác động của luật trên Pima V1 | Dùng bảng đếm holdout **đã công bố** cho ML và tổ hợp. FN 30 → 14, FP 19 → 31. Nhãn hình ghi rõ V1, 154 mẫu. [Bảng đếm V1](../REVIEW.md) |
| Mở rộng Cleveland V2 | Nối F1 của A và B trong cùng fold, kèm bảng số FP/FN và recall. Khi thí nghiệm chờ dữ liệu, hiển thị trạng thái và chỉ trình bày những kết quả đã có. |

## Trợ lý ngày 4

Trợ lý hội thoại tiếng Việt có hai luồng dùng chung với giao diện trực tiếp. Luồng chỉ số hỏi nhóm bệnh và các trường theo schema, cho sửa hoặc chọn “chưa biết”, gọi API suy luận và diễn giải điểm từ trace. Nội dung sức khỏe dẫn về hai mục kiến thức đã có nguồn. Luồng hẹn tra chuyên gia và giờ còn trống, nhắc lại chuyên gia, giờ và chỉ tạo lịch khi người dùng xác nhận. Nếu nhận 409, trợ lý đưa các giờ còn lại để người dùng chọn và xác nhận lại. Câu hỏi ngoài nội dung đã duyệt được hướng tới trao đổi với chuyên gia.
