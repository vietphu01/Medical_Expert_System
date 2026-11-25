# Kế hoạch phát triển trong 3–4 ngày cho ba học phần

**Phạm vi đã chốt ngày 25/11/2026.** Chọn một website Flask chạy cục bộ. Người dùng minh họa là người đã có một số chỉ số trên phiếu khám, muốn hiểu ứng dụng dùng những chỉ số nào và muốn tìm lịch trao đổi với chuyên gia. Họ có thể đặt lịch trực tiếp, kể cả khi chưa chạy suy luận. Dùng ca tự tạo và lịch chuyên gia giả lập cho buổi bảo vệ.

## Khả thi đến đâu

Ước lượng với hai người, mỗi người có 5–6 giờ tập trung mỗi ngày, tương đương 30–36 giờ công trong ba ngày hoặc 40–48 giờ công trong bốn ngày. Codex và Antigravity có thể hỗ trợ viết mã, dựng giao diện, chạy kiểm thử và dò sai lệch số liệu. Phần hai thành viên cần tự làm là chọn giả thuyết, hiểu cách tạo từng hình và giải thích được một ca khi giảng viên thay đổi đầu vào.

| Phần | Phạm vi đề xuất | Mốc |
|---|---|---|
| Core và môn Học máy | Giải thích phiên bản đã đánh giá, tái hiện bảng chọn mô hình và hoàn thành một đối chứng thay đổi đúng một đặc trưng trên Cleveland nếu lấy được đúng tệp nguồn | Ưu tiên cao nhất, ngày 1–3 |
| Python và đồ thị | Giữ Flask, SQLite và NumPy. Dùng pandas để phân tích dữ liệu train và tổng hợp metric. Dùng Matplotlib tạo hình từ đúng dữ liệu rồi hiển thị trong mục thực nghiệm của website | Ngày 1–3 |
| Trang giới thiệu và kiến thức | Một trang có hai lối vào là xem ca minh họa và xem lịch. Hai mục kiến thức ngắn giải thích cách đọc chỉ số trên phiếu và cách đọc điểm hỗ trợ, kèm nguồn cho nội dung sức khỏe | Ngày 1–2 |
| Chuyên gia và lịch hẹn | Danh sách chuyên gia mẫu, chuyên khoa, giờ trống, xác nhận và mã hẹn. Khi hai người cùng chọn một giờ của cùng chuyên gia, chỉ một lượt được ghi nhận | Ngày 2–3 |
| Trợ lý hội thoại | Hội thoại có hướng dẫn bằng tiếng Việt, giải thích chỉ số từ nội dung đã duyệt, thu các trường, gọi core hiện có hoặc tra giờ trống và đặt lịch sau xác nhận | Ngày 4 nếu luồng trực tiếp đã đạt |
| Mở rộng sau đợt này | Lịch thật của phòng khám, chatbot tư vấn y khoa tự do, tích hợp MySQL hoặc đánh giá mô hình mới trên quần thể độc lập đều cần thêm điều kiện và thời gian riêng | Sau demo |

**Căn cứ hiện tại.** Bốn bộ dữ liệu có mô hình tự viết bằng NumPy. Cleveland và Pima có luật đích để làm đối chứng, còn gan và thận đang dùng ML. Website đã có form, đồ thị minh họa, giải thích từng bước và lịch sử SQLite. Ngày 25/11, 50/50 kiểm thử chạy đạt trên DB tạm, mã phương pháp và tệp mô hình khớp khóa T10. Môi trường của repo hiện thiếu pandas và Matplotlib. Các điểm dưới đây lấy từ kết quả đã lưu của phiên bản ban đầu (V1). [Đặc tả](../SPEC.md) · [Kết quả CV](../tasks/T06_TRAINING.md) · [Đánh giá V1](../REVIEW.md)

## Mỗi học phần nhìn thấy điều gì

