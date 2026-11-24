# Phiếu nghiệm thu và vấn đáp giai đoạn 2

Trạng thái ban đầu ngày 25/11/2026: nhóm đã chốt tiêu chí. Các ô dưới đây dành cho lần chạy V2. Điền **đạt**, **chưa đạt**, **chờ nguồn** hoặc **bỏ qua ngày 4**, kèm lệnh, bảng kết quả, ảnh hoặc ghi chú quan sát vào [STATUS](STATUS.md). Dùng ca tự tạo cho thao tác giao diện và DB tạm cho mọi kiểm thử. [Công việc](TASKS.md) · [Đặc tả](SPEC.md)

## Kiểm trên máy demo

| Task | Thao tác để người còn lại kiểm độc lập | Dấu hiệu đạt | Kết quả V2 |
|---|---|---|---|
| V2-01 | Đối chiếu SHA-256 nguồn và manifest. Kiểm đếm theo nhãn và missing trước điền thiếu trên train | Cleveland có 242 ID train, 131 âm và 111 dương. Bảng ghi số hàng, cột và mẫu số. pandas và Matplotlib import được trên môi trường dự án | Chưa kiểm |
| V2-02 | Từ trang chủ mở hai mục kiến thức, một ca mẫu và danh sách chuyên gia. Quay lại màn suy luận ở cả bốn nhóm | Đường dẫn dùng được, nguồn mở được, người xem nhận ra dữ liệu demo và hiểu ý nghĩa của điểm hỗ trợ | Chưa kiểm |
| V2-02, V2-06 | Chạy ca Pima số 5, một ca thiếu dữ kiện và ca ngoài miền. Đối chiếu màn hình với trace và lịch sử | Ca 5 hiện 14,3% ML, 50,0% luật, 57,1% kết hợp. Giá trị thiếu là chưa biết đối với luật. Đầu vào ngoài miền hiện lỗi và không tăng số lượt trong lịch sử | Chưa kiểm |
| V2-03 | Đi thẳng từ trang chủ đến đặt lịch. Gửi hai lần xác nhận đồng thời cho cùng một giờ bằng hai kết nối. Tải lại trang và khởi động lại trên cùng DB tạm | Một 201, một 409, một bản ghi. Giờ đã đặt biến mất khỏi giờ trống, mã vẫn tra được, lịch sử suy luận còn nguyên. Chuyên gia hết giờ hiển thị trạng thái phù hợp | Chưa kiểm |
| V2-04 | So hai danh sách ID ngoài fold, từng F1 của A với T06, cấu hình A/B và thống kê fit. Tái tính F1, recall, FP, FN từ CSV dự đoán | Mỗi cấu hình có đúng 242 ID train, mỗi ID xuất hiện một lần, cùng fold và nhãn thật. A trung bình 0,5868. B có thêm đúng một biến. Kết luận cho biết độ nhất quán giữa các fold và chiều thay đổi của các lỗi | Chưa kiểm |
| V2-05 | Chạy lệnh dựng hình trên máy demo. Chọn một điểm hoặc cột trên từng hình, lấy lại con số từ đúng CSV hoặc bảng đếm V1 đã công bố | Hình Pima ghi đúng CV hoặc holdout tùy phép đo. Hình Cleveland có năm cặp A/B khi có kết quả. Mục thực nghiệm phản ánh đúng dữ liệu đã có | Chưa kiểm |
| V2-06 | Chạy bộ kiểm thử trên DB tạm. Cùng trình bày trọn luồng trong 5–7 phút, đổi người giải thích một ca và một bảng | Hai người chỉ được nguồn con số, giải thích kết quả bất lợi, cho xem mã hẹn. Ghi giờ thực tế, lỗi còn mở và trạng thái riêng của V2-04 | Chưa kiểm |
| V2-07 | Làm lại ca 5 qua trợ lý, cho một trường chưa biết, nhập sai rồi sửa. Thử đặt lịch, đổi ý, xác nhận và xung đột giờ | Cùng đầu vào cho cùng điểm và luật như form. Đổi ý không tạo lịch. Xác nhận tạo đúng một lịch. Giờ vừa bị lấy dẫn đến chọn và xác nhận giờ mới | Tùy ngày 4 |

## Câu hỏi vấn đáp cho ba học phần

| Học phần | Câu hỏi | Minh chứng cần chỉ được |
|---|---|---|
| Python | Nếu thay một dòng trong bảng nguồn hợp lệ, vì sao hình vẽ đổi? Hai người bấm đặt cùng giờ thì chuyện gì xảy ra? | Chỉ đoạn pandas đọc và nhóm dữ liệu, Matplotlib lấy cột nào làm trục, một giá trị từ CSV đi lên hình. Giải thích giao dịch SQLite và kết quả 201/409 từ bài thử cạnh tranh. |
| Hệ chuyên gia | Vì sao ca 5 cho 57,1% và vì sao một ô trống lại ảnh hưởng ML và luật khác nhau? | Ca tự tạo tuổi 45, glucose OGTT 90, BMI 26. Điểm ML là 1/7. Luật tuổi và BMI cho CF 0,50 do nhóm đặt. Tính tay 0,50 + (1/7) × (1 − 0,50). Chỉ ra fact chưa biết trong một ca khác. |
| Học máy | Nhãn thuộc quần thể nào? Vì sao chọn KNN trên Pima? Mean F1 cao hơn có đủ để đưa V2 vào ứng dụng? | Nêu quần thể phụ nữ gốc Pima từ 21 tuổi. KNN 0,6655 so với cây 0,6552 và logistic 0,6289 trên cùng 5 fold train. Baseline luôn chọn âm nên F1 dương bằng 0. Với Cleveland, đọc F1 từng fold, FP/FN, mức sẵn có của `thalach` và nhu cầu đánh giá độc lập. |
| Đối chứng | Thêm luật đã sửa lỗi nào và gây thêm lỗi nào? Đổi công thức gộp tác động ra sao? | Trên holdout Pima V1 có 154 ca, thêm luật tìm thêm 16 ca dương và tạo thêm 12 dương giả. So riêng công thức gộp cũ với mới có 0 ca đổi nhãn trên lần chia này. [Số liệu V1](../REVIEW.md) |

## Cách kết luận sau thực nghiệm

Ghi F1 trung bình của A và B, chênh lệch B trừ A, số fold tăng/giảm/hòa, FP và FN của từng cấu hình. Giải thích bằng số ca và chỉ ra việc người dùng phải có thêm một kết quả nghiệm pháp. Nếu hiệu quả thiếu nhất quán hoặc giảm, ghi nhận và giải thích giới hạn. Nếu tín hiệu nhất quán và chỉ số khả dụng, ghi nhận ứng viên cho đánh giá độc lập. Khi thiếu nguồn hoặc mốc A chưa tái lập được, kết luận V2 là **chưa đủ dữ liệu để so sánh**.

**Kết luận bàn giao ngày 3:** chờ kiểm tra trực tiếp. **Phần thêm ngày 4:** chờ xác định thời gian và kết quả luồng trực tiếp.
