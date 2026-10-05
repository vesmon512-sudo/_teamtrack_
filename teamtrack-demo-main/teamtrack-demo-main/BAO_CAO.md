# BÁO CÁO DỰ ÁN TEAMTRACK

**Nền tảng quản lý bài tập nhóm & đo lường đóng góp dành cho sinh viên**

- **Sinh viên thực hiện:** 
1. Nguyễn Hà Anh - 2412150037
2. Nguyễn Thị Minh Nguyệt - 2412150237
3. Vũ Ngọc Khánh Linh - 2412150178
4. Nguyễn Huy Nhật - 2412150238
- **Môn học / Giảng viên hướng dẫn:** TINH314 - Ths. Trần Công Minh

---

## PHẦN 1. BỐI CẢNH VÀ BÀI TOÁN

### 1.1. Thực trạng

Làm việc nhóm (teamwork) là hình thức học tập phổ biến và đóng vai trò quan trọng đối với sinh viên đại học. Tuy nhiên quá trình làm việc nhóm vẫn tồn tại nhiều rào cản khiến hiệu quả bị suy giảm:

1. **Thiếu quy chuẩn và thông tin phân mảnh.** Sinh viên thường không có mẫu (template) kế hoạch phân chia công việc thông minh, dẫn tới giao việc theo cảm tính. Tài liệu, link họp, deadline bị rải rác trên quá nhiều nền tảng (Zalo, Messenger, Google Drive, Notion...), khó tra cứu và đồng bộ.
2. **Bất cập trong đo lường đóng góp (Contribution Points).** Khối lượng công việc và thái độ làm việc của từng thành viên rất khó định lượng, gây khó khăn cho Nhóm trưởng và Giảng viên trong việc chia điểm nhóm một cách công bằng, minh bạch.

### 1.2. Bài toán đặt ra

Xây dựng một nền tảng web cho phép:

- Tập trung hóa toàn bộ thông tin của nhiều bài tập nhóm trong cùng một nơi;
- Chuẩn hóa lộ trình làm việc theo các template phổ biến của sinh viên Việt Nam;
- Phân chia công việc trực quan, có nộp minh chứng và thưởng đúng hạn;
- **Tự động tính điểm đóng góp** của từng thành viên theo công thức nhóm tự định nghĩa, và xuất báo cáo nộp giảng viên làm căn cứ chấm điểm.

---

## PHẦN 2. GIẢI PHÁP TEAMTRACK

### 2.1. Tổng quan

TeamTrack là ứng dụng web đa người dùng, được xây dựng theo mô hình **3 lớp (3-tier)**:

```
┌────────────────┐      ┌───────────────────────┐      ┌──────────────────────┐
│ Trình duyệt    │      │ Backend (Render)      │      │ Database (Supabase)  │
│ HTML + CSS     │◄────►│ Python (Flask)        │◄────►│ PostgreSQL           │
│ (Jinja2)       │      │ + Gunicorn (WSGI)     │      │ (Session pooler)     │
└────────────────┘      └───────────────────────┘      └──────────────────────┘
   HTTPS (Render cấp chứng chỉ)      SQL qua DATABASE_URL
```

### 2.2. Tech stack và lý do lựa chọn

| Thành phần | Công nghệ | Lý do lựa chọn |
|---|---|---|
| Frontend | HTML + CSS thuần, Jinja2 template | Đơn giản, không phụ thuộc JS framework, phù hợp quy mô sinh viên; server render giúp code dễ đọc, dễ bảo trì |
| Font & thiết kế | Plus Jakarta Sans, phong cách Bento Card | Giao diện hiện đại, hiển thị tốt trên mobile |
| Backend | Python 3 + Flask | Framework nhẹ, cú pháp rõ ràng, phù hợp người mới học web backend; toàn bộ logic nằm trong 1 file `app.py` |
| DB driver | psycopg2 (`psycopg2-binary`) | Driver PostgreSQL phổ biến nhất cho Python, bản binary cài trực tiếp bằng pip, không cần biên dịch |
| Database | PostgreSQL trên Supabase | CSDL quan hệ mạnh, hỗ trợ khóa ngoại và ràng buộc toàn vẹn; Supabase cung cấp bản managed miễn phí, có giao diện quản trị và sao lưu, không phải tự vận hành server database |
| WSGI | Gunicorn | Chuẩn production cho Flask, được Render khởi chạy và tự restart khi tiến trình lỗi |
| Hosting | Render (gói Free) | Kết nối trực tiếp với GitHub, **tự động build và deploy mỗi lần push**, có sẵn HTTPS và chứng chỉ hợp lệ, không cần tự quản trị server |
| Cấu hình & bí mật | Biến môi trường, `python-dotenv` | Chuỗi kết nối database và `SECRET_KEY` nằm ngoài mã nguồn: file `.env` khi chạy local, mục Environment khi chạy trên Render |

