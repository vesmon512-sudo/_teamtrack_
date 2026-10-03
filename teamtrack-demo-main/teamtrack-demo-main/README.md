# TeamTrack — Nền tảng quản lý bài tập nhóm dành cho sinh viên

## 1. Mục đích ứng dụng

Làm việc nhóm là hình thức học tập phổ biến ở các trường đại học Việt Nam, nhưng thường gặp 3 vấn đề:

- **Thiếu quy chuẩn**: sinh viên giao việc theo cảm tính, không có khung kế hoạch chuẩn (template) cho các dạng bài phổ biến như thuyết trình, tiểu luận, NCKH.
- **Thông tin phân mảnh**: tài liệu, link họp, deadline nằm rải rác trên Zalo, Messenger, Drive, Notion...
- **Khó đo lường đóng góp**: khó định lượng khối lượng và thái độ làm việc của từng thành viên, gây bất công khi chia điểm nhóm.

**TeamTrack** giải quyết bằng một không gian làm việc tập trung: quản lý đa dự án, lộ trình chuẩn hóa theo template, phân việc dạng Kanban, nộp minh chứng có thưởng đúng hạn, và **tính điểm đóng góp tự động - minh bạch** theo công thức nhóm tự định nghĩa, xuất báo cáo nộp giảng viên.

## 2. Tech stack

| Thành phần | Công nghệ | Ghi chú |
|---|---|---|
| Frontend | HTML + CSS thuần | Jinja2 template, không dùng JS framework, theo phong cách thiết kế Bento |
| Backend | Python 3.14 + Flask | 1 file `app.py` (~400 dòng), route rõ ràng, dễ đọc |
| Database | MySQL 8.4 | 8 bảng InnoDB, kết nối qua PyMySQL |
| WSGI server | Gunicorn | 2 worker, chạy dưới systemd |
| Reverse proxy | Caddy | Tự động xin/gia hạn chứng chỉ Let's Encrypt |
| Public access | Cloudflare Tunnel | HTTPS + cert công khai hợp lệ không cần mở port |
| Hệ điều hành | Ubuntu (server) | Các service chạy qua systemd, tự khởi động khi reboot |

## 3. Chức năng chính

1. **Đăng nhập & hồ sơ sinh viên** — email + mật khẩu (werkzeug hash), hiển thị MSSV, trường, vai trò, điểm uy tín, streak.
2. **Dự án của tôi (đa dự án)** — danh sách dự án kèm tiến độ, deadline, vai trò trong nhóm; tạo dự án mới chọn template.
3. **Bento Dashboard** — tiến độ %, đếm ngược deadline, mục tiêu điểm, Gantt 4 giai đoạn, milestones, thành viên & leaderboard.
4. **Masterplan & Template** — 4 mẫu lộ trình chuẩn (Thuyết trình 🎤, SV NCKH 🔬, Tiểu luận 📝, Tự tạo 💼), mỗi mẫu 4 giai đoạn kèm deliverables, tự sinh milestone khi tạo dự án.
5. **Họp & Kho tài liệu** — lên lịch họp kèm link Google Meet + agenda; lưu tài liệu minh chứng nhóm.
6. **Kanban & nộp bài** — 4 cột (To-Do / In Progress / Review / Done), Task Points theo độ khó, nộp link minh chứng, tự cộng +10% nếu nộp trước hạn.
7. **Contribution** — công thức tùy chỉnh (Workload % + On-time % + Peer Review % + Leader Bonus 0/5/10%), tính % đóng góp từng thành viên tự động, cập nhật real-time.
8. **Leaderboard & Báo cáo GV** — xếp hạng MVP, trang báo cáo in/xuất PDF (Ctrl+P) kèm bảng đóng góp và ô chữ ký trưởng nhóm.

## 4. Cấu trúc mã nguồn

```
webapp/
├── app/
│   ├── app.py            # Flask app: routes + logic (đơn giản, 1 file)
│   ├── db.py             # Helper kết nối MySQL (PyMySQL)
│   ├── schema.sql        # DDL: tạo DB, 8 bảng, user MySQL
│   ├── seed.py           # Dữ liệu mẫu: 4 user, 3 dự án, 30 task...
│   ├── requirements.txt  # flask, PyMySQL, gunicorn
│   ├── templates/        # 8 trang .html (base, login, dashboard, project,
│   │                     #   tasks, contribution, meetings, report)
│   └── static/style.css  # Toàn bộ CSS (không dùng CSS framework)
├── deploy/
│   └── enable-tls.sh     # Bật HTTPS cho domain (Caddy auto Let's Encrypt)
├── README.md             # File này
└── BAO_CAO.md            # Báo cáo chi tiết nộp môn
```

## 5. Hướng dẫn chạy app trên localhost

### 5.1. Yêu cầu môi trường

Trước khi bắt đầu, máy bạn cần có:

| Phần mềm | Phiên bản khuyến nghị | Cách kiểm tra đã cài |
|---|---|---|
| Python | 3.12 trở lên | `python3 --version` |
| MySQL Server | 8.x | `mysql --version` |
| pip | đi kèm Python | `pip3 --version` |

