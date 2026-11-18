# Đánh giá đồ án và hướng tự cải thiện

**Ngày 18/11/2026.** Với mục tiêu học phần Hệ chuyên gia kết hợp Machine Learning, đồ án đã đủ cơ sở để bảo vệ. Điểm thuyết phục nhất là nhóm có thể theo một ca từ chỉ số đầu vào qua ML, luật và phép gộp, rồi dùng kết quả thực nghiệm để chỉ ra khi nào luật giúp sửa sai và khi nào luật gây thêm lỗi. Mức độ khái quát sang quần thể mới và giá trị sử dụng lâm sàng vẫn là câu hỏi mở.

## Đánh giá theo từng phần

| Phần | Đánh giá và căn cứ |
|---|---|
| Dữ liệu và tái lập | Bốn bộ dữ liệu thật có nguồn, schema và quy ước missing. Manifest cố định ID của holdout và 5 fold. Median và scaler chỉ học từ tập train tương ứng. Mã phương pháp, artifact CV và bằng chứng validation khớp khóa T10. Hai checksum CSV holdout khớp hồ sơ đã công bố. [Đặc tả](SPEC.md) · [Khóa](t10_lock.json) |
| Machine Learning | Bốn mô hình NumPy, ensemble và baseline chạy trên cùng split. Chọn mô hình theo F1 dương trên CV phù hợp với câu hỏi đã đặt. F1 lớp dương có thể che hiệu năng kém trên lớp âm khi dữ liệu lệch lớp, đặc biệt với ILPD. [Huấn luyện](T06_TRAINING.md) |
| Hệ chuyên gia | Cleveland có một luật đích và một luật phụ. Hai luật đích Pima chia sẻ tuổi và dùng hai mốc BMI lồng nhau. Có tài liệu cho căn cứ chọn tiền đề, còn CF do nhóm đặt. Gan và thận hiện tính điểm bằng ML. Đây là phạm vi cụ thể cần nêu khi giới thiệu đồ án có bốn nhóm bệnh. [Bảng nguồn luật](T07_RULES.md) |
| Phần mềm và demo | Backend kiểm tra đầu vào trước khi ghi SQLite. Dữ kiện thiếu vẫn xuất hiện trong trace, trong khi ML dùng median của train. Sáu ca tự tạo bao gồm cả bất đồng, đúng biên fuzzy và lỗi nhập. GUI hiện tách điểm ML, luật, kết hợp và giải thích khi thiếu toàn bộ chỉ số. [Ca demo](T13_DEMO.md) |
| Bàn giao | README có quy trình dựng môi trường, tái tạo artifact và chạy với DB riêng. Git vẫn đang theo dõi một tệp lịch sử SQLite và sáu tệp cache Python từ trước. Khi chuẩn bị bản nộp, giữ bản lịch sử của người dùng riêng và kiểm tra danh sách tệp phân phối. [Hướng dẫn chạy](../README.md) |

## Đọc đúng hiệu năng mô hình đã chọn

| Bộ | Số ca holdout | F1 ML / F1 baseline | ROC-AUC ML | Ý nghĩa |
|---|---:|---:|---:|---|
| Cleveland | 61 | 0,500 / 0,000 | 0,534 | Khả năng xếp hạng gần mức ngẫu nhiên trên lần chia này. Baseline luôn dự đoán âm nên F1 dương bằng 0. |
| Pima | 154 | 0,495 / 0,000 | 0,748 | Khả năng xếp hạng và khả năng phân lớp tại ngưỡng đã khóa là hai câu hỏi khác nhau. ML bỏ sót 30 ca dương. Quần thể nguồn gồm phụ nữ gốc Pima từ 21 tuổi. |
| ILPD | 114 | 0,834 / 0,831 | 0,633 | Baseline luôn dự đoán dương. Logistic Regression chỉ nhận đúng 5 trong 33 ca âm. |
| CKD | 80 | 0,891 / 0,769 | 0,889 | Decision Tree vượt baseline 0,122 điểm F1. Cỡ mẫu và quần thể của CKD giới hạn khả năng khái quát. |

Các số là kết quả trên holdout đã khóa, với ba đặc trưng cho mỗi bộ. [Kết quả T10](T10_HOLDOUT.md) · [Metric tổng hợp cục bộ](../results/t10-test-seed42/metrics.csv)

### Giá trị của luật và của phép gộp

| So sánh trên toàn holdout | Cleveland | Pima |
|---|---:|---:|
| Ca có ít nhất một luật đích khớp | 27/61 | 50/154 |
| F1 khi chuyển từ ML sang gộp mới | 0,500 → 0,613 | 0,495 → 0,640 |
| Ca dương bị bỏ sót (FN) | 14 → 9 | 30 → 14 |
| Ca âm bị báo dương (FP) | 14 → 15 | 19 → 31 |
| Ca đổi nhãn khi chuyển từ gộp cũ sang gộp mới | 0 | 0 |

