-- ====================================================================
-- HỆ THỐNG PHÂN LOẠI PHẢN HỒI CỦA SINH VIÊN BẰNG AI
-- Môn học: Phân tích và Thiết kế Hệ thống (PTTKHT)
-- Thành viên:
--   1. Nguyễn Ngọc Phúc
--   2. Hà Minh Diệu (Nhóm trưởng - C)
-- Schema DDL cho SQLite / RDBMS Chuẩn
-- ====================================================================

-- 1. Bảng Users: Tài khoản & Xác thực chung
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('STUDENT', 'TEACHER', 'ADMIN')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Students: Thông tin chi tiết Sinh viên (Quan hệ 1-1 với Users)
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    major VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Bảng Teachers: Thông tin chi tiết Giảng viên (Quan hệ 1-1 với Users)
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    teacher_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    academic_title VARCHAR(50),
    department VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Bảng Admins: Ban quản trị & Cán bộ phòng ban (Quan hệ 1-1 với Users)
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    office_department VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Bảng Categories: Danh mục phân loại phản hồi
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'bi-tag',
    color VARCHAR(20) DEFAULT '#4f46e5'
);

-- 6. Bảng Feedbacks: Phản hồi/Góp ý của sinh viên
CREATE TABLE IF NOT EXISTS feedbacks (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    attachment_url VARCHAR(255),
    is_anonymous BOOLEAN DEFAULT 0,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'PROCESSING', 'RESOLVED', 'REJECTED')),
    assigned_department VARCHAR(100) DEFAULT 'Phòng Tiếp nhận & Xử lý',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 7. Bảng AI_Classifications: Kết quả dự đoán tổng thể & Cảm xúc từ AI
CREATE TABLE IF NOT EXISTS ai_classifications (
    classification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id INTEGER UNIQUE NOT NULL,
    sentiment_label VARCHAR(20) CHECK(sentiment_label IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')),
    sentiment_score REAL DEFAULT 0.0,
    overall_confidence REAL DEFAULT 0.0,
    is_urgent BOOLEAN DEFAULT 0,
    is_reviewed BOOLEAN DEFAULT 0,
    is_corrected_by_admin BOOLEAN DEFAULT 0,
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 8. Bảng Feedback_Categories: Xử lý Đa nhãn (Multi-label Classification N - N)
CREATE TABLE IF NOT EXISTS feedback_categories (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    is_ai_predicted BOOLEAN DEFAULT 1,
    confidence_score REAL DEFAULT 0.0,
    is_final BOOLEAN DEFAULT 1,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
    UNIQUE(feedback_id, category_id)
);

-- 9. Bảng Feedback_Responses: Câu trả lời từ nhà trường/phòng ban
CREATE TABLE IF NOT EXISTS feedback_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    response_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Bảng AI_Retrain_Logs: Ghi nhận Feedback Loop để tái huấn luyện mô hình AI
CREATE TABLE IF NOT EXISTS ai_retrain_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id INTEGER NOT NULL,
    feedback_text TEXT NOT NULL,
    predicted_categories TEXT NOT NULL,
    approved_categories TEXT NOT NULL,
    sentiment_label VARCHAR(20),
    was_modified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE
);
