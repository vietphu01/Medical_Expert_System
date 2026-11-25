# Đối chứng ML và luật trên validation

Lệnh dùng điểm ngoài fold của mô hình được chọn ở T06. Mỗi ID ở phần train xuất hiện một lần, với điểm từ mô hình của fold đã giữ ID đó ở validation. Luật nhận dữ kiện gốc từ loader.

```bash
.venv/bin/python -B -m scripts.validate_ablation \
  --cleveland /path/to/processed.cleveland.data \
  --pima /path/to/diabetes.arff
```

Kết quả nằm trong `results/t09-validation-seed42/`. `metrics.csv` chứa điểm trên toàn bộ validation và trên tập con có luật đích khớp. `predictions.csv` chứa cả bốn cấu hình theo ID, để trống điểm và nhãn ở cấu hình chỉ luật khi không có luật đích. `metadata.json` ghi nhãn tập con, độ bao phủ và chênh lệch giữa hai công thức.

| Bộ | Có luật đích khớp | Âm / dương trong tập con | Điểm mới trừ điểm cũ, trung bình toàn bộ | Chênh lệch tuyệt đối lớn nhất | Số ca đổi nhãn |
|---|---:|---:|---:|---:|---:|
| Cleveland | 112/242 (46,3%) | 43 / 69 | 0,0000 | 0,0000 | 0 |
| Pima | 197/614 (32,1%) | 92 / 105 | −0,0096 | 0,0551 | 0 |

Cleveland có một luật đích nên hai công thức cho cùng điểm. Pima có hai luật đích lồng nhau và công thức cũ có thể tính điểm ML hai lần. Với các CF hiện tại, khi có luật đích thì điểm đã đạt ngưỡng 0,5 theo cả hai cách. Các ca không khớp dùng cùng điểm ML. Vì vậy chênh lệch điểm không tạo ca đổi nhãn trong cấu hình này. Fixture kiểm tra thêm trường hợp CF nhỏ hơn có thể làm hai công thức đổi nhãn, cũng như tập con rỗng hoặc chỉ có một lớp. [Luật và ngưỡng](T07_RULES.md)
