# Luật và ngữ nghĩa dữ liệu

Các luật hỗ trợ đối chứng của đồ án. Đích là nhãn dương của từng bộ dữ liệu. Hệ số CF do đồ án đặt để kiểm tra cách gộp và đọc trace. Luật có đích trống chỉ mô tả một dấu hiệu phụ.

| Luật | Điều kiện trên dữ kiện gốc | Đích | CF | Căn cứ chọn điều kiện |
|---|---|---|---:|---|
| CLEV_TARGET_01 | Tuổi ≥55 và cholesterol toàn phần >200 mg/dL | Cleveland | 0,55 | Tuổi và cholesterol là yếu tố nguy cơ. Tuổi 55 là lựa chọn chung của đồ án vì schema không dùng giới tính. [NHLBI](https://www.nhlbi.nih.gov/health/coronary-heart-disease/risk-factors) · [MedlinePlus](https://medlineplus.gov/cholesterollevelswhatyouneedtoknow.html) |
| CLEV_SECONDARY_01 | Cholesterol toàn phần >200 mg/dL | Dấu hiệu phụ | 0,40 | Cùng chỉ số cholesterol, kể cả khi thiếu tuổi. [MedlinePlus](https://medlineplus.gov/cholesterollevelswhatyouneedtoknow.html) |
| PIMA_TARGET_01 | Tuổi 35–70 và BMI >25 kg/m² | Pima | 0,50 | Tiêu chí tuổi và thừa cân trong khuyến nghị sàng lọc được dùng làm dấu hiệu nguy cơ. [USPSTF](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/screening-for-prediabetes-and-type-2-diabetes) |
| PIMA_TARGET_02 | Tuổi 35–70 và BMI >30 kg/m² | Pima | 0,55 | Mốc BMI cao hơn để kiểm tra hai cách gộp khi tiền đề lồng nhau. [CDC](https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html) |

Hàm liên thuộc tuyến tính của cholesterol và BMI có tâm lần lượt ở 200, 25 và 30. Tại tâm, mức liên thuộc bằng 0,5, nên điều kiện dùng dấu `>` theo giao thức. Tuổi dùng điều kiện rời rạc. Dữ kiện thiếu tạo fact chưa biết. Hai luật Pima chia sẻ tuổi và ngưỡng BMI lồng nhau, vì vậy việc cả hai cùng khớp không chứng minh có hai nguồn bằng chứng độc lập.

- Cleveland chỉ ánh xạ tới nhãn bệnh tim của bộ Cleveland. Các kết luận cũ về nhồi máu cơ tim, cao huyết áp và rối loạn mỡ máu không có ánh xạ trực tiếp sang nhãn.
- Pima giữ glucose ngoài luật vì đơn vị cột chưa xác minh. Nhãn của bộ Pima và điều kiện sàng lọc có ngữ nghĩa riêng.
- ILPD chưa có luật đích do chưa xác minh đơn vị bilirubin và albumin. CKD chưa có luật đích do schema thiếu dữ kiện thời gian và chưa xác minh loại huyết áp. Trace giữ giá trị gốc của các trường này. [Hồ sơ T03](T03_DATA_SOURCES.md) · [Hồ sơ T05](T05_DATA_SOURCES.md) · [KDIGO](https://kdigo.org/guidelines/ckd-evaluation-and-management/)

| Dataset | Có luật đích khớp trên 5 fold validation | Tổng |
|---|---|---:|
| Cleveland | 21/49, 28/49, 23/48, 19/48, 21/48 | 112/242 |
| Pima | 32/123, 34/123, 45/123, 41/123, 45/122 | 197/614 |

Cả năm fold đều có ca khớp luật đích. Số liệu lấy từ các mẫu validation theo manifest và giá trị gốc của loader.