| Học phần | Câu hỏi giảng viên có thể đặt | Bằng chứng hai bạn mở được khi trả lời |
|---|---|---|
| Python | Dữ liệu đi từ trình duyệt đến Python, DB và biểu đồ như thế nào? | Một lần đặt lịch qua Flask được lưu trong SQLite. Một lệnh Python dùng pandas đọc bảng kết quả, Matplotlib dựng lại hình F1 từng mô hình, và con số trên web đối chiếu được với CSV. |
| Hệ chuyên gia | Dữ kiện nào kích hoạt luật, CF do ai đặt, và khi thiếu chỉ số thì sao? | Ca Pima có ML và luật bất đồng. Mở trace, chỉ rõ tiền đề, CF nhóm chọn và tính lại điểm gộp. Đổi sang ca thiếu dữ kiện để thấy ML dùng trung vị học từ train còn luật giữ giá trị chưa biết. |
| Đồ án cơ sở về Học máy | Nhãn là gì, vì sao chọn mô hình này, thay một đặc trưng tạo khác biệt gì? | Bảng đặc trưng và quần thể, phân bố nhãn trên train, kết quả các mô hình trên cùng 5 fold, một bảng đối chứng 3 so với 4 đặc trưng và kết luận có đề cập loại lỗi tăng hoặc giảm. |

Website là lựa chọn nền tảng cho yêu cầu GUI. Part 1 của Chapter 6 có kết nối và truy vấn MySQL. Part 2 có TCP/IP, socket client/server, truy cập website qua socket, SMTP và RPC. SQLite đáp ứng hướng đi hiện tại của repo. Nếu muốn trình diễn sát bài mạng sau khi hoàn thành các mục chính, có thể dùng một chương trình Python nhỏ kết nối qua socket tới Flask trên máy demo, gửi yêu cầu HTTP đọc giờ trống rồi in phản hồi. Điểm khuyến khích cụ thể phụ thuộc cách giảng viên chấm. [Slide MySQL](<../../../python-programming/document/Chapter 6. Part 1 Connecting MySQL.pdf>) · [Slide truyền thông mạng](<../../../python-programming/document/Chapter 6. Part 2 Communication Network.pdf>)

## Câu chuyện bảo vệ core hiện tại

1. **Từ nhu cầu tới nhãn.** Chọn Pima để kể trọn một ví dụ. Mỗi dòng tương ứng một quan sát, nhãn là kết quả dương hoặc âm trong bộ dữ liệu. V1 dùng glucose hai giờ trong nghiệm pháp dung nạp glucose, BMI và tuổi. Quần thể nguồn gồm phụ nữ gốc Pima từ 21 tuổi. Điều này giới hạn suy rộng sang người dùng website. [Đặc tả dữ liệu](../SPEC.md)
2. **Từ dữ liệu tới thử nghiệm.** Cho xem bảng số mẫu theo nhãn và số ô thiếu trên train. Giải thích vì sao số 0 ở glucose và BMI được xử lý là thiếu, còn 0 lần mang thai có nghĩa. Chia phân tầng 80/20 và dùng 5 fold trong phần train. Trung vị và tham số chuẩn hóa được học lại bằng phần huấn luyện của từng fold để đánh giá trên những mẫu chưa tham gia fit. [Pipeline](../tasks/T04_DATA_PIPELINE.md)
3. **Từ thử nghiệm tới quyết định.** Baseline Pima luôn chọn âm nên F1 lớp dương bằng 0. Trên cùng 5 fold, F1 dương trung bình của KNN là 0,6655, cây quyết định 0,6552 và Logistic Regression 0,6289. KNN được chọn theo tiêu chí F1 đã đặt. Minh họa cơ chế bằng bảy hàng xóm gần nhất trong không gian đã chuẩn hóa. Chênh lệch nhỏ với cây giúp giải thích vì sao cần ghi cả độ dao động giữa các fold. [Metric CV](../../results/t06-cv-seed42/metrics.csv) · [Huấn luyện](../tasks/T06_TRAINING.md)
4. **Từ mô hình tới lời giải thích.** Với ca tự tạo tuổi 45, glucose OGTT 90 và BMI 26, có một trong bảy hàng xóm thuộc lớp dương. KNN cho 1/7, luật theo tuổi và BMI cho 0,50. Tính tay được 0,50 + (1/7) × (1 − 0,50) ≈ 0,5714. Phần trăm trên giao diện biểu diễn điểm hỗ trợ cho nhãn của bộ dữ liệu. [Ca demo 5](../tasks/T13_DEMO.md)
5. **Từ kết quả tới giới hạn.** Trên 154 ca test Pima đã khóa, F1 từ 0,495 lên 0,640 khi thêm luật. Số ca dương bị bỏ sót giảm từ 30 còn 14, còn số ca âm bị báo dương tăng từ 19 lên 31. Luật khớp ở 50/154 ca. Tách riêng phép so sánh hai công thức gộp cũ và mới thì số ca đổi nhãn bằng 0. Người trình bày cần giải thích được cả hai phép so sánh. [Đánh giá](../REVIEW.md) · [Phân tích lỗi](../tasks/T12_ERROR_ANALYSIS.md)

