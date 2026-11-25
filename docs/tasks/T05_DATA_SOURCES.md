# Xác minh ILPD và CKD

Đối chiếu ngày 18/11/2026. Cả hai bộ nguồn được UCI công bố theo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Repo lưu [metadata tổng hợp](../../manifests/t05_dataset_metadata.json) và [manifest ID](../../manifests/t05_split_manifest.json). SHA-256 của từng tệp nguồn nằm trong cả hai file. Hai nguồn không có cột ID bệnh nhân.

## ILPD

Dùng thành viên `Indian Liver Patient Dataset (ILPD).csv` của [kho nén UCI #225](https://archive.ics.uci.edu/static/public/225/ilpd+indian+liver+patient+dataset.zip). Đây là bản CSV 11 cột không có header. Thứ tự cột nằm trong [metadata UCI](https://archive.ics.uci.edu/api/dataset?id=225) và được ghi lại trong metadata T05. Trích dẫn: Ramana và Venkateswarlu (2022), DOI [10.24432/C5D02C](https://doi.org/10.24432/C5D02C).

- `TB → bilirubin` là bilirubin toàn phần, `ALB → albumin` là albumin. [Bảng biến của UCI](https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset) không nêu đơn vị của hai cột; metadata ghi `null`. `Age → age` tính bằng năm; nguồn mã hóa tuổi trên 89 thành 90.
- `Selector` có 416 giá trị `1` (bệnh gan) và 167 giá trị `2` (không bệnh gan); ánh xạ lần lượt sang 1 và 0. Tệp có 583 dòng, phù hợp mục *Instances* của UCI; đoạn giới thiệu ghi 584. Tệp có 4 ô thiếu ở `A/G Ratio` dù trang UCI ghi không có missing. Ba cột dùng cho ML đủ dữ liệu.
- Loader giữ dòng đầu trong mỗi nhóm trùng toàn bộ nội dung đã chuẩn hóa, gồm nhãn. Sau khi bỏ 13 dòng trùng còn 570 mẫu (164 âm, 406 dương). Không suy ra hai dòng có cùng ba đặc trưng là một người.

## CKD

Dùng [`data.csv` của UCI #336](https://archive.ics.uci.edu/static/public/336/data.csv), là bản CSV được trỏ đến từ [metadata UCI](https://archive.ics.uci.edu/api/dataset?id=336). Loader kiểm tra header và thứ tự 25 cột của bản này. Trích dẫn: Rubini, Soundarapandian và Eswaran (2015), DOI [10.24432/C5G020](https://doi.org/10.24432/C5G020).

- `sc → creatinine` là creatinine huyết thanh, mg/dL. `bp → bp` được [UCI](https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease) mô tả là huyết áp, mmHg. UCI chưa xác định đây là huyết áp tâm thu hay tâm trương. Có thể dùng giá trị gốc làm đặc trưng ML; chưa gán ngưỡng luật cho trường này. `age` tính bằng năm.
- `class` nhận `ckd → 1` và `notckd → 0`. Loader bỏ khoảng trắng ở hai đầu, kể cả tab, và nhận `NaN`, `?` hoặc ô rỗng là missing. Bộ nguồn có 400 dòng, không có dòng trùng toàn bộ, gồm 150 âm và 250 dương.
- Ba đặc trưng có 17 giá trị creatinine, 12 giá trị huyết áp và 9 giá trị tuổi bị thiếu. Loader để `None`; tiền xử lý ML học cách điền riêng từ train của từng fold.

## Tái lập

Đặt hai tệp nguồn ngoài repo. Chạy từ thư mục gốc với đường dẫn thực:

```bash
.venv/bin/python -B -m scripts.inspect_datasets \
  --ilpd "/path/to/Indian Liver Patient Dataset (ILPD).csv" \
  --ckd /path/to/data.csv > /tmp/t05_dataset_metadata.json
.venv/bin/python -B -m scripts.split_datasets \
  --ilpd "/path/to/Indian Liver Patient Dataset (ILPD).csv" \
  --ckd /path/to/data.csv --output /tmp/t05_split_manifest.json
cmp docs/t05_dataset_metadata.json /tmp/t05_dataset_metadata.json
cmp docs/t05_split_manifest.json /tmp/t05_split_manifest.json
```

Hai lệnh cũng nhận `--cleveland` và `--pima` để chạy cả bốn bộ cùng lúc. Split dùng [giao thức T04](T04_DATA_PIPELINE.md). Cả 5 fold của mỗi bộ đều có đủ hai lớp và giữ toàn bộ holdout bên ngoài.

| Bộ dữ liệu | Train (âm/dương) | Holdout (âm/dương) | Kích cỡ các fold validation |
|---|---:|---:|---|
| ILPD | 456 (131/325) | 114 (33/81) | 92, 91, 91, 91, 91 |
| CKD | 320 (120/200) | 80 (30/50) | 64, 64, 64, 64, 64 |
