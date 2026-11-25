# Đặc tả Medical Expert System

## Phạm vi

Ứng dụng Flask/SQLite chạy local phục vụ đồ án. Dùng chung một pipeline dữ liệu và đánh giá cho Cleveland (tim mạch), Pima (tiểu đường), ILPD (gan) và CKD (thận). Cả bốn bộ có bảng so sánh ML. Phân tích ML–luật, so sánh cách gộp và phân tích lỗi tập trung vào Cleveland và Pima. Demo dùng ca mẫu.

## Hợp đồng dữ liệu

### Cleveland

Nguồn đã đối chiếu là `processed.cleveland.data` từ UCI Heart Disease #45. CSV không có header, thứ tự cột `age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, num`. Phiên bản đầu dùng ba đặc trưng theo thứ tự dưới đây. [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease) · [Hồ sơ nguồn T03](tasks/T03_DATA_SOURCES.md)

| Cột nguồn | Khóa chuẩn | Kiểu và ý nghĩa |
|---|---|---|
| `age` | `age` | Số nguyên, năm |
| `trestbps` | `bp` | Số, huyết áp lúc nghỉ theo tài liệu Cleveland, mmHg |
| `chol` | `chol` | Số, cholesterol huyết thanh, mg/dL |
| `num` | `y` | 0 → 0, 1–4 → 1, giá trị khác → lỗi dữ liệu |

`?` và ô rỗng là missing. Không loại cả dòng chỉ vì thiếu cột không dùng. Nhãn dương là có bệnh tim theo Cleveland. Các kết luận như nhồi máu cơ tim hoặc rối loạn mỡ máu trong bộ luật hiện tại không dùng thay nhãn này.

### Pima

Loader đọc `diabetes.arff` của OpenML `diabetes` #37, version 1. Tệp có tám cột số và nhãn nominal ở cột cuối. Quyền tái phân phối bản gốc chưa được xác minh. [OpenML #37](https://www.openml.org/d/37) · [Hồ sơ nguồn T03](tasks/T03_DATA_SOURCES.md)

| Vị trí (từ 1) | Cột OpenML | Khóa chuẩn | Kiểu và ý nghĩa |
|---|---|---|---|
| 1 | `preg` | — | Số lần mang thai |
| 2 | `plas` | `glucose` | Số, glucose huyết tương hai giờ trong nghiệm pháp dung nạp glucose đường uống, đơn vị cột chưa được xác nhận |
| 3 | `pres` | — | Huyết áp tâm trương, mmHg |
| 4 | `skin` | — | Độ dày nếp gấp da cơ tam đầu, mm |
| 5 | `insu` | — | Insulin huyết thanh hai giờ, µU/mL |
| 6 | `mass` | `bmi` | Số, kg/m² |
| 7 | `pedi` | — | Chỉ số tiền sử gia đình |
| 8 | `age` | `age` | Số nguyên, năm |
| 9 | `class` | `y` | `tested_negative` → 0, `tested_positive` → 1 |

Thứ tự đặc trưng ML là `glucose, bmi, age`. Glucose và BMI bằng 0 được xử lý là missing theo quy ước hiệu chỉnh của `PimaIndiansDiabetes2`. Số lần mang thai bằng 0 là một giá trị hợp lệ. Khi chuyển form và luật sang Pima, dùng đúng định nghĩa glucose hai giờ OGTT và xác minh đơn vị của cột `plas` trước khi áp dụng ngưỡng có đơn vị. Bản OpenML gồm nữ từ 21 tuổi trở lên có gốc Pima, thuộc quần thể được nghiên cứu gần Phoenix, Arizona. [Hồ sơ nguồn T03](tasks/T03_DATA_SOURCES.md)

### ILPD và CKD