---

## PHẦN 3. THIẾT KẾ HỆ THỐNG

### 3.1. Sơ đồ cơ sở dữ liệu (PostgreSQL — 8 bảng)

```
users ──< project_members >── projects ──< tasks
  │                             │    └────< milestones
  │                             │    └────< meetings
  │                             │    └────< documents
  │                             └─────── formula_settings (1-1)
```

| Bảng | Mục đích | Các cột chính |
|---|---|---|
| `users` | Tài khoản sinh viên | email, password (hash), full_name, student_id, university, default_role, streak_days, credibility_points, ontime_rate_pct |
| `projects` | Bài tập nhóm | code (môn + nhóm), title (đề tài), template_key, teacher (GVHD), target (mục tiêu điểm), deadline, created_by |
| `project_members` | Thành viên dự án | project_id, user_id, role (`leader`/`member`) |
| `milestones` | Cột mốc dự án | project_id, label, due_date, sort_order |
| `tasks` | Công việc | title, assignee_id, **points** (độ khó 3–5pt), **status** (todo/in_progress/review/done), due_at, proof_url, note, submitted_at, **early_bonus_pct** |
| `meetings` | Cuộc họp | title, scheduled_at, host_name, meet_link, agenda |
| `documents` | Kho tài liệu | name, file_type, size_label, drive_url, uploaded_by |
| `formula_settings` | Công thức đóng góp | workload_pct, ontime_pct, peer_pct, leader_bonus_pct |

Toàn bộ bảng dùng **PRIMARY KEY (kiểu `SERIAL` tự tăng) + FOREIGN KEY + ON DELETE CASCADE** để đảm bảo toàn vẹn tham chiếu; PostgreSQL lưu chuỗi dạng UTF-8 nên hỗ trợ đầy đủ tiếng Việt. Thời gian dùng kiểu `TIMESTAMP`, ngày dùng kiểu `DATE`. Mã tạo bảng nằm trong `app/schema.sql`.

### 3.2. Luồng xử lý chính

1. **Đăng nhập:** người dùng POST email + mật khẩu → Flask so sánh hash (werkzeug `check_password_hash`) → lưu `user_id` vào session (cookie ký số).
2. **Tạo dự án:** chọn template → hệ thống tự sinh 4 milestone theo lộ trình + bản ghi formula mặc định → người tạo trở thành Leader.
3. **Kanban:** task di chuyển giữa 4 cột qua form POST (mô phỏng kéo-thả bằng cách thuần HTML, không cần JS). Khi chuyển sang *Done* mà chưa nộp minh chứng, hệ thống tự ghi `submitted_at`.
4. **Nộp bài:** điền link minh chứng + ghi chú → task chuyển `done`; nếu `submitted_at <= due_at` thì cộng **early_bonus_pct = 10** (thưởng nộp đúng/sớm hạn), ngược lại 0.
5. **Contribution:** tính lại theo thời gian thực mỗi lần mở trang (xem 3.3).
6. **Báo cáo GV:** trang tĩnh render từ dữ liệu hiện tại, dùng `@media print` + Ctrl+P để xuất PDF.

### 3.3. Thuật toán tính điểm đóng góp (Contribution)

Với mỗi thành viên *m* trong dự án:

```
points_m   = Σ (task.points)                    với các task đã DONE của m
ontime_m   = số task DONE có early_bonus > 0
done_m     = số task DONE của m
assigned_m = tổng số task được giao cho m

workload_m   = points_m / max(points mọi thành viên) × 100        (thang 0–100)
ontimeRate_m = ontime_m / done_m × 100                            (100 nếu chưa có task done)
peerBase     = 60                                                 (điểm peer review nền chung)

raw_m = workload_m × W/100 + ontimeRate_m × O/100 + peerBase × P/100
raw_leader += LeaderBonus (0/5/10)

Contribution_m = raw_m / Σ(raw) × 100 %
```

