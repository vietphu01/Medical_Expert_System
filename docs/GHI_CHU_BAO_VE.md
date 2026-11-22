# Sổ tay bảo vệ · Medical Expert System

**Nếu chỉ còn 5 phút để ôn**, hãy đọc [ca 5 tính tay](#ca5), [hai bảng kết quả](#ketqua) và [kịch bản cầm máy](#demo). Khi thầy cô hỏi sâu, đi theo thứ tự **đầu vào nào → đoạn nào xử lý → con số nào chứng minh → kết luận được đến đâu**.

<a id="ca5"></a>

## 1. Một ca để nhớ cả đồ án

**Câu mở đầu có thể nói nguyên văn**

> “Em muốn trả lời một câu hỏi cụ thể. Nếu một mô hình học từ dữ liệu cho điểm thấp, nhưng một luật viết rõ ràng lại khớp, hệ thống sẽ kết luận thế nào? Em xin chạy một ca để thấy hai nguồn điểm, rồi dùng kết quả trên dữ liệu có nhãn để xem việc thêm luật giúp ở đâu và sai thêm ở đâu.”

Trong **Suy luận**, bấm **05 · ML ≠ Luật**. Đây là ca tự tạo trên form Pima với tuổi 45, BMI 26 và glucose hai giờ OGTT bằng 90. Hãy chỉ vào từng dòng khi nói.

| Câu hỏi trước màn hình | Cách trả lời bằng chính ca đang mở |
|---|---|
| **14,3% từ đâu ra?** | KNN so ba chỉ số đã chuẩn hóa với dữ liệu train. Trong 7 láng giềng gần nhất, 1 mẫu có nhãn dương. Điểm ML là 1/7, dưới ngưỡng 0,5. |
| **Máy biết luật nào khớp bằng cách nào?** | Tuổi 45 nằm trong khoảng 35–70. BMI 26 nằm trên đoạn 23–27, mức liên thuộc là (26−23)/(27−23) = 0,75. Giá trị này vượt 0,5 nên fact BMI cao là đúng. Hai tiền đề đủ cho PIMA_TARGET_01. Mốc BMI của luật thứ hai chưa đạt. |
| **Sao luật cho 50% trong khi vừa nói 75%?** | 0,75 mô tả mức thuộc của **một chỉ số**. Khi các tiền đề đã đúng, luật dùng **CF 0,50** do nhóm đặt. Bản chạy này dùng fuzzy để quyết định bật luật, rồi lấy nguyên CF. |
| **57,1% tính thế nào?** | Luật đã cho 0,50. Phần còn lại tới 1 là 0,50. ML đóng góp (1/7) × 0,50. Điểm cuối là 0,50 + 0,0714 = **0,5714**. Quy ước điểm ≥ 0,5 cho nhãn 1. |
| **Vậy hệ thống đã sửa đúng một ca bệnh?** | “Ca này do em tạo để kiểm tra hành vi nên chưa có nhãn thật. Em chứng minh được luật đổi quyết định. Muốn đếm đổi đúng hay đổi sai, em cần so với nhãn trên holdout.” |

Trên màn hình, **14,3%** là điểm cho một ca, **F1** là metric trên nhiều ca có nhãn, và **57,1%** là điểm hỗ trợ sau gộp. Muốn hiểu 57,1% như tần suất mắc bệnh còn cần dữ liệu kiểm định và hiệu chỉnh xác suất. [Mã KNN](../math_ml_from_scratch.py) · [Luật Pima](../research_rules.py) · [Phép gộp](../fusion.py)

## 2. Core dự án và đường đi của một yêu cầu

**“Đồ án của em giải quyết bài toán gì, ai dùng?”** — “Người trình bày và người học có thể nhập một ca, xem mô hình và luật đã dùng bằng chứng nào, rồi đối chiếu hành vi đó với số liệu thực nghiệm. Người dùng chọn nhóm bệnh trước. Mỗi nhóm có một bài toán nhị phân riêng với nhãn 0/1 của chính bộ dữ liệu ấy.” Phạm vi ứng dụng hiện tại là giảng dạy và thực nghiệm tại máy cục bộ.

**“Em đã làm gì ở phần lõi?”** — Có ba phần có thể mở và chứng minh ngay. Một là pipeline biến dữ liệu nguồn thành các lần huấn luyện so sánh được. Hai là các thuật toán ML bằng NumPy và cơ chế đối chiếu luật, gộp điểm. Ba là thí nghiệm tách từng thành phần và màn hình cho phép theo từng bước của một ca. Flask nhận yêu cầu, trả JSON và phục vụ giao diện. SQLite lưu lịch sử lượt chạy.

| Lúc nào | Đường đi thực tế | Mở đâu nếu được yêu cầu chỉ code |
|---|---|---|
| Trước buổi demo | File dữ liệu → loader ánh xạ nhãn/đặc trưng → chia ID → fit tiền xử lý và mô hình → ghi trạng thái vào models.json. | [Loader](../dataset_loaders.py) · [Chia và tiền xử lý](../data_pipeline.py) · [Huấn luyện](../scripts/train.py) |
| Khi khởi động Flask | Đọc artifact, khôi phục bộ tiền xử lý, thứ tự đặc trưng và mô hình đã chọn cho từng bộ. Khởi tạo bảng lịch sử nếu cần. | [load_run và RuntimeModel](../model_runtime.py) · [Khởi tạo ứng dụng](../app.py) |
| Khi bấm chạy | Form gửi POST /api/diagnose. Backend kiểm tra nhóm, khóa, kiểu và miền. Nhánh ML điền thiếu, chuẩn hóa và cho điểm. Song song về mặt logic, nhánh luật đọc số gốc và xác định điều kiện đúng. | [diagnose](../app.py) · [evaluate_rules](../research_rules.py) |
| Khi hiện kết quả | make_trace lọc luật cùng đích, gộp điểm và chốt nhãn. Flask lưu lượt hợp lệ vào SQLite. Giao diện hiện điểm cùng các bước giải thích. | [make_trace](../fusion.py) · [Giao diện](../static/workspace.js) |

**“File nào mới là cơ sở tri thức?”** — Với đường chạy trên, mở bảng `FACTS` và `RULES` trong `research_rules.py`, rồi chỉ dòng `evaluate_rules(dataset, inputs)` trong `app.py`. Repo còn `knowledge_base.json`, `inference_engine.py` và hàm sinh dữ liệu trong `diseases_config.py` từ phiên bản trước. Có thể kiểm tra import và lời gọi trong Flask hoặc script train để xác định phần đang thực thi. Hệ hiện tại duyệt một lượt các luật có tất cả tiền đề đúng. Kết luận của luật này chưa được dùng làm tiền đề cho luật kế tiếp. [Mã ứng dụng](../app.py) · [Luật chạy thực tế](../research_rules.py) · [Pipeline huấn luyện](../scripts/train.py)

## 3. Dữ liệu, cách chia và cách ngăn rò rỉ

| Bộ và nguồn | Ba đầu vào của mô hình | Lớp 1 nghĩa là gì? | Số mẫu dùng → train / test |
|---|---|---|---:|
| Cleveland · UCI | Tuổi, huyết áp lúc nghỉ, cholesterol toàn phần | Nhãn nguồn num từ 1 đến 4. Giá trị 0 là lớp âm. | 303 → 242 / 61 |
| Pima · OpenML #37 v1 | Glucose huyết tương hai giờ OGTT, BMI, tuổi | Nhãn nguồn tested_positive. Quần thể gồm phụ nữ gốc Pima từ 21 tuổi. | 768 → 614 / 154 |
| ILPD · UCI | Bilirubin toàn phần, albumin, tuổi | Selector = 1 là lớp dương, Selector = 2 là lớp âm. | 570 → 456 / 114 |
| CKD · UCI | Creatinine huyết thanh, huyết áp, tuổi | Nhãn nguồn ckd là lớp dương, notckd là lớp âm. | 400 → 320 / 80 |

**Vì sao mỗi bộ chỉ dùng ba chỉ số?** Đây là schema đã chốt để nhập được trên form, theo được trong trace và so các phương pháp trên cùng đầu vào. Đồ án chưa làm thí nghiệm chọn tập đặc trưng tối ưu. Nếu hỏi “thêm một biến có tăng F1 không?”, câu trả lời cần một thí nghiệm riêng. [Đặc tả](SPEC.md) · [Nguồn Cleveland/Pima](T03_DATA_SOURCES.md) · [Nguồn ILPD/CKD](T05_DATA_SOURCES.md)

**Một bản ghi đi qua quá trình đánh giá thế nào?**

1. Loader chuẩn hóa ký hiệu thiếu và nhãn, kiểm tra trùng theo cả bản ghi nguồn trước khi chia. ILPD có 583 dòng ban đầu, bỏ 13 dòng trùng còn 570. Hai người có cùng ba chỉ số vẫn có thể là hai bản ghi khác nhau. Cleveland và Pima thiếu mã bệnh nhân để xác nhận độc lập ở cấp người.
2. Tách khoảng 20% làm **holdout**, tức phần để riêng đến đánh giá cuối. Chia phân tầng để giữ tỷ lệ hai lớp gần với dữ liệu gốc. Seed 42 và manifest lưu ID cho phép chạy lại đúng phép chia.
3. Với 80% còn lại, chia 5 fold phân tầng. Mỗi lượt dùng 4 fold để học và 1 fold để chấm, luân phiên đủ 5 lượt. Một điểm **ngoài fold** là điểm cho mẫu mà mô hình của lượt đó chưa học. Các ứng viên dùng cùng ID để so công bằng.
4. Trong mỗi lượt, học median từng cột từ phần học, điền thiếu, rồi học mean và độ lệch chuẩn để tính `z = (x − mean) / std`. Phần chấm dùng lại các thống kê này. Nếu lấy median trên toàn bộ dữ liệu trước khi chia, thông tin phân bố từ phần chấm đã lọt vào bước học. KNN đặc biệt nhạy với thang đo vì dùng khoảng cách.
5. Chọn ứng viên theo **F1 lớp dương trung bình trên 5 fold**. Fit lại bằng toàn bộ phần train. T09 so sánh ML và luật bằng điểm ngoài fold. T10 khóa mô hình, luật, CF, ngưỡng, split và artifact trước khi đo trên holdout. Trang **Mô hình CV** hiển thị số ở bước CV. Bảng holdout nằm trong báo cáo T10. [Pipeline](T04_DATA_PIPELINE.md) · [Chọn mô hình](T06_TRAINING.md) · [Đối chứng validation](T09_VALIDATION.md) · [Khóa T10](t10_lock.json)

**“Bỏ trống cholesterol mà vẫn ra số, máy đã tự tạo bằng chứng à?”** — Nhánh ML cần vector số nên dùng trung vị đã học. Nhánh luật vẫn nhìn cholesterol là chưa biết. Mở ca 02 để thấy ML vẫn ra điểm và luật bỏ ngỏ. Khi cả ba ô trống, kết quả ML chỉ phản ánh vector trung vị. Trên file Pima, 5 glucose bằng 0 và 11 BMI bằng 0 được đọc thành thiếu. Trên form, thao tác tương ứng là để trống để gửi JSON `null`. Backend kiểm tra riêng trường hợp bỏ hẳn khóa, nhập sai kiểu hay vượt miền. [Xử lý dữ liệu](../data_pipeline.py) · [Kiểm tra đầu vào](../app.py)

## 4. Nếu bị yêu cầu giải thích từng thuật toán

| Phương pháp | Nó học hoặc giữ gì? | Nó cho điểm của một ca bằng cách nào? |
|---|---|---|
| Logistic Regression | Học trọng số và bias bằng gradient descent, learning rate 0,1 trong 300 epoch. Hàm mất mát là binary cross-entropy. | Tính tổng có trọng số của ba đầu vào chuẩn hóa rồi đưa qua sigmoid. Hệ số dương làm tăng log-odds khi các biến còn lại cố định. |
| KNN | Lưu ma trận train đã biến đổi và nhãn. Cấu hình chạy dùng k = 7. | Tính khoảng cách Euclid, lấy 7 mẫu gần nhất, đếm tỷ lệ dương. Vì thế điểm có các nấc 0/7, 1/7, …, 7/7. |
| Gaussian Naive Bayes | Học tỷ lệ từng lớp, mean và phương sai của từng đặc trưng theo lớp. Giả định các đặc trưng độc lập khi đã biết lớp, mỗi đặc trưng có phân bố Gaussian theo lớp. | Cộng log-prior và các log-mật độ rồi chuẩn hóa hai lớp. Tính trong không gian log giúp tránh nhân nhiều số rất nhỏ. |
| Decision Tree | Tại mỗi nút, chọn đặc trưng và ngưỡng số làm giảm entropy nhiều nhất. Cấu hình độ sâu tối đa 4, cần ít nhất 5 mẫu ở nút để xét tách. | Đi theo các nhánh đến lá, lấy tỷ lệ mẫu dương ở lá. Ngưỡng trong cây đã qua chuẩn hóa. |
| Ensemble Voting | Fit cả bốn mô hình trên cùng phần train. | Lấy trung bình cộng **điểm** của bốn mô hình rồi áp ngưỡng. Đây là soft voting. |
| Baseline lớp phổ biến | Tìm lớp đông nhất ở phần train của lượt đó. | Cho mọi ca cùng nhãn. Mốc này cho biết chỉ riêng tỷ lệ lớp đã đạt F1 bao nhiêu. |

**“Phần nào tự viết, phần nào dùng thư viện?”** — “Em dùng NumPy để tính toán mảng. Các bước cập nhật trọng số, đo khoảng cách, tính log-mật độ, chọn ngưỡng tách và gộp điểm nằm trong các class của repo. Còn Flask làm web và SQLite lưu lịch sử.” Nếu thầy chọn một thuật toán, mở thẳng `fit` và `predict_proba` của class đó. Các hyperparameter được cố định trong cấu hình thí nghiệm. F1 dùng để chọn giữa các ứng viên. Đồ án chưa chứng minh k = 7 hay độ sâu 4 là tối ưu. [Bốn thuật toán và ensemble](../math_ml_from_scratch.py) · [Cấu hình thực dùng](../model_runtime.py)

**“Cây trên giao diện có giải thích KNN của ca Pima không?”** — Trang CV hiển thị được cây Decision Tree huấn luyện để so sánh trên Pima. Quyết định ML của ca 05 đến từ KNN. Tương tự, biểu đồ hệ số Logistic ở T12 giúp đọc riêng mô hình Logistic. Chẳng hạn hệ số glucose Pima +1,136 nghĩa là tăng một độ lệch chuẩn thì log-odds trong Logistic tăng 1,136 khi giữ BMI và tuổi cố định. Số đó không giải thích nhân quả. [Phân tích mô hình](T12_ERROR_ANALYSIS.md)

## 5. Hệ luật, fuzzy và hai công thức gộp

**Fact** là mệnh đề rút từ chỉ số, có thể đúng, sai hoặc chưa biết. **Luật** liệt kê những fact phải đồng thời đúng. **Luật đích** có kết luận ánh xạ được đến lớp 1 của bộ đang xét. **CF** là mức hỗ trợ cố định của một luật đã khớp. Tài liệu T07 ghi căn cứ tham khảo cho điều kiện. Các CF và một số mốc vận hành do đồ án chọn để làm đối chứng, chưa qua ước lượng lâm sàng. [Bảng nguồn từng luật](T07_RULES.md)

| Luật | Điều kiện thực dùng | CF và tác dụng |
|---|---|---|
| CLEV_TARGET_01 | Tuổi ≥ 55 và cholesterol > 200 mg/dL | 0,55 vào điểm Cleveland |
| CLEV_SECONDARY_01 | Cholesterol > 200 mg/dL | 0,40, giải thích dấu hiệu phụ trong trace |
| PIMA_TARGET_01 | 35 ≤ tuổi ≤ 70 và BMI > 25 | 0,50 vào điểm Pima |
| PIMA_TARGET_02 | 35 ≤ tuổi ≤ 70 và BMI > 30 | 0,55 vào điểm Pima |

**“Fuzzy nằm ở đâu, sao đổi rất ít mà bật cả luật?”** — Với cholesterol, mức liên thuộc μ tăng tuyến tính từ 0 tại 180 đến 1 tại 220 mg/dL, chặn ở hai đầu. Tại 200, μ = 0,50, fact sai vì quy tắc bật là **μ > 0,5**. Tại 201, μ = 0,525, fact đúng. Ở tuổi 60, thay đổi này đủ bật luật đích. Còn quyết định cuối dùng **điểm ≥ 0,5** nên đúng 0,50 đã là lớp 1. Bản hiện tại giữ độ liên thuộc trong trace, sau bước kiểm tra điều kiện dùng CF cố định. T14 dùng fuzzy liên tục là phương án tùy chọn đã bỏ qua trước khi khóa. [Fact và ngưỡng](../research_rules.py) · [Quyết định T14](TASKS.md)

**“Vì sao gan, thận chỉ chạy ML? Sao glucose Pima dùng cho ML mà bỏ ngoài luật?”** — Với gan, nhóm chưa xác minh đơn vị bilirubin và albumin. Với thận, schema ba trường thiếu thông tin diễn biến theo thời gian và loại phép đo huyết áp còn chưa rõ. Nhóm chưa thiết lập luật đích cho hai bộ này. Glucose Pima có định nghĩa phép đo hai giờ OGTT, đơn vị riêng của cột còn chưa xác minh. ML có thể học quan hệ trong cùng bộ số liệu và cùng thang đo. Một luật áp ngưỡng có đơn vị hoặc việc chuyển sang máy đo khác đòi hỏi xác minh thêm. [Hồ sơ luật](T07_RULES.md)

**Tính tay khi nhiều luật cùng khớp.** Gọi p là điểm ML, cᵢ là CF của từng luật đích đã khớp. Chỉ dùng các luật cùng đích.

- **Chỉ luật:** R = 1 − ∏(1 − cᵢ). Ca 04 có hai CF là 0,50 và 0,55. R = 1 − 0,50 × 0,45 = **0,775**.
- **Gộp mới:** S = R + p × (1 − R). Ca 04 có p = 5/7 nên S = 0,775 + (5/7) × 0,225 ≈ **0,9357**. Điểm ML góp một lần.
- **Gộp cũ:** nâng từng CF thành cᵢ + p × (1 − cᵢ), rồi gộp các điểm đã nâng theo công thức tích. Hai luật đưa cùng một p vào hai lần. Với một luật đích, hai cách trùng nhau. Khi thiếu luật đích, nhánh chỉ luật bỏ ngỏ (điểm null), cả hai cách gộp trả p. [Thực thi phép gộp](../fusion.py)

**“Luật có thể kéo điểm ML xuống không? Hai luật BMI có phải hai bằng chứng độc lập?”** — Trong cấu hình hiện tại toàn luật dương, S − p = R × (1 − p) ≥ 0. Luật chỉ có thể giữ hoặc tăng điểm, điều này giải thích hướng thay đổi FP/FN ở bảng dưới. BMI > 30 cũng thỏa BMI > 25, cả hai luật dùng chung tuổi. Gộp mới xử lý việc lặp **điểm ML**. Việc đếm hai điều kiện BMI lồng nhau vẫn là hạn chế của bộ luật. [Đối chứng](T09_VALIDATION.md)

<a id="ketqua"></a>

## 6. Đọc kết quả và trả lời khi bị bắt bẻ

**Bảng 1. Bốn mô hình đã chọn trước khi mở holdout.** F1 tính cho lớp 1. Cột CV là trung bình và độ lệch chuẩn giữa các fold. Các cột còn lại tính trên phần test giữ riêng.

| Bộ · mô hình | F1 CV | F1 test | F1 baseline test | AUC test |
|---|---:|---:|---:|---:|
| Cleveland · Gaussian NB | 0,587 ± 0,026 | 0,500 | 0,000 | 0,534 |
| Pima · KNN | 0,666 ± 0,064 | 0,495 | 0,000 | 0,748 |
| ILPD · Logistic | 0,820 ± 0,027 | 0,834 | 0,831 | 0,633 |
| CKD · Decision Tree | 0,935 ± 0,019 | 0,891 | 0,769 | 0,889 |

**Bảng 2. Tác động của việc thêm luật vào ML trên toàn holdout.** FN là ca thật sự dương nhưng bị bỏ sót. FP là ca thật sự âm nhưng bị báo dương. Mũi tên đi từ chỉ ML sang gộp mới.

| Bộ | Luật đích khớp | F1 | FN | FP |
|---|---:|---:|---:|---:|
| Cleveland | 27/61 (44,3%) | 0,500 → 0,613 | 14 → 9 | 14 → 15 |
| Pima | 50/154 (32,5%) | 0,495 → 0,640 | 30 → 14 | 19 → 31 |

**Câu chốt khi chiếu số liệu:** “Trên 154 ca Pima, luật giúp hệ tìm thêm 16 ca dương và đồng thời báo dương nhầm thêm 12 ca âm. Đây là sự đánh đổi quan sát được ở ngưỡng đã khóa. Riêng ca 05 chỉ cho thấy cơ chế tạo ra sự thay đổi ấy.” [F1 và baseline qua CV](T06_TRAINING.md) · [Kết quả holdout](T10_HOLDOUT.md) · [Phân tích FP/FN](T12_ERROR_ANALYSIS.md) · [CSV metric gốc](../results/t10-test-seed42/metrics.csv)

| Nếu người hướng dẫn hỏi… | Câu trả lời ngắn, có thể kiểm chứng |
|---|---|
| **Accuracy, precision, recall, F1 khác gì nhau?** | Accuracy là số đoán đúng / tổng số ca. Precision hỏi “trong số ca báo dương, bao nhiêu ca thật sự dương?”. Recall hỏi “trong số ca thật sự dương, tìm ra bao nhiêu?”. F1 = 2TP/(2TP + FP + FN). Với Pima gộp mới, trong 54 ca dương có 40 TP và 14 FN, thêm 31 FP. F1 = 80/(80 + 31 + 14) = 0,640. |
| **Vì sao chọn F1? Sao gan đạt 0,834 mà còn nói yếu?** | F1 quan tâm việc tìm đúng lớp dương và chi phí báo dương sai, nhưng bỏ qua TN. ILPD có 81 dương trên 114 ca test, đoán dương tất cả đã đạt F1 0,831. Logistic chỉ nhận đúng 5/33 ca âm. Ngay trên CV, baseline 0,832 còn cao hơn Logistic 0,820. Quy tắc chọn trong 5 mô hình ứng viên, baseline làm mốc. |
| **Pima AUC 0,748 mà F1 chỉ 0,495 có mâu thuẫn?** | AUC đo xếp hạng điểm giữa cặp dương–âm, hòa tính nửa điểm. F1 đo nhãn sau khi cắt tại 0,5. KNN vẫn có thể xếp một ca dương cao hơn ca âm dù cả hai điểm đều dưới 0,5. |
| **Cleveland gần đoán ngẫu nhiên, em lý giải thế nào?** | AUC 0,534 trên 61 ca cho thấy sức phân biệt hạn chế trên lần chia này. Chỉ dùng ba biến và số mẫu ít là các giới hạn đã biết. Muốn quy mức giảm cho biến nào cần thí nghiệm đối chứng mới. CKD có AUC 0,889 trên 80 ca và vẫn cần kiểm chứng trên quần thể khác. |
| **Hệ luật recall 100% nghĩa là tìm được mọi ca bệnh?** | Mẫu số ở đây chỉ gồm các ca **đã khớp luật**. Trên Pima, trong 50 ca khớp có 32 dương và 18 âm. Luật cho dương cả 50 nên bắt được cả 32 và báo nhầm cả 18. Trên 104 ca còn lại, nhánh chỉ luật bỏ ngỏ. Coverage là 50/154. |
| **Sao vừa nói có đổi nhãn, vừa nói 0 ca đổi nhãn?** | Có hai thí nghiệm. **ML → gộp mới** đo tác động của việc thêm luật. **Gộp cũ → gộp mới** đo tác động của việc chỉ đưa ML vào một lần. Trên Pima, so cũ với mới có 38/154 ca thay đổi điểm, 0 ca đổi nhãn. CF của mỗi luật đích đã ≥ 0,5 nên khi luật khớp, hai cách đều đạt ngưỡng. |
| **Độ lệch chuẩn CV có cho biết độ chắc chắn của một ca? Sao không hạ ngưỡng cho Pima?** | Độ lệch chuẩn mô tả biến động metric giữa 5 fold train. Ngưỡng 0,5 là quy ước cố định trước T10. Nếu nghiên cứu ngưỡng khác, phải chọn bằng dữ liệu phát triển và đánh giá lại theo giao thức mới. |
| **Đồ án đóng góp gì khi thuật toán đã có?** | Phần có thể chứng minh là triển khai NumPy, quy trình so sánh dùng chung ID, cách tách nguồn điểm trong trace và đối chứng định lượng. Ví dụ em chỉ ra được cả mức giảm bỏ sót lẫn mức tăng báo sai khi thêm luật, và trường hợp đổi công thức chỉ đổi điểm. |

Nếu được yêu cầu chứng minh một lỗi cụ thể, mở báo cáo T12. Hai ca Cleveland trong bảng đã phân tích minh họa hai hướng: `cleveland:0013` từ âm giả thành dương đúng, còn `cleveland:0006` từ âm đúng thành dương giả. Đây là phân tích sau đánh giá. Sáu nút demo dùng ca tự tạo riêng. [Phân tích lỗi theo ID](T12_ERROR_ANALYSIS.md) · [Mã tính metric](../experiment_metrics.py)

<a id="demo"></a>

## 7. Kịch bản cầm máy trong 5–7 phút

**Trước buổi.** Chạy từ thư mục gốc với artifact T06 và SQLite riêng cho demo. Máy hiện tại đã có artifact. Flask đọc các tham số đã học ngay lúc khởi động.

```bash
demo_db_dir=$(mktemp -d)
MEDICAL_HISTORY_DB="$demo_db_dir/history.sqlite" \
  MEDICAL_MODEL_RUN=results/t06-cv-seed42 \
  .venv/bin/python -B -m flask --app app run --host 127.0.0.1 --port 5000
```

Mở [ứng dụng trên máy](http://127.0.0.1:5000). Trong giao diện hiện tại, bấm một nút **Kịch bản demo T13** sẽ tự nạp ca và gửi yêu cầu. Khi sửa tay, bấm **Chạy suy luận**. Khi cần chuyển số liệu thật nhanh, mở sẵn [bảng kết quả và giới hạn](REVIEW.md) ở cửa sổ thứ hai.

| Thời gian | Tay làm | Miệng nói |
|---|---|---|
| 0:00–0:40 | Mở **Suy luận**, chỉ bốn nhóm và hai chế độ. | “Bốn nhóm có bốn mô hình riêng. Em dùng Cleveland và Pima để kiểm tra thêm xem luật tác động thế nào đến dự đoán.” |
| 0:40–2:10 | Bấm **05 · ML ≠ Luật**, chỉ lần lượt ML, Hệ luật, điểm kết hợp. Mở **Giải thích chi tiết (Trace)**. | Kể lại ca 05 bằng 1/7 → 0,50 → 0,5714. Chỉ tuổi, BMI, ID luật. Dừng ở câu “em biết vì sao quyết định đổi, còn đúng hay sai cần nhãn thật”. |
| 2:10–3:00 | Bấm **02 · Thiếu chol**. Chỉ ô trống, fact chưa biết và trạng thái luật. | “ML có trung vị để tính tiếp. Em giữ nguyên tình trạng thiếu ở nhánh luật, nên dòng cholesterol trống không sinh bằng chứng.” |
| 3:00–4:00 | Mở **Mô hình CV**, chỉ mô hình được chọn và F1 ± std. | “Em giữ riêng khoảng 20%, dùng 5 fold trên phần còn lại để chọn mô hình. Bảng trên màn hình là điểm CV. Sau khi khóa phương pháp em mới đo trên phần để riêng.” |
| 4:00–5:00 | Mở bảng FP/FN ở mục 6 hoặc trong REVIEW. Chỉ một hàng Pima. | “Thêm luật giúp tìm thêm 16 ca dương, đổi lại có thêm 12 ca báo dương sai. Số này cho biết cái giá của việc nâng điểm khi khớp luật.” |
| 5:00–6:00 nếu còn giờ | Bấm **04 · 2 luật đích** nếu được hỏi về công thức, hoặc **Lịch sử** nếu được hỏi kết quả lưu ở đâu. | Với ca 04, tính 0,775 rồi 0,9357. Với lịch sử, chỉ cột **điểm ML** và giải thích vì sao khác điểm kết hợp. Kết lại bằng giới hạn của dữ liệu nhỏ, một holdout và điểm chưa hiệu chỉnh. |

**Bảng tra sáu nút.** Số làm tròn theo màn hình. Dấu “—” nghĩa là nhánh luật chưa có điểm.

| Nút | Dữ liệu nhập | ML / luật / gộp | Chỉ điều gì khi được hỏi? |
|---|---|---|---|
| 01 · Hợp lệ | Tim, tuổi 60, BP 135, chol 230 | 53,9% / 55,0% / 79,3% | Hai luật hiện trong trace, chỉ CLEV_TARGET_01 góp vào điểm. |
| 02 · Thiếu chol | Tim, tuổi 60, BP 135, chol trống | 55,4% / — / 55,4% | Fact thiếu giữ trạng thái chưa biết. |
| 03 · Biên fuzzy 50% | Tim, tuổi 60, BP 135, chol 200 | 49,6% / — / 49,6% | Tại μ = 0,5, fact sai. Nhãn cuối là 0. |
| 04 · 2 luật đích | Pima, glucose 175, BMI 33, tuổi 45 | 71,4% / 77,5% / 93,6% | Hai luật BMI dùng chung tiền đề tuổi. |
| 05 · ML ≠ Luật | Pima, glucose 90, BMI 26, tuổi 45 | 14,3% / 50,0% / 57,1% | Một luật đủ đưa điểm cuối qua ngưỡng. |
| 06 · Ngoài miền | Tim, tuổi 60, BP 135, chol 900 | HTTP 400 | Form báo lỗi cholesterol ngoài miền 150–400. SQLite chỉ ghi sau khi kiểm tra đầu vào thành công. |

Đã kiểm tra lại sáu bộ đầu vào bằng Flask test client với artifact T06 và DB tạm. Năm ca hợp lệ trả 200, ca 06 trả 400, lịch sử có năm dòng. Ảnh chụp của lần chạy demo đã lưu có thể dùng để đối chiếu kết quả. [Kịch bản và ảnh sáu ca](T13_DEMO.md) · [Các nút demo trên giao diện](../static/workspace.js)

**Các tình huống dễ khựng khi đang trình bày**

- **Lịch sử hiện 14,3% trong khi vừa nói 57,1%.** SQLite lưu trường ml_prob của nhánh ML, còn ô kết quả chính dùng combined_score của trace. API lịch sử lấy tối đa 10 lượt gần nhất. Tạo thư mục tạm mới ở lần khởi động sau sẽ mở một lịch sử mới. [Backend](../app.py)
- **Máy khác báo “Mô hình chưa sẵn sàng”.** Kiểm tra biến MEDICAL_MODEL_RUN trỏ đến **thư mục chứa models.json**, rồi khởi động lại Flask. Nếu máy chưa có artifact hợp lệ, tái tạo bằng bốn nguồn theo T06 trước buổi demo. Run có lưu ma trận train của KNN và thư mục results được bỏ qua trong Git. [Cách chuẩn bị máy](../README.md) · [Lệnh T06](T06_TRAINING.md)
- **Thầy hỏi tại sao CKD không nhập được huyết áp 80.** Miền form hiện tại là 90–200 mmHg dù median huyết áp trên train là 80. Đây là hạn chế cụ thể của GUI khi nhập ca. T10 chấm qua loader trực tiếp. [Schema form](../diseases_config.py) · [Review CKD](REVIEW.md)
- **Thầy hỏi có thể giao cho bệnh viện dùng ngay không.** “Nhóm đã kiểm tra phần mềm, có đơn vị dữ liệu còn chưa xác minh và chỉ có đánh giá nội bộ trên từng bộ. Chưa có đánh giá tiền cứu, kiểm định ngoài hay hiệu chỉnh điểm để diễn giải rủi ro cá nhân. Điều em bàn giao được là công cụ thực nghiệm và các kết quả có thể đối chiếu.” [Giới hạn dự án](REVIEW.md)
- **Gặp câu chưa đo**, ví dụ “dùng 8 biến Pima có tốt hơn không?”. Có thể trả lời: “Trong đợt đã khóa, em mới đo ba biến trên cùng split, F1 test của KNN là 0,495. Em chưa có đối chứng tám biến để kết luận. Để trả lời, em sẽ so hai cấu hình trên cùng các fold phát triển và dành dữ liệu độc lập để xác nhận.” Cách trả lời này cho thấy bạn phân biệt được điều đã làm và phép thử còn thiếu.