| Bộ dữ liệu | Ánh xạ theo thứ tự đặc trưng | Ngữ nghĩa nguồn và giới hạn |
|---|---|---|
| [UCI ILPD](https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset) | `TB → bilirubin`, `ALB → albumin`, `Age → age`; `Selector`: 1 → 1, 2 → 0 | Tuổi tính theo năm; đơn vị của `TB` và `ALB` chưa xác minh. Ô rỗng và `?` là missing. |
| [UCI CKD](https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease) | `sc → creatinine`, `bp → bp`, `age → age`; `class`: `ckd → 1`, `notckd → 0` | Creatinine huyết thanh mg/dL, huyết áp mmHg, tuổi tính theo năm. Tệp CSV có header; trim khoảng trắng/tab và coi `NaN`, ô rỗng, `?` là missing. Chỉ dùng `bp` trong luật khi kiểu phép đo đã rõ. |

Phiên bản tệp, số dòng, nhãn và missing theo đúng nguồn đã xác minh được ghi trong [hồ sơ T05](tasks/T05_DATA_SOURCES.md).

### Quy tắc chung

- Mỗi bộ có một loader trả về `sample_id`, đặc trưng gốc theo schema và nhãn nhị phân. `sample_id` ổn định qua các lần chạy với cùng file nguồn và không dùng làm đặc trưng. Ghi nguồn, bản dữ liệu, điều khoản sử dụng, số mẫu và số missing vào metadata.
- Kiểm tra schema, xác định duplicate theo bản ghi nguồn và xử lý trước khi chia. Nếu nhận diện được nhiều mẫu của cùng một người, giữ chúng cùng một phần chia. Không xem các dòng trùng ba đặc trưng đã chọn là trùng bệnh nhân.
- Dùng median học từ train cho đặc trưng số bị thiếu khi chạy ML. Fuzzy và luật nhận giá trị gốc, với missing là chưa biết. Giá trị đã điền chỉ phục vụ mô hình.
- Backend kiểm tra disease key, khóa đầu vào, kiểu, giá trị hữu hạn và miền nhập đã ghi trong schema. Chỉ nhận triệu chứng boolean trong danh sách cho phép. Không cho request ghi đè fact phát sinh từ dữ liệu hoặc suy luận.
- API yêu cầu đủ khóa chỉ số. Giá trị JSON `null` biểu thị chủ động để trống và được form gửi khi ô không có giá trị. Backend từ chối khóa bị bỏ, chuỗi rỗng và các giá trị ngoài miền nhập.

## Chia dữ liệu và đánh giá

- Holdout phân tầng theo nhãn, train 80% và test 20%, seed **42**. Lưu danh sách ID cho từng phần và fold. Mọi mô hình và cấu hình đối chứng dùng cùng các ID.
- Dùng stratified 5-fold CV trên 80% train, seed **42**. Fit imputer và scaler trong mỗi fold bằng phần train của fold, sau đó áp dụng lên validation. Sau khi chốt cấu hình, fit lại bằng toàn bộ train rồi áp dụng lên test.
- Chọn ML mặc định cho từng bộ theo mean F1 của lớp dương qua CV trên train. Chạy Logistic Regression, KNN, Gaussian NB, Decision Tree, Ensemble Voting và baseline lớp phổ biến học từ train của từng lần fit. Với điểm bằng nhau, ưu tiên mô hình đơn theo thứ tự vừa liệt kê, rồi ensemble. Baseline làm mốc so sánh.
- Báo accuracy, precision, recall, F1, ROC-AUC và confusion matrix. Tính F1 trực tiếp bằng `2TP / (2TP + FP + FN)`. Dùng điểm số cho ROC-AUC, kể cả điểm hằng của baseline. Metric không xác định để trống trong CSV, dùng `null` trong JSON và nêu lý do trong metadata. Báo mean ± std qua CV và điểm test riêng. Các điểm metric dùng thang 0–1, các ô confusion matrix dùng số đếm.
- Khóa schema, split, model, luật, ngưỡng và cấu hình thí nghiệm trước khi chạy test cuối. Test chỉ dành cho đánh giá các cấu hình đã khóa và phân tích lỗi sau đó. Dùng fixture hoặc validation cho phát triển và demo.

## Gộp ML và luật

Cho một đích nhị phân cụ thể, chỉ gộp các luật dương ánh xạ tường minh tới lớp 1 của đích đó. Ghi nguồn và điều kiện của từng luật. Luật mô tả dấu hiệu hoặc kết luận phụ vẫn có thể xuất hiện trong trace. Không tự suy triệu chứng còn thiếu từ cột đo khác để làm luật khớp.

