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
┌───────────────┐      ┌──────────────────────┐      ┌─────────────┐
│  Frontend      │ HTTP │  Backend              │ SQL  │  Database   │
│  HTML + CSS    │◄────►│  Python (Flask)       │◄────►│  MySQL 8.4  │
│  (Jinja2)      │      │  + Gunicorn (WSGI)    │      └─────────────┘
└───────────────┘      └──────────┬───────────┘
                                  │ reverse proxy
                       ┌──────────▼───────────┐
                       │  Caddy (port 80/443)  │──► Cloudflare Tunnel (HTTPS public)
                       └──────────────────────┘
```

### 2.2. Tech stack và lý do lựa chọn

| Thành phần | Công nghệ | Lý do lựa chọn |
|---|---|---|
| Frontend | HTML + CSS thuần, Jinja2 template | Đơn giản, không phụ thuộc JS framework, phù hợp quy mô sinh viên; server render giúp code dễ đọc, dễ bảo trì |
| Font & thiết kế | Plus Jakarta Sans, phong cách Bento Card | Giao diện hiện đại, hiển thị tốt trên mobile |
| Backend | Python 3 + Flask | Framework nhẹ, cú pháp rõ ràng, phù hợp người mới học web backend; toàn bộ logic nằm trong 1 file `app.py` |
| DB driver | PyMySQL | Pure-Python, cài đặt đơn giản, không cần build C extension |
| Database | MySQL 8.4 (InnoDB) | Phổ biến nhất trong doanh nghiệp và giáo trình; hỗ trợ khóa ngoại, đảm bảo toàn vẹn dữ liệu |
| WSGI | Gunicorn | Chuẩn producción cho Flask, chạy dưới systemd tự restart |
| Reverse proxy | Caddy | Cấu hình tối giản; **tự động xin và gia hạn chứng chỉ TLS Let's Encrypt** |
| Public access | Cloudflare Tunnel | Xuất bản ra internet qua kết nối outbound, không cần mở port modem, có chứng chỉ công khai hợp lệ |

---

## PHẦN 3. THIẾT KẾ HỆ THỐNG

### 3.1. Sơ đồ cơ sở dữ liệu (MySQL — 8 bảng)

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

Toàn bộ bảng dùng **InnoDB + FOREIGN KEY + ON DELETE CASCADE** để đảm bảo toàn vẹn tham chiếu; charset `utf8mb4` hỗ trợ đầy đủ tiếng Việt.

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
- Production: app chỉ bind `127.0.0.1`, mọi truy cập ra ngoài qua Caddy (HTTPS) / Cloudflare Tunnel.

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

- Ubuntu Server trên máy ảo Proxmox; Python 3.14; MySQL 8.4;
- Tất cả dịch vụ quản lý bằng **systemd**, tự khởi động khi reboot:

| Service | Vai trò |
|---|---|
| `mysql.service` | Cơ sở dữ liệu |
| `teamtrack-web.service` | Gunicorn 2 worker, lắng nghe `127.0.0.1:5000` |
| `caddy` | Reverse proxy, phục vụ HTTPS port 443 (tự quản lý chứng chỉ) |
| `cloudflared-tunnel.service` | Cloudflare Tunnel — công bố app ra internet với HTTPS + chứng chỉ công khai |

### 5.2. Quy trình triển khai

```bash
# 1. Database
mysql -u root < app/schema.sql        # tạo DB, bảng, user MySQL
# 2. Ứng dụng
cd app && python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py              # nạp dữ liệu mẫu
# 3. Dịch vụ
systemctl enable --now mysql teamtrack-web caddy cloudflared-tunnel
```

### 5.3. HTTPS & chứng chỉ

- **Kênh public hiện tại:** Cloudflare Tunnel → domain `*.trycloudflare.com` với **chứng chỉ TLS công khai hợp lệ** (bình chọn bởi Google Trust Services), hoạt động kể cả khi modem không mở port.
- **Kênh domain riêng:** script `deploy/enable-tls.sh <domain>` thêm site vào Caddyfile; Caddy tự động thực hiện ACME HTTP-01 với Let's Encrypt, **tự xin và tự gia hạn chứng chỉ** theo chu kỳ. Điều kiện: bản ghi A của domain trỏ về IP public của server và port 80/443 được forward tới server.

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
| Kiểm thử các route qua HTTPS public | Tất cả trả 200/302 đúng, chứng chỉ hợp lệ |

### 6.2. Hạn chế hiện tại

1. Chưa có đăng ký tài khoản tự do và phân quyền theo nhiều cấp (chỉ demo 4 tài khoản sẵn);
2. Peer Review mới dùng điểm nền chung, chưa có form đánh giá chéo từng cặp;
3. Tính năng đồng bộ Google Calendar mới ở mức link ngoài;
4. Quick tunnel của Cloudflare đổi URL mỗi lần khởi động lại dịch vụ;
5. Chưa có test tự động (unit test) và CI/CD.

### 6.3. Hướng phát triển

- Form Peer Review thật giữa các thành viên (dữ liệu đưa thẳng vào công thức);
- Thông báo deadline qua email/Zalo OA;
- Xuất báo cáo PDF thật (weasyprint) thay vì in trình duyệt;
- Tích hợp Google Calendar API và Drive API;
- Viết unit test + pytest, triển khai CI/CD.

---

## PHỤ LỤC A. HƯỚNG DẪN SỬ DỤNG NHANH

1. Mở trang web → đăng nhập bằng tài khoản demo (xem `README.md` mục 6, mật khẩu `123456`);
2. **Dự án của tôi** → chọn một dự án để vào Dashboard;
3. Tab **Kanban** → thử "Chuyển" task hoặc "Nộp minh chứng";
4. Tab **Contribution** (đăng nhập bằng Mai Anh) → chỉnh tỷ trọng công thức → Apply;
5. Tab **Báo cáo GV** → Ctrl+P để lưu PDF.

## PHỤ LỤC B. TÀI LIỆU THAM KHẢO

1. Flask Documentation — https://flask.palletsprojects.com
2. MySQL 8.4 Reference Manual — https://dev.mysql.com/doc/
3. PyMySQL Documentation — https://pymysql.readthedocs.io
4. Caddy Documentation — https://caddyserver.com/docs
5. Cloudflare Tunnel — https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
6. Let's Encrypt — https://letsencrypt.org/docs/
