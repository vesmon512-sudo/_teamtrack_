DROP TABLE IF EXISTS formula_settings, tasks, documents, meetings,
  milestones, project_members, projects, users CASCADE;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(190) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  full_name VARCHAR(190) NOT NULL,
  short_name VARCHAR(90) NOT NULL,
  student_id VARCHAR(60),
  university VARCHAR(150),
  default_role VARCHAR(40),
  streak_days INT DEFAULT 0,
  credibility_points INT DEFAULT 0,
  ontime_rate_pct INT DEFAULT 100,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  code VARCHAR(150) NOT NULL,
  title TEXT NOT NULL,
  template_key VARCHAR(40) NOT NULL DEFAULT 'thuyettrinh',
  teacher VARCHAR(150),
  target VARCHAR(150),
  deadline TIMESTAMP,
  active SMALLINT DEFAULT 1,
  created_by INT REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_members (
  project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL DEFAULT 'member',
  PRIMARY KEY (project_id, user_id)
);

CREATE TABLE milestones (
  id SERIAL PRIMARY KEY,
  project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  label VARCHAR(255) NOT NULL,
  due_date DATE,
  sort_order INT DEFAULT 0
);

CREATE TABLE meetings (
  id SERIAL PRIMARY KEY,
  project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  scheduled_at TIMESTAMP,
  host_name VARCHAR(120),
  meet_link VARCHAR(255),
  agenda TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  file_type VARCHAR(40),
  size_label VARCHAR(40),
  drive_url VARCHAR(255),
  uploaded_by VARCHAR(120),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  assignee_id INT REFERENCES users(id) ON DELETE SET NULL,
  points INT NOT NULL DEFAULT 3,
  status VARCHAR(20) NOT NULL DEFAULT 'todo',
  due_at TIMESTAMP,
  proof_url VARCHAR(255),
  note VARCHAR(255),
  submitted_at TIMESTAMP,
  early_bonus_pct INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE formula_settings (
  project_id INT PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE,
  workload_pct INT NOT NULL DEFAULT 60,
  ontime_pct INT NOT NULL DEFAULT 25,
  peer_pct INT NOT NULL DEFAULT 15,
  leader_bonus_pct INT NOT NULL DEFAULT 0
);

-- Chặn truy cập công khai qua Supabase API (bảng users chứa hash mật khẩu).
-- Flask kết nối bằng role postgres nên vẫn đọc/ghi bình thường.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE formula_settings ENABLE ROW LEVEL SECURITY;