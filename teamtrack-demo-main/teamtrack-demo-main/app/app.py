import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import db

app = Flask(__name__)
app.secret_key = os.environ.get("TT_SECRET_KEY", "dev-only-not-for-production")

TEMPLATES = {
    "thuyettrinh": {
        "icon": "🎤", "name": "Thuyết trình",
        "phases": [
            ("GĐ1: Xác lập đề tài, dàn ý & Phân vai", ["Phân vai thành viên rõ trách nhiệm", "Khung kịch bản thuyết trình theo thời lượng", "Quy chuẩn thiết kế slide (tối đa 5 dòng/slide)"]),
            ("GĐ2: Soạn kịch bản & Thu thập Case Study", ["Lời thoại chi tiết từng phần", "Khảo sát nhanh định lượng cho đề tài", "2 case study thực tế trong ngành"]),
            ("GĐ3: Thiết kế Slide & Trực quan dữ liệu", ["Bộ slide master đồng bộ nhận diện", "Infographic & biểu đồ so sánh", "Tài liệu đính kèm & phụ lục"]),
            ("GĐ4: Tổng duyệt & Nộp bài", ["Buổi rehearsal bấm giờ nghiêm ngặt", "Bộ câu hỏi phản biện dự kiến", "Nộp file hoàn chỉnh cho GVHD"]),
        ],
    },
    "nckh": {
        "icon": "🔬", "name": "Sinh viên NCKH",
        "phases": [
            ("GĐ1: Đề cương & Tổng quan lý luận", ["Đề cương chi tiết qua Hội đồng", "Lược khảo tài liệu quốc tế (Scopus/ISI)", "Mô hình nghiên cứu & giả thuyết"]),
            ("GĐ2: Thiết kế thang đo & Thu thập dữ liệu", ["Bảng hỏi chuẩn hóa nhiều biến", "Pilot test kiểm tra độ tin cậy", "Khảo sát thực nghiệm N lớn"]),
            ("GĐ3: Xử lý số liệu & Kiểm định", ["Làm sạch dữ liệu, Cronbach's Alpha", "Phân tích nhân tố & hồi quy", "Kiểm định các giả thuyết nghiên cứu"]),
            ("GĐ4: Toàn văn & Poster bảo vệ", ["Bài báo toàn văn đóng bìa", "Poster hội đồng", "Slide & phần bảo vệ trực tiếp"]),
        ],
    },
    "tieuluan": {
        "icon": "📝", "name": "Tiểu luận cuối kỳ",
        "phases": [
            ("GĐ1: Đề cương & Cơ sở lý luận (Ch.1)", ["Đề cương 3 chương được GV duyệt", "Chương 1: khung lý thuyết kinh điển", "Tài liệu tham khảo chuẩn"]),
            ("GĐ2: Thực trạng & Phân tích (Ch.2)", ["Số liệu báo cáo tài chính / thị trường", "Ma trận SWOT - PESTEL", "Chương 2 hoàn chỉnh kèm biểu đồ"]),
            ("GĐ3: Giải pháp & Kết luận (Ch.3)", ["Nhóm giải pháp khả thi + lộ trình", "Dự trù & đo lường hiệu quả", "Phần kết luận & kiến nghị"]),
            ("GĐ4: Định dạng & Nộp bài", ["Định dạng chuẩn, trích dẫn đồng bộ", "Kiểm tra đạo văn < 15%", "Nộp bản in & bản mềm đúng hạn"]),
        ],
    },
    "tu_taao": {
        "icon": "💼", "name": "Tự tạo",
        "phases": [
            ("GĐ1: Khởi tạo & Lập kế hoạch", ["Mục tiêu & phạm vi đề tài", "Phân công trách nhiệm thành viên", "Báo cáo tiến độ theo tuần"]),
            ("GĐ2: Thu thập & Triển Khai nội dung", ["Dữ liệu khảo sát / phỏng vấn", "Phân tích case study liên quan", "Bản thảo phần thân"]),
            ("GĐ3: Tổng hợp & Đánh giá kết quả", ["Phát hiện chính & đánh giá", "Giải pháp và kiến nghị", "Phản biện nội bộ"]),
            ("GĐ4: Hoàn thiện & Nghiệm thu", ["Báo cáo hoàn chỉnh theo quy định", "Slide tóm tắt 15 phút", "Minh chứng đóng góp từng thành viên"]),
        ],
    },
}