Với ngưỡng fuzzy boolean ban đầu, một fact đúng khi mức liên thuộc lớn hơn 0,5. Fact thiếu có giá trị chưa biết. Ký hiệu `p` là điểm lớp 1 từ mô hình đã chọn và `c_i` là CF của luật đích thứ `i` đã khớp.

- **Chỉ luật** dùng `C_rule = 1 - product(1 - c_i)`.
- **Kết hợp mới** dùng `C_new = C_rule + p * (1 - C_rule)`.
- **Đối chứng cũ** tính `c_i_old = c_i + p * (1 - c_i)` cho mỗi luật rồi gộp các `c_i_old` bằng cùng công thức tích.

Dùng ngưỡng quyết định cố định `score >= 0.5` cho ablation và đối chứng cũ–mới. Báo các mức điểm là điểm hỗ trợ. Khi không có luật đích khớp, cấu hình chỉ luật trả `null` cho điểm và nhãn. Cả hai cách kết hợp dùng điểm ML trong trường hợp này để giữ đối chứng công bằng.

Trên tập test con có luật đưa ra điểm, so sánh ML, luật và kết hợp với cùng nhãn thật. Báo số mẫu, phân bố nhãn của tập con và tỷ lệ bao phủ so với toàn bộ test. Trên toàn bộ test, báo thêm ML, kết hợp mới và kết hợp cũ. Báo chênh lệch điểm và số ca đổi nhãn giữa cách cũ và mới. Lưu ý các luật có chung tiền đề vẫn có thể làm điểm hỗ trợ tăng mạnh.

Fuzzy liên tục là tùy chọn. Nếu triển khai trước khi khóa cấu hình, đặt mức kích hoạt luật bằng minimum của các tiền đề và dùng `CF × mức kích hoạt`, giữ cố định các thành phần còn lại.

## Trace và đầu ra thí nghiệm

API giữ các trường tương thích cho giao diện trong quá trình chuyển đổi, đồng thời bổ sung `trace`. Thang điểm trong trace là 0–1. Hình dạng dưới đây dùng khóa giả và số minh họa.

```json
{
  "target": "dataset_target",
  "ml": {"model": "Logistic Regression", "score": 0.4},
  "facts": [
    {"feature": "marker", "value": 30, "unit": "unit", "membership": 0.75, "key": "high_marker", "value_boolean": true}
  ],
  "fired_rules": [
    {"id": "RULE_01", "conditions": ["high_marker"], "target": "dataset_target", "conclusion": "Dấu hiệu phù hợp với nhãn đích", "cf": 0.6, "used_in_fusion": true}
  ],
  "result": {"rule_status": "matched", "rule_score": 0.6, "combined_score": 0.76, "predicted_label": 1}
}
```

Thiếu đặc trưng thì các giá trị liên quan trong fact là `null`. Khi chưa có luật đích khớp, dùng `rule_status: "no_matching_target_rule"` và `rule_score: null`. Luật phụ có `used_in_fusion: false`. UI đọc trace theo luồng chỉ số → fact → luật → kết luận.

Mỗi lần đánh giá ghi vào `results/<run_id>/`.

| File | Nội dung bắt buộc |
|---|---|
| `metadata.json` | Seed, ngày huấn luyện, nguồn và bản dữ liệu, cấu hình, số mẫu từng phần, split/fold manifest hoặc đường dẫn tới manifest |
| `metrics.csv` | `dataset,experiment,variant,split,subset,n,metric,value,std`. `std` chỉ điền cho tổng hợp CV |
| `predictions.csv` | `dataset,sample_id,split,experiment,variant,y_true,y_pred,score,covered`. Để trống điểm và nhãn khi hệ luật không đưa ra kết luận |

Lưu confusion matrix và coverage trong `metrics.csv`. Dùng dự đoán từng mẫu để đối chiếu các ca sai và ca bất đồng. Báo cáo lấy số trực tiếp từ các file này.
