# Ghi chú tổng hợp các điểm giá trị để đưa vào Báo cáo & Bảo vệ

*Tổng hợp đầy đủ đợt rà soát kiến trúc, kiểm định logic suy luận, sửa lỗi hệ chuyên gia–GUI và phân tích dữ liệu Train-Only (25/11/2026).*

Tài liệu này gom toàn bộ các phát hiện, cải tiến, con số đối chứng và lưu ý kỹ thuật đã kiểm chứng từ đầu đợt rà soát, sắp xếp theo từng chương/mục để có thể đưa thẳng vào báo cáo đồ án hoặc slide bảo vệ.

---

## 1. Đưa vào mục Kiến trúc phần mềm & Tổ chức dự án

### 1.1. Tái cấu trúc từ thư mục phẳng sang gói phân tầng một chiều (commit `a4bd87f`, `f88e037`)
- **Vấn đề ban đầu:** 13 tệp `.py` nằm phẳng ở thư mục gốc, trộn lẫn code chạy thật với nguyên mẫu cũ (`inference_engine.py`, `knowledge_base.json`), trộn tài liệu hướng dẫn với manifest JSON, và Git đang theo dõi nhầm 6 tệp `__pycache__/*.pyc` cùng `medical_history.db`.
- **Cấu trúc chuẩn hóa sau tái cấu trúc (74 tệp di chuyển/cập nhật, giữ nguyên 100% logic tại bước tái cấu trúc):**
  - `app.py` (gốc): điểm vào mỏng giữ nguyên lệnh chạy `python app.py` và `flask --app app run`.
  - `medical_expert/web/`: Flask API ([app.py](../../medical_expert/web/app.py)), cấu hình form ([diseases.py](../../medical_expert/web/diseases.py)), `templates/`, `static/`.
  - `medical_expert/data/`: nạp 4 nguồn dữ liệu ([loaders.py](../../medical_expert/data/loaders.py), [ilpd.py](../../medical_expert/data/ilpd.py), [ckd.py](../../medical_expert/data/ckd.py)), [registry.py](../../medical_expert/data/registry.py), chia tập & tiền xử lý ([pipeline.py](../../medical_expert/data/pipeline.py)).
  - `medical_expert/ml/`: thuật toán NumPy tự viết ([algorithms.py](../../medical_expert/ml/algorithms.py)), khôi phục artifact ([runtime.py](../../medical_expert/ml/runtime.py)), tính metric ([metrics.py](../../medical_expert/ml/metrics.py)).
  - `medical_expert/expert/`: luật mờ ([rules.py](../../medical_expert/expert/rules.py)), hàm liên thuộc ([fuzzy.py](../../medical_expert/expert/fuzzy.py)), gộp ML–Luật ([fusion.py](../../medical_expert/expert/fusion.py)).
  - `manifests/`: tách riêng split manifest, metadata nguồn và khóa T10 ([t10_lock.json](../../manifests/t10_lock.json)).
  - `legacy/`: cô lập nguyên mẫu cũ (`inference_engine.py`, `knowledge_base.json`) khỏi luồng thực thi chính.
  - `notebooks/`: chứa notebook phân tích dữ liệu tái lập ([eda_and_rule_mining.ipynb](../../notebooks/eda_and_rule_mining.ipynb)).
  - `docs/`: tách rõ `reports/` (báo cáo, vấn đáp), `tasks/` (ghi chú T03–T13), `v2/` (kế hoạch giai đoạn 2).
- **Quy ước phụ thuộc một chiều (không vòng lặp):** `web → expert, ml`; `ml → data`; `data` và `expert` hoàn toàn độc lập, giúp tách biệt rõ tầng giao diện với tầng thuật toán và dễ kiểm thử đơn vị.
- **Dọn repo & kiểm chứng không hồi quy:** Thêm `.gitignore`, gỡ `__pycache__/` và `medical_history.db` khỏi chỉ mục Git (`git rm --cached`, giữ nguyên tệp trên đĩa), không đưa thay đổi có sẵn của `legacy/knowledge_base.json` vào commit. Kết quả kiểm chứng: 50/50 test đạt cả trên bản xuất sạch từ Git, điểm ML 4 bộ trên đầu vào cố định giống hệt trước–sau, 358 liên kết Markdown nội bộ không hỏng, 5 script trong `scripts/` chạy `--help` ổn định, và 17/17 mã băm khóa T10 khớp nguyên vẹn tại commit `b24a03c` (bảng ánh xạ đường dẫn cũ → mới lưu ở [STATUS.md](../STATUS.md)).