Trong đó **W, O, P, LeaderBonus** do Nhóm trưởng tự cấu hình (mặc định 60 / 25 / 15 / 0) và lưu tại bảng `formula_settings`. Nhờ chuẩn hóa theo max và tổng, **tổng % đóng góp của nhóm luôn bằng 100%** — minh bạch, không ai chỉnh tay được.

### 3.4. Bảo mật đã áp dụng

- Mật khẩu lưu dạng **hash PBKDF2** (werkzeug), không lưu plain-text;
- Session cookie ký bằng `SECRET_KEY`;
- Tất cả truy vấn SQL dùng **parameterized query** (chống SQL Injection);
- Templates tự escape biến (Jinja2 autoescape) — chống XSS;
- Phân quyền: chỉ Leader chỉnh được công thức Contribution (nút bấm bị khóa với thành viên thường);
- Chuỗi kết nối database (chứa mật khẩu) và `SECRET_KEY` **không nằm trong mã nguồn**: lưu trong biến môi trường, file `.env` được đưa vào `.gitignore` nên không bị đẩy lên GitHub;
- Bật **Row Level Security (RLS)** trên toàn bộ 8 bảng, không tạo policy công khai, nên không ai truy cập được dữ liệu trực tiếp qua Supabase Data API bằng khóa công khai; chỉ backend Flask (kết nối bằng chuỗi riêng) đọc/ghi được;
- Production: toàn bộ truy cập đi qua **HTTPS** do Render cung cấp.

---

## PHẦN 4. MÔ TẢ CHỨC NĂNG (THEO 7 NHÓM TÍNH NĂNG)

### 4.1. Không gian làm việc cá nhân & đa dự án
Trang "Dự án của tôi" hiển thị hồ sơ sinh viên (MSSV, trường, vai trò, điểm uy tín, tỷ lệ đúng hạn, chuỗi ngày hoạt động) và lưới thẻ dự án kèm thanh tiến độ. Hỗ trợ theo dõi đồng thời nhiều bài tập từ các môn khác nhau; tạo dự án mới bằng form chọn template.

### 4.2. Bento Dashboard của dự án
Một trang tổng quan dạng "hộp bento": banner đề tài + GVHD + đếm ngược deadline + mục tiêu điểm; khối tiến độ lớn (%, x/y task); mini Gantt 4 giai đoạn; grid Milestones; thanh Contribution; bảng Leaderboard; thẻ cuộc họp sắp tới kèm nút tham gia Meet.

### 4.3. Masterplan & Template chuẩn hóa
4 template dựng sẵn phản ánh các dạng bài phổ biến: **Thuyết trình, SV NCKH, Tiểu luận cuối kỳ, Tự tạo**. Mỗi template chia 4 giai đoạn (GĐ1 → GĐ4) kèm deliverables cụ thể. Khi tạo dự án, hệ thống tự sinh 4 cột mốc với hạn cách nhau 1 tuần.

### 4.4. Họp & Kho tài liệu tập trung
Danh sách cuộc họp kèm thời gian, chủ trì, agenda và nút "Tham gia Meet"; kho tài liệu (loại file, dung lượng, người tải lên, link Drive) với form thêm nhanh — giải quyết vấn đề thông tin phân mảnh.

### 4.5. Kanban & hệ thống nộp task
4 cột chuẩn: **To-Do → In Progress → Review → Done**. Mỗi thẻ task hiển thị người phụ trách, độ khó (3–5pt), hạn chót (tự tô đỏ khi sắp đến hạn trong 48h), nút chuyển trạng thái và form nộp minh chứng. Cơ chế **thưởng +10% điểm** khi nộp trước hạn ghi trực tiếp vào dữ liệu task.

### 4.6. Contribution & công thức tùy chỉnh
Trang Contribution hiển thị công thức đang áp dụng, form chỉnh tỷ trọng (chỉ Leader thao tác được), và bảng tổng hợp: số task hoàn tất/tổng giao, tỷ lệ đúng hạn, tổng điểm, bonus, thanh % đóng góp. Mọi thay đổi công thức phản ánh ngay lập tức vào % đóng góp.