STATUSES = ["todo", "in_progress", "review", "done"]


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def require_login(next_name):
    user = db.query_one("SELECT * FROM users WHERE id=%s", (session.get("uid"),))
    if not user:
        flash("Vui lòng đăng nhập để tiếp tục.")
        return None, redirect(url_for("login", next=next_name))
    return user, None


def get_project(pid):
    return db.query_one(
        "SELECT p.*, u.short_name AS created_by_name FROM projects p "
        "LEFT JOIN users u ON u.id=p.created_by WHERE p.id=%s", (pid,))


def project_progress(pid):
    row = db.query_one("SELECT COUNT(*) AS total, "
                       "SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS done "
                       "FROM tasks WHERE project_id=%s", (pid,))
    total = row["total"] or 0
    done = row["done"] or 0
    return (int(done * 100 / total) if total else 0), total, done


def deadline_info(deadline):
    if not deadline:
        return "Chưa đặt"
    delta = (deadline - datetime.now()).total_seconds() / 3600
    if delta < 0:
        return "Đã quá hạn"
    days = int(delta // 86400)
    hours = int(delta % 86400 // 3600)
    if days > 0:
        return f"Còn {days} ngày {hours} giờ"
    return f"Còn {max(hours, 1)} giờ"


def get_members(pid):
    return db.query(
        "SELECT u.id, u.full_name, u.short_name, u.student_id, u.default_role, "
        "u.credibility_points, u.ontime_rate_pct, u.streak_days, pm.role AS member_role "
        "FROM project_members pm JOIN users u ON u.id=pm.user_id "
        "WHERE pm.project_id=%s ORDER BY (pm.role='leader') DESC, u.id", (pid,))


def compute_contribution(pid):
    formula = db.query_one("SELECT * FROM formula_settings WHERE project_id=%s", (pid,))
    if not formula:
        formula = dict(workload_pct=60, ontime_pct=25, peer_pct=15, leader_bonus_pct=0)
    members = get_members(pid)
    tasks = db.query("SELECT assignee_id, points, status, early_bonus_pct FROM tasks WHERE project_id=%s", (pid,))
    rows = []
    for m in members:
        mine = [t for t in tasks if t["assignee_id"] == m["id"] and t["status"] == "done"]
        assigned = [t for t in tasks if t["assignee_id"] == m["id"]]
        points = sum(t["points"] for t in mine)
        bonus = sum(t["early_bonus_pct"] for t in mine)
        ontime = sum(1 for t in mine if t["early_bonus_pct"] > 0)
        rows.append(dict(m, assigned=len(assigned), done=len(mine),
                         points=points, bonus=bonus, ontime=ontime,
                         raw=0, contrib=0.0))
    max_pts = max((r["points"] for r in rows), default=0)
    W, O, P, B = formula["workload_pct"], formula["ontime_pct"], formula["peer_pct"], formula["leader_bonus_pct"]
    for r in rows:
        workload = 100.0 * r["points"] / max(max_pts, 1)
        ontime_rate = (100.0 * r["ontime"] / r["done"]) if r["done"] else 100.0
        r["raw"] = workload * W / 100 + ontime_rate * O / 100 + 60 * P / 100
        if r["member_role"] == "leader" and B:
            r["raw"] += B
    total_raw = sum(r["raw"] for r in rows) or 1
    for r in rows:
        r["contrib"] = round(100.0 * r["raw"] / total_raw, 1)
        r["total_points"] = r["points"] + r["bonus"]
    return formula, rows


def is_leader(user, pid):
    row = db.query_one("SELECT role FROM project_members WHERE project_id=%s AND user_id=%s", (pid, user["id"]))
    return row and row["role"] == "leader"


def is_milestone_past(m):
    if not m.get("due_date"):
        return False
    due = m["due_date"] if isinstance(m["due_date"], datetime) else datetime.strptime(str(m["due_date"]), "%Y-%m-%d")
    return due.date() <= datetime.now().date()


@app.context_processor
def inject_helpers():
    return dict(milestone_done=is_milestone_past, now=datetime.now())


@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next", "dashboard")
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = db.query_one("SELECT * FROM users WHERE email=%s", (email,))
        if not user or not check_password_hash(user["password"], password):
            flash("Email hoặc mật khẩu không đúng.")
            return redirect(url_for("login"))
        session["uid"] = user["id"]
        flash(f"Xin chào {user['full_name']}! Đã đăng nhập thành công.")
        if next_page in ("dashboard", "project", "tasks", "contribution", "meetings", "report"):
            pid = request.args.get("pid")
            if next_page == "dashboard":
                return redirect(url_for("dashboard"))
            if pid:
                return redirect(url_for(next_page, pid=pid))
            return redirect(url_for("dashboard"))
        return redirect(url_for("dashboard"))
    users = db.query("SELECT email, short_name, default_role FROM users ORDER BY id LIMIT 6")
    return render_template("login.html", users=users)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    if "uid" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    user, err = require_login("dashboard")
    if err:
        return err
    user = db.query_one("SELECT * FROM users WHERE id=%s", (session["uid"],))
    projects = db.query(
        "SELECT p.*, pm.role FROM projects p "
        "LEFT JOIN project_members pm ON pm.project_id=p.id AND pm.user_id=%s "
        "WHERE p.active=1 ORDER BY p.id", (user["id"],))
    projs = []
    for p in projects:
        progress, total, done = project_progress(p["id"])
        projs.append(dict(p, progress=progress, total=total, done=done,
                          deadline_text=deadline_info(p["deadline"]),
                         is_member=p["role"] is not None,
                          template_name=TEMPLATES.get(p["template_key"], TEMPLATES["tu_taao"])))
    all_members = db.query("SELECT id, short_name, default_role FROM users ORDER by id")
    return render_template("dashboard.html", user=user, projects=projs,
                           templates=TEMPLATES, all_members=all_members)


@app.route("/projects", methods=["POST"])
def create_project():
    user, err = require_login("dashboard")
    if err:
        return err
    code = (request.form.get("code") or "").strip()
    title = (request.form.get("title") or "").strip()
    tpl_key = request.form.get("template_key") or "tu_taao"
    if tpl_key not in TEMPLATES:
        tpl_key = "tu_taao"
    tpl = TEMPLATES[tpl_key]
    deadline = request.form.get("deadline")
    deadline = f"{deadline} 23:59:00" if deadline else None
    pid = db.execute(
        "INSERT INTO projects (code, title, template_key, teacher, target, deadline, created_by) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (code or "Dự án mới", title or "Đề tài chưa đặt tên", tpl_key,
         (request.form.get("teacher") or "").strip() or "Chưa cập nhật",
         (request.form.get("target") or "").strip() or "Điểm A",
         deadline, user["id"]))
    db.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s,%s,'leader')", (pid, user["id"]))
    for uid in (request.form.getlist("members") or []):
        if uid != str(user["id"]):
            db.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s,%s,'member') ON CONFLICT (project_id, user_id) DO NOTHING", (pid, uid))
    start = datetime.now()
    for i, (phase, _) in enumerate(tpl["phases"]):
        db.execute("INSERT INTO milestones (project_id, label, due_date, sort_order) VALUES (%s,%s,%s,%s)",
                   (pid, phase, (start + timedelta(weeks=i + 1)).strftime("%Y-%m-%d"), i + 1))
    db.execute("INSERT INTO formula_settings (project_id) VALUES (%s)", (pid,))
    flash(f"Đã tạo dự án “{code}” với template {tpl['icon']} {tpl['name']}.")
    return redirect(url_for("project", pid=pid))


