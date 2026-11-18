# Medical Expert System

Đồ án Flask, SQLite và các mô hình ML tự viết bằng NumPy cho bốn bộ dữ liệu tim mạch, tiểu đường, gan và thận. Ứng dụng trình bày điểm hỗ trợ và trace chỉ số → fact → luật → kết quả. Đây là công cụ nghiên cứu, không phải hệ thống chẩn đoán y khoa.

[Đánh giá đồ án và hướng tự cải thiện](docs/REVIEW.md) · [Sáu ca demo](docs/T13_DEMO.md)

## Cài đặt

Cần Python 3.12, `uv` và Node.js nếu muốn chạy kiểm thử giao diện dùng DOM giả lập. Chạy từ thư mục gốc:

```bash
uv venv --python 3.12 .venv
uv pip sync --python .venv/bin/python requirements.txt
.venv/bin/python -B -m unittest discover -s tests -v
```

Các test ứng dụng dùng SQLite tạm và fixture tự tạo. Test giao diện dùng Node.js được bỏ qua nếu không có Node. Flask phục vụ CSS và JavaScript cục bộ. Khi đã có môi trường và artifact mô hình, cả bốn form, bảng CV và lịch sử đều dùng được ngoại tuyến.

## Dữ liệu nguồn

Giữ tệp nguồn ngoài repo. Đường dẫn trong lệnh bên dưới là ví dụ, thay bằng đường dẫn thực. Các loader yêu cầu đúng bản và định dạng sau; SHA-256 đã đối chiếu nằm trong [hồ sơ T03](docs/T03_DATA_SOURCES.md), [hồ sơ T05](docs/T05_DATA_SOURCES.md) và [khóa T10](docs/t10_lock.json).

| Bộ | Tệp đầu vào | Nguồn và điều kiện |
|---|---|---|
| Cleveland | `processed.cleveland.data`, CSV 14 cột không header, giải nén từ kho UCI | [UCI Heart Disease #45](https://archive.ics.uci.edu/dataset/45/heart+disease), CC BY 4.0 |
| Pima | `diabetes.arff`, OpenML #37 phiên bản 1 | [OpenML #37](https://www.openml.org/d/37), nhãn `Public`; quyền tái phân phối bản gốc chưa xác minh. Xem giới hạn trong hồ sơ T03 trước khi sử dụng hoặc chia sẻ. |
| ILPD | `Indian Liver Patient Dataset (ILPD).csv`, CSV 11 cột không header, giải nén từ kho UCI | [UCI ILPD #225](https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset), CC BY 4.0 |
| CKD | `data.csv`, CSV 25 cột có header từ UCI | [UCI CKD #336](https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease), CC BY 4.0 |

Đặc trưng được chọn, nhãn, cách xử lý missing, trùng và split được mô tả trong [SPEC](docs/SPEC.md). Glucose Pima là glucose huyết tương sau hai giờ OGTT, nhưng đơn vị riêng của cột chưa xác minh. Đơn vị bilirubin và albumin ILPD chưa được UCI xác minh; huyết áp CKD tính bằng mmHg nhưng chưa rõ tâm thu hay tâm trương. Các giới hạn này ảnh hưởng cách diễn giải và dùng luật.

## Huấn luyện và chạy ứng dụng

Lệnh sau dùng đúng bốn bản nguồn đã đối chiếu, seed 42 và 5-fold CV trên train, rồi fit lại mô hình trên toàn bộ train. Khi chạy lần đầu, giữ run ID mặc định để tái lập T09 và T10. Lệnh từ chối ghi đè thư mục kết quả đã tồn tại.

```bash
.venv/bin/python -B -m scripts.train --dataset all --seed 42 \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff \
  --ilpd "/path/to/Indian Liver Patient Dataset (ILPD).csv" \
  --ckd /path/to/data.csv

demo_db_dir=$(mktemp -d)
MEDICAL_HISTORY_DB="$demo_db_dir/history.db" \
  .venv/bin/python -B -m flask --app app run --host 127.0.0.1
```

Mở `http://127.0.0.1:5000/`. Nếu bỏ `MEDICAL_MODEL_RUN`, ứng dụng đọc `results/t06-cv-seed42`; nếu thiếu hoặc sai artifact, API trả 503 và giao diện báo mô hình chưa sẵn sàng. Nếu bỏ `MEDICAL_HISTORY_DB`, ứng dụng dùng `medical_history.db` tại thư mục chạy; biến môi trường trong ví dụ chọn DB riêng. Ô chỉ số bỏ trống được gửi là giá trị chưa biết: luật giữ unknown, còn ML điền median đã học từ train. [Chi tiết huấn luyện](docs/T06_TRAINING.md)

## Tái lập và đọc kết quả

Manifest cố định holdout phân tầng 80/20 và 5 fold train, seed 42: [Cleveland/Pima](docs/t04_split_manifest.json), [ILPD/CKD](docs/t05_split_manifest.json). Imputer và scaler học từ train của từng fold. `results/<run_id>/metadata.json`, `metrics.csv`, `predictions.csv`, `split_manifest.json` và `models.json` là nguồn để đối chiếu kết quả CV; không lấy số từ dữ liệu tổng hợp. Artifact KNN chứa ma trận train đã biến đổi, nên quản lý tệp kết quả cẩn thận theo điều kiện dữ liệu nguồn.

Lệnh đối chứng dưới đây đọc dự đoán ngoài fold từ run CV mặc định và ghi vào `results/t09-validation-seed42`. Có thể dùng `--cv-run` và `--output` để đối chứng một lần huấn luyện khác. [T09](docs/T09_VALIDATION.md)

```bash
.venv/bin/python -B -m scripts.validate_ablation \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff
```

Đánh giá holdout cuối chỉ dành cho cấu hình đã khóa trong [T10](docs/t10_lock.json), sau T09, không dùng để chọn mô hình, sửa luật hoặc ngưỡng. Lệnh dưới đây dùng run và đường dẫn đã khóa; nó kiểm tra hash cấu hình, dữ liệu và artifact, và từ chối ghi đè kết quả đã có. Tham khảo [STATUS](docs/STATUS.md) để biết đợt đánh giá đã được chạy và nghiệm thu hay chưa.

```bash
.venv/bin/python -B -m scripts.evaluate --run-id t10-test-seed42 --split test \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff \
  --ilpd "/path/to/Indian Liver Patient Dataset (ILPD).csv" \
  --ckd /path/to/data.csv
```

Kết quả holdout đã được lưu và chuyển thành báo cáo tổng hợp cùng các ca sai theo ID. Các CSV và artifact nằm trong thư mục run cục bộ. [Kết quả T10](docs/T10_HOLDOUT.md) · [Phân tích lỗi T12](docs/T12_ERROR_ANALYSIS.md) · [Sáu ca demo có ảnh](docs/T13_DEMO.md)

Các điểm hỗ trợ chưa được hiệu chỉnh. Bộ dữ liệu nhỏ và quần thể Pima đặc thù hạn chế khả năng khái quát. Luật và CF phục vụ đối chứng trong đồ án. ILPD và CKD hiện không có luật đích. [Nguồn và ánh xạ luật](docs/T07_RULES.md) · [Đặc tả](docs/SPEC.md) · [Trạng thái](docs/STATUS.md)
