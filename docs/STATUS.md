# Trạng thái Medical Expert System

Cập nhật ngày **18/11/2026**.

[Báo cáo tiến độ Tuần 1](BAO_CAO_TIEN_DO_TUAN_1.md) tóm tắt kết quả T01–T05, lần rà soát cuối tuần và mốc T06.

## Đã có

- Ứng dụng Flask/SQLite có form cho bốn nhóm, tải mô hình fit trên dữ liệu thật và hiển thị trace từ chỉ số gốc đến điểm hỗ trợ.
- Gaussian NB tính mật độ trực tiếp trong không gian log từ T06. `requirements.txt` ghi dependency đã dùng với Python 3.12.
- Phạm vi, giao thức thí nghiệm và backlog đã được ghi trong [SPEC.md](SPEC.md), [TASKS.md](TASKS.md) và [AGENTS.md](../AGENTS.md).
- T01 đã nghiệm thu. SQLite tạo bảng `history` khi cần và giữ dữ liệu qua các lần khởi động. Biến môi trường `MEDICAL_HISTORY_DB` chọn tệp SQLite trước khi khởi động. Mặc định dùng `medical_history.db`.
- T02 đã nghiệm thu. `POST /api/diagnose` trả HTTP 400 với thông báo dưới `errors`, theo khóa trường như `inputs.age`. Form hiển thị thông báo và đánh dấu ô tương ứng. Số JSON và chuỗi số hữu hạn được chấp nhận nếu đúng miền. Tuổi phải là số nguyên. T11 thêm giá trị `null` tường minh cho chỉ số chưa biết. Chỉ nhóm tim mạch nhận hai triệu chứng boolean `chest_pain` và `short_breath`. Request lỗi dừng trước suy luận và ghi lịch sử.
- T03 đã nghiệm thu phần xác minh nguồn và nạp dữ liệu. Cleveland có 303 mẫu (164 âm, 139 dương). Pima có 768 mẫu (500 âm, 268 dương), với 5 giá trị glucose và 11 giá trị BMI bằng 0 được đánh dấu missing. Loader kiểm tra schema và nhãn, dùng toàn bộ cột nguồn cho kiểm tra trùng và tạo ID ổn định. [Hồ sơ nguồn T03](T03_DATA_SOURCES.md) · [Metadata JSON](t03_dataset_metadata.json)
- T04 đã nghiệm thu split holdout phân tầng và 5-fold CV bằng seed 42. Imputer và scaler chỉ học từ train của fold, giữ nguyên dữ liệu gốc. [Hướng dẫn T04](T04_DATA_PIPELINE.md) · [Manifest JSON](t04_split_manifest.json)
- T05 đã nghiệm thu loader ILPD và CKD cùng pipeline. ILPD còn 570 mẫu (164 âm, 406 dương) sau khi loại 13 dòng trùng toàn bộ. CKD có 400 mẫu (150 âm, 250 dương), thiếu 17 creatinine, 12 huyết áp và 9 tuổi. [Hồ sơ nguồn T05](T05_DATA_SOURCES.md) · [Metadata JSON](t05_dataset_metadata.json) · [Manifest JSON](t05_split_manifest.json)

- T06–T13 đã nghiệm thu. Đã lưu đầu ra CV, validation và holdout ở `results/`, phân tích lỗi theo ID và chuẩn bị sáu ca demo được chạy trên Chrome. [Kết quả T10](T10_HOLDOUT.md) · [Phân tích lỗi](T12_ERROR_ANALYSIS.md) · [Demo](T13_DEMO.md)
- T15 đã nghiệm thu. Bản xuất sạch từ Git chạy 46/46 kiểm thử với môi trường Python 3.12 mới, tái tạo artifact T06 và metadata T09 khớp khóa T10, chạy thành công bốn nhóm với SQLite tạm. [Hướng dẫn bàn giao](../README.md)

