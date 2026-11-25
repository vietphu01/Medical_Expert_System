# Luyện vấn đáp khó · Medical Expert System

Tài liệu này giúp bạn **tự trả lời và chỉ ra bằng chứng** khi bảo vệ. Các câu hỏi được xây dựng từ mã nguồn, báo cáo và số liệu hiện có của đồ án. Phần chiến lược là kế hoạch luyện tập được đề xuất, vì chưa có thang điểm chính thức của giảng viên. Không có cách nào bảo đảm điểm tuyệt đối, nhưng bạn có thể chủ động chuẩn bị cho những điểm thường quyết định chất lượng một buổi bảo vệ.

Lời đáp mẫu dùng “em”. Hãy sửa thành “nhóm em” ở những việc nhóm thực hiện chung, và tự ghi rõ phần bạn trực tiếp làm. Chỉ nhận công việc hoặc mức độ hiểu biết đúng với thực tế.

## 1. Chiến lược cho buổi bảo vệ

### Câu chuyện chính trong 5–7 phút

Giả sử bạn có 5–7 phút như thời lượng đã chuẩn bị trước đó. Nếu giảng viên quy định khác, co giãn phần demo và phần số liệu theo thời gian thực tế.

| Thời gian | Việc cần làm | Điều người nghe cần nắm |
|---|---|---|
| 0:00–0:45 | Nêu bài toán và giới hạn. | Bốn nhóm dữ liệu có bốn mô hình riêng. Luật và đối chứng được làm sâu trên Cleveland, Pima. Hệ thống phục vụ học tập và thực nghiệm. |
| 0:45–1:30 | Tóm tắt dữ liệu và đánh giá. | Mỗi bộ dùng ba đặc trưng. Giữ riêng khoảng 20%, chọn mô hình bằng 5-fold CV trên 80% còn lại, khóa cấu hình rồi đánh giá holdout. |
| 1:30–3:00 | Chạy ca 5, cho xem điểm ML, luật, gộp và trace. | Một ca có thể đi từ chỉ số đến fact, luật và kết quả. Tự tính được 1/7 → 0,50 → 0,5714. |
| 3:00–4:30 | Đưa bảng Pima ML so với ML + luật. | Thêm luật tìm thêm 16 ca dương và tạo thêm 12 ca dương giả trên holdout 154 ca. |
| 4:30–5:30 | Chủ động nói hai hạn chế có số liệu. | AUC Cleveland là 0,534 trên 61 ca. ILPD nhận đúng 5/33 ca âm dù F1 dương 0,834. |
| Thời gian còn lại | Mở sẵn một file code và bảng kết quả. | Sẵn sàng trả lời về rò rỉ dữ liệu, nguồn luật, hai công thức và điểm chưa hiệu chỉnh. |

Nếu giảng viên ngắt lời sớm, dừng thao tác và trả lời câu hỏi. Sau câu trả lời, quay về đúng đoạn đang trình bày. Một ví dụ đi hết luồng cùng một bảng kiểm chứng đủ để người nghe theo dõi. [Bảng kết quả](../tasks/T10_HOLDOUT.md) · [Phân tích lỗi](../tasks/T12_ERROR_ANALYSIS.md)

### Công thức trả lời khi bị hỏi sâu

Đi theo bốn bước, thường gói trong 20–40 giây.

1. **Trả lời trực tiếp.** Ví dụ “Dạ, F1 của baseline bằng 0 vì baseline đoán tất cả là lớp âm.”
2. **Dẫn một bằng chứng.** “Trong 614 dự đoán ngoài fold của Pima, có 214 ca dương và baseline bỏ sót cả 214.”
3. **Nêu giới hạn đúng câu hỏi.** “Accuracy vẫn khoảng 65%, nên cần nhìn cả lớp dương lẫn lớp âm.”
4. **Mở đúng bằng chứng nếu được hỏi tiếp.** Mở bảng CV, metric CSV hoặc hàm tương ứng.

Khi chưa biết, nói đúng phần đã xác minh và chỉ ra phép đo cần làm. Chẳng hạn “Em chưa có đối chứng tám đặc trưng trên cùng giao thức nên chưa kết luận được. Nếu tiếp tục, em sẽ chốt phép so trên dữ liệu phát triển và đánh giá bằng dữ liệu độc lập.” Không đặt ra con số hoặc công việc chưa thực hiện.

### Bảng số liệu cần nhớ

