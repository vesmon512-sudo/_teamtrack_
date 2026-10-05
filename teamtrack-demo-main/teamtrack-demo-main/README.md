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
| Backend | Python 3.12+ + Flask | 1 file `app.py` (~400 dòng), route rõ ràng, dễ đọc |
| Database | PostgreSQL trên Supabase | 8 bảng, kết nối qua `psycopg2` bằng chuỗi `DATABASE_URL` (Session pooler) |
| WSGI server | Gunicorn | Dùng khi deploy production |
| Hosting | Render (gói Free) | Tự động deploy lại mỗi khi push lên GitHub, có sẵn HTTPS |
| Cấu hình | Biến môi trường / file `.env` | `DATABASE_URL`, `TT_SECRET_KEY` (thư viện `python-dotenv`) |


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

App chạy trên máy (Flask), còn dữ liệu lưu trên **Supabase (PostgreSQL)**. Vì vậy máy cần có **kết nối Internet** khi chạy.

### 5.1. Yêu cầu môi trường

| Thứ cần có | Phiên bản | Cách kiểm tra |
|---|---|---|
| Python | 3.12 trở lên | Windows: `py --version` · macOS/Linux: `python3 --version` |
| Tài khoản Supabase | Gói Free | Đăng ký tại [supabase.com](https://supabase.com) |
| Git (không bắt buộc) | bất kỳ | `git --version` |

- **Chưa có Python?** Tải tại [python.org/downloads](https://www.python.org/downloads/). Khi cài trên Windows, **tick ô "Add python.exe to PATH"**, cài xong **đóng và mở lại terminal**.
- Không cần cài MySQL hay PostgreSQL trên máy, database nằm trên Supabase.

### 5.2. Lấy mã nguồn và mở terminal đúng thư mục

```bash
git clone <link-repo-của-bạn>
cd <tên-repo>/app
```

Hoặc tải ZIP từ GitHub, giải nén, rồi mở terminal tại thư mục **`app`** (thư mục chứa `app.py`, `db.py`, `seed.py`, `requirements.txt`).

> **Windows:** mở thư mục `app` trong File Explorer, click vào thanh địa chỉ, gõ `powershell` rồi nhấn Enter.
> Kiểm tra đúng chỗ bằng lệnh `dir` (Windows) hoặc `ls` (macOS/Linux): phải thấy `app.py`, `db.py`, `requirements.txt`.
>
> Lưu ý: nếu tải ZIP, đôi khi thư mục bị lồng 2 lớp (`repo-main/repo-main/app`). Hãy `cd` vào cho tới khi thấy `app.py`.

### 5.3. Tạo project và bảng dữ liệu trên Supabase

1. Vào Supabase → **New project**. Đặt tên, tạo **mật khẩu database** (nên chỉ dùng chữ và số để tránh lỗi, ví dụ `TeamTrack2026abc`) và **ghi nhớ mật khẩu này**. Chọn region gần bạn (ví dụ Singapore). Chờ project khởi tạo xong.
2. Vào **SQL Editor → New query**.
3. Mở file `schema.sql` trong dự án, copy **toàn bộ** nội dung, dán vào SQL Editor rồi bấm **Run**.
4. Vào **Table Editor** kiểm tra đã có 8 bảng: `users`, `projects`, `project_members`, `milestones`, `meetings`, `documents`, `tasks`, `formula_settings`.

> `schema.sql` bắt đầu bằng lệnh `DROP TABLE`, nên chạy lại file này sẽ **xóa sạch dữ liệu cũ** và tạo bảng trống.

### 5.4. Lấy chuỗi kết nối Supabase (Session pooler)

1. Trong project Supabase, bấm nút **Connect** ở thanh trên cùng.
2. Chọn **Connection String**, ở phần **Method** chọn **Session pooler**.
3. Copy chuỗi, có dạng:

```
postgresql://postgres.<project-ref>:[YOUR-PASSWORD]@aws-0-<region>.pooler.supabase.com:5432/postgres
```

4. Thay `[YOUR-PASSWORD]` bằng mật khẩu ở bước 5.3 (bỏ luôn dấu `[ ]`).

> ⚠️ **Phải dùng Session pooler**, không dùng "Direct connection" (`db.xxx.supabase.co`). Direct connection chỉ hỗ trợ IPv6 nên nhiều mạng và nhiều dịch vụ hosting sẽ báo `Network is unreachable`.
> Dấu hiệu chuỗi đúng: tên user có dạng `postgres.<project-ref>`, host có chữ `pooler.supabase.com`, port `5432`.

### 5.5. Tạo file cấu hình `.env`

Trong thư mục `app`, copy file mẫu:

```bash
cp .env.example .env          # macOS/Linux
copy .env.example .env        # Windows (cmd)
Copy-Item .env.example .env   # Windows (PowerShell)
```

Mở `.env` và điền 2 dòng:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<mật-khẩu>@aws-0-<region>.pooler.supabase.com:5432/postgres
TT_SECRET_KEY=<chuỗi ngẫu nhiên>
```

Tạo `TT_SECRET_KEY` bằng lệnh (Windows dùng `py` thay cho `python3`):

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

> ⚠️ File `.env` chứa mật khẩu database. Đã được đưa vào `.gitignore`, **tuyệt đối không commit hay gửi cho người khác**. Nếu lỡ lộ, vào Supabase → **Project Settings → Database → Reset database password** rồi cập nhật lại `.env`.
>
> Trên Windows, đảm bảo file tên đúng là `.env`, không phải `.env.txt`.

### 5.6. Cài thư viện Python

Tạo môi trường ảo (chỉ làm 1 lần) rồi cài thư viện:

**Windows (PowerShell):**
```powershell
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Cài xong sẽ hiện `Successfully installed ...`.

### 5.7. Nạp dữ liệu mẫu (chỉ làm 1 lần)

Tạo 4 user demo, 3 dự án và ~30 task:

**Windows:**
```powershell
.\.venv\Scripts\python seed.py
```

**macOS / Linux:**
```bash
.venv/bin/python seed.py
```

- Lệnh này mất khoảng **1-2 phút** vì ghi từng bản ghi lên Supabase qua mạng. Con trỏ đứng im là bình thường, **đừng bấm Ctrl+C**.
- Thành công khi hiện: `seeded ok: 4 users, 3 projects`.
- Nếu chạy lần 2 sẽ báo `duplicate key value violates unique constraint "users_email_key"`. Muốn nạp lại: chạy lại `schema.sql` trên Supabase (bước 5.3) để xóa sạch, rồi chạy `seed.py`.

### 5.8. Chạy server

**Windows:**
```powershell
.\.venv\Scripts\flask --app app run --port 5000
```

**macOS / Linux:**
```bash
.venv/bin/flask --app app run --port 5000
```

Khi terminal hiện `Running on http://127.0.0.1:5000` là server đã chạy. Mở trình duyệt vào **http://127.0.0.1:5000** và đăng nhập bằng tài khoản demo ở [mục 6](#6-tài-khoản-demo) (ví dụ `maianh.k62@neu.edu.vn` / `123456`).

Nhấn `Ctrl+C` trong terminal để dừng server. Những lần sau chỉ cần chạy lại **bước 5.8** (không cần cài lại hay nạp lại dữ liệu).

> Muốn đưa bạn bè trong cùng mạng Wi-Fi xem thử: thêm `--host 0.0.0.0` vào lệnh trên, rồi họ truy cập `http://<IP-máy-bạn>:5000`.

### 5.9. Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân & cách sửa |
|---|---|
| `Python was not found; run without arguments to install from the Microsoft Store` | Chưa cài Python hoặc đang dính lối tắt Microsoft Store. Cài Python (nhớ tick *Add to PATH*), hoặc vào **Settings → Apps → Advanced app settings → App execution aliases** và tắt `python.exe`, `python3.exe`. Có thể dùng lệnh `py` thay cho `python`. |
| `Could not open requirements file: No such file or directory` | Đang đứng sai thư mục. Dùng `dir`/`ls` kiểm tra phải thấy `requirements.txt`, nếu không thì `cd` vào thư mục `app`. |
| `KeyError: 'DATABASE_URL'` | Chưa có file `.env`, đặt sai chỗ (phải nằm cạnh `app.py`), hoặc bị đặt tên `.env.txt`. |
| `Network is unreachable` (kèm địa chỉ `2406:...`) | Đang dùng Direct connection. Đổi sang chuỗi **Session pooler** (bước 5.4). |
| `password authentication failed` | Sai mật khẩu trong `DATABASE_URL`, còn sót dấu `[ ]`, hoặc mật khẩu có ký tự đặc biệt (`@ # / ? :`). Đặt lại mật khẩu chỉ gồm chữ và số. |
| `Tenant or user not found` | Với pooler, user phải là `postgres.<project-ref>`, không phải `postgres`. Copy lại chuỗi từ nút **Connect**. |
| `relation "users" does not exist` | Chưa chạy `schema.sql` trên Supabase (bước 5.3). |
| `duplicate key value violates unique constraint` khi chạy `seed.py` | Dữ liệu mẫu đã được nạp. Xem hướng dẫn nạp lại ở bước 5.7. |
| `seed.py` đứng im rất lâu | Bình thường, chờ 1-2 phút. Nếu quá 5 phút, kiểm tra mạng và chuỗi kết nối. |
| `TemplateNotFound` | Thiếu thư mục `templates/` hoặc đang chạy sai thư mục (phải chạy trong `app`). |
| `Port 5000 is in use` | Đổi cổng: thêm `--port 8000` vào lệnh `flask`. |
| Web báo lỗi sau vài ngày không dùng | Supabase gói Free tự tạm dừng project sau 7 ngày không hoạt động. Vào dashboard Supabase bấm **Restore project**. |

### 5.10. Chạy ở chế độ production (tùy chọn, chỉ macOS/Linux/WSL)

```bash
.venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

> Gunicorn không chạy trên Windows thuần. Trên Windows, dùng lệnh `flask run` ở bước 5.8 cho môi trường phát triển.
> Ứng dụng đọc `DATABASE_URL` và `TT_SECRET_KEY` từ biến môi trường (file `.env`). Khi deploy lên hosting (ví dụ Render), khai báo hai biến này trong phần **Environment** thay vì dùng file `.env`.

## 6. Tài khoản demo

| Họ tên | Email | Vai trò | Mật khẩu |
|---|---|---|---|
| Trần Mai Anh | maianh.k62@neu.edu.vn | Trưởng nhóm | 123456 |
| Nguyễn Hoàng Long | long.nh@neu.edu.vn | Thành viên (số liệu) | 123456 |
| Lê Thu Trang | trang.lt@neu.edu.vn | Thành viên (slide) | 123456 |
| Vũ Đức Minh | minh.vd@neu.edu.vn | Thành viên (design) | 123456 |

> Chỉ **Trưởng nhóm** mới chỉnh được công thức Contribution (nút apply sẽ khóa với thành viên thường).

## 7. Triển khai online (Render + Supabase)

Ứng dụng đang chạy công khai tại: **https://teamtrack-5zqa.onrender.com**

Kiến trúc: **Flask chạy trên Render**, **dữ liệu nằm trên Supabase**. Máy cá nhân tắt vẫn không ảnh hưởng.

### 7.1. Cách deploy

1. Đẩy code lên GitHub (đảm bảo **không có file `.env`** trong repo).
2. Vào [render.com](https://render.com), đăng nhập bằng GitHub → **New → Web Service** → chọn repo.
3. Điền cấu hình:

| Mục | Giá trị |
|---|---|
| Root Directory | Thư mục chứa `app.py` (thường là `app`; nếu repo bị lồng thư mục thì `<thư-mục>/app`) |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free |

4. Thêm 2 biến trong **Environment**:
   - `DATABASE_URL` = chuỗi **Session pooler** của Supabase (xem bước 5.4)
   - `TT_SECRET_KEY` = chuỗi ngẫu nhiên dài
5. Bấm **Deploy Web Service**. Khi hiện **Live** là xong. Từ đó mỗi lần `git push`, Render tự động deploy lại.

### 7.2. Lưu ý khi dùng gói Free

- **Server tự "ngủ" sau 15 phút không có ai truy cập.** Lần mở đầu tiên sau đó mất khoảng 30-50 giây để dậy. Trước giờ demo khoảng 5-10 phút, hãy tự mở link web một lần để đánh thức server. Không cần mở VS Code hay Supabase.
- **Muốn server luôn sẵn sàng:** tạo monitor miễn phí trên [UptimeRobot](https://uptimerobot.com) (loại HTTP(s), chu kỳ 5 phút) trỏ tới `https://<tên-app>.onrender.com/login`. Dùng đuôi `/login` vì trang này có truy vấn database nên đồng thời giữ cho Supabase không bị tạm dừng.
- **Supabase Free** tự tạm dừng project nếu 7 ngày liền không có hoạt động. Khi đó vào dashboard bấm **Restore project**.
- Gói Free của Render có 750 giờ chạy mỗi tháng, đủ cho 1 service chạy liên tục.

### 7.3. Lỗi thường gặp khi deploy

| Lỗi trong log Render | Cách sửa |
|---|---|
| `Network is unreachable` | `DATABASE_URL` đang là Direct connection. Đổi sang **Session pooler**. |
| `password authentication failed` | Sai mật khẩu hoặc có ký tự đặc biệt chưa xử lý. Đặt lại mật khẩu chỉ gồm chữ và số. |
| `Tenant or user not found` | User của pooler phải là `postgres.<project-ref>`. |
| `KeyError: 'DATABASE_URL'` | Chưa khai báo biến môi trường trên Render. |
| `TemplateNotFound` hoặc không tìm thấy `app.py` | Sai **Root Directory**, hoặc thiếu thư mục `templates/` trên GitHub. |

### 7.4. (Tùy chọn) Tự host trên server riêng với domain và HTTPS

Nếu có server Ubuntu riêng chạy Caddy làm reverse proxy cho `127.0.0.1:5000`: trỏ bản ghi A của domain về IP public của server rồi chạy `deploy/enable-tls.sh <domain>`. Script sẽ thêm site vào Caddyfile và Caddy tự xin, gia hạn chứng chỉ Let's Encrypt. Cách này không bắt buộc khi đã deploy bằng Render.