## Thí nghiệm mở rộng core

**Câu hỏi cho vòng hai.** Hiệu năng của Gaussian Naive Bayes thay đổi thế nào khi bổ sung nhịp tim cao nhất đạt được trong nghiệm pháp gắng sức (`thalach`) vào ba chỉ số ban đầu của Cleveland là tuổi, huyết áp lúc nghỉ và cholesterol? Chọn biến số này vì có nghĩa đo cụ thể, nằm sẵn trong dữ liệu nguồn và phù hợp với pipeline số hiện có. Nếu tính đến việc đưa vào sản phẩm, người dùng cần có kết quả nghiệm pháp này trên hồ sơ. [Từ điển UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease)

| Bước | Việc làm và đầu ra |
|---|---|
| Lập giao thức V2 trước khi chạy | Ghi giả thuyết, hai bộ đầu vào, Gaussian NB, cùng 5 fold của 242 mẫu train Cleveland, ngưỡng 0,5, F1 lớp dương là tiêu chí chính. Đối chiếu bản tệp nguồn với mã kiểm tra đã lưu. |
| Chạy hai cấu hình trên cùng hàng dữ liệu | A dùng 3 biến V1, B thêm `thalach`. Giữ các lựa chọn khác như nhau. Tính trung vị và chuẩn hóa từ phần train của mỗi fold. Đối chiếu A với mốc F1 CV V1 là 0,5868 trước khi diễn giải B. |
| Đọc kết quả | Xuất số liệu mỗi fold, F1 trung bình và độ lệch chuẩn, chênh lệch B trừ A theo cặp, recall, số dương giả và âm giả từ dự đoán ngoài fold. Vẽ một hình nối A với B trong từng fold. Ghi kết luận cả khi kết quả giảm hoặc thay đổi thiếu nhất quán. |
| Quyết định vòng tiếp | Kết quả trong đợt này là bằng chứng phát triển trên train/CV. Nếu tín hiệu nhất quán và đầu vào khả dụng, khóa ứng viên rồi lập kế hoạch đánh giá trên dữ liệu độc lập phù hợp trước khi đề xuất dùng trên website. Nếu tín hiệu yếu, ghi điều đã học và xem lại chi phí thu thập đặc trưng. |

Holdout T10 đã được xem sau khi khóa V1 và chỉ dùng để trình bày kết quả của V1. V2 sử dụng 242 ID thuộc phần train, giữ seed 42 và ghi vào thư mục kết quả riêng. Nếu hết ngày 1 chưa có đúng tệp Cleveland, vẫn hoàn thành phần vấn đáp và biểu đồ bằng kết quả CV đã xuất, ghi thí nghiệm 4 biến là việc đang chờ dữ liệu. [Khóa V1](../../manifests/t10_lock.json) · [Quy trình dự án](../../AGENTS.md)

## Lịch làm việc và điều kiện bàn giao