---

## 2. Đưa vào mục Kiểm định logic suy luận & Cải tiến hệ chuyên gia

Đây là phần rất thuyết phục cho báo cáo vì thể hiện **tư duy phản biện và tự kiểm định lỗi logic** thay vì chỉ dừng ở mức "chạy ra số".

### 2.1. Năm nhóm lỗi logic đã phát hiện và khắc phục

| # | Lỗi / điểm vô lý ở bản V1 | Nguyên nhân gốc | Cách khắc phục đã triển khai |
|---|---|---|---|
| 1 | **Luật phủ quyết tuyệt đối ML** | Phép gộp $C_{\text{new}} = C_{\text{rule}} + p(1 - C_{\text{rule}})$ chỉ cộng dương, trong khi mọi luật đích có $\text{CF} \ge 0{,}50$ (trùng ngưỡng phân lớp $0{,}5$). Hễ khớp 1 luật, kể cả `ML = 0%` vẫn bị ép thành nhãn `1` (thoái hóa thành phép `OR`). | Giảm `base_cf = 0,35` (`< 0,5`) cho luật đích (`CLEV_TARGET_01`, `PIMA_TARGET_01`) và `0,30` cho luật phụ `CLEV_SECONDARY_01` trong [rules.py](../../medical_expert/expert/rules.py). Luật chỉ đẩy ca ML sát ngưỡng ($p \ge 23{,}1\%$) vượt ngưỡng dương, không còn phủ quyết ca ML rất thấp. |
| 2 | **Tính trùng bằng chứng (Double Counting) & cắt trần tuổi 70 ở Pima** | Hai luật BMI lồng nhau (`> 25`, CF 0,50 và `> 30`, CF 0,55) luôn cùng kích hoạt khi `BMI > 30`, áp công thức MYCIN (giả định độc lập) đẩy $C_{\text{rule}} = 0{,}775$. Mốc tuổi `35–70` khiến người `71–85` tuổi béo phì đột ngột mất hỗ trợ luật. | Gộp thành **1 luật mờ liên tục duy nhất** `bmi_elevated` trên `[25, 32]` và mở rộng `age_35_to_70` thành `age_at_least_35`. |
| 3 | **Hiệu ứng "giả mờ" (nhảy bậc tại biên)** | Tính độ liên thuộc $\mu$ nhưng cắt cứng `μ > 0,5` và không nhân $\mu$ vào CF. Trên Cleveland (`age=60, bp=135`), `chol = 200` cho `49,6%` (âm), tăng 1 đơn vị lên `chol = 201` nhảy vọt `+27,8%` thành `77,4%` (dương). | Chuyển sang **mờ liên tục**: luật kích hoạt khi $\alpha = \min(\mu_i) > 0$ và tính $\text{CF}_{\text{hiệu lực}} = \text{CF}_{\text{gốc}} \times \alpha$, lưu đủ `base_cf`, `degree`, `cf` trong trace và hiển thị `CF gốc × μ` trên UI. Trong [fuzzy.py](../../medical_expert/expert/fuzzy.py) xóa hàm chết `compute_fuzzy_facts()` và thêm kiểm tra `low < high` và `direction`. |
| 4 | **Mâu thuẫn nhãn ở lá hòa trong Decision Tree** | `DecisionTreeScratch._build()` dùng `np.argmax(dist)` ghi `class = 0` khi lá hòa `[1, 1]` (xuất hiện ở cây Pima), trong khi `predict()` so `d[1]/total >= 0,5` lại trả `1`. | Sửa thành `int(dist[1] >= dist[0])` trong [algorithms.py](../../medical_expert/ml/algorithms.py) để `export_rules()` và `predict()` khớp 100%. |
| 5 | **Lệch pha Backend – Form – SQLite – UI** | (a) Form CKD khóa `bp ∈ [90, 200]` trong khi trung vị train là `80` (`247/320` mẫu `< 90`) → quét lưới 3.360 điểm hợp lệ trên form CKD, **100% báo 100% bệnh**!<br>(b) `risk_level` trong SQLite tính theo `ml_prob` ngưỡng `0,4/0,7` lệch với kết quả kết hợp (`0,5/0,7`).<br>(c) Bỏ trống toàn bộ chỉ số (`null`) vẫn trả nhãn dương ở 3/4 bệnh (`Pima 57,1%`, `ILPD 67,5%`, `CKD 100%`) mà không có câu cảnh báo riêng.<br>(d) Code `fuzzy`/`healthy_params`/`sick_params`/`generate_dataset` chết trong `diseases.py` mâu thuẫn với `rules.py`; JS hardcode lại luật; `extra_facts` bị nuốt im lặng. | (a) Mở miền `bp` CKD về `[50, 200]` (mặc định `80`) trong [diseases.py](../../medical_expert/web/diseases.py) và dọn toàn bộ code/cấu hình chết.<br>(b) Đồng bộ `risk_level` theo `combined_score` ngưỡng `0,5/0,7` trong [app.py](../../medical_expert/web/app.py) (giữ nguyên schema 7 cột & cột `ml_prob`).<br>(c) UI [workspace.js](../../medical_expert/web/static/workspace.js) cảnh báo rõ khi chưa nhập chỉ số bệnh nhân nào (`Chưa nhập chỉ số bệnh nhân — điểm hiện tại chỉ phản ánh trung vị tập train`).<br>(d) `/api/diseases` trả `fact_specs` & `target_rules` làm nguồn chuẩn cho JS, trả `ignored_extra_facts` minh bạch và cập nhật mô tả 6 ca mẫu preset (`c1–c6`). |