@app.route("/project/<int:pid>")
def project(pid):
    user, err = require_login("project")
    if err:
        return err
    p = get_project(pid)
    if not p:
        flash("Không tìm thấy dự án.")
        return redirect(url_for("dashboard"))
    progress, total, done = project_progress(pid)
    formula, contrib = compute_contribution(pid)
    milestones = db.query("SELECT * FROM milestones WHERE project_id=%s ORDER BY sort_order", (pid,))
    tpl = TEMPLATES.get(p["template_key"], TEMPLATES["tu_taao"])
    return render_template("project.html", p=p, user=user, progress=progress, total=total, done=done,
                           deadline_text=deadline_info(p["deadline"]), formula=formula,
                           contrib=contrib, milestones=milestones, tpl=tpl,
                           leader=is_leader(user, pid),
                           meeting_next=db.query_one("SELECT * FROM meetings WHERE project_id=%s ORDER BY scheduled_at DESC LIMIT 1", (pid,)))


@app.route("/project/<int:pid>/tasks", methods=["GET", "POST"])
def tasks(pid):
    user, err = require_login("tasks")
    if err:
        return err
    p = get_project(pid)
    if not p:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            title = (request.form.get("title") or "").strip()
            if title:
                due = request.form.get("due_at")
                db.execute("INSERT INTO tasks (project_id, title, assignee_id, points, status, due_at) VALUES (%s,%s,%s,%s,'todo',%s)",
                           (pid, title, request.form.get("assignee_id") or None,
                            request.form.get("points") or 3, due or None))
                flash("Đã thêm task mới vào cột Cần làm.")
        elif action == "move":
            tk = db.query_one("SELECT * FROM tasks WHERE id=%s AND project_id=%s", (request.form.get("task_id"), pid))
            status = request.form.get("new_status")
            if tk and status in STATUSES:
                if status == "done" and not tk["submitted_at"]:
                    db.execute("UPDATE tasks SET status=%s, submitted_at=%s WHERE id=%s", (status, now_str(), tk["id"]))
                else:
                    db.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, tk["id"]))
                flash(f"Đã chuyển “{tk['title']}” sang cột {status}.")
            return redirect(url_for("tasks", pid=pid))
        elif action == "submit":
            tk = db.query_one("SELECT * FROM tasks WHERE id=%s AND project_id=%s", (request.form.get("task_id"), pid))
            if tk:
                on_time = 10
                if tk["due_at"] and datetime.now() > tk["due_at"]:
                    on_time = 0
                db.execute("UPDATE tasks SET status='done', submitted_at=%s, proof_url=%s, note=%s, early_bonus_pct=%s "
                           "WHERE id=%s",
                           (now_str(), request.form.get("proof_url") or "",
                            (request.form.get("note") or "").strip(), on_time, tk["id"]))
                flash(f"🎉 Đã nộp “{tk['title']}” thành công" + (f" (+{on_time}% thưởng nộp đúng hạn)." if on_time else " (quá hạn, không thưởng)."))
        return redirect(url_for("tasks", pid=pid))
    all_tasks = db.query(
        "SELECT t.*, u.short_name AS assignee_name FROM tasks t "
        "LEFT JOIN users u ON u.id=t.assignee_id WHERE t.project_id=%s ORDER BY FIELD(t.status,'todo','in_progress','review','done'), t.points DESC",
        (pid,))
    columns = {s: [] for s in STATUSES}
    for t in all_tasks:
        columns[t["status"]].append(dict(t, assignee=t["assignee_name"] or "Chưa gán",
                                        deadline_short=deadline_info(t["due_at"])))
    members = get_members(pid)
    return render_template("tasks.html", p=p, user=user, columns=columns, statuses=STATUSES,
                           members=members, deadline_info=deadline_info)