| Ngày | Bạn phụ trách hệ chuyên gia và sản phẩm | Partner phụ trách học máy | Cuối ngày cùng kiểm tra |
|---|---|---|---|
| 1 | Vẽ luồng trang chủ → suy luận hoặc chuyên gia → lịch hẹn. Chốt nội dung sức khỏe và phác thảo bảng chuyên gia, khung giờ, lịch hẹn | Đối chiếu dữ liệu, chốt giao thức V2, dùng pandas lập bảng nhãn và missing trên train, tái tạo bảng chọn mô hình V1 | Hai người tự giải thích được nhãn, mô hình và một hạn chế. Có nguồn của từng trường định đưa lên form |
| 2 | Làm trang chủ, nội dung, danh sách chuyên gia và đặt lịch trực tiếp trên SQLite demo. Bảo đảm một khung giờ chỉ có một lịch bằng ràng buộc trong DB | Chạy A/B trên cùng fold. Tạo hình từ dữ liệu train và kết quả CV bằng Matplotlib, đặt tên nguồn và tập chia trên từng hình | Đặt được lịch mẫu và thấy giờ đó hết trống. Mỗi con số trên hình truy được về bảng đầu vào |
| 3 | Tích hợp đồ thị, trang suy luận và lịch hẹn. Thử hai yêu cầu cùng giờ, khởi động lại vẫn tra được lịch | Vẽ số FN/FP từ bảng đếm đã công bố cho Pima V1. Đọc ca sai trên validation của thí nghiệm mới, viết kết luận V2 hoặc ghi rõ trở ngại | Demo 5–7 phút, đổi vai trả lời, chạy test với DB tạm. Đây là mốc nộp nếu có ba ngày |
| 4 | Thêm trợ lý có hướng dẫn, dùng cùng API suy luận và đặt lịch. Hiện lại chuyên gia và giờ để người dùng xác nhận trước khi ghi | Kiểm tra báo cáo và tái tạo biểu đồ trên máy demo. Đổi đầu vào ca mẫu để kiểm tra lời giải thích | Nhập thiếu → hỏi bổ sung hoặc ghi chưa biết, xem điểm từ core, xem giờ trống, xác nhận hẹn. Nếu người khác vừa lấy giờ, hiển thị giờ khác |

Kịch bản buổi bảo vệ đi từ trang giới thiệu đến ca Pima số 5. Partner giải thích vì sao chọn KNN và chỉ ra một trong bảy hàng xóm dương. Bạn tính điểm kết hợp, mở biểu đồ để nói về 16 ca tìm thêm và 12 dương giả tăng thêm, rồi chuyển sang đặt lịch. Giữ một hình A/B Cleveland cho câu hỏi “nhóm đã tự cải thiện mô hình như thế nào?”. Nếu thiếu thời gian phát triển, cắt trợ lý trước và giữ lượt tập để cả hai đều trả lời được khi bị hỏi chéo.

## Phạm vi đưa sang SSTR sau khi chốt

- **STATUS** ghi mốc V1 đã kiểm chứng, môi trường Python, giờ công thực tế của hai người, quyết định phạm vi ba hoặc bốn ngày và trở ngại nguồn dữ liệu.
- **SPEC** ghi nhóm người dùng, luồng website, hợp đồng API suy luận và lịch hẹn, ranh giới nội dung sức khỏe, giao thức V2 và các hình cần giao.
- **TASKS** chia việc theo người, phụ thuộc, mốc ba ngày và phần thêm ngày bốn. Mỗi việc kết thúc bằng một thao tác demo hoặc một kết quả có thể kiểm tra.
- **REVIEW** đặt tiêu chí từ trước cho minh chứng ba môn, tái lập biểu đồ, cách đọc kết quả bất lợi, kiểm tra tranh cùng một giờ và hai người tự vấn đáp. Kết quả thực tế sẽ được điền sau khi chạy.

Nhóm triển khai giai đoạn 2 theo [trạng thái](../v2/STATUS.md), [đặc tả](../v2/SPEC.md), [danh sách công việc](../v2/TASKS.md) và [phiếu nghiệm thu](../v2/REVIEW.md).