| Đại lượng | Cleveland | Pima |
|---|---:|---:|
| Tổng mẫu → train / holdout | 303 → 242 / 61 | 768 → 614 / 154 |
| Mô hình được chọn qua CV | Gaussian Naive Bayes | KNN, k = 7 |
| F1 CV → F1 holdout, chỉ ML | 0,587 → 0,500 | 0,666 → 0,495 |
| ML → gộp mới, F1 holdout | 0,500 → 0,613 | 0,495 → 0,640 |
| ML → gộp mới, FN | 14 → 9 | 30 → 14 |
| ML → gộp mới, FP | 14 → 15 | 19 → 31 |
| Holdout có luật đích khớp | 27/61 | 50/154 |

Các số là **một lần chia** với seed 42. Không cần thuộc hết mọi chữ số thập phân, nhưng phải biết mỗi số ở tập nào, mẫu số là bao nhiêu và nó trả lời câu hỏi nào. [Kết quả CV](../tasks/T06_TRAINING.md) · [Kết quả holdout](../tasks/T10_HOLDOUT.md) · [Chi tiết FP/FN](../tasks/T12_ERROR_ANALYSIS.md)

## 2. Những câu hỏi có thể bị hỏi liên tiếp

### Tình huống A · “Đồ án của em thật sự làm gì?”

**1. “Người dùng là ai và em giải quyết vấn đề gì?”**

“Đồ án phục vụ người học và người trình bày muốn quan sát một dự đoán được hình thành như thế nào. Người dùng chọn một trong bốn nhóm dữ liệu, nhập các chỉ số, rồi xem điểm ML, luật nào khớp và điểm sau gộp. Phần thực nghiệm kiểm tra trên dữ liệu có nhãn xem việc thêm luật thay đổi kết quả ra sao.”

**Hỏi tiếp — “Em chứng minh giá trị đó thế nào?”** Chạy ca 5 để giải thích cơ chế, sau đó đưa bảng Pima trên 154 ca holdout. Ca tự tạo giúp minh họa cách hệ thống hoạt động. Bảng holdout giúp đo số ca đúng và sai.

**2. “Em gọi là hệ chuyên gia nhưng chỉ có vài luật?”**

“Phần hệ chuyên gia gồm các fact và luật được biểu diễn tường minh, rồi có bộ kiểm tra điều kiện và tạo trace. Luật đích hiện có một luật cho Cleveland và hai luật Pima. Hệ còn có một luật phụ Cleveland. Đây là bộ luật nhỏ để học và đối chứng, chưa phải một cơ sở tri thức lâm sàng toàn diện.”

**Hỏi tiếp — “Đây có phải suy diễn tiến nhiều tầng?”** “Hệ duyệt các luật dựa trên fact từ đầu vào. Kết luận của luật chưa trở thành tiền đề của vòng luật kế tiếp.” [Luật đang chạy](../../medical_expert/expert/rules.py) · [Điểm và trace](../../medical_expert/expert/fusion.py)

**3. “Bốn bệnh đều có hệ chuyên gia à?”**

“Bốn bộ đều có mô hình ML. Cleveland và Pima có luật đích tham gia gộp. Với ILPD và CKD, hiện chưa có luật đích nên kết quả dùng điểm ML và trace vẫn hiện các chỉ số gốc.” Với ILPD, đơn vị hai chỉ số chưa được xác minh trong hồ sơ nguồn. Với CKD, loại huyết áp và dữ kiện thời gian cần cho bài toán thận mạn chưa đủ rõ trong schema hiện tại. [Hồ sơ luật](../tasks/T07_RULES.md)

**4. “Em đóng góp gì? Có dùng AI không?”**

Bạn tự chuẩn bị một câu theo đúng thực tế, theo mẫu “Phần em trực tiếp làm là …, em kiểm chứng bằng …, điểm em có thể mở code giải thích là …”. Nếu có dùng công cụ AI, mô tả trung thực cách dùng và phần mình đã kiểm tra. Thực hành mở fit, predict_proba, evaluate_rules hoặc make_trace và giải thích được một ví dụ cụ thể. [Mô hình NumPy](../../medical_expert/ml/algorithms.py) · [Luật](../../medical_expert/expert/rules.py) · [Gộp](../../medical_expert/expert/fusion.py)

### Tình huống B · “Dữ liệu này có đáng tin và dùng đúng không?”

**5. “Nhãn dương trong bốn nhóm có cùng nghĩa không?”**

Không. Với Cleveland, mã nguồn num từ 1–4 được gộp thành lớp 1, mã 0 thành lớp 0. Pima dùng tested_positive và tested_negative trong bản OpenML. ILPD ánh xạ Selector 1 thành dương và 2 thành âm. CKD ánh xạ ckd thành dương. Mỗi điểm phải được đọc theo nhãn của bộ tương ứng. [Đặc tả nhãn](../SPEC.md)