Trên Pima, việc thêm luật tìm thêm **16 ca dương** và tạo thêm **12 dương giả**. So riêng hai công thức gộp, điểm thay đổi ở 38/154 ca Pima nhưng cả hai công thức cho cùng nhãn ở mọi ca. Nguyên nhân nằm ở thiết kế. Mỗi luật đích có CF ít nhất 0,5, đủ đạt ngưỡng dương ngay khi khớp. Khi quy tắc BMI cao khớp, quy tắc BMI thấp cũng khớp. Gộp mới đưa bằng chứng ML vào một lần, còn sự phụ thuộc giữa các tiền đề của hai luật vẫn tồn tại. [Đối chứng validation](T09_VALIDATION.md) · [Phân tích lỗi holdout](T12_ERROR_ANALYSIS.md)

## Những điểm đã sửa trên GUI

- Bảng kết quả đặt điểm ML và điểm luật ngay dưới điểm kết hợp. Khi bỏ trống đầu vào, người xem thấy số trường đã nhập và tên trường ML phải điền trung vị. Khi gan hoặc thận chỉ dùng ML, giao diện nêu rõ lý do.
- Hai câu hỏi về đau ngực và khó thở đã được bỏ khỏi form vì luồng suy luận hiện tại chỉ sử dụng ba chỉ số. Lịch sử ghi rõ điểm ML. Các lượt có cùng timestamp được xếp theo ID mới nhất.
- Bảng so sánh dùng số liệu 5-fold CV, đánh dấu mô hình đã chọn và hiển thị F1 cùng độ lệch chuẩn. Phần cây giải thích ngưỡng đã chuẩn hóa và quy ước ở lá hòa. Ví dụ, cây Pima có một lá với một mẫu mỗi lớp. Chuỗi mô tả lá ghi lớp 0 theo lớp phổ biến, còn bộ phân loại trả nhãn 1 khi điểm bằng 0,5. [Cách xuất cây](../math_ml_from_scratch.py)
- Đã chạy lại sáu ca demo trên Chrome, cả bốn form và màn hình rộng 390 px. Trình duyệt tải CSS, JavaScript và dữ liệu qua Flask cục bộ. [Kịch bản và ảnh](T13_DEMO.md)

## Ba việc nên tự làm trước khi bảo vệ

1. **Tự giải thích ca 5 trong 60 giây.** Nhập tuổi 45, glucose OGTT 90, BMI 26 trên Pima. Chỉ ra ML cho 0,1429, luật cho 0,50 và tự tính điểm gộp bằng 0,50 + 0,1429 × (1 − 0,50) ≈ 0,5714. Giải thích vì sao nhãn của bộ dữ liệu đổi ở ngưỡng 0,5 và vì sao không thể diễn giải con số này thành xác suất mắc bệnh của một cá nhân. [Kịch bản thao tác](T13_DEMO.md)
2. **Tự đọc nhược điểm từ bảng đếm.** Dùng 5 âm đúng và 28 dương giả của ILPD để giải thích vì sao F1 dương vẫn cao dù mô hình nhận diện kém lớp âm. Sau đó dùng bảng Pima phía trên để trả lời câu hỏi “thêm luật đã đổi loại lỗi nào?”. Thành công khi giải thích được bằng số ca, kể cả phần kết quả bất lợi. [Kết quả T10](T10_HOLDOUT.md) · [T12](T12_ERROR_ANALYSIS.md)
3. **Rà soát miền nhập CKD bằng train và hồ sơ nguồn.** Form nhận huyết áp 90–200 mmHg, trong khi median train là 80. Sau bước điền thiếu, 247/320 giá trị huyết áp train nằm ngoài miền này. Con số lấy từ ma trận train của KNN trong artifact T06 sau khi đảo chuẩn hóa, bao gồm các vị trí đã điền median. Lập bảng miền nhập, số quan sát gốc ngoài miền, số missing và đơn vị cho cả ba trường CKD. Đề xuất miền dùng cho demo sau khi xác minh nghĩa cột huyết áp. Hạn chế này ảnh hưởng khả năng nhập ca trên GUI. Phép đo T10 dùng loader trực tiếp. [Schema của form](../diseases_config.py) · [Hồ sơ CKD](T05_DATA_SOURCES.md)

Bản review dùng các kết quả đã xuất. Nếu nghiên cứu tiếp về luật, CF hoặc đặc trưng, hãy xác lập một giao thức đánh giá mới trước khi thay đổi phương pháp. [Quy định dự án](../AGENTS.md)
