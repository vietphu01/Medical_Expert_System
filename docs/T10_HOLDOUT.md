# Kết quả đánh giá holdout đã khóa

Run `t10-test-seed42` dùng [cấu hình đã commit trước đánh giá](t10_lock.json) và mô hình T06 fit trên train. Chọn mô hình theo F1 validation trước khi chạy. Các giá trị dưới đây lấy từ `results/t10-test-seed42/metrics.csv`.

| Bộ | Mẫu holdout | Mô hình đã chọn | F1 | ROC-AUC | F1 baseline |
|---|---:|---|---:|---:|---:|
| Cleveland | 61 | Gaussian Naive Bayes | 0,5000 | 0,5335 | 0,0000 |
| Pima | 154 | K-Nearest Neighbors | 0,4948 | 0,7480 | 0,0000 |
| ILPD | 114 | Logistic Regression | 0,8342 | 0,6330 | 0,8308 |
| CKD | 80 | Decision Tree | 0,8913 | 0,8893 | 0,7692 |

| Bộ | Luật đích khớp | Âm / dương khi khớp | Trung bình điểm mới trừ điểm cũ | Chênh tuyệt đối lớn nhất | Đổi nhãn |
|---|---:|---:|---:|---:|---:|
| Cleveland | 27/61 (44,3%) | 12 / 15 | 0,0000 | 0,0000 | 0 |
| Pima | 50/154 (32,5%) | 18 / 32 | −0,0120 | 0,0551 | 0 |

Đã đối chiếu 3.314 dòng dự đoán và 380 dòng metric với ID holdout, điểm, nhãn và confusion matrix. Dự đoán chỉ luật để trống điểm và nhãn khi không có luật đích. Kết quả và mẫu được lưu cục bộ theo quyền phân phối của nguồn.

- SHA-256 `metrics.csv` là `283e57b2480b5ed826dc5bf9706f0090cad9bcc4591ddf7b69a5e90599fd7d25`.
- SHA-256 `predictions.csv` là `5ba8baa377a8828ce92cbd49af5e9f8d12d8b042af55cf989e9af8b6a00751c5`.