**Hỏi tiếp về Pima.** Bài báo nguồn mô tả bài toán dự báo khởi phát trong quần thể nghiên cứu. Báo cáo của đồ án gọi tên nhãn của bản OpenML, nêu quần thể nguồn và tránh diễn giải điểm thành chẩn đoán hiện tại hoặc tiên lượng cá nhân. [Hồ sơ Pima](../tasks/T03_DATA_SOURCES.md) · [Bài báo Smith và cộng sự](https://pmc.ncbi.nlm.nih.gov/articles/PMC2245318/)

**6. “Vì sao chỉ chọn ba đặc trưng, có chứng minh chúng tối ưu không?”**

“Ba biến được chọn theo schema form và phạm vi đồ án để theo được toàn bộ luồng. Tất cả ứng viên của cùng bộ dùng cùng ba biến. Em chưa chạy đối chứng để kết luận đây là tập biến tối ưu. Thêm biến có thể thay đổi kết quả, nhưng cần thí nghiệm mới để biết mức thay đổi.”

**7. “Xóa dòng trùng thì có xóa nhầm hai người giống nhau?”**

“Loader đối chiếu toàn bộ bản ghi nguồn sau chuẩn hóa, gồm nhãn. Nó không gộp những dòng chỉ trùng ba biến đã chọn. ILPD có 583 dòng nguồn, loại 13 dòng trùng toàn bộ còn 570. Tuy vậy, dữ liệu thiếu ID bệnh nhân nên không thể chứng minh mọi dòng giống nhau hoặc khác nhau tương ứng với cùng một người.” [Hồ sơ ILPD](../tasks/T05_DATA_SOURCES.md)

**8. “Không có mã bệnh nhân thì có chắc train và test không trùng người?”**

“Em kiểm tra không trùng ID bản ghi giữa các phần. Nguồn không cung cấp mã người bệnh nên chưa thể bảo đảm hai bản ghi cùng người nằm chung một phía. Đây là giới hạn của dữ liệu và ảnh hưởng đến cách diễn giải tính độc lập.”

**9. “Pima glucose = 0 nghĩa là gì? Glucose được đo lúc đói à?”**

“Trong file nguồn, đồ án xem glucose hoặc BMI bằng 0 là giá trị thiếu theo quy ước đã ghi. Còn số lần mang thai bằng 0 là hợp lệ. Trường glucose được mô tả là glucose huyết tương sau hai giờ OGTT. Đơn vị riêng của cột trong bản dùng cho đồ án chưa được xác minh.” [Hồ sơ Pima](../tasks/T03_DATA_SOURCES.md)

**10. “Tại sao dữ liệu đã công khai mà không gửi nguyên file Pima cho người khác?”**

“OpenML hiển thị nhãn Public, nhưng hồ sơ dự án chưa xác minh được quyền phân phối lại bản gốc. Em có thể chỉ nguồn, phiên bản và cách đối chiếu file. Khi nộp hay chia sẻ, cần đối chiếu điều khoản dữ liệu trước.” Artifact KNN có ma trận train đã biến đổi, nên vẫn cần xem xét quyền sử dụng và chia sẻ artifact. [Hồ sơ nguồn và điều khoản](../tasks/T03_DATA_SOURCES.md) · [Hướng dẫn artifact](../tasks/T06_TRAINING.md)

### Tình huống C · “Chia dữ liệu có bị rò rỉ không?”

**11. “Hãy kể lại đầy đủ từ raw đến test.”**

“Em kiểm tra schema, nhãn, missing và trùng. Sau đó chia phân tầng khoảng 80/20 bằng seed 42 và lưu ID. Trong 80% train, em chạy năm fold. Mỗi lượt học median, mean, độ lệch chuẩn và mô hình từ bốn fold, rồi chấm fold còn lại. Em chọn mô hình theo F1 dương trung bình, fit lại trên toàn bộ train, khóa cấu hình và đánh giá holdout.”

**Hỏi tiếp — “Seed 42 chứng minh mô hình tốt chứ?”** “Seed giúp tái tạo đúng phép chia. Chất lượng vẫn phải xem trên metric và dữ liệu khác. Một seed chưa nói hết biến động.” [Chia và tiền xử lý](../tasks/T04_DATA_PIPELINE.md) · [Khóa T10](../../manifests/t10_lock.json)

**12. “Tính median trước khi chia thì hại gì?”**

“Khi đó median dùng cả phân bố của phần đem chấm. Mô hình đã nhận thông tin từ phần đánh giá qua bước tiền xử lý. Trong pipeline này, median và scaler được học riêng từ phần train của mỗi fold.” [Mã tiền xử lý](../../medical_expert/data/pipeline.py)

**13. “Kết quả ngoài fold T09 có phải kiểm định độc lập hoàn toàn không?”**

“Mỗi điểm ngoài fold đến từ mô hình của lượt chưa học chính mẫu đó. Tuy nhiên, thuật toán được chọn bằng F1 trên chính năm fold này. Vì vậy bảng T09 phục vụ đối chứng trong giai đoạn phát triển và có thể chịu thiên lệch do chọn mô hình. Holdout T10 được giữ riêng và cấu hình đã khóa trước khi chạy.” [Chọn mô hình](../../scripts/train.py) · [Cách lấy điểm T09](../../scripts/validate_ablation.py)

**14. “Sao không chọn mô hình tốt nhất ngay trên test? Đổi seed có được không?”**

“Chọn theo test sẽ làm tập test tham gia quá trình chọn mô hình và kết quả trên chính tập đó trở nên lạc quan. Đợt T10 đã khóa dùng seed 42. Nếu thay đặc trưng, luật, ngưỡng hay cách chọn sau khi đã xem test, em phải mô tả kết quả cũ là của giao thức cũ và lập giao thức đánh giá mới với dữ liệu xác nhận độc lập.”

**15. “Các con số CV trên giao diện có phải điểm test không?”**

“Không. Giao diện lấy thống kê từ artifact T06 và ghi rõ 5-fold CV. Ví dụ KNN Pima có F1 CV khoảng 0,666. Sau khi khóa, F1 trên 154 ca holdout là khoảng 0,495.” F1 CV là trung bình F1 của các fold. Các ô TP, TN, FP, FN tổng hợp trong CSV là tổng số đếm từ các fold ngoài mẫu. Hai phép tổng hợp này có thể cho số hơi khác nếu tự tính F1 từ tổng ô. [Huấn luyện T06](../tasks/T06_TRAINING.md)

### Tình huống D · “Em hiểu mô hình tự viết đến đâu?”

**16. “KNN trong ca 5 ra 14,3% bằng cách nào?”**

“Em biến đổi ba đặc trưng bằng thống kê train, tính khoảng cách Euclid tới các mẫu train đã biến đổi, lấy 7 láng giềng gần nhất. Có 1 láng giềng mang nhãn dương nên điểm là 1/7 ≈ 0,143.”

**Hỏi tiếp — “Sao phải chuẩn hóa?”** “Các biến có thang đo khác nhau. Nếu dùng khoảng cách trên số gốc, biến có độ lớn lớn hơn có thể chi phối khoảng cách. Thống kê chuẩn hóa được học từ train.” Giá trị k = 7 là cấu hình đã khóa, chưa có bằng chứng nó là k tối ưu. [KNN](../../medical_expert/ml/algorithms.py) · [Cấu hình](../../medical_expert/ml/runtime.py)

**17. “Logistic Regression thực sự học cái gì?”**

“Hàm sigmoid biến tổ hợp tuyến tính của đầu vào thành điểm trong khoảng 0–1. Code khởi tạo trọng số, tính sai số p − y, cập nhật trọng số bằng gradient descent trong 300 vòng với learning rate 0,1. Hệ số dương làm log-odds tăng khi đặc trưng chuẩn hóa tăng, giữ các biến khác cố định.”

**Hỏi tiếp — “Đó có phải tác động nhân quả?”** “Chưa. Hệ số mô tả quan hệ trong mô hình và dữ liệu đã dùng. Đồ án chưa có thiết kế để kết luận nguyên nhân.”

**18. “Naive Bayes giả định gì? Tại sao dùng log?”**

“Code giả định các đặc trưng độc lập có điều kiện theo lớp và mỗi đặc trưng có phân bố Gaussian theo lớp. Nó học prior, trung bình và phương sai từng lớp. Dùng tổng log-mật độ thay cho tích mật độ để giảm rủi ro số rất nhỏ bị làm tròn về 0.”

**19. “Cây quyết định chọn điểm tách ra sao? Có đúng là ID3 nguyên bản không?”**

“Cây thử từng giá trị đặc trưng làm ngưỡng, tính độ giảm entropy rồi chọn mức giảm lớn nhất. Code tạo hai nhánh theo ngưỡng số, sâu tối đa 4, và cần ít nhất 5 mẫu ở nút để xét tách. Tên giao diện có chữ ID3 vì dùng entropy và information gain. Cách chia nhị phân cho biến số là phần triển khai cụ thể của đồ án.”

Nếu hỏi về nhãn ở lá hòa, trace cây trích xuất ghi lớp 0 theo argmax, trong khi dự đoán từ tỷ lệ dương 0,5 qua ngưỡng ≥ 0,5 cho lớp 1. Phần giải thích cây có nêu quy ước này. [Triển khai cây](../../medical_expert/ml/algorithms.py) · [Review](../REVIEW.md)

**20. “Ensemble voting là bầu theo nhãn hay theo điểm?”**

“Bốn mô hình đều được fit. Hệ lấy trung bình cộng bốn điểm lớp dương rồi áp ngưỡng 0,5. Đó là soft voting. Em so ensemble cùng bốn mô hình đơn trên cùng các fold.”

### Tình huống E · “Luật, fuzzy và phép gộp có hợp lý không?”

**21. “Nguồn nào nói tuổi 35–70 và BMI trên 25 đồng nghĩa với mắc bệnh?”**

“Khuyến nghị nguồn dùng tuổi và tình trạng thừa cân để xác định nhóm cần xem xét sàng lọc. Đồ án dùng các điều kiện đó làm luật hỗ trợ để đối chứng với nhãn Pima. Đó là một ánh xạ do đồ án thiết kế, chưa được xác nhận là quy tắc chẩn đoán. Hai CF 0,50 và 0,55 do nhóm đặt cho thí nghiệm.” [Bảng nguồn và CF](../tasks/T07_RULES.md) · [Khuyến nghị USPSTF](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/screening-for-prediabetes-and-type-2-diabetes)

**22. “CF 0,5 là xác suất bác sĩ khẳng định mắc bệnh 50% à?”**

“CF là hệ số hỗ trợ do nhóm đặt trong bộ luật. Dự án chưa có bằng chứng cho thấy CF này đã được chuyên gia lâm sàng ước lượng hoặc kiểm định thành xác suất. Điểm ML và điểm gộp cũng chưa được hiệu chỉnh để diễn giải thành xác suất mắc bệnh cá nhân.”

**23. “Tại BMI 26, vì sao μ = 0,75 mà CF chỉ 0,50?”**

“μ = (26 − 23)/(27 − 23) = 0,75 mô tả mức thuộc của fact BMI cao. Vì μ > 0,5, fact được xem là đúng. Khi toàn bộ điều kiện khớp, bản chạy này dùng CF cố định 0,50 của luật. Nó không nhân 0,75 với CF.” [Fact và luật Pima](../../medical_expert/expert/rules.py)

**24. “Đã dùng fuzzy mà tại sao nhảy đột ngột qua một ngưỡng?”**

“Đồ án tính mức liên thuộc liên tục rồi chuyển thành fact đúng khi μ > 0,5. Luật hoạt động theo fact đúng/sai, nên kết quả có thể thay đổi đột ngột ở biên. Với cholesterol 200, μ = 0,5 và fact chưa đúng. Tại 201, μ = 0,525 và fact đúng. Bản thử này chưa triển khai fuzzy liên tục ở mức kích hoạt luật.” [Quy tắc](../tasks/T07_RULES.md)

**25. “Hai luật BMI lồng nhau sao lại cộng cả hai? Các bằng chứng có độc lập không?”**

“Hai luật cùng dùng tuổi và BMI > 30 cũng thỏa BMI > 25. Vì vậy chúng phụ thuộc nhau, nhưng công thức vẫn tích lũy cả hai CF. Đây là điểm yếu cần nêu khi diễn giải điểm. Việc đưa điểm ML vào công thức mới một lần giải quyết việc lặp riêng điểm ML trong công thức cũ. Nó chưa chứng minh các nguồn thông tin trong mô hình và luật độc lập.”

**26. “Công thức của em có phải công thức Bayes không?”**

“Đó là quy tắc tích lũy điểm hỗ trợ được chọn cho đối chứng của đồ án. Em chưa có cơ sở để gọi kết quả là xác suất hậu nghiệm Bayes. Cả ML lẫn luật có thể dùng thông tin đầu vào chung, và các CF được đặt thủ công.” [Phép gộp thực thi](../../medical_expert/expert/fusion.py)

**27. “Cho hai luật, hãy tính công thức mới và cũ ngay.”**

Ca 4 có p = 5/7, c₁ = 0,50 và c₂ = 0,55.

- Gộp luật trước, R = 1 − (1 − 0,50)(1 − 0,55) = 0,775.
- Mới, S = R + p(1 − R) = 0,775 + (5/7) × 0,225 ≈ 0,9357.
- Cũ, tính cᵢ + p(1 − cᵢ) cho từng luật rồi gộp hai điểm ấy. Kết quả khoảng 0,9816.
- Một luật cho cùng điểm ở hai cách. Khi nhiều luật khớp, cách cũ đưa cùng điểm ML vào qua từng luật. Hai điểm trong ví dụ đều vượt ngưỡng 0,5.

**28. “Nếu ML bằng 0 mà luật khớp, sao hệ vẫn cho dương?”**

“Với PIMA_TARGET_01, CF = 0,50 nên 0,50 + 0 × (1 − 0,50) = 0,50. Quy tắc nhãn là điểm ≥ 0,5 thì dương. Do đó luật đã đủ quyết định nhãn trong ca này. Với bộ luật đích dương hiện tại, gộp mới chỉ giữ hoặc tăng điểm so với ML, vì S − p = R(1 − p) ≥ 0.”

**29. “Thiếu dữ kiện thì sao? Nếu cả ba trường trống?”**

“ML điền median học từ train để có đầu vào. Nhánh luật giữ fact thiếu ở trạng thái chưa biết. Khi cả ba trường trống, ML đang dựa trên vector median, chứ không có thông tin đo riêng của ca đó. Điểm này cần được hiểu cùng tình trạng thiếu trên giao diện.”

### Tình huống F · “Đọc kết quả như thế nào cho chặt?”

**30. “Baseline Cleveland và Pima hiện 0 ± 0, có lỗi không?”**

“Baseline chọn lớp phổ biến trong train của từng fold. Ở cả năm fold Cleveland và Pima, lớp phổ biến là lớp 0, nên baseline đoán âm cho tất cả. F1 lớp dương bằng 0 trên mỗi fold, dẫn tới trung bình 0 và độ lệch chuẩn 0. Với Pima, 214 ca dương ngoài fold đều bị bỏ sót, còn 400 ca âm được đoán đúng.”

**Hỏi tiếp — “Thế precision?”** TP/(TP + FP) có mẫu số bằng 0 vì baseline không dự đoán ca nào là dương. Metric này được để trống và giao diện hiển thị dấu gạch. F1 được tính trực tiếp bằng 2TP/(2TP + FP + FN), có mẫu số dương ở đây nên bằng 0. Accuracy CV trung bình vẫn khoảng 65,15% ở Pima. [Metric CV](../../results/t06-cv-seed42/metrics.csv) · [Cách tính](../../medical_expert/ml/metrics.py)

**31. “Hệ kết hợp tốt hơn ML được bao nhiêu?”**

“Trên toàn bộ 154 ca Pima holdout, F1 tăng từ khoảng 0,495 lên 0,640. FN giảm từ 30 xuống 14, trong khi FP tăng từ 19 lên 31. Tức là hệ tìm thêm 16 ca dương và báo dương nhầm thêm 12 ca âm trên lần chia này. Sự đánh đổi có phù hợp hay không còn phụ thuộc mục đích sử dụng và chi phí các loại sai.”

**32. “Recall của luật là 100%, nghĩa là luật phát hiện hết bệnh?”**

“Recall 100% trong bảng chỉ luật được tính trên 50 ca Pima có luật đích khớp, trong đó có 32 dương. Luật gọi dương cả 50, nên tìm đủ 32 ca dương và đồng thời báo dương sai cả 18 ca âm. 104 ca còn lại không có điểm chỉ luật. Coverage là 50/154.” Khi so ML, luật và gộp trong vùng này, cần dùng cùng 50 ca. [Phân tích theo coverage](../tasks/T12_ERROR_ANALYSIS.md)

**33. “Em nói luật đổi nhiều nhãn, sao lại báo đổi nhãn bằng 0?”**

“Em đang nói về hai phép so khác nhau. So ML với gộp mới cho thấy thêm luật đã thay đổi nhãn. So gộp cũ với gộp mới thì có 38/154 điểm Pima khác nhau, còn số nhãn khác nhau bằng 0. Các luật đích đang có CF ít nhất 0,5, nên khi khớp, cả hai cách đã đạt ngưỡng dương.”

**34. “Vì sao AUC Pima 0,748 mà F1 chỉ 0,495?”**

“AUC đo khả năng xếp điểm của một ca dương cao hơn một ca âm, xét trên các ngưỡng. F1 ở đây đo kết quả sau khi cắt cố định tại 0,5. Hai chỉ số trả lời hai câu hỏi khác nhau.” Trên holdout Pima, KNN tìm đúng 24/54 ca dương và báo dương nhầm 19 ca âm.

**35. “Mô hình gan F1 0,834 là tốt rồi, vì sao nói có vấn đề?”**

“ILPD holdout có 81 dương và 33 âm. Nếu đoán dương tất cả thì F1 dương đã là 0,831. Logistic đạt 0,834 nhưng chỉ đoán đúng 5 trong 33 ca âm. F1 dương một mình che bớt khả năng nhận diện lớp âm.” Baseline là mốc đối chứng theo thiết kế chọn mô hình, nên Logistic vẫn được chọn từ năm ứng viên dù baseline có F1 CV cao hơn. [Bảng ML và baseline](../tasks/T10_HOLDOUT.md) · [Ma trận nhầm lẫn](../REVIEW.md)

**36. “Thêm luật làm F1 tăng. Vậy đã chứng minh luật hiệu quả chưa?”**

“Ta quan sát được F1 tăng trên holdout của giao thức này cùng sự thay đổi FP và FN. Dữ liệu nhỏ và chỉ một lần chia nên em chưa kết luận lợi ích chắc chắn trên quần thể khác hoặc có ý nghĩa thống kê. Em cần một đánh giá độc lập theo giao thức mới để kiểm tra độ ổn định.”

**37. “Cleveland AUC gần 0,5. Mô hình sai do chỉ dùng ba biến đúng không?”**

“Em quan sát AUC 0,534 trên 61 ca holdout, nghĩa là khả năng xếp hạng hạn chế trên lần chia này. Số mẫu nhỏ và ba biến là những giới hạn có thể liên quan. Chưa có đối chứng để quy nguyên nhân cho riêng một yếu tố.”

## 3. Các tình huống demo thực tế

Các thao tác dưới đây đã được kiểm tra trên giao diện ngày 22/11/2026. Chọn **Suy luận → Đổi ca → Ca 5 · ML bất đồng luật**. Hệ thống tự chạy và hiện điểm ML, luật và kết hợp trên biểu đồ. Mở **Vì sao điểm tăng?** để xem lời giải thích, rồi mở **Chi tiết kỹ thuật** để chỉ công thức, fact và ID luật.

| Tình huống | Cách xử lý ngay tại buổi bảo vệ |
|---|---|
| Giảng viên yêu cầu “em tự tính ca này” | Ca 5 có KNN 1/7, luật 0,50, gộp 0,5714. Chỉ điều kiện tuổi và μ BMI = 0,75 trong chi tiết kỹ thuật. |
| Hỏi “có hai luật thì sao?” | Chọn **Đổi ca → Ca 4 · 2 luật đích**. Tính R = 0,775, p = 5/7, gộp mới ≈ 0,9357. Thừa nhận hai điều kiện BMI lồng nhau. |
| Hỏi “thiếu chỉ số thì xử lý sao?” | Chọn **Ca 2 · Thiếu cholesterol**. Nói ML dùng median train và fact cholesterol là chưa biết. Nếu thay đổi ô bằng tay, bấm chạy lại. |
| Hỏi “nhập sai thì sao?” | Chọn **Ca 6 · Ngoài miền nhập**. Cholesterol 900 vượt miền form 150–400, backend trả 400. Kiểm tra lỗi hiện dưới ô và giải thích request lỗi dừng trước khi lưu lịch sử. |
| Hỏi “sao lịch sử khác kết quả vừa thấy?” | Lịch sử hiện điểm riêng của ML. Ca 5 có ML 14,3% và điểm gộp 57,1%. |
| Hỏi “sao cây hiển thị mà Pima lại dùng KNN?” | Cây ở trang so sánh là một ứng viên đã huấn luyện. Mô hình đang chạy cho Pima là KNN được chọn theo F1 CV. |
| CKD không cho nhập huyết áp 80 | Miền form hiện là 90–200, còn median train được báo cáo là 80. Đây là hạn chế của form. Đánh giá T10 dùng loader dữ liệu trực tiếp. |
| Ứng dụng báo chưa có mô hình | Kiểm tra thư mục artifact và MEDICAL_MODEL_RUN, sau đó khởi động lại. Nếu không kịp, mở ảnh ca mẫu và bảng kết quả đã chuẩn bị, nói rõ đó là kết quả lưu trước. |
| Không nhớ một công thức hoặc một con số | Mở mục tương ứng trong sổ tay hoặc code, nói phần mình chắc chắn. Có thể trình bày cách kiểm tra ngay tại chỗ. |

Đã kiểm tra giao diện ca 5 trên trình duyệt với server cục bộ, artifact T06 và SQLite tạm. Các ảnh trong tài liệu T13 được chụp ở lần demo trước và có thể khác bố cục giao diện hiện tại. [Sáu ca và ảnh](../tasks/T13_DEMO.md) · [Hạn chế CKD](../REVIEW.md) · [Cấu hình form](../../medical_expert/web/diseases.py)

## 4. Bản đồ mở bằng chứng trong 10 giây

| Giảng viên muốn xem | Mở file | Từ khóa để tìm |
|---|---|---|
| API nhận dữ liệu và validate | [medical_expert/web/app.py](../../medical_expert/web/app.py) | diagnose, validate_diagnosis_fields |
| Tách fold và học median/scaler | [medical_expert/data/pipeline.py](../../medical_expert/data/pipeline.py) | make_manifest, fit_preprocessor, prepare_fold |
| KNN, Logistic, NB, cây, ensemble | [medical_expert/ml/algorithms.py](../../medical_expert/ml/algorithms.py) | Tên class, fit, predict_proba |
| Chọn mô hình và tổng hợp CV | [scripts/train.py](../../scripts/train.py) | train_dataset, selected |
| Fact và luật thực sự chạy | [medical_expert/expert/rules.py](../../medical_expert/expert/rules.py) | FACTS, RULES, evaluate_rules |
| Cách gộp và trace | [medical_expert/expert/fusion.py](../../medical_expert/expert/fusion.py) | fusion_scores, make_trace |
| Khóa trước test | [t10_lock.json](../../manifests/t10_lock.json) | selected, threshold, method_sha256 |
| Số liệu holdout | [T10_HOLDOUT.md](../tasks/T10_HOLDOUT.md), [metrics.csv](../../results/t10-test-seed42/metrics.csv) | Tên bộ, f1, tn, fp, fn, tp |
| Đổi đúng và đổi sai | [T12_ERROR_ANALYSIS.md](../tasks/T12_ERROR_ANALYSIS.md) | Pima, FP, FN |

Trong đợt chuẩn bị này, 17 file phương pháp được liệt kê trong khóa T10 và artifact models.json hiện có đều khớp SHA-256 đã khóa. Đối chiếu hash cho biết nội dung hiện tại khớp bản ghi khóa, còn kết luận về kết quả cần đọc cùng giao thức và số liệu. [Khóa T10](../../manifests/t10_lock.json)

## 5. Kế hoạch tự luyện trước buổi bảo vệ

Nếu có khoảng hai giờ, thực hiện theo thứ tự sau. Nếu ít thời gian hơn, hoàn thành ba việc đầu và tập phần bạn yếu nhất.

| Thời lượng | Việc luyện | Dấu hiệu đã làm được |
|---|---|---|
| 20 phút | Tự vẽ luồng từ dữ liệu đến holdout, rồi từ form đến trace. | Không nhìn tài liệu vẫn giải thích được fold, median train, mô hình, luật, gộp và SQLite. |
| 20 phút | Chạy ca 5 và tính tay. | Tự nói được 1/7, μ = 0,75, CF = 0,50 và kết quả 0,5714. |
| 20 phút | Tập ba câu số liệu khó. | Giải thích được baseline 0 ± 0, Pima thêm 16 TP và 12 FP, ILPD đúng 5/33 ca âm. |
| 20 phút | Mở bốn điểm code theo bản đồ. | Tìm được KNN, tiền xử lý, RULES và fusion trong mỗi file, giải thích được đầu vào và đầu ra. |
| 20 phút | Nhờ một người hỏi ngược 8 câu bên dưới, hoặc tự ghi âm. | Mỗi câu có trả lời trực tiếp, một bằng chứng và giới hạn khi cần. |
| 20 phút | Tổng duyệt có bấm giờ, thử ca thiếu, ca ngoài miền và phương án ảnh dự phòng. | Chạy được trong thời gian được giao, chuyển cửa sổ gọn và xử lý được câu hỏi chen ngang. |

**Tám câu tự kiểm tra**

1. Vì sao F1 baseline Pima là 0 ± 0 mà accuracy khoảng 65%?
2. Ca 5 có đầu vào gì và vì sao ra 14,3%, 50%, 57,1%?
3. Vì sao thiếu cholesterol mà ML còn chạy, và luật xử lý fact đó ra sao?
4. Phần nào của pipeline được fit riêng trong từng fold? T09 có độc lập hoàn toàn với bước chọn mô hình không?
5. Luật giúp thêm bao nhiêu ca dương và tạo thêm bao nhiêu ca dương giả trên Pima holdout?
6. Vì sao so gộp cũ–mới lại có 0 ca đổi nhãn?
7. ILPD có F1 0,834 nhưng nhận diện lớp âm thế nào?
8. Nếu giảng viên yêu cầu khẳng định ứng dụng dùng được cho bệnh nhân thực, bạn sẽ nêu các bằng chứng còn thiếu nào?

Tập lần lượt câu trả lời 20 giây, rồi câu trả lời 60 giây có mở bằng chứng. Với câu 4, 5 và 6, hãy giải thích cả mẫu số và tập dữ liệu đang nói tới.

[Sổ tay tính toán và kịch bản gốc](GHI_CHU_BAO_VE.md) · [Đặc tả dự án](../SPEC.md) · [Trạng thái và giới hạn](../STATUS.md)