## Giới hạn cần ghi trong báo cáo
- OpenML gắn nhãn `Public` cho Pima #37 và có điều khoản về nghiên cứu riêng do người tải cấp. Quyền của bên tải ban đầu và quyền tái phân phối bản gốc vẫn chưa được xác nhận. Cột `plas` là glucose huyết tương hai giờ OGTT, đơn vị riêng của cột chưa xác nhận. Hai giới hạn đã ghi trong [hồ sơ nguồn](T03_DATA_SOURCES.md).
- Đơn vị nguồn của `TB` và `ALB` trong ILPD chưa xác minh. UCI ghi `bp` của CKD tính bằng mmHg nhưng chưa xác định tâm thu/tâm trương; để ngoài luật cho đến khi xác minh kiểu phép đo. Các giá trị gốc vẫn dùng được trong ML. [Hồ sơ nguồn T05](T05_DATA_SOURCES.md)
- T14 được bỏ qua trước khi khóa T10. Đợt đánh giá dùng hóa mờ boolean, ngưỡng liên thuộc >0,5 và ngưỡng nhãn ≥0,5. Kết quả phản ánh một lần chia dữ liệu, điểm hỗ trợ chưa hiệu chỉnh. [Khóa T10](t10_lock.json)

## Quyết định và lý do

| Quyết định | Lý do |
|---|---|
| Giữ bốn nhóm bệnh, chạy chung pipeline ML | Tận dụng form và cấu hình sẵn có, thêm dữ liệu thật mà vẫn giữ khối lượng code vừa sức |
| Làm sâu trên Cleveland và Pima | Có đủ bằng chứng cho câu hỏi ML–luật trong báo cáo, giữ thời gian rà soát luật trong tầm kiểm soát |
| Ưu tiên ba đặc trưng số hiện có theo từng bộ, sau khi xác minh ánh xạ | Giảm thay đổi ở form và pipeline, giúp giải thích được từng đầu vào |
| Dùng holdout 80/20 và 5-fold CV trên train với seed 42 | Giữ test độc lập, cho phép đối chiếu mô hình trên cùng mẫu |
| Gộp các luật cùng đích trước, đưa ML vào một lần và giữ công thức cũ làm đối chứng | Đo trực tiếp ảnh hưởng của việc cùng một điểm ML bị tính qua nhiều luật |
| Ghi metadata JSON, metric và dự đoán CSV | Có nguồn số liệu cho báo cáo và phân tích từng ca |
| Fuzzy liên tục là tùy chọn | Ưu tiên hoàn thành các thí nghiệm chính |

## Bước tiếp theo

Các mục bắt buộc đã nghiệm thu. Dùng [README](../README.md) để chạy lại pipeline và [sáu ca demo](T13_DEMO.md) khi trình bày. Run holdout `t10-test-seed42` đã chạy với [khóa cấu hình](t10_lock.json) được commit trước đánh giá. Các mô hình đã khóa là Gaussian NB (Cleveland), KNN (Pima), Logistic Regression (ILPD) và Decision Tree (CKD).

Khi nghiệm thu một task, thêm một dòng vào bảng dưới và đánh dấu mục tương ứng trong TASKS.

