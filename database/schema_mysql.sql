-- ====================================================================
-- HỆ THỐNG PHÂN LOẠI PHẢN HỒI CỦA SINH VIÊN BẰNG AI
-- File: schema_mysql.sql (Dùng cho MySQL 8.0+)
-- Môn: Phân tích và Thiết kế Hệ thống
-- Thành viên: Nguyễn Ngọc Phúc, Hà Minh Diệu (C)
-- ====================================================================

DROP DATABASE IF EXISTS student_feedback_db;
CREATE DATABASE student_feedback_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_feedback_db;

-- 1. Bảng users
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'TEACHER', 'ADMIN') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Bảng students
CREATE TABLE students (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    major VARCHAR(100) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Bảng teachers
CREATE TABLE teachers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    teacher_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    academic_title VARCHAR(50) NULL,
    department VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Bảng admins
CREATE TABLE admins (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    office_department VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Bảng categories
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    icon VARCHAR(50) DEFAULT 'bi-tag',
    color VARCHAR(20) DEFAULT '#4f46e5'
) ENGINE=InnoDB;

-- 6. Bảng feedbacks
CREATE TABLE feedbacks (
    feedback_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    attachment_url VARCHAR(255) NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    status ENUM('PENDING', 'PROCESSING', 'RESOLVED', 'REJECTED') DEFAULT 'PENDING',
    assigned_department VARCHAR(100) DEFAULT 'Phòng Tiếp nhận & Xử lý',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Bảng ai_classifications
CREATE TABLE ai_classifications (
    classification_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    feedback_id BIGINT NOT NULL UNIQUE,
    sentiment_label ENUM('POSITIVE', 'NEUTRAL', 'NEGATIVE') NOT NULL DEFAULT 'NEUTRAL',
    sentiment_score FLOAT DEFAULT 0.0,
    overall_confidence FLOAT DEFAULT 0.0,
    is_urgent BOOLEAN DEFAULT FALSE,
    is_reviewed BOOLEAN DEFAULT FALSE,
    is_corrected_by_admin BOOLEAN DEFAULT FALSE,
    reviewed_by BIGINT NULL,
    reviewed_at TIMESTAMP NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. Bảng feedback_categories (Multi-label mapping N - N)
CREATE TABLE feedback_categories (
    mapping_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    feedback_id BIGINT NOT NULL,
    category_id INT NOT NULL,
    is_ai_predicted BOOLEAN DEFAULT TRUE,
    confidence_score FLOAT DEFAULT 0.0,
    is_final BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
    UNIQUE KEY uq_feedback_category (feedback_id, category_id)
) ENGINE=InnoDB;

-- 9. Bảng feedback_responses
CREATE TABLE feedback_responses (
    response_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    feedback_id BIGINT NOT NULL,
    staff_id BIGINT NOT NULL,
    response_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 10. Bảng ai_retrain_logs
CREATE TABLE ai_retrain_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    feedback_id BIGINT NOT NULL,
    feedback_text TEXT NOT NULL,
    predicted_categories TEXT NOT NULL,
    approved_categories TEXT NOT NULL,
    sentiment_label VARCHAR(20) NULL,
    was_modified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(feedback_id) ON DELETE CASCADE
) ENGINE=InnoDB;
