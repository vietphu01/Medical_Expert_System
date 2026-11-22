# Sáu ca demo hệ chuyên gia

Các đầu vào dưới đây được tạo để minh họa hành vi của ứng dụng với mô hình đã huấn luyện trong `results/t06-cv-seed42`. Các phần trăm là điểm hỗ trợ cho lớp 1 của bộ dữ liệu. Năm ca hợp lệ trả HTTP 200 và ca nhập ngoài miền trả HTTP 400.

## Chạy lại demo

Từ thư mục gốc của repo, khởi động Flask với một cơ sở dữ liệu tạm. Nếu chưa có artifact mô hình, làm theo [hướng dẫn T06](T06_TRAINING.md) để huấn luyện.

```bash
demo_db_dir=$(mktemp -d)
MEDICAL_HISTORY_DB="$demo_db_dir/history.sqlite" \
  MEDICAL_MODEL_RUN=results/t06-cv-seed42 \
  .venv/bin/python -B -m flask --app app run --host 127.0.0.1 --port 5000
```

Mở [ứng dụng cục bộ](http://127.0.0.1:5000), chọn **Đổi ca** rồi chọn một ca minh họa; hệ thống tự điền và chạy. Cũng có thể chọn nhóm bệnh, nhập tay các giá trị trong bảng rồi bấm **Chạy suy luận**. Ở ca 2, để trống hoặc chọn **Chưa biết** cho cholesterol. Dừng Flask bằng Ctrl+C sau khi trình bày.

## Đầu vào và kết quả

| Ca | Đầu vào | Kỳ vọng | Kết quả quan sát |
|---|---|---|---|
| 1. Hợp lệ | Tim mạch · Tuổi 60, huyết áp 135 mmHg, cholesterol 230 mg/dL | Hiện trace. Chỉ luật cùng đích được gộp. | `CLEV_TARGET_01` được gộp, `CLEV_SECONDARY_01` hiện là luật phụ. ML 53,95%, luật 55%, kết hợp 79,28%, nhãn 1. [Ảnh ca 1](demo/01-hop-le.png) |
| 2. Thiếu dữ kiện | Tim mạch · Tuổi 60, huyết áp 135 mmHg, cholesterol để trống | ML dùng giá trị điền từ train. Fact cholesterol ở trạng thái chưa biết. | `chol_elevated` có mức liên thuộc và giá trị boolean là `null`. Không có luật đích khớp. ML và kết hợp đều 55,43%, nhãn 1. [Ảnh ca 2](demo/02-thieu-du-kien.png) |
| 3. Sát ngưỡng fuzzy | Tim mạch · Tuổi 60, huyết áp 135 mmHg, cholesterol 200 mg/dL | Ở đúng trung điểm của đoạn 180–220 mg/dL, fact là sai theo điều kiện liên thuộc > 0,5. | `chol_elevated` có mức liên thuộc 50% và boolean `false`. Không có luật đích khớp. ML và kết hợp đều 49,59%, nhãn 0. [Ảnh ca 3](demo/03-nguong-fuzzy.png) |
| 4. Nhiều luật đích | Tiểu đường · Tuổi 45, glucose OGTT 175, BMI 33 kg/m² | Hai luật BMI cùng khớp và gộp với một điểm ML. | `PIMA_TARGET_01` (CF 0,50) và `PIMA_TARGET_02` (CF 0,55). ML 71,43%, luật 77,50%, kết hợp 93,57%, nhãn 1. [Ảnh ca 4](demo/04-hai-luat-dich.png) |
| 5. ML bất đồng luật | Tiểu đường · Tuổi 45, glucose OGTT 90, BMI 26 kg/m² | ML dưới ngưỡng 0,5 và luật đích đạt ngưỡng 0,5. | ML 14,29% cho nhãn 0. `PIMA_TARGET_01` cho điểm luật 50%, tương ứng nhãn 1. Điểm kết hợp 57,14%, nhãn 1. [Ảnh ca 5](demo/05-ml-bat-dong-luat.png) |
| 6. Ngoài miền nhập | Tim mạch · Tuổi 60, huyết áp 135 mmHg, cholesterol 900 mg/dL | Báo lỗi tại ô cholesterol và ẩn kết quả. | Giao diện đánh dấu ô cholesterol. Phản hồi `inputs.chol` nêu miền hợp lệ 150–400 mg/dL. [Ảnh ca 6](demo/06-ngoai-mien.png) |

Giao diện hiện điểm làm tròn đến một chữ số thập phân. Với ca 5, phần kết quả hiển thị 14,3% (ML) → 57,1% (ML + luật); mở **Vì sao điểm tăng?** để xem lời giải thích và **Chi tiết kỹ thuật** để xem điểm luật, công thức, fact và mã luật. Các ảnh trên được chụp ở phiên bản giao diện trước, dùng để đối chiếu nội dung ca.
