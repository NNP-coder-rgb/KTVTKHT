-- ====================================================================
-- HỆ THỐNG PHÂN LOẠI PHẢN HỒI CỦA SINH VIÊN BẰNG AI
-- File: schema_postgres.sql (Dùng cho PostgreSQL 14+)
-- Môn: Phân tích và Thiết kế Hệ thống
-- Thành viên: Nguyễn Ngọc Phúc, Hà Minh Diệu (C)
-- ====================================================================

CREATE TYPE user_role AS ENUM ('STUDENT', 'TEACHER', 'ADMIN');
CREATE TYPE feedback_status AS ENUM ('PENDING', 'PROCESSING', 'RESOLVED', 'REJECTED');
CREATE TYPE sentiment_type AS ENUM ('POSITIVE', 'NEUTRAL', 'NEGATIVE');

-- 1. Bảng users
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng students
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    major VARCHAR(100)
);

-- 3. Bảng teachers
CREATE TABLE teachers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    teacher_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    academic_title VARCHAR(50),
    department VARCHAR(100) NOT NULL
);

-- 4. Bảng admins
CREATE TABLE admins (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    office_department VARCHAR(100) NOT NULL
);

-- 5. Bảng categories
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'bi-tag',
    color VARCHAR(20) DEFAULT '#4f46e5'
);

-- 6. Bảng feedbacks
CREATE TABLE feedbacks (
    feedback_id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    attachment_url VARCHAR(255),
    is_anonymous BOOLEAN DEFAULT FALSE,
    status feedback_status DEFAULT 'PENDING',
    assigned_department VARCHAR(100) DEFAULT 'Phòng Tiếp nhận & Xử lý',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Bảng ai_classifications
CREATE TABLE ai_classifications (
    classification_id BIGSERIAL PRIMARY KEY,
    feedback_id BIGINT NOT NULL UNIQUE REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    sentiment_label sentiment_type NOT NULL DEFAULT 'NEUTRAL',
    sentiment_score REAL DEFAULT 0.0,
    overall_confidence REAL DEFAULT 0.0,
    is_urgent BOOLEAN DEFAULT FALSE,
    is_reviewed BOOLEAN DEFAULT FALSE,
    is_corrected_by_admin BOOLEAN DEFAULT FALSE,
    reviewed_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Bảng feedback_categories (Multi-label mapping N - N)
CREATE TABLE feedback_categories (
    mapping_id BIGSERIAL PRIMARY KEY,
    feedback_id BIGINT NOT NULL REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    is_ai_predicted BOOLEAN DEFAULT TRUE,
    confidence_score REAL DEFAULT 0.0,
    is_final BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_feedback_category UNIQUE (feedback_id, category_id)
);

-- 9. Bảng feedback_responses
CREATE TABLE feedback_responses (
    response_id BIGSERIAL PRIMARY KEY,
    feedback_id BIGINT NOT NULL REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    staff_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    response_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Bảng ai_retrain_logs
CREATE TABLE ai_retrain_logs (
    log_id BIGSERIAL PRIMARY KEY,
    feedback_id BIGINT NOT NULL REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    feedback_text TEXT NOT NULL,
    predicted_categories TEXT NOT NULL,
    approved_categories TEXT NOT NULL,
    sentiment_label VARCHAR(20),
    was_modified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