### 2.2. Bằng chứng Trước → Sau trên các ca kiểm chứng cụ thể

| Ca kiểm chứng | Trước khi sửa (V1) | Sau khi sửa (Mờ liên tục) | Ý nghĩa |
|---|---|---|---|
| Cleveland `age=60, bp=135, chol=200 → 201` | `49,6% (âm)` → **`77,4% (dương)`** (nhảy `+27,8%`) | `58,4%` (`CF=17,5%`) → **`59,0%`** (`CF=18,4%`, tăng mượt `+0,6%`) | Hết lỗi nhảy bậc tại biên mờ |
| Cleveland `age=54, chol=200` (luật phụ) | Không kích hoạt (`μ = 0,5` bị cắt cứng) | Khớp `CLEV_SECONDARY_01` với `CF=15,0%` (`target=None`, không cộng điểm) | Luật phụ cũng mờ liên tục |
| **Ca 5 bảo vệ** — Pima `glucose=90, age=45, bmi=26,0` | `ML=14,3%` + `rule=50,0%` → **`57,1% (dương)`** | `ML=14,3%` + `rule=5,0%` ($\mu=14{,}3\%$) → **`18,6% (âm)`** | Luật mờ nhẹ không phủ quyết ML khi đường huyết bình thường |
| Pima `glucose=75, age=40, bmi=25,1` | `ML=0,0%` → **`50,0% (dương)`** | `ML=0,0%` + `rule=0,5%` → **`0,5% (âm)`** | Hết lỗi phủ quyết tuyệt đối khi `ML = 0%` |
| Pima `glucose=80, age=45, bmi=31,0` | `ML=14,3%` + 2 luật (`77,5%`) → **`80,7% (mức cao)`** | `ML=14,3%` + 1 luật (`30,0%`) → **`40,0% (âm)`** | Hết lỗi tính trùng 2 luật BMI lồng nhau |
| Pima `glucose=130, age=75, bmi=33,0` | `ML=28,6%`, **không khớp luật** (bị cắt trần 70) | `ML=28,6%`, luật `35,0%` → **`53,6% (dương)`** | Người cao tuổi được bao phủ, cộng hưởng đúng ở ca sát ngưỡng |
| CKD `creatinine=0,5, bp=80, age=30` | **Bị form cấm nhập** (`bp < 90`); mọi điểm nhập được đều ra `100%` | Hợp lệ → **`0,0% (âm)`** (mặc định `1,2 / 80 / 45` → `15,2%`) | Form CKD phản ánh đúng cả lớp âm và lớp dương |
| Bỏ trống toàn bộ (`all null`) | Pima `57,1%`, ILPD `67,5%`, CKD `100%` (không cảnh báo riêng) | Vẫn trả điểm trung vị theo đặc tả, kèm **câu cảnh báo rõ ngay dòng kết luận** | Tránh người dùng hiểu nhầm form trống là chẩn đoán dương |

