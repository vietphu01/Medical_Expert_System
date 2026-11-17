# Xác minh Cleveland và Pima

Đối chiếu nguồn ngày 18/11/2026. Hai tệp chính thức được đọc trong thư mục tạm. Repo lưu loader, fixture tự tạo và thống kê tổng hợp. [Metadata JSON](t03_dataset_metadata.json)

## Cleveland

Dùng riêng thành viên `processed.cleveland.data` trong kho nén UCI Heart Disease #45, DOI `10.24432/C52P4X`, năm trích dẫn 1989. UCI công bố CC BY 4.0, cho phép chia sẻ và sửa đổi với ghi công thích hợp. [Bản ghi UCI](https://archive.ics.uci.edu/dataset/45/heart+disease) · [Kho nén và `heart-disease.names`](https://archive.ics.uci.edu/static/public/45/heart+disease.zip) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Tệp CSV có 14 cột, theo thứ tự `age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, num`. Loader xuất tuổi theo năm, huyết áp lúc nghỉ khi nhập viện theo mmHg và cholesterol huyết thanh theo mg/dL. Nhãn `num` ghi tình trạng bệnh tim theo chụp mạch. Mã 0 ánh xạ sang 0, các mã 1–4 ánh xạ sang 1.

Cả 303 dòng được giữ lại. Số mẫu theo mã 0–4 lần lượt là 164, 55, 36, 35 và 13, tương ứng 164 âm và 139 dương sau ánh xạ. Ký hiệu `?` xuất hiện 4 lần ở `ca` và 2 lần ở `thal`. Ba cột dùng cho mô hình đều đủ dữ liệu. Loader cũng nhận ô rỗng là missing.

## Pima

Dùng `diabetes.arff` của OpenML `diabetes` #37, version 1, tải lên ngày 06/04/2014. MD5 của tệp tải về khớp MD5 trong API OpenML. Tệp có relation `pima_diabetes`, tám cột `real` và nhãn nominal `class`. Loader kiểm tra đúng tên, thứ tự và kiểu cột của bản này. [Bản ghi OpenML](https://www.openml.org/d/37) · [Metadata bản phát hành](https://www.openml.org/api/v1/json/data/37) · [Metadata cột](https://www.openml.org/api/v1/json/data/features/37)

| Cột ARFF | Tên mô tả | Dùng trong đồ án |
|---|---|---|
| `preg` | Số lần mang thai | 0 là giá trị hợp lệ |
| `plas` | Glucose huyết tương hai giờ trong nghiệm pháp dung nạp glucose đường uống (OGTT) | `glucose`, đơn vị cột chưa được xác nhận |
| `pres` | Huyết áp tâm trương (mmHg) | Giữ cột khi xác định dòng trùng |
| `skin` | Độ dày nếp gấp da cơ tam đầu (mm) | Giữ cột khi xác định dòng trùng |
| `insu` | Insulin huyết thanh hai giờ (µU/mL) | Giữ cột khi xác định dòng trùng |
| `mass` | Chỉ số khối cơ thể (kg/m²) | `bmi` |
| `pedi` | Chỉ số tiền sử gia đình | Giữ cột khi xác định dòng trùng |
| `age` | Tuổi (năm) | `age` |
| `class` | `tested_negative` hoặc `tested_positive` | Lần lượt 0 và 1 |

Mô tả OpenML và danh sách biến đầu vào trong Smith và cộng sự (1988, trang 262) xác nhận phép đo glucose là glucose huyết tương hai giờ trong OGTT. Bài báo ghi mg/dL cho ngưỡng dùng để xác định kết cục. Hai tài liệu chưa nêu đơn vị riêng của cột `plas`. Vì vậy metadata để `feature_units.glucose` là `null`. Cần xác nhận đơn vị cột trước khi chuyển ngưỡng glucose vào luật hoặc cập nhật nhãn đơn vị trên form Pima. [OpenML #37](https://www.openml.org/api/v1/json/data/37) · [Smith và cộng sự (1988), trang 261–262](https://pmc.ncbi.nlm.nih.gov/articles/PMC2245318/)

OpenML ghi 768 nữ từ 21 tuổi trở lên có gốc Pima, thuộc quần thể được nghiên cứu gần Phoenix, Arizona. Bài báo mô tả một lần khám chỉ mục chưa mắc bệnh cho mỗi người, dự báo khởi phát trong năm năm và loại ca phát bệnh trong năm đầu. Bản OpenML mang nhãn `tested_negative` và `tested_positive`. Báo cáo nên gọi đây là nhãn của bộ dữ liệu và nêu quần thể nghiên cứu khi diễn giải kết quả. [OpenML #37](https://www.openml.org/api/v1/json/data/37) · [Smith và cộng sự (1988), trang 261–262](https://pmc.ncbi.nlm.nih.gov/articles/PMC2245318/)

Tệp có 500 mẫu âm và 268 mẫu dương, không có missing biểu diễn bằng `?` hay ô rỗng. Áp dụng quy ước hiệu chỉnh của `PimaIndiansDiabetes2` cho hai cột dùng trong mô hình, nên 5 số 0 ở `plas` và 11 số 0 ở `mass` trở thành missing. Số 0 ở `preg` vẫn hợp lệ. Bản nguồn còn có 35 số 0 ở `pres`, 227 ở `skin` và 374 ở `insu`. Các cột này nằm ngoài tập đặc trưng. [Quy ước missing của mlbench](https://search.r-project.org/CRAN/refmans/mlbench/html/PimaIndiansDiabetes.html)

OpenML hiển thị nhãn giấy phép `Public`. Điều khoản nền tảng mô tả quyền truy cập và sử dụng cho nghiên cứu riêng do người tải cấp, theo giấy phép người tải cấp và với điều kiện người tải có đủ quyền hoặc đồng thuận. Tài liệu hiện hành của `mlbench` ghi rằng UCI và `mlbench` đã ngừng phân phối dữ liệu gốc sau khi nhận được thông tin về khả năng dữ liệu được chia sẻ thiếu đồng thuận. Quyền của bên tải bản #37 và quyền tái phân phối tệp gốc vẫn chưa được xác minh. Repo chỉ giữ thống kê tổng hợp và đường dẫn nguồn. [Điều khoản OpenML](https://docs.openml.org/intro/terms/) · [Ghi chú về bộ gốc trong mlbench](https://cran.r-project.org/web/packages/mlbench/refman/mlbench.html#SynthDiabetes)

## Tái lập thống kê

Lấy thành viên `processed.cleveland.data` từ kho nén UCI. Để đối chiếu bản Pima, dùng đúng tệp ARFF OpenML #37 như trong metadata. Chạy từ thư mục gốc và thay hai đường dẫn đầu vào.

```bash
.venv/bin/python -B -m scripts.inspect_datasets \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff
```

`matches_verified_release` cho biết SHA-256 của tệp có khớp bản đã đối chiếu. `raw_rows`, `raw_label_counts`, `source_missing_by_column` và `zero_sentinel_by_column` được đếm trước khi loại trùng. `n_samples`, `label_counts` và `missing_by_feature` mô tả đầu ra loader. Cả hai tệp chính thức có 0 dòng trùng theo toàn bộ cột nguồn, gồm nhãn gốc. Nếu gặp dòng trùng, loader giữ dòng đầu. `sample_id` dùng thứ tự dòng dữ liệu trong cùng tệp, giữ nguyên cả khi một dòng trùng bị bỏ. Không có cột mã bệnh nhân trong hai tệp.
