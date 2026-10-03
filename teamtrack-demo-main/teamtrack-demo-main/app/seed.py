from werkzeug.security import generate_password_hash
import db

PWD = generate_password_hash("123456")

USERS = [
    ("maianh.k62@neu.edu.vn", "Trần Mai Anh", "Mai Anh", "22020145", "ĐH Kinh tế Quốc dân (NEU)", "Trưởng nhóm", 5, 420, 98),
    ("long.nh@neu.edu.vn", "Nguyễn Hoàng Long", "Hoàng Long", "22020188", "ĐH Kinh tế Quốc dân (NEU)", "Thành viên - Số liệu", 3, 380, 96),
    ("trang.lt@neu.edu.vn", "Lê Thu Trang", "Thu Trang", "22020210", "ĐH Kinh tế Quốc dân (NEU)", "Thành viên - Slide", 4, 360, 100),
    ("minh.vd@neu.edu.vn", "Vũ Đức Minh", "Đức Minh", "22020099", "ĐH Kinh tế Quốc dân (NEU)", "Thành viên - Design", 2, 290, 88),
]


def seed_users():
    ids = []
    for email, full, short, sid, uni, role, streak, points, ontime in USERS:
        uid = db.execute(
            "INSERT INTO users (email, password, full_name, short_name, student_id, university, default_role, streak_days, credibility_points, ontime_rate_pct) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (email, PWD, full, short, sid, uni, role, streak, points, ontime),
        )
        ids.append(uid)
    return ids


def add_milestones(pid, items):
    for i, (label, due) in enumerate(items):
        db.execute("INSERT INTO milestones (project_id, label, due_date, sort_order) VALUES (%s,%s,%s,%s)", (pid, label, due, i + 1))


def add_tasks(pid, rows):
    for title, uid, pts, status, due, sub, bonus, proof in rows:
        db.execute(
            "INSERT INTO tasks (project_id, title, assignee_id, points, status, due_at, proof_url, submitted_at, early_bonus_pct) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (pid, title, uid, pts, status, due, proof, sub, bonus),
        )