- **Kiểm thử tự động:** Tăng từ `50/50` lên **`54/54` đạt** (bổ sung [test_decision_tree.py](../../tests/test_decision_tree.py) cho lá hòa `DecisionTreeScratch` & biên `fuzzy_membership`, mở rộng kiểm thử cho schema luật API, CKD `bp=80`, `risk_level` SQLite, `ignored_extra_facts` và preview mờ liên tục).

---

## 3. Đưa vào mục Phân tích dữ liệu chuyên sâu (Train-Only EDA) & Đề xuất hướng V2

Toàn bộ bảng biểu và đồ thị tái lập được lưu trong [notebooks/eda_and_rule_mining.ipynb](../../notebooks/eda_and_rule_mining.ipynb) (13 cell, đã kiểm tra cú pháp 6/6 cell code; chạy được sau khi cài `pandas`, `matplotlib`, `ipykernel` vào `.venv`). **Tuyệt đối chỉ sử dụng tập train (`train_ids`) và dự đoán ngoài fold (OOF validation) từ `results/t06-cv-seed42`, không chạm tập holdout `t10-test-seed42`.**

### 3.1. Những phát hiện quan trọng từ phân phối 4 bộ dữ liệu

1. **Cleveland ($n_{\text{train}}=242$, nền $45{,}9\%$ dương):**
   - Thứ bậc tách lớp đơn biến: `age` (`AUC = 0,649`) > `bp` (`AUC = 0,607`, tăng đơn điệu từ `36%` lên `72%`) > `chol` (`AUC = 0,584`, yếu nhất).
   - **Phát hiện bất ngờ:** Khoảng `chol (200, 220]` có tỷ lệ dương chỉ **`32%`** ($n=41$), thấp hơn cả `≤ 200` (`43%`). Rủi ro `chol` trên tập này chỉ vượt nền từ **`> 240 mg/dL`** (`age ≥ 55 & chol > 240` đạt `68,1%`). Trong khi đó, `bp` đã xác minh đơn vị `mmHg` lại chưa được đưa vào luật (`age ≥ 55 & bp ≥ 130` đạt `66,7%`, `bp > 150` đạt `72%`).
   - **Ba hành vi phi đơn điệu (ngược trực giác y khoa) của Gaussian NB do chênh phương sai (`var_0` vs `var_1`):**
     - `age` (`var_0 = 1,110 > var_1 = 0,739`): giữ `bp=130, chol=240`, xác suất đạt `53,8%` ở tuổi 65 nhưng tụt còn `47,5%` ở tuổi 75 và **`28,5%` ở tuổi 85**.
     - `chol` (`var_0 = 1,062 > var_1 = 0,904`, do ngoại lai lớp âm tới `564 mg/dL`): giữ `age=60, bp=135`, xác suất ở `chol=320` là `59,2%` nhưng tăng lên `chol=400` tụt còn **`54,3%`**.
     - `bp` (`var_1 = 1,183 > var_0 = 0,760`): dạng chữ U — ở `age=55, chol=240`, `bp=110` cho `41,8%` nhưng hạ xuống `bp=90` lại tăng ngược lên **`52,6%`**.
