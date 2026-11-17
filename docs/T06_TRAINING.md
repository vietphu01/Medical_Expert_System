# Huấn luyện và kiểm chứng chéo

Dùng bốn tệp nguồn có SHA-256 đã xác minh trong [T03](T03_DATA_SOURCES.md) và [T05](T05_DATA_SOURCES.md). Chạy từ thư mục gốc, thay các đường dẫn bằng tệp đã tải:

```bash
.venv/bin/python -B -m scripts.train --dataset all --seed 42 \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff \
  --ilpd "/path/to/Indian Liver Patient Dataset (ILPD).csv" \
  --ckd /path/to/data.csv
```

Lệnh cũng chấp nhận `--data-dir` nếu bốn tệp giữ nguyên tên nguồn. Mặc định kết quả nằm trong `results/t06-cv-seed42/`. Dùng `--run-id` để tạo lần chạy khác. Flask tự đọc run mặc định khi khởi động, hoặc đọc thư mục do `MEDICAL_MODEL_RUN` chỉ định.

Mỗi fold fit median, scaler và mô hình bằng train của fold. Chọn trong 5 mô hình theo F1 lớp dương trung bình của validation. Baseline dùng lớp phổ biến trong train của fold, hòa chọn 0. Gaussian NB tính mật độ trực tiếp trong không gian log để giá trị nhỏ vẫn tham gia tính điểm. Ensemble lấy trung bình điểm của bốn mô hình. Các mô hình được fit lại trên toàn bộ train để phục vụ đánh giá sau này và chạy ứng dụng.

| Bộ | Mô hình được chọn | F1 CV trung bình ± độ lệch chuẩn | F1 baseline |
|---|---|---:|---:|
| Cleveland | Gaussian Naive Bayes | 0,5868 ± 0,0263 | 0,0000 |
| Pima | K-Nearest Neighbors | 0,6655 ± 0,0644 | 0,0000 |
| ILPD | Logistic Regression | 0,8199 ± 0,0268 | 0,8323 |
| CKD | Decision Tree | 0,9352 ± 0,0189 | 0,7692 |

Baseline dự đoán 0 cho Cleveland/Pima nên F1 lớp dương bằng 0 và precision không xác định. Với ILPD, baseline dự đoán 1 cho mọi mẫu và có F1 cao hơn năm mô hình ứng viên. Kết quả trên là CV của phần train. Holdout dành cho T10.

- `metrics.csv` có kết quả từng fold và tổng hợp CV, trong đó confusion matrix tổng hợp là tổng số đếm của dự đoán ngoài fold.
- `predictions.csv` lưu dự đoán ngoài fold cho từng ID và mỗi mô hình. `metadata.json` ghi cấu hình, số mẫu, nguồn và nguyên nhân metric thiếu.
- `models.json` lưu trạng thái mô hình cùng bộ tiền xử lý; KNN cần lưu ma trận train đã biến đổi nên run chỉ lưu cục bộ. `split_manifest.json` sao lưu đúng các manifest T04–T05.