### 4.7. Leaderboard & báo cáo cho Giảng viên
Leaderboard xếp hạng theo % đóng góp, gắn huy hiệu **MVP**; trang **Báo cáo GV** trình bày chuẩn văn bản: thông tin môn/đề tài/GVHD, công thức áp dụng, tiến độ tổng thể, cột mốc, bảng xếp hạng chi tiết từng thành viên (kèm MSSV), ô chữ ký trưởng nhóm — in ra PDF bằng Ctrl+P để nộp.

---

## PHẦN 5. TRIỂN KHAI (DEPLOYMENT)

### 5.1. Môi trường

Ứng dụng được triển khai theo mô hình **PaaS + Database-as-a-Service**, không dùng server tự quản trị:

| Thành phần | Dịch vụ | Vai trò |
|---|---|---|
| Mã nguồn | GitHub | Lưu trữ repo, là nguồn kích hoạt deploy tự động |
| Backend | Render Web Service (gói Free, Python 3.14) | Chạy Flask qua Gunicorn, cấp HTTPS |
| Database | Supabase (gói Free), PostgreSQL | Lưu toàn bộ dữ liệu, kết nối qua **Session pooler** |
| Giám sát (tùy chọn) | UptimeRobot (gói Free) | Gọi định kỳ vào `/login` để giữ server không bị "ngủ" |

Địa chỉ ứng dụng: **https://teamtrack-5zqa.onrender.com**

### 5.2. Quy trình triển khai

**Bước 1. Tạo database trên Supabase**

- Tạo project mới, đặt mật khẩu database;
- Vào **SQL Editor**, chạy toàn bộ `app/schema.sql` để tạo 8 bảng và bật RLS;
- Vào **Connect → Session pooler**, lấy chuỗi kết nối dạng `postgresql://postgres.<project-ref>:<mật-khẩu>@aws-0-<region>.pooler.supabase.com:5432/postgres`.

> Phải dùng **Session pooler** thay vì Direct connection, vì Direct connection chỉ hỗ trợ IPv6, còn Render kết nối bằng IPv4 nên báo `Network is unreachable`.

**Bước 2. Nạp dữ liệu mẫu (chạy một lần trên máy cá nhân)**

```bash
cd app && python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# tạo file .env chứa DATABASE_URL và TT_SECRET_KEY
.venv/bin/python seed.py              # nạp 4 user, 3 dự án, 30 task
```

**Bước 3. Tạo Web Service trên Render**

| Mục | Giá trị |
|---|---|
| Nguồn | Repo GitHub của dự án |
| Root Directory | Thư mục chứa `app.py` (`app`) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free |
| Environment | `DATABASE_URL` (chuỗi Session pooler), `TT_SECRET_KEY` (chuỗi ngẫu nhiên dài) |

Sau khi Render báo **Live**, ứng dụng truy cập được qua URL công khai. Từ đó mỗi lần `git push`, Render tự động build và deploy lại (Continuous Deployment).

### 5.3. HTTPS & tên miền

