# Công việc triển khai

Đánh dấu từng mục sau khi đạt tiêu chí và review diff. Trạng thái và bằng chứng chạy lệnh ghi trong [STATUS.md](STATUS.md). Hợp đồng kỹ thuật nằm trong [SPEC.md](SPEC.md).

## Tuần 1 · Nền tảng và pipeline dữ liệu

- [x] **T01 · Giữ lịch sử khi khởi động.** Bỏ `DROP TABLE`, khởi tạo SQLite lặp lại an toàn và cho phép test chỉ định DB tạm. Xong khi bản ghi mẫu còn nguyên sau hai lần khởi tạo trên DB tạm và DB mới có đủ schema.
- [x] **T02 · Kiểm tra API và báo lỗi trên form.** Xong khi đầu vào hợp lệ đi qua luồng hiện có, disease key không hỗ trợ, thiếu trường, sai kiểu, NaN/Inf và ngoài miền đều trả lỗi 4xx có trường lỗi. Request chứa fact trái phép bị từ chối và request lỗi không ghi lịch sử.
- [x] **T03 · Xác minh và nạp Cleveland/Pima.** Xong khi xác minh nguồn, bản phát hành và điều khoản dùng, kiểm tra nhãn/đơn vị/missing, rồi có loader và fixture cho các trường hợp hợp lệ, sentinel và nhãn sai. Ghi số dòng, nhãn và missing vào metadata. Ghi rõ kiểm tra phép đo glucose Pima.
- [x] **T04 · Chia dữ liệu và tiền xử lý đúng.** Phụ thuộc T03. Xong khi manifest holdout 80/20 và 5 fold tái lập bằng seed 42, tập test không giao với train hoặc bất kỳ fold nào, các fold có đủ lớp và fixture chứng minh imputer/scaler chỉ fit bằng phần train của fold. Test tích hợp pipeline bằng fixture.
- [x] **T05 · Nạp ILPD/CKD qua cùng pipeline.** Phụ thuộc T03–T04. Xong khi cả hai loader xác minh được schema và mã nhãn, kiểm tra missing và đơn vị, tạo split được và ghi metadata như Cleveland/Pima. Ghi nhận cột CKD có nghĩa phép đo chưa xác minh trước khi dùng trong luật.

## Tuần 2 · Thực nghiệm và giải thích

- [x] **T06 · Huấn luyện và xuất kết quả CV.** Phụ thuộc T04–T05. Xong khi một lệnh chạy được 4 mô hình tự viết, ensemble và baseline cho cả 4 bộ, chọn mô hình bằng F1 trên CV và xuất đủ CSV/JSON theo SPEC. Ứng dụng tải mô hình đã fit trên train. Khi chưa có artifact, giao diện nêu trạng thái rõ ràng.
- [x] **T07 · Rà soát luật cho bốn nhóm.** Xong khi luật/fact trả về nhất quán với tên trường và đơn vị, có bảng nguồn và ánh xạ tới đích hoặc kết luận phụ. Cleveland/Pima có luật đích với đầu vào quan sát được trên dữ liệu đánh giá, đã kiểm tra coverage trên validation. Mọi luật dùng cho test được khóa trước T10.
- [x] **T08 · Gộp cũ–mới và trace.** Phụ thuộc T07. Xong khi fixture kiểm tra một luật, nhiều luật, thiếu fact và không có luật đích khớp. Gộp mới chỉ đưa ML vào một lần, gộp cũ phục vụ đối chứng. JSON trace tuân schema và chỉ đưa luật cùng đích vào điểm.
- [x] **T09 · Chạy thử bộ đối chứng trên validation.** Phụ thuộc T06–T08. Xong khi ML, luật, gộp mới và gộp cũ xuất đủ output trên validation hoặc dự đoán ngoài fold của Cleveland/Pima, có coverage và số ca đổi nhãn. Kiểm tra trường hợp không có luật và tập con chỉ có một lớp. Nếu chọn fuzzy liên tục, hoàn thiện T14 trước khi khóa test.
- [x] **T10 · Khóa cấu hình và đánh giá test cuối.** Phụ thuộc T09. Xong khi STATUS ghi cấu hình, ngưỡng, split manifest và mapping luật đã khóa trước khi chạy. Xuất so sánh ML cho 4 bộ, ablation và gộp cũ–mới cho Cleveland/Pima, có metadata, metric và dự đoán theo ID. Đối chiếu số dự đoán, coverage và confusion matrix với số dòng thực tế.

## Tuần 3 · Phân tích và demo

- [x] **T11 · Hiển thị kết quả và trace.** Phụ thuộc T01–T02, T06, T08. Xong khi cả bốn form gửi đúng schema, hiển thị điểm hỗ trợ và trace, báo lỗi đầu vào rõ và đọc được lịch sử. Trường hợp không có luật đích hiển thị trạng thái thiếu bằng chứng từ luật.
- [x] **T12 · Phân tích lỗi và giải thích ML.** Phụ thuộc T10. Xong khi báo cáo có ca sai của ML, ca sai của luật trong vùng có kết luận và ca bất đồng, hoặc ghi rõ nhóm nào không có ca quan sát được. Mỗi ca tham chiếu được kết quả theo ID. Có một biểu đồ hệ số Logistic Regression kèm tên đặc trưng và cách đọc.
- [x] **T13 · Chuẩn bị 6 ca demo.** Phụ thuộc T11. Xong khi có ca hợp lệ, thiếu dữ kiện, sát ngưỡng fuzzy, nhiều luật đích cùng kích hoạt, ML bất đồng luật và ngoài miền. Mỗi ca có input mẫu, kỳ vọng, kết quả và ảnh. Dùng fixture hoặc validation.
- [ ] **T14 · Fuzzy liên tục (tùy chọn).** Sau T08 và trước khi khóa ở T10 nếu đưa vào đối chứng chính thức. Xong khi một bảng validation so sánh boolean với minimum × CF trên cùng mẫu và các thành phần khác cố định. Nếu bỏ qua, ghi quyết định vào STATUS. Quyết định: bỏ qua trước khi khóa T10.

## Tuần 4 · Hoàn thiện

- [x] **T15 · Tái lập và bàn giao.** Xong khi môi trường mới chạy được theo README, lệnh test pass, giao diện bốn nhóm chạy bằng ca mẫu và số trong báo cáo đối chiếu được với CSV/JSON. Báo cáo nêu giới hạn của dữ liệu nhỏ, quần thể Pima, luật và điểm chưa hiệu chỉnh.

## Sau bàn giao · Review và GUI

- [x] Rà soát dữ liệu, mô hình, luật, kết quả và ứng dụng. Bàn giao [đánh giá cùng ba bài tự cải thiện](REVIEW.md), GUI ngoại tuyến và sáu ảnh demo mới. [Bằng chứng nghiệm thu](STATUS.md)
- [x] Bàn giao [báo cáo dự án từ A đến Z](BAO_CAO_DU_AN.md), gồm tiến trình phát triển, kiến trúc, luồng suy luận, cách vận hành và kết quả thực nghiệm có nguồn đối chiếu.
- [x] Bàn giao [sổ tay bảo vệ](GHI_CHU_BAO_VE.md) với lời đáp cho câu hỏi kỹ thuật, phép tính ca Pima, số liệu đối chứng và kịch bản cầm máy 5–7 phút.