@app.route("/project/<int:pid>/contribution", methods=["GET", "POST"])
def contribution(pid):
    user, err = require_login("contribution")
    if err:
        return err
    p = get_project(pid)
    if not p:
        return redirect(url_for("dashboard"))
    leader = is_leader(user, pid)
    if request.method == "POST" and leader:
        w = int(request.form.get("workload") or 60)
        o = int(request.form.get("ontime") or 25)
        pp = int(request.form.get("peer") or 15)
        b = int(request.form.get("leader_bonus") or 0)
        if db.query_one("SELECT project_id FROM formula_settings WHERE project_id=%s", (pid,)):
            db.execute("UPDATE formula_settings SET workload_pct=%s, ontime_pct=%s, peer_pct=%s, leader_bonus_pct=%s WHERE project_id=%s",
                       (w, o, pp, b, pid))
        else:
            db.execute("INSERT INTO formula_settings (project_id, workload_pct, ontime_pct, peer_pct, leader_bonus_pct) VALUES (%s,%s,%s,%s,%s)",
                       (pid, w, o, pp, b))
        flash("Đã lưu công thức Contribution mới.")
        return redirect(url_for("contribution", pid=pid))
    formula, contrib = compute_contribution(pid)
    return render_template("contribution.html", p=p, user=user, formula=formula, contrib=contrib,
                           leader=leader, total_points=sum(r["total_points"] for r in contrib))


