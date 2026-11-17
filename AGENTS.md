# Hướng dẫn làm việc trong repo

Mục tiêu là hoàn thiện đồ án hệ chuyên gia kết hợp ML tự viết, có kết quả tái lập để làm báo cáo. Giữ Flask, SQLite và NumPy. Dùng dữ liệu thật cho tim mạch, tiểu đường, gan và thận. Làm phân tích đối chứng chuyên sâu trên Cleveland và Pima.

- [SPEC.md](docs/SPEC.md) quy định schema, chia dữ liệu, suy luận và định dạng kết quả.
- [TASKS.md](docs/TASKS.md) liệt kê task, phụ thuộc và tiêu chí nghiệm thu.
- [STATUS.md](docs/STATUS.md) ghi trạng thái, quyết định, bằng chứng và việc tiếp theo.

## Việc không được làm

- Không thêm tính năng ngoài task hoặc mở rộng phạm vi đồ án. Forward chaining nhiều tầng, calibration, nested CV và bootstrap nằm ngoài phạm vi. Fuzzy liên tục chỉ thuộc task tùy chọn T14.
- Không dùng tập test cuối để xem mẫu trong lúc phát triển, fit tiền xử lý, chọn đặc trưng hoặc mô hình, điều chỉnh ngưỡng/CF, sửa luật hay chọn ca demo. Sau khi tạo split, chỉ đọc dự đoán và metric test ở bước đánh giá cuối và phân tích lỗi sau đó. Không đổi split, seed hoặc loại mẫu test để cải thiện số liệu.
- Không sửa luật, mô hình hoặc ngưỡng sau khi đã xem kết quả test của đợt đó. Nếu phát hiện lỗi làm phép đo mất hiệu lực, ghi rõ lỗi và các kết quả bị ảnh hưởng trong STATUS trước khi xử lý. Mọi thay đổi phương pháp sau khi đã xem test cần giao thức đánh giá mới và ghi rõ giới hạn của kết quả cũ.
- Không dùng dữ liệu tổng hợp để báo cáo hiệu năng trên dữ liệu thật, điền số liệu chưa chạy hoặc che kết quả bất lợi. Không dùng dữ liệu test làm fixture hay snapshot cho kiểm thử ứng dụng.
- Không dùng DB thật để test, xóa lịch sử, dọn các thay đổi sẵn có hoặc stage file ngoài task. Không commit môi trường ảo, cache Python, DB chạy thử hoặc dữ liệu có điều khoản phân phối chưa rõ.

## Lệnh chạy và kiểm tra

Chạy từ thư mục gốc. Nếu chưa có môi trường, dùng Python 3.12 và `uv`.

```bash
uv venv --python 3.12 .venv
uv pip sync --python .venv/bin/python requirements.txt
```

Lệnh ứng dụng hiện tại là `.venv/bin/python app.py`. Cho tới khi T01 hoàn thành, chỉ chạy ứng dụng hoặc import `app` trong bản sao tạm vì bản hiện tại xóa bảng lịch sử khi khởi động. Với T01 và các bài test sau đó, cấu hình DB tạm.

Các lệnh sau là giao diện dự kiến, cần được bổ sung và kiểm tra trong T01–T10.

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m scripts.train --dataset all --seed 42
.venv/bin/python -m scripts.evaluate --run-id RUN_ID --split test
```

Thay `RUN_ID` bằng run ID của cấu hình đã khóa ở T10, sau khi T09 đạt tiêu chí. Các bước phát triển dùng fixture, CV hoặc validation.

## Quy trình từng task

1. Đọc SPEC, TASKS và STATUS. Giao mỗi agent một task có tiêu chí rõ. Kiểm tra `git status --short` và các phụ thuộc trước khi sửa.
2. Làm đúng phạm vi được giao, chạy kiểm thử liên quan và xuất CSV/JSON nếu task chạy thí nghiệm.
3. Người điều phối đọc diff, kể cả file mới. Kiểm tra đủ tiêu chí, đúng dữ liệu được phép dùng và không lẫn thay đổi của người khác. Xem diff đã stage trước khi commit riêng cho task.
4. Sau commit, cập nhật checkbox trong TASKS và ghi commit, lệnh đã chạy, pass/fail, đường dẫn kết quả và bước tiếp theo trong STATUS.

Một task được đánh dấu **xong** khi đạt toàn bộ tiêu chí trong TASKS, kiểm thử liên quan pass, kết quả thí nghiệm (nếu có) đã ghi ra CSV/JSON theo SPEC và người điều phối đã đọc diff. Với task tài liệu, kiểm tra liên kết, định dạng và tính nhất quán giữa các file.