def main():
    mai, long, trang, minh = seed_users()

    p1 = db.execute(
        "INSERT INTO projects (code, title, template_key, teacher, target, deadline, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        ("Kinh tế số - Nhóm 4 (K62)", "Bài thuyết trình: Phân tích Hành vi Tiêu dùng GenZ trên E-Commerce",
         "thuyettrinh", "TS. Nguyễn Hải Nam", "Điểm A (9.5+)", "2026-10-06 23:59:00", mai),
    )
    p2 = db.execute(
        "INSERT INTO projects (code, title, template_key, teacher, target, deadline, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        ("Quản trị học - Nhóm 2", "Tiểu luận cuối kỳ: Phân tích Chiến lược Cạnh tranh Quốc tế của VinFast",
         "tieuluan", "PGS. TS. Trần Đình Long", "Điểm A (9.0+)", "2026-10-12 23:59:00", long),
    )
    p3 = db.execute(
        "INSERT INTO projects (code, title, template_key, teacher, target, deadline, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        ("NCKH Cấp Khoa 2026 - Nhóm Alpha", "Ứng dụng AI & Học máy trong Dự báo Tắc nghẽn Logistics Đô thị",
         "nckh", "TS. Đỗ Thu Hằng", "Giải Nhất NCKH Cấp Khoa", "2026-11-20 17:00:00", mai),
    )

    for pid in (p1, p2, p3):
        db.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s,%s,'leader')", (pid, mai))
        for uid in (long, trang, minh):
            db.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s,%s,'member')", (pid, uid))

    add_milestones(p1, [
        ("Chốt kịch bản & Phân vai thuyết trình", "2026-09-17"),
        ("Bản thảo kịch bản 3 phần & Case study", "2026-09-28"),
        ("Demo Slide Canva 25 trang & Visuals", "2026-10-03"),
        ("Rehearsal & Nộp file Giảng viên", "2026-10-06"),
    ])
    add_milestones(p2, [
        ("Duyệt đề cương 3 chương với GVHD", "2026-09-25"),
        ("Hoàn tất Chương 1 & Chương 2 (Thực trạng VinFast)", "2026-10-02"),
        ("Nộp Bản thảo 1 cho GV nhận xét", "2026-10-08"),
        ("Turnitin < 15% & Nộp bản in", "2026-10-12"),
    ])
    add_milestones(p3, [
        ("Duyệt đề cương NCKH cấp Khoa (9.2 điểm)", "2026-09-25"),
        ("Thu thập đủ 250 phiếu khảo sát hợp lệ", "2026-10-15"),
        ("Kết quả kiểm định SPSS & Hồi quy SEM", "2026-11-05"),
        ("Nộp toàn văn công trình & Poster", "2026-11-20"),
    ])

    add_tasks(p1, [
        ("Xác lập đề tài & Phân vai 4 thành viên", mai, 4, "done", "2026-09-17 23:59", "2026-09-16 20:00", 10, "https://drive.google.com/TT-de-tai"),
        ("Chốt bảng màu & Layout Master trên Canva", minh, 3, "done", "2026-09-25 23:59", "2026-09-24 18:00", 10, "https://canva.com/TT-cau-mau"),
        ("Lên kịch bản slide mở đầu & Demo 10 slide Canva", trang, 4, "done", "2026-09-28 23:59", "2026-09-26 21:00", 10, "https://canva.com/TT-demo"),
        ("Case study chiến dịch Shopee KOLs & Livestream", long, 3, "done", "2026-09-22 23:59", "2026-09-24 23:59", 0, "https://drive.google.com/TT-case"),
        ("Thiết kế bảng hỏi khảo sát 120 mẫu phiên 1", mai, 3, "done", "2026-09-20 23:59", "2026-09-18 10:00", 10, "https://forms.gle/TT-khao-sat"),
        ("Infographic so sánh hành vi GenZ & GenY", minh, 4, "done", "2026-09-27 23:59", "2026-09-25 22:00", 10, "https://canva.com/TT-infographic"),
        ("Khảo sát 120 mẫu GenZ tại ĐH về thói quen mua sắm", mai, 5, "in_progress", "2026-09-30 08:00", None, 0, None),
        ("Soạn nội dung Case study Shopee vs TikTok Shop", long, 3, "in_progress", "2026-10-01 23:59", None, 0, None),
        ("Hoàn thiện kịch bản dẫn chuyện khung 15 phút", trang, 4, "in_progress", "2026-10-02 23:59", None, 0, None),
        ("Thiết kế bộ 25 slide Canva & nhúng video 45s", trang, 5, "todo", "2026-10-03 23:59", None, 0, None),
        ("Bộ 10 câu hỏi phản biện & 5 slide phụ lục", long, 3, "todo", "2026-10-05 23:59", None, 0, None),
        ("Tổng duyệt khớp giờ 15 phút & Nộp bài", mai, 5, "todo", "2026-10-05 23:59", None, 0, None),
    ])
    add_tasks(p2, [
        ("Thông qua đề cương chi tiết 3 chương với GVHD", mai, 4, "done", "2026-09-25 23:59", "2026-09-24 16:00", 10, "https://drive.google.com/TL-decuong"),
        ("Thu thập BCTC VinFast 3 năm gần nhất", long, 3, "done", "2026-09-28 23:59", "2026-09-22 20:00", 10, "https://drive.google.com/TL-bctc"),
        ("Soạn Chương 1: Cơ sở lý luận chiến lược cạnh tranh", mai, 4, "done", "2026-09-25 23:59", "2026-09-25 20:00", 10, "https://drive.google.com/TL-chu1"),
        ("Ma trận SWOT VinFast trong cạnh tranh xe điện", long, 4, "done", "2026-09-30 23:59", "2026-09-29 21:00", 10, "https://drive.google.com/TL-swot"),
        ("Viết Chương 2: Chuỗi cung ứng & rào cản xuất khẩu Mỹ", mai, 5, "in_progress", "2026-10-09 23:59", None, 0, None),
        ("Viết Chương 3: 4 nhóm giải pháp chiến lược", minh, 5, "in_progress", "2026-10-10 23:59", None, 0, None),
        ("Soạn Marketing Mix 4P cho Chương 3", trang, 3, "in_progress", "2026-10-08 23:59", None, 0, None),
        ("Định dạng APA 7th & Chạy thử Turnitin (<15%)", minh, 3, "todo", "2026-10-12 23:59", None, 0, None),
    ])
    add_tasks(p3, [
        ("Hội đồng: Bảo vệ đề cương NCKH cấp Khoa (9.2 điểm)", mai, 5, "done", "2026-09-25 17:00", "2026-09-25 14:00", 10, "https://docs.google.com/NCKH-decuong"),
        ("Tổng hợp 30 bài báo Scopus/ISI về mô hình TAM", long, 5, "done", "2026-09-25 23:59", "2026-09-20 22:00", 10, "https://drive.google.com/NCKH-tai-lieu"),
        ("Mô hình nghiên cứu TAM + UTAUT2 (5 giả thuyết)", mai, 4, "done", "2026-09-25 23:59", "2026-09-23 18:00", 10, "https://drive.google.com/NCKH-mohinh"),
        ("Pilot test 30 mẫu kiểm tra thang đo", trang, 3, "done", "2026-09-28 23:59", "2026-09-27 20:00", 10, "https://drive.google.com/NCKH-pilot"),
        ("Thiết kế bảng hỏi Google Forms 28 biến Likert", mai, 5, "in_progress", "2026-09-30 23:59", None, 0, None),
        ("Thu thập đủ 250 phiếu khảo sát (hiện 180/250)", trang, 5, "in_progress", "2026-10-15 23:59", None, 0, None),
        ("Viết Chương 2: Phương pháp luận & mô hình SEM", long, 5, "in_progress", "2026-10-25 23:59", None, 0, None),
        ("Làm sạch bộ dữ liệu khảo sát thô (.sav)", minh, 4, "todo", "2026-10-22 23:59", None, 0, None),
        ("Cronbach's Alpha, EFA & Hồi quy SEM", long, 5, "todo", "2026-11-05 23:59", None, 0, None),
        ("Toàn văn công trình NCKH & Poster Hội đồng", mai, 5, "todo", "2026-11-18 23:59", None, 0, None),
    ])

    for pid, title, sched, host, link, agenda in [
        (p1, "Họp đợt 3: Khớp kịch bản lời thoại & Demo 15 slide đầu Canva", "2026-09-30 20:00", "Mai Anh (Leader)", "https://meet.google.com/tt-genz-slide",
         "Long báo cáo số liệu tổng hợp từ 120 mẫu khảo sát GenZ\nTrang demo 15 slide đầu trên Canva & nhận góp ý màu sắc\nMinh bấm giờ thử kịch bản mở đầu xem có bị lố 3 phút không"),
        (p2, "Họp chốt nội dung Chương 2 & Rà soát phân công viết Chương 3", "2026-10-04 15:00", "Mai Anh & Hoàng Long", "https://meet.google.com/vinfast-tieuluan",
         "Long trình bày số liệu doanh số VinFast tại Mỹ quý 1-2\nThảo luận 4 định hướng giải pháp Chương 3 theo góp ý của Thầy Long\nMinh phổ biến quy chuẩn trích dẫn APA 7th để không lỗi Turnitin"),
        (p3, "Họp NCKH Tuần 6: Đánh giá 180/250 phiếu & Chuẩn bị chạy SPSS", "2026-10-01 19:30", "Mai Anh & TS. Đỗ Thu Hằng", "https://meet.google.com/nckh-alpha-spss",
         "Trang báo cáo tiến độ 180 phiếu & các phiếu bị loại\nLong trình bày cấu trúc file dữ liệu SPSS đã mã hóa\nThống nhất thời gian xin ý kiến đóng góp của TS. Đỗ Thu Hằng"),
    ]:
        db.execute(
            "INSERT INTO meetings (project_id, title, scheduled_at, host_name, meet_link, agenda) VALUES (%s,%s,%s,%s,%s,%s)",
            (pid, title, sched, host, link, agenda),
        )

    for pid, name, ftype, size, url, by in [
        (p1, "Canva Master Slide Deck (25 Trang)", "Canva", "Canva Pro Link", "https://canva.com/TT-master", "Thu Trang"),
        (p1, "Kịch bản lời thoại thuyết trình 15 phút.docx", "Word", "1.2 MB", "https://drive.google.com/TT-kich-ban", "Hoàng Long"),
        (p1, "Dữ liệu khảo sát 120 mẫu GenZ.xlsx", "Excel", "850 KB", "https://drive.google.com/TT-du-lieu", "Mai Anh"),
        (p2, "Báo Cáo Thường Niên VinFast 2025.pdf", "PDF", "6.2 MB", "https://drive.google.com/TL-bctc", "Hoàng Long"),
        (p2, "Đề Cương Tiểu Luận 3 Chương Đã Duyệt.docx", "Word", "1.5 MB", "https://drive.google.com/TL-decuong", "Mai Anh"),
        (p3, "Bộ Dữ Liệu Khảo Sát Thô Logistics 2026.sav", "SPSS", "2.4 MB", "https://drive.google.com/NCKH-du-lieu", "Đức Minh"),
        (p3, "Đề Cương NCKH Cấp Khoa Đã Phê Duyệt.pdf", "PDF", "4.8 MB", "https://drive.google.com/NCKH-decuong", "Cả nhóm"),
    ]:
        db.execute(
            "INSERT INTO documents (project_id, name, file_type, size_label, drive_url, uploaded_by) VALUES (%s,%s,%s,%s,%s,%s)",
            (pid, name, ftype, size, url, by),
        )

    for pid, (w, o, p, b) in ((p1, (60, 25, 15, 5)), (p2, (60, 25, 15, 0)), (p3, (50, 30, 20, 0))):
        db.execute(
            "INSERT INTO formula_settings (project_id, workload_pct, ontime_pct, peer_pct, leader_bonus_pct) VALUES (%s,%s,%s,%s,%s)",
            (pid, w, o, p, b),
        )

    print("seeded ok: 4 users, 3 projects")


if __name__ == "__main__":
    main()