2. **Pima ($n_{\text{train}}=614$, nền $34{,}9\%$ dương):**
   - `glucose` áp đảo tuyệt đối (`AUC = 0,805`: `≤ 100` chỉ `7%` dương, `> 160` tới `82%`), vượt xa `bmi` (`0,680`) và `age` (`0,680`).
   - **Phát hiện lệch mốc quần thể:** Khoảng `BMI (25, 28]` chỉ có **`20%`** dương (thấp hơn nền $34{,}9\%$); rủi ro thực tế nhảy bậc từ **`BMI ≥ 30`** (`46%`) và **`age ≥ 30`** (`52%`, sớm hơn mốc 35 — trung vị tuổi của 76 ca FN từ KNN chính là `32,0`).
   - **Nguồn gốc dương giả (FP) khi luật bỏ `glucose`:** Nhóm `glucose ≤ 100 & age ≥ 35 & bmi > 25` có tỷ lệ mắc chỉ **`14,7%`** ($5/34$), còn nhóm `glucose ≤ 100 & bmi < 30` chỉ **`2,5%`** ($2/79$).
3. **ILPD ($n_{\text{train}}=456$, nền $71{,}3\%$ dương):**
   - `bilirubin ≥ 2,5` đạt **`95,7%`** dương ($112/117$), nhưng biến này lệch phải cực mạnh (`median = 1,0`, `max = 75,0`). Chuẩn hóa z-score tuyến tính nén vùng bình thường lại quá sát, cộng với lệch lớp `71,3%` làm Logistic Regression có `bias = +1,076` và chỉ nhận đúng **`6/131` ca âm (`FP = 125`)** — ngay cả ca có chỉ số bình thường (`bilirubin=0,8, albumin=4,5, age=30`) đã ra `50,4%` (dương), mặc định form (`1,0 / 4,0 / 45`) ra `60,9%`.
   - Vùng bảo vệ `bilirubin ≤ 1,2 & albumin ≥ 3,5 & age ≤ 30` hạ tỷ lệ dương xuống **`40,0%`** ($16/40$), là tín hiệu cốt lõi để giảm FP.
4. **CKD ($n_{\text{train}}=320$, nền $62{,}5\%$ dương):**
   - Hai quy tắc cực sắc trong dữ liệu: `creatinine > 1,3 mg/dL` đạt **`100%` dương ($152/152$)** và `bp > 80 mmHg` đạt **`100%` dương ($73/73$)**.
   - Toàn bộ 120 ca âm tính đều có `bp ∈ [60, 80]` (làm tròn chục), là bằng chứng thống kê rất mạnh cho thấy cột `bp` của CKD là huyết áp tâm trương.
   - **Lá overfit 1 mẫu trong cây CKD V1:** Cây có 1 lá `dist = [1, 0]` ở dải rất hẹp `1,2 < creatinine ≤ 1,3` và `age > 71` (do `max_depth = 4` không giới hạn `min_samples_leaf`), dẫn đến nhập `creatinine=1,25, bp=200, age=75` lại trả **`0,0%`** dù huyết áp 200 mmHg.
   - 19 ca âm giả (FN) của cây quyết định đều nằm trong vùng `creatinine ≤ 1,2 & bp ≤ 80` (CKD giai đoạn sớm), là giới hạn bất khả kháng nếu chỉ dùng 3 đặc trưng.

### 3.2. Bảng đối chứng miền nhập Form vs Dữ liệu Train thực tế (giới hạn GUI so với Loader)

Sau khi mở `ckd.bp` về `[50, 200]` (`0` mẫu ngoài miền, trước đó là `247/320`), thống kê số mẫu train nằm ngoài miền nhập của form ở các trường còn lại (dùng cho mục Giới hạn phần mềm):

| Trường | Miền Form hiện tại | Miền thực tế trên Train | Số mẫu Train ngoài miền Form |
|---|---|---|---|
| `cleveland.chol` | `[150, 400]` | `[131,0 ; 564,0]` | 4 dưới, 4 trên / 242 |
| `pima.glucose` | `[70, 250]` | `[44,0 ; 199,0]` | 9 dưới / 614 |
| `pima.bmi` | `[15, 50]` | `[18,2 ; 67,1]` | 6 trên / 614 |
| `ilpd.bilirubin` | `[0,3 ; 10]` | `[0,4 ; 75,0]` | **42 trên / 456 (~9,2%)** |
| `ilpd.albumin` | `[2 ; 6]` | `[0,9 ; 5,5]` | **27 dưới / 456 (~5,9%)** |
| `ilpd.age` | `[20, 85]` | `[4,0 ; 90,0]` | 22 dưới, 1 trên / 456 |
| `ckd.creatinine` | `[0,4 ; 10]` | `[0,4 ; 76,0]` | 1 dưới, 19 trên / 320 |
| `ckd.age` | `[20, 85]` | `[2,0 ; 90,0]` | 18 dưới (gồm 7 ca nhi ≤ 11 tuổi), 1 trên / 320 |
| `ckd.bp` *(đã sửa)* | `[50, 200]` | `[50,0 ; 180,0]` | **0 / 320** *(trước là 247 / 320)* |