| Task | Commit | Kiểm tra và kết quả | File bằng chứng | Bước tiếp |
|---|---|---|---|---|
| Chuẩn bị tài liệu | — | Đã đọc diff và kiểm tra liên kết, khoảng trắng, JSON trace và mã task | `AGENTS.md` và ba file trong `docs/` | T01 |
| T01 | `6c8f5dc` | `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v` pass 3/3 trên DB tạm. Smoke test khởi động trong tiến trình mới hai lần cũng giữ nguyên bản ghi mẫu. Đã review diff và `git diff --cached --check` pass trước commit. | [tests/test_history.py](../tests/test_history.py) | T02 |
| T02 | `1f35d98` | `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v` pass 10/10 trên DB tạm. Smoke test Chrome headless qua Flask loopback pass với lỗi ở hai ô, gửi lại sau khi sửa và gửi hợp lệ cả bốn form. Test trình duyệt dùng CSS tối thiểu và Chart.js giả lập để chạy offline. Đã review diff và `git diff --cached --check` pass trước commit. | [tests/test_diagnosis_validation.py](../tests/test_diagnosis_validation.py), [templates/index.html](../templates/index.html) | T03 |
| T03 | `862a7f3` | `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v` pass 16/16. `.venv/bin/python -B -m scripts.inspect_datasets --cleveland PATH --pima PATH` chạy trên đúng hai bản đã đối chiếu SHA-256, xuất lại JSON giống từng byte. Đã review diff và `git diff --cached --check` pass trước commit. | [Fixture](../tests/test_dataset_loaders.py), [metadata](t03_dataset_metadata.json), [hồ sơ nguồn](T03_DATA_SOURCES.md) | T04 |
| T04 | `44ac1b5` | `.venv/bin/python -B -m unittest discover -s tests -v` pass 19/19. Chạy lệnh tạo manifest hai lần trên đúng bản T03 và `cmp` pass; đối chiếu ID/nhãn tổng hợp, 5 fold có đủ hai lớp và chỉ fit/transform trên các mẫu thuộc train holdout. Đã review diff và `git diff --cached --check` pass trước commit. | [Fixture](../tests/test_data_pipeline.py), [manifest](t04_split_manifest.json), [hướng dẫn](T04_DATA_PIPELINE.md) | T05 |
| T05 | `4b3c241` | `.venv/bin/python -B -m unittest discover -s tests -v` pass 25/25. Hai lệnh `scripts.inspect_datasets` và `scripts.split_datasets` tái tạo metadata và manifest T05, không làm đổi byte đầu ra T03/T04. Kiểm tra đủ hai lớp và tiền xử lý hữu hạn trong train/validation của cả 20 fold; holdout chỉ được kiểm tra ID và tổng nhãn. Đã review diff và `git diff --cached --check` pass trước commit. | [Hồ sơ](T05_DATA_SOURCES.md), [metadata](t05_dataset_metadata.json), [manifest](t05_split_manifest.json), [fixture ILPD](../tests/test_ilpd_loader.py), [fixture CKD](../tests/test_ckd_loader.py) | T06 |
| T06 | `46e7836` | Huấn luyện lặp hai lần trên bốn bộ, CSV và mô hình khớp từng byte. 32/32 test pass, Flask tải đúng mô hình của cả bốn nhóm trên DB tạm. | [Hướng dẫn và F1 CV](T06_TRAINING.md) | T07 |
| T07 | `7ee3b5a` | Fixture biên và missing pass. Cleveland 112/242 và Pima 197/614 ca ngoài fold có luật đích. | [Nguồn và ánh xạ luật](T07_RULES.md) | T08 |
| T08 | `cb396f3` | Fixture kiểm tra không luật, một luật, nhiều luật, fact thiếu, luật phụ và JSON trace. API dùng trace mới trên DB tạm. | [Fusion](../fusion.py), [fixture](../tests/test_fusion.py) | T09 |
| T09 | `5df8e64` | `.venv/bin/python -B -m scripts.validate_ablation` với tệp Cleveland/Pima đã xác minh. Cả 44 test hiện có pass. Đã đối chiếu từng ID ngoài fold, coverage và số ca đổi nhãn. | [Kết quả validation](T09_VALIDATION.md) | T10 |
| T10 | `0f79c31`, `3427051` | Commit khóa trước khi chạy `.venv/bin/python -B -m scripts.evaluate --run-id t10-test-seed42 --split test` với bốn đường dẫn đã xác minh. Đối chiếu 3.314 dòng dự đoán và 380 dòng metric. | [Khóa](t10_lock.json), [F1/ROC-AUC và SHA-256](T10_HOLDOUT.md) | T11, T12 |
| T11 | `51c62a4` | Test API và DOM pass. Chrome kiểm tra cả bốn form, dữ kiện chưa biết, trace và lịch sử trên SQLite tạm. | [Giao diện](../templates/index.html), [fixture DOM](../tests/test_trace_ui.py) | T13 |
| T12 | `aa35a37` | Đối chiếu ca sai và ca bất đồng bằng CSV theo ID. Hệ số đọc từ Logistic Regression fit trên train. | [Phân tích](T12_ERROR_ANALYSIS.md), [biểu đồ](t12_logistic_coefficients.svg) | T15 |
| T13 | `e9210b1` | Sáu ca tự tạo chạy qua form Chrome với artifact T06 và DB tạm, có ảnh kết quả và lỗi ngoài miền. | [Kịch bản và ảnh](T13_DEMO.md) | T15 |
| T14 | — | Quyết định bỏ phần fuzzy liên tục trước khi chạy holdout. | [Khóa T10](t10_lock.json) | — |
| T15 | `539b442` | `uv venv --python 3.12` và `uv pip sync` thành công trong môi trường mới. Bản xuất từ `git archive` chạy 46/46 test, tái lập T06/T09 khớp khóa T10, bốn form chạy trên Chrome và trang lịch sử đọc từ DB tạm. Đã đối chiếu các số báo cáo với CSV/JSON và kiểm tra liên kết. | [README](../README.md), [kết quả holdout](T10_HOLDOUT.md) | Bàn giao |