- Render tự cấp và **tự gia hạn chứng chỉ TLS** cho tên miền `*.onrender.com`, mọi truy cập đều qua HTTPS, không cần cấu hình thủ công;
- Có thể gắn tên miền riêng trong phần **Custom Domains** của Render (Render tự cấp chứng chỉ cho tên miền đó);
- Ngoài ra, mã nguồn vẫn giữ script `deploy/enable-tls.sh <domain>` cho trường hợp tự host trên server Ubuntu riêng với Caddy (tự xin chứng chỉ Let's Encrypt). Cách này không được dùng trong bản triển khai hiện tại.

### 5.4. Vận hành và giới hạn của gói miễn phí

| Giới hạn | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Render Free tự "ngủ" sau 15 phút không có truy cập | Lần mở đầu tiên sau đó chậm khoảng 30-50 giây | Mở link trước giờ demo vài phút, hoặc dùng UptimeRobot ping `/login` mỗi 5 phút |
| Supabase Free tự tạm dừng project sau 7 ngày không hoạt động | Web báo lỗi kết nối database | Bấm **Restore project** trên dashboard; ping định kỳ vào `/login` (có truy vấn DB) cũng giúp tránh bị tạm dừng |
| Render Free có 750 giờ chạy mỗi tháng | Đủ cho 1 service chạy liên tục | Không tạo thêm service Free khác trên cùng tài khoản |

### 5.5. Các thay đổi khi chuyển từ MySQL sang PostgreSQL

Phiên bản đầu của dự án dùng MySQL tự host. Khi chuyển sang Supabase (PostgreSQL), mã nguồn được điều chỉnh như sau:

| Nội dung | MySQL (cũ) | PostgreSQL (mới) |
|---|---|---|
| Driver | `PyMySQL` | `psycopg2-binary` |
| Khóa tự tăng | `INT AUTO_INCREMENT` | `SERIAL` |
| Lấy id vừa chèn | `lastrowid` | `INSERT ... RETURNING id` (xử lý trong `db.py`; riêng hai bảng không có cột `id` là `project_members` và `formula_settings` thì bỏ qua) |
| Bỏ qua bản ghi trùng | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT (project_id, user_id) DO NOTHING` |
| Kiểu cờ bật/tắt | `TINYINT(1)` | `SMALLINT` |
| Kiểu thời gian | `DATETIME` | `TIMESTAMP` |
| Cấu hình kết nối | `TT_DB_HOST`, `TT_DB_USER`, `TT_DB_PASSWORD`... | Một biến duy nhất `DATABASE_URL` |

---

## PHẦN 6. KẾT QUẢ & KIỂM THỬ

### 6.1. Kết quả kiểm thử chính

| Kịch bản | Kết quả |
|---|---|
| Đăng nhập đúng/sai mật khẩu | Đúng → redirect dashboard; sai → thông báo lỗi, không vào được |
| Truy cập trang khi chưa đăng nhập | Tự redirect về /login |
| Tạo dự án mới với template | Sinh đủ 4 milestone + formula mặc định; người tạo là Leader |
| Thêm task / chuyển trạng thái Kanban | Task cập nhật đúng cột, đếm số lượng đúng |
| Nộp minh chứng trước hạn | Task → Done, cộng +10% bonus, hiện "Minh chứng ↗" |
| Nộp sau hạn | Task → Done, bonus = 0 |
| Chỉnh công thức (Leader / thường) | Leader → lưu và tính lại %; thành viên thường → form bị khóa |
| Tổng % đóng góp của nhóm | Luôn bằng 100% sau mọi lần cấu hình lại |
| Báo cáo GV | Render đúng số liệu thực tế từ DB, in PDF chuẩn |
| Truy cập bản deploy qua HTTPS (Render) | Trang tải được qua HTTPS, đăng nhập và đọc/ghi dữ liệu trên Supabase hoạt động |

### 6.2. Hạn chế hiện tại

1. Chưa có đăng ký tài khoản tự do và phân quyền theo nhiều cấp (chỉ demo 4 tài khoản sẵn);
2. Peer Review mới dùng điểm nền chung, chưa có form đánh giá chéo từng cặp;
3. Tính năng đồng bộ Google Calendar mới ở mức link ngoài;
4. Gói miễn phí của Render tự "ngủ" sau 15 phút không truy cập (lần mở đầu mất 30-50 giây) và Supabase Free tự tạm dừng sau 7 ngày không hoạt động;
5. Chưa có test tự động (unit test) và CI/CD.

### 6.3. Hướng phát triển

- Form Peer Review thật giữa các thành viên (dữ liệu đưa thẳng vào công thức);
- Thông báo deadline qua email/Zalo OA;
- Xuất báo cáo PDF thật (weasyprint) thay vì in trình duyệt;
- Tích hợp Google Calendar API và Drive API;
- Viết unit test + pytest, thêm CI chạy test tự động (GitHub Actions) trước khi deploy.

---

## PHỤ LỤC A. HƯỚNG DẪN SỬ DỤNG NHANH

1. Mở trang web → đăng nhập bằng tài khoản demo (xem `README.md` mục 6, mật khẩu `123456`);
2. **Dự án của tôi** → chọn một dự án để vào Dashboard;
3. Tab **Kanban** → thử "Chuyển" task hoặc "Nộp minh chứng";
4. Tab **Contribution** (đăng nhập bằng Mai Anh) → chỉnh tỷ trọng công thức → Apply;
5. Tab **Báo cáo GV** → Ctrl+P để lưu PDF.

## PHỤ LỤC B. TÀI LIỆU THAM KHẢO

1. Flask Documentation — https://flask.palletsprojects.com
2. PostgreSQL Documentation — https://www.postgresql.org/docs/
3. Supabase Documentation — https://supabase.com/docs
4. Psycopg2 Documentation — https://www.psycopg.org/docs/
5. Gunicorn Documentation — https://docs.gunicorn.org
6. Render Documentation — https://render.com/docs