@app.route("/project/<int:pid>/meetings", methods=["GET", "POST"])
def meetings(pid):
    user, err = require_login("meetings")
    if err:
        return err
    p = get_project(pid)
    if not p:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "meeting":
            db.execute("INSERT INTO meetings (project_id, title, scheduled_at, host_name, meet_link, agenda) VALUES (%s,%s,%s,%s,%s,%s)",
                       (pid, (request.form.get("title") or "Cuộc họp nhóm").strip(),
                        request.form.get("time") or None, (request.form.get("host") or "").strip() or user["short_name"],
                        request.form.get("meet_link") or "https://meet.google.com/",
                        (request.form.get("agenda") or "").strip()))
            flash("Đã lên lịch cuộc họp mới.")
        elif action == "doc":
            db.execute("INSERT INTO documents (project_id, name, file_type, size_label, drive_url, uploaded_by) VALUES (%s,%s,%s,%s,%s,%s)",
                       (pid, (request.form.get("name") or "Tài liệu").strip(),
                        (request.form.get("file_type") or "Docs").strip() or "Docs",
                        (request.form.get("size_label") or "").strip(),
                        (request.form.get("drive_url") or "").strip(),
                        user["short_name"]))
            flash("Đã thêm tài liệu vào Kho.")
        return redirect(url_for("meetings", pid=pid))
    meets = db.query("SELECT * FROM meetings WHERE project_id=%s ORDER BY scheduled_at DESC", (pid,))
    docs = db.query("SELECT * FROM documents WHERE project_id=%s ORDER BY id DESC", (pid,))
    return render_template("meetings.html", p=p, user=user, meetings=meets, docs=docs, fmt=fmt_dt)


def fmt_dt(d):
    if not d:
        return ""
    return d.strftime("%d/%m/%Y %H:%M")


@app.route("/project/<int:pid>/report")
def report(pid):
    user, err = require_login("report")
    if err:
        return err
    p = get_project(pid)
    if not p:
        return redirect(url_for("dashboard"))
    formula, contrib = compute_contribution(pid)
    progress, total, done = project_progress(pid)
    members = get_members(pid)
    milestones = db.query("SELECT * FROM milestones WHERE project_id=%s ORDER BY sort_order", (pid,))
    leader = next((m for m in members if m["member_role"] == "leader"), None)
    return render_template("report.html", p=p, user=user, formula=formula, contrib=contrib,
                           progress=progress, total=total, done=done,
                           deadline_text=deadline_info(p["deadline"]),
                           members=members, milestones=milestones, leader=leader,
                           print_note=datetime.now().strftime("%d/%m/%Y"))
