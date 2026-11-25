# Chia dữ liệu và tiền xử lý

[Manifest Cleveland/Pima](../../manifests/t04_split_manifest.json) lưu ID của holdout và từng phần train/validation trong 5 fold, kèm SHA-256 nguồn, thứ tự đặc trưng và seed. Mỗi dataset xuất hiện dưới một khóa riêng. Manifest không lưu giá trị đo, nhãn từng mẫu hay dự đoán.

Từ thư mục gốc, dùng đúng phiên bản nguồn trong [hồ sơ T03](T03_DATA_SOURCES.md). Lệnh chỉ ghi vào đường dẫn chưa tồn tại để tránh ghi đè manifest đã dùng.

```bash
.venv/bin/python -B -m scripts.split_datasets \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff \
  --output /tmp/t04_split_manifest.json
cmp docs/t04_split_manifest.json /tmp/t04_split_manifest.json
```

Holdout có `ceil(n/5)` mẫu, làm tròn phân bổ theo tỷ lệ nhãn và giữ đủ cả hai lớp trong holdout và từng fold. Trong mỗi lớp, thuật toán sắp xếp ID trước khi xáo bằng PCG64 seed 42. Các ID còn lại được phân lần lượt vào 5 fold, sao cho kích cỡ fold và số mẫu của mỗi lớp chênh nhau tối đa một mẫu. Hai bộ nguồn T03 không có mã bệnh nhân để chia theo nhóm.

| Bộ dữ liệu | Train (âm/dương) | Holdout (âm/dương) | Kích cỡ các fold validation |
|---|---:|---:|---|
| Cleveland | 242 (131/111) | 61 (33/28) | 49, 49, 48, 48, 48 |
| Pima | 614 (400/214) | 154 (100/54) | 123, 123, 123, 123, 122 |

`prepare_fold` chọn mẫu theo ID trong manifest. Mỗi lần fit học median từ phần train của fold, điền các giá trị thiếu trên bản sao rồi học mean và độ lệch chuẩn tổng thể. Phần validation dùng lại ba thống kê này. Cột hằng có scale 1; cột thiếu toàn bộ trong train báo lỗi với tên đặc trưng. Mẫu gốc giữ nguyên, kể cả các giá trị thiếu dành cho luật. Holdout chưa được tiền xử lý hay đánh giá trong T04.

[Kiểm thử tích hợp](../../tests/test_data_pipeline.py) dùng dữ liệu tự tạo theo các đặc điểm T03: mã Cleveland 4 vẫn thuộc lớp dương, missing trong cột ngoài schema được giữ nguyên ở bước nạp và không làm rơi mẫu, Pima lệch lớp và có số 0 thay cho glucose/BMI thiếu, các bản ghi có cùng ba đặc trưng vẫn có ID riêng. Kiểm thử thay riêng validation và holdout bằng các giá trị cực lớn để xác nhận thống kê fit và đầu ra train không đổi.