### 3.3. Bảng số liệu đối chứng 5-Fold CV (OOF Validation)

| Bộ dữ liệu | Phương án | F1 ($\pm$ std) | Accuracy | Precision | Recall | ROC-AUC | FP / FN / TN |
|---|---|---:|---:|---:|---:|---:|---|
| **Pima** ($n=614$) | ML thuần (KNN $k=7$) | $0{,}6655 \pm 0{,}0644$ | 0,775 | 0,690 | 0,645 | 0,812 | 62 / 76 / 338 |
| | Luật V1 cũ (lồng BMI, cắt cứng) | $0{,}6654 \pm 0{,}0567$ | 0,726 | 0,586 | 0,776 | 0,795 | **120** / 48 / 280 |
| | **Luật mờ liên tục hiện tại** | **$0{,}6840 \pm 0{,}0452$** | 0,762 | 0,639 | 0,739 | 0,814 | **90** / 56 / 310 |
| | Hướng V2: Theo data (không glucose, 2 chiều) | **$0{,}6927 \pm 0{,}0378$** | 0,770 | 0,650 | 0,743 | 0,816 | **86** / 55 / 314 |
| | Hướng V2: Theo data (có glucose, 2 chiều) | **$0{,}7020 \pm 0{,}0662$** | **0,777** | 0,660 | 0,753 | **0,830** | **84** / 53 / 316 |
| **Cleveland** ($n=242$) | ML thuần (Gaussian NB) | $0{,}5868 \pm 0{,}0263$ | 0,640 | 0,621 | 0,559 | 0,662 | 38 / 49 / 93 |
| | Luật V1 cũ | $0{,}6355 \pm 0{,}0503$ | 0,636 | 0,588 | 0,693 | 0,682 | 54 / 34 / 77 |
| | **Luật mờ liên tục hiện tại** | **$0{,}6382 \pm 0{,}0515$** | 0,640 | 0,592 | 0,693 | 0,678 | 53 / 34 / 78 |
| | Hướng V2: Theo data (`+bp`, dời `chol`, 2 chiều) | $0{,}6342 \pm 0{,}0419$ | **0,653** | **0,614** | 0,657 | **0,680** | **46** / 38 / 85 |
| **ILPD** ($n=456$) | ML thuần (Logistic Reg) | $0{,}8199 \pm 0{,}0268$ | 0,699 | 0,714 | 0,963 | 0,705 | 125 / 12 / **6** |
| | Hướng V2: Luật 2 chiều (thêm vùng bảo vệ) | $0{,}8185 \pm 0{,}0239$ | **0,708** | **0,735** | 0,923 | **0,719** | **108** / 25 / **23** |
| **CKD** ($n=320$) | ML thuần (Decision Tree) | $0{,}9352 \pm 0{,}0189$ | 0,922 | 0,968 | 0,905 | 0,934 | 6 / 19 / 114 |
| | Hướng V2: Luật `creatinine + bp` | $0{,}9352 \pm 0{,}0189$ | 0,922 | 0,968 | 0,905 | **0,937** | 6 / 19 / 114 |