## Sau bàn giao · Review và GUI

Commit `0f85450` cập nhật GUI, [bản review](REVIEW.md) và [sáu ca demo](T13_DEMO.md). Lệnh `.venv/bin/python -B -m unittest discover -s tests -q` pass 47/47. `node --check static/workspace.js` và `git diff --cached --check` pass. Chrome headless chạy với Flask trên loopback, artifact T06 và SQLite tạm. Đã kiểm tra sáu fixture T13, bốn nhóm bệnh, trường hợp thiếu toàn bộ đầu vào và chiều rộng 390 px. Các ca demo cho điểm đúng như kịch bản, giao diện tải tài nguyên cục bộ.

Đã đối chiếu mã phương pháp và artifact theo khóa T10, cùng hai checksum CSV holdout đã công bố. Bước tiếp theo là luyện giải thích tác động lên FN/FP và rà soát miền nhập CKD trên train. Form nhận huyết áp từ 90 mmHg trong khi median train là 80 mmHg. Xem cách đếm và giới hạn trong [bản review](REVIEW.md).

Commit `810a47f` bàn giao [báo cáo từ A đến Z](BAO_CAO_DU_AN.md) và liên kết từ README. Đã kiểm tra mục lục, liên kết tệp, bảng metric CV/OOF/holdout, hai ca Pima với artifact T06, khóa T10 và checksum hai CSV đã xuất. Lệnh `.venv/bin/python -B -m unittest discover -s tests -q` đạt 47/47, dùng SQLite tạm trong kiểm thử. Bản báo cáo có mục hướng dẫn vận hành và bốn câu tự kiểm tra để ôn bảo vệ.

## Ghi chú bảo vệ ngày 22/11/2026

Commit `947592c` bổ sung [sổ tay từ core đến demo](GHI_CHU_BAO_VE.md). Đã dùng `.venv/bin/python -B` với Flask test client, artifact T06 và SQLite tạm để gửi sáu ca T13. Năm lượt hợp lệ trả 200, ca ngoài miền trả 400, lịch sử có năm dòng. Bốn endpoint thống kê trả đúng mô hình đã chọn theo CV. Đã đối chiếu số liệu với metric tổng hợp, kiểm tra liên kết, bảng Markdown và chạy `git diff --cached --check` thành công. Bước tiếp theo khi luyện trình bày là tính ca 05 bằng tay và giải thích thay đổi FN/FP trên Pima.

## Luyện vấn đáp và chiến lược bảo vệ ngày 22/11/2026

Commit `4400e40` bổ sung [37 câu hỏi vấn đáp và kế hoạch luyện tập](VAN_DAP_BAO_VE.md), đồng thời cập nhật thao tác chọn ca trong [sổ tay bảo vệ](GHI_CHU_BAO_VE.md). Đã đối chiếu metric tổng hợp và phép tính ca 4, kiểm tra 17 hash phương pháp và hash mô hình với khóa T10, kiểm tra liên kết và bảng Markdown. `node --check static/workspace.js` pass. `MEDICAL_HISTORY_DB=DB_TẠM .venv/bin/python -B -m unittest discover -s tests -q` pass 47/47. Trên trình duyệt, ca 5 chạy qua Flask với DB tạm và hiện 14,3% ML, 50,0% luật, 57,1% kết hợp cùng trace. Giao diện và các file ngoài tài liệu có thay đổi sẵn trong workspace. Bước tiếp theo là luyện trả lời và đối chiếu với tiêu chí chấm của giảng viên khi có.