- **Chưa cài Python?** Tải tại [python.org/downloads](https://www.python.org/downloads/) (Ubuntu thường có sẵn).
- **Chưa cài MySQL?**
  - Ubuntu/WSL: `sudo apt update && sudo apt install mysql-server`
  - Windows/macOS: tải [MySQL Installer](https://dev.mysql.com/downloads/installer/)

### 5.2. Tạo database

Mở terminal, di chuyển vào thư mục dự án rồi chạy file `schema.sql` để tạo database `teamtrack` cùng 8 bảng:

```bash
cd webapp            # vào thư mục dự án (nếu chưa ở trong)
mysql -u root -p < app/schema.sql
```

- Lệnh sẽ hỏi mật khẩu root của MySQL bạn đã đặt khi cài.
- Nếu MySQL yêu cầu mật khẩu mạnh, hoặc bạn muốn dùng user riêng thay vì `root`, hãy chạy các lệnh SQL sau trong `mysql -u root -p` (thay `<mật-khẩu>` bằng mật khẩu bạn muốn — **phải trùng** với `TT_DB_PASSWORD` ở bước sau):

```sql
CREATE USER IF NOT EXISTS 'tt_user'@'localhost' IDENTIFIED BY '<mật-khẩu>';
GRANT ALL PRIVILEGES ON teamtrack.* TO 'tt_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5.3. Cài Python dependency

```bash
cd app
python3 -m venv .venv          # tạo môi trường ảo (chỉ cần làm 1 lần)
.venv/bin/pip install -r requirements.txt
```

> Trên Windows dùng Git Bash/PowerShell: `.venv\Scripts\pip install -r requirements.txt`

### 5.4. Cấu hình biến môi trường

Copy file mẫu `.env.example` thành `.env` rồi điền giá trị thật:

```bash
cp .env.example .env
```

Mở `.env` và sửa 2 dòng quan trọng nhất:

```env
TT_DB_PASSWORD=<mật-khẩu-đã-đặt-ở-bước-5.2>
TT_SECRET_KEY=<chuỗi ngẫu nhiên, tạo bằng: python3 -c "import secrets; print(secrets.token_hex(32))">
```

> ⚠️ File `.env` chứa mật khẩu — đã được đưa vào `.gitignore`, **không commit** lên git.

### 5.5. Nạp dữ liệu mẫu

Tạo 4 user demo, 3 dự án và ~30 task để có dữ liệu xem ngay:

```bash
.venv/bin/python seed.py
```

### 5.6. Chạy server

```bash
.venv/bin/flask --app app run --port 5000
```

Mở trình duyệt và truy cập: **http://127.0.0.1:5000** — đăng nhập bằng tài khoản demo ở [mục 6](#6-tài-khoản-demo) (ví dụ `maianh.k62@neu.edu.vn` / `123456`).

> Nếu thấy `Running on http://127.0.0.1:5000` trong terminal là server đã chạy thành công. Nhấn `Ctrl+C` để dừng.

### 5.7. Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân & cách sửa |
|---|---|
| `Access denied for user 'tt_user'@'localhost'` | Mật khẩu trong `.env` khác với mật khẩu MySQL. Sửa lại `TT_DB_PASSWORD` (bước 5.4) hoặc tạo lại user (bước 5.2). |
| `Unknown database 'teamtrack'` | Chưa chạy `schema.sql` — quay lại bước 5.2. |
| `Can't connect to MySQL server` | MySQL chưa chạy. Ubuntu: `sudo systemctl start mysql`. Windows: mở app **Services** và start MySQL80. |
| `ModuleNotFoundError: No module named 'flask'` | Chưa kích hoạt môi trường ảo đúng cách — dùng `.venv/bin/flask` (Linux/macOS) hoặc `.venv\Scripts\flask` (Windows). |
| Port 5000 đã được sử dụng | Chạy với port khác: thêm `--port 8000` vào lệnh flask. |

### 5.8. Chạy ở chế độ production (tùy chọn)

Khi cần mô phỏng môi trường server thật trên máy local:

```bash
.venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

> Ứng dụng đọc cấu hình DB và `SECRET_KEY` từ biến môi trường (file `.env`). Trên server, systemd nạp file này qua chỉ thị `EnvironmentFile`.

## 6. Tài khoản demo

| Họ tên | Email | Vai trò | Mật khẩu |
|---|---|---|---|
| Trần Mai Anh | maianh.k62@neu.edu.vn | Trưởng nhóm | 123456 |
| Nguyễn Hoàng Long | long.nh@neu.edu.vn | Thành viên (số liệu) | 123456 |
| Lê Thu Trang | trang.lt@neu.edu.vn | Thành viên (slide) | 123456 |
| Vũ Đức Minh | minh.vd@neu.edu.vn | Thành viên (design) | 123456 |

> Chỉ **Trưởng nhóm** mới chỉnh được công thức Contribution (nút apply sẽ khóa với thành viên thường).

## 7. Triển khai trên server (đang chạy)

- `mysql.service` — MySQL 8.4
- `teamtrack-web.service` — gunicorn `127.0.0.1:5000`
- `caddy` — reverse proxy LAN (port 80/443)
- `cloudflared-tunnel.service` — tunnel public HTTPS

URL public hiện tại xem lệnh: `journalctl -u cloudflared-tunnel | grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" | head -1`

Để dùng domain riêng có cert Let's Encrypt: trỏ bản ghi A về IP public rồi chạy `deploy/enable-tls.sh <domain>`.