**Ba luận điểm đắt giá rút từ bảng trên để viết chương Thảo luận:**
1. *Chỉ riêng việc bỏ cắt cứng sang mờ liên tục và hạ CF chống phủ quyết (không thêm biến mới)* đã kéo F1 Pima từ `0,6654 → 0,6840` và giảm `30 FP` (`120 → 90`), khắc phục nhược điểm tụt Accuracy của bản V1.
2. *Hệ luật một chiều chỉ tăng Recall và đẩy FP lên cao; bổ sung luật bằng chứng âm (phép gộp 2 chiều `CF ∈ [-1, 1]`)* là chìa khóa giảm FP rõ rệt trên cả Cleveland (`54 → 46`), Pima (`120 → 84`) và tăng gần 4 lần `TN` trên ILPD (`6 → 23`).
3. *Mức tăng hiệu năng phụ thuộc mạnh vào mức độ xác minh ngữ nghĩa đặc trưng:* Khi đưa `glucose` vào luật Pima (chỉ áp dụng sau khi xác minh đơn vị hoặc ghi rõ ngưỡng thực nghiệm theo quần thể train), cả F1, Accuracy lẫn ROC-AUC đều vượt trội ML thuần.

---

## 4. Lưu ý thuật toán tự viết, vận hành & Kỷ luật thực nghiệm (Ghi điểm phản biện)

### 4.1. Chi tiết cài đặt thuật toán tự viết nên biết khi vấn đáp
- **`KNNScratch` ([algorithms.py](../../medical_expert/ml/algorithms.py)):** Dùng `np.argsort` mặc định (`quicksort`, không ổn định khi các điểm có khoảng cách bằng nhau).
- **`DecisionTreeScratch` ([algorithms.py](../../medical_expert/ml/algorithms.py)):** Thử ngưỡng tách tại đúng giá trị quan sát `X[:, f] <= t` (thay vì trung điểm hai điểm liên tiếp) và `export_rules()` in ngưỡng trong không gian **z-score đã chuẩn hóa** chứ không phải đơn vị gốc. Đã sửa dứt điểm lỗi bất nhất nhãn tại lá hòa.
- **Môi trường & dữ liệu nguồn hiện tại:** `.venv` đang cài `Flask 3.1.3` và `NumPy 2.5.5`; cần cài thêm `pandas`, `matplotlib`, `ipykernel` vào `.venv` để chạy notebook. Repo hiện chưa có thư mục `data/` chứa các tệp nguồn đầy đủ cột (nên EDA mới dừng ở 3 đặc trưng đã trích xuất; khi có tệp `processed.cleveland.data` gốc mới chạy tiếp đối chứng 4 biến `thalach` của V2-04).

### 4.2. Ranh giới hiệu lực kết quả (theo quy định [AGENTS.md](../../AGENTS.md))
Khi trình bày trong báo cáo hoặc trả lời hội đồng, **bắt buộc tách bạch hai mốc**:
1. **Mốc V1 đã khóa (commit `b24a03c` / `f88e037`):** Toàn bộ số liệu holdout độc lập trong `results/t10-test-seed42`, [khóa T10](../../manifests/t10_lock.json) và kịch bản Ca 5 cũ (`14,3% → 57,1%`) trong [GHI_CHU_BAO_VE.md](GHI_CHU_BAO_VE.md) chỉ áp dụng cho bản V1 này.
2. **Mốc cải tiến logic suy luận & EDA (25/11/2026):** Mọi điều chỉnh luật mờ liên tục, hạ `CF`, sửa lá hòa Decision Tree và thử nghiệm luật theo dữ liệu đều **chỉ quan sát và đối chứng trên tập train / 5-fold CV (OOF)**. Nhóm **không dùng lại số liệu holdout V1** để báo cáo cho phiên bản mới nhằm tránh data leakage; nếu dùng bản luật mới để bảo vệ cần cập nhật lại lời thoại Ca 5 trong [GHI_CHU_BAO_VE.md](GHI_CHU_BAO_VE.md) và lập giao thức đánh giá mới độc lập.

---

## 5. Tài liệu & bằng chứng liên quan trong repo

- [Trạng thái dự án & lịch sử thay đổi](../STATUS.md)
- [Notebook phân tích dữ liệu & biểu đồ tái lập](../../notebooks/eda_and_rule_mining.ipynb)
- [Báo cáo dự án V1 đầy đủ](BAO_CAO_DU_AN.md) · [Sổ tay bảo vệ](GHI_CHU_BAO_VE.md) · [Bộ câu hỏi vấn đáp](VAN_DAP_BAO_VE.md)
