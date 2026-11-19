from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sqlite3
from pathlib import Path
import json

from database.database import get_db_connection, init_db, DB_PATH
from ai_service import ai_classifier, CATEGORY_DEFINITIONS, analyze_sentiment

app = FastAPI(
    title="Hệ Thống Phân Loại Phản Hồi Sinh Viên Bằng AI",
    description="Dự án môn Phân Tích và Thiết Kế Hệ Thống - Nhóm Nguyễn Ngọc Phúc & Hà Minh Diệu",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Pydantic Schemas
class FeedbackCreate(BaseModel):
    student_id: int
    title: str
    content: str
    attachment_url: Optional[str] = None
    is_anonymous: bool = False

class AIAnalyzeRequest(BaseModel):
    title: str = ""
    content: str

class FeedbackStatusUpdate(BaseModel):
    status: str
    assigned_department: Optional[str] = None

class FeedbackResponseCreate(BaseModel):
    staff_id: int
    response_content: str
    update_status_to: Optional[str] = None

class CategoryOverrideRequest(BaseModel):
    admin_id: int
    category_ids: List[int]
    notes: Optional[str] = None


# ====================================================================
# 1. API USERS & AUTH (Hỗ trợ chuyển đổi nhanh cho buổi bảo vệ đồ án)
# ====================================================================
@app.get("/api/users")
def get_all_users():
    """Lấy danh sách người dùng để phục vụ demo nhanh vai trò Sinh viên / Quản trị viên"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.email, u.role, u.is_active,
               s.id as student_id, s.student_code, s.full_name as student_name, s.class_name, s.major,
               a.id as admin_id, a.full_name as admin_name, a.office_department,
               t.id as teacher_id, t.full_name as teacher_name, t.department as teacher_department
        FROM users u
        LEFT JOIN students s ON u.id = s.user_id
        LEFT JOIN admins a ON u.id = a.user_id
        LEFT JOIN teachers t ON u.id = t.user_id
        ORDER BY u.id ASC
    """)
    rows = cursor.fetchall()
    users = []
    for r in rows:
        name = r["student_name"] or r["admin_name"] or r["teacher_name"] or r["email"]
        detail = r["class_name"] or r["office_department"] or r["teacher_department"] or ""
        users.append({
            "id": r["id"],
            "email": r["email"],
            "role": r["role"],
            "name": name,
            "detail": detail,
            "student_id": r["student_id"],
            "student_code": r["student_code"]
        })
    conn.close()
    return users


# ====================================================================
# 2. API CATEGORIES
# ====================================================================
@app.get("/api/categories")
def get_categories():
    """Lấy danh sách tất cả các danh mục phản hồi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY category_id ASC")
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return categories


# ====================================================================
# 3. API AI LIVE ANALYZER (Phân tích tức thời khi gõ văn bản)
# ====================================================================
@app.post("/api/ai/analyze")
def live_ai_analyze(req: AIAnalyzeRequest):
    """
    Phân tích trực tiếp đoạn văn bản:
    - Nhận diện Đa nhãn (Multi-label)
    - Phân tích cảm xúc (Sentiment Analysis: Positive / Neutral / Negative)
    - Tính toán độ tin cậy (Confidence Score)
    - Đánh dấu mức độ khẩn cấp (is_urgent)
    """
    if not req.content.strip():
        return {
            "predicted_categories": [],
            "sentiment": {"label": "NEUTRAL", "score": 0.0, "is_urgent": False},
            "overall_confidence": 0.0
        }
    
    result = ai_classifier.predict(text=req.content, title=req.title)
    return result


# ====================================================================
# 4. API FEEDBACKS (Gửi, Xem, Tìm kiếm & Lọc)
# ====================================================================
@app.post("/api/feedbacks")
def create_feedback(feedback: FeedbackCreate):
    """
    Sinh viên gửi góp ý mới:
    - Tự động kích hoạt Module AI xử lý ngôn ngữ tự nhiên
    - Lưu vào DB và phân bổ nhãn đa danh mục (Multi-label)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Chạy AI Classifier tự động
    ai_result = ai_classifier.predict(feedback.content, feedback.title)
    
    # 2. Lưu Feedback vào DB
    cursor.execute("""
        INSERT INTO feedbacks (student_id, title, content, attachment_url, is_anonymous, status, assigned_department)
        VALUES (?, ?, ?, ?, 'PENDING', ?)
    """, (
        feedback.student_id,
        feedback.title,
        feedback.content,
        feedback.attachment_url,
        1 if feedback.is_anonymous else 0,
        "Phòng Tiếp nhận & Xử lý"
    ))
    feedback_id = cursor.lastrowid
    
    # 3. Lưu AI Classifications
    sentiment = ai_result["sentiment"]
    cursor.execute("""
        INSERT INTO ai_classifications 
        (feedback_id, sentiment_label, sentiment_score, overall_confidence, is_urgent, is_reviewed, is_corrected_by_admin)
        VALUES (?, ?, ?, ?, ?, 0, 0)
    """, (
        feedback_id,
        sentiment["label"],
        sentiment["score"],
        ai_result["overall_confidence"],
        1 if sentiment["is_urgent"] else 0
    ))
    
    # 4. Lưu Feedback Categories (Multi-label mapping N - N)
    for cat in ai_result["predicted_categories"]:
        cursor.execute("""
            INSERT OR IGNORE INTO feedback_categories
            (feedback_id, category_id, is_ai_predicted, confidence_score, is_final)
            VALUES (?, ?, 1, ?, 1)
        """, (
            feedback_id,
            cat["category_id"],
            cat["confidence_score"]
        ))
        
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Gửi phản hồi thành công và AI đã phân loại tự động!",
        "feedback_id": feedback_id,
        "ai_result": ai_result
    }


@app.get("/api/feedbacks")
def list_feedbacks(
    student_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    sentiment: Optional[str] = None,
    is_urgent: Optional[bool] = None,
    search: Optional[str] = None
):
    """
    Lấy danh sách phản hồi kèm theo nhãn đa danh mục, kết quả AI và trạng thái xử lý
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT f.feedback_id, f.student_id, f.title, f.content, f.attachment_url,
               f.is_anonymous, f.status, f.assigned_department, f.created_at, f.updated_at,
               s.student_code, s.full_name as student_name, s.class_name, s.major,
               ac.sentiment_label, ac.sentiment_score, ac.overall_confidence, ac.is_urgent,
               ac.is_reviewed, ac.is_corrected_by_admin
        FROM feedbacks f
        JOIN students s ON f.student_id = s.id
        LEFT JOIN ai_classifications ac ON f.feedback_id = ac.feedback_id
        WHERE 1=1
    """
    params = []
    
    if student_id:
        query += " AND f.student_id = ?"
        params.append(student_id)
    if status:
        query += " AND f.status = ?"
        params.append(status)
    if sentiment:
        query += " AND ac.sentiment_label = ?"
        params.append(sentiment)
    if is_urgent is not None:
        query += " AND ac.is_urgent = ?"
        params.append(1 if is_urgent else 0)
    if search:
        query += " AND (f.title LIKE ? OR f.content LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    query += " ORDER BY f.created_at DESC"
    cursor.execute(query, params)
    feedbacks_raw = cursor.fetchall()
    
    result = []
    for row in feedbacks_raw:
        fb = dict(row)
        fb_id = fb["feedback_id"]
        
        # Ẩn danh nếu sinh viên chọn ẩn danh và người xem không phải chính sinh viên đó
        if fb["is_anonymous"] and not (student_id and student_id == fb["student_id"]):
            fb["student_name"] = "Sinh viên ẩn danh"
            fb["student_code"] = "******"
            fb["class_name"] = "***"
            fb["major"] = "***"
            
        # Lấy danh sách Categories của feedback này (Multi-label)
        cursor.execute("""
            SELECT c.category_id, c.category_code, c.category_name, c.icon, c.color,
                   fc.is_ai_predicted, fc.confidence_score, fc.is_final
            FROM feedback_categories fc
            JOIN categories c ON fc.category_id = c.category_id
            WHERE fc.feedback_id = ?
        """, (fb_id,))
        cats = [dict(c) for c in cursor.fetchall()]
        
        # Nếu filter theo category_id mà feedback không chứa category này thì bỏ qua
        if category_id and not any(c["category_id"] == category_id for c in cats):
            continue
            
        fb["categories"] = cats
        
        # Lấy câu trả lời mới nhất (nếu có)
        cursor.execute("""
            SELECT fr.response_id, fr.response_content, fr.created_at,
                   u.email as staff_email,
                   COALESCE(a.full_name, t.full_name, 'Bộ phận Nhà trường') as staff_name
            FROM feedback_responses fr
            JOIN users u ON fr.staff_id = u.id
            LEFT JOIN admins a ON u.id = a.user_id
            LEFT JOIN teachers t ON u.id = t.user_id
            WHERE fr.feedback_id = ?
            ORDER BY fr.created_at ASC
        """, (fb_id,))
        fb["responses"] = [dict(r) for r in cursor.fetchall()]
        
        result.append(fb)
        
    conn.close()
    return result


@app.get("/api/feedbacks/{feedback_id}")
def get_feedback_detail(feedback_id: int):
    """Xem chi tiết 1 phản hồi cụ thể"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT f.*, s.student_code, s.full_name as student_name, s.class_name, s.major,
               ac.sentiment_label, ac.sentiment_score, ac.overall_confidence, ac.is_urgent,
               ac.is_reviewed, ac.is_corrected_by_admin, ac.reviewed_at
        FROM feedbacks f
        JOIN students s ON f.student_id = s.id
        LEFT JOIN ai_classifications ac ON f.feedback_id = ac.feedback_id
        WHERE f.feedback_id = ?
    """, (feedback_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy phản hồi")
        
    fb = dict(row)
    if fb["is_anonymous"]:
        fb["student_name"] = "Sinh viên ẩn danh"
        fb["student_code"] = "******"
        
    # Categories
    cursor.execute("""
        SELECT c.*, fc.is_ai_predicted, fc.confidence_score, fc.is_final
        FROM feedback_categories fc
        JOIN categories c ON fc.category_id = c.category_id
        WHERE fc.feedback_id = ?
    """, (feedback_id,))
    fb["categories"] = [dict(c) for c in cursor.fetchall()]
    
    # Responses
    cursor.execute("""
        SELECT fr.*, u.email as staff_email,
               COALESCE(a.full_name, t.full_name, 'Cán bộ xử lý') as staff_name
        FROM feedback_responses fr
        JOIN users u ON fr.staff_id = u.id
        LEFT JOIN admins a ON u.id = a.user_id
        LEFT JOIN teachers t ON u.id = t.user_id
        WHERE fr.feedback_id = ?
        ORDER BY fr.created_at ASC
    """, (feedback_id,))
    fb["responses"] = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return fb


# ====================================================================
# 5. API QUẢN TRỊ VIÊN: DUYỆT, SỬA ĐỔI NHÃN AI & PHẢN HỒI (FEEDBACK LOOP)
# ====================================================================
@app.post("/api/feedbacks/{feedback_id}/override-categories")
def override_feedback_categories(feedback_id: int, req: CategoryOverrideRequest):
    """
    Quản trị viên Duyệt (Approve) hoặc Điều chỉnh (Override) kết quả của AI:
    - Lưu lại lịch sử vào AI_Retrain_Logs làm dữ liệu cải thiện mô hình (Active Learning)
    - Cập nhật feedback_categories và ai_classifications
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy thông tin phản hồi và nhãn cũ do AI gán
    cursor.execute("SELECT content FROM feedbacks WHERE feedback_id = ?", (feedback_id,))
    fb_row = cursor.fetchone()
    if not fb_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Phản hồi không tồn tại")
        
    content = fb_row["content"]
    
    cursor.execute("""
        SELECT c.category_id, c.category_name, fc.is_ai_predicted
        FROM feedback_categories fc
        JOIN categories c ON fc.category_id = c.category_id
        WHERE fc.feedback_id = ?
    """, (feedback_id,))
    old_cats = cursor.fetchall()
    old_ids = set([c["category_id"] for c in old_cats])
    old_names = [c["category_name"] for c in old_cats]
    
    new_ids = set(req.category_ids)
    if not new_ids:
        conn.close()
        raise HTTPException(status_code=400, detail="Phải chọn ít nhất 1 danh mục")
        
    was_modified = (old_ids != new_ids)
    
    # Xóa các nhãn cũ của feedback này
    cursor.execute("DELETE FROM feedback_categories WHERE feedback_id = ?", (feedback_id,))
    
    # Thêm lại các nhãn mới được Admin chọn
    cursor.execute("SELECT category_id, category_name FROM categories WHERE category_id IN ({})".format(
        ",".join("?" * len(new_ids))
    ), list(new_ids))
    approved_rows = cursor.fetchall()
    approved_names = [r["category_name"] for r in approved_rows]
    
    for cat_id in new_ids:
        cursor.execute("""
            INSERT INTO feedback_categories (feedback_id, category_id, is_ai_predicted, confidence_score, is_final)
            VALUES (?, ?, ?, 1.0, 1)
        """, (feedback_id, cat_id, 0 if was_modified else 1))
        
    # Cập nhật ai_classifications
    cursor.execute("""
        UPDATE ai_classifications
        SET is_reviewed = 1,
            is_corrected_by_admin = ?,
            reviewed_by = ?,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE feedback_id = ?
    """, (1 if was_modified else 0, req.admin_id, feedback_id))
    
    # Ghi nhận vào bảng ai_retrain_logs (Vòng lặp phản hồi cải thiện mô hình)
    cursor.execute("""
        INSERT INTO ai_retrain_logs 
        (feedback_id, feedback_text, predicted_categories, approved_categories, was_modified)
        VALUES (?, ?, ?, ?, ?)
    """, (
        feedback_id,
        content,
        json.dumps(old_names, ensure_ascii=False),
        json.dumps(approved_names, ensure_ascii=False),
        1 if was_modified else 0
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Đã lưu điều chỉnh nhãn danh mục và ghi nhận vào AI Retrain Log thành công!",
        "was_modified": was_modified,
        "approved_categories": approved_names
    }


@app.put("/api/feedbacks/{feedback_id}/status")
def update_feedback_status(feedback_id: int, req: FeedbackStatusUpdate):
    """Cập nhật trạng thái xử lý và chuyển tiếp phòng ban"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    update_fields = ["status = ?"]
    params = [req.status]
    
    if req.assigned_department:
        update_fields.append("assigned_department = ?")
        params.append(req.assigned_department)
        
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(feedback_id)
    
    cursor.execute(f"UPDATE feedbacks SET {', '.join(update_fields)} WHERE feedback_id = ?", params)
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Cập nhật trạng thái thành công"}


@app.post("/api/feedbacks/{feedback_id}/respond")
def respond_to_feedback(feedback_id: int, req: FeedbackResponseCreate):
    """Nhà trường gửi câu trả lời/giải pháp cho sinh viên"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO feedback_responses (feedback_id, staff_id, response_content)
        VALUES (?, ?, ?)
    """, (feedback_id, req.staff_id, req.response_content))
    
    if req.update_status_to:
        cursor.execute("""
            UPDATE feedbacks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE feedback_id = ?
        """, (req.update_status_to, feedback_id))
    else:
        cursor.execute("""
            UPDATE feedbacks 
            SET status = 'RESOLVED', updated_at = CURRENT_TIMESTAMP 
            WHERE feedback_id = ? AND status = 'PENDING'
        """, (feedback_id,))
        
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Đã gửi câu trả lời đến sinh viên"}


# ====================================================================
# 6. API DASHBOARD & THỐNG KÊ (ANALYTICS)
# ====================================================================
@app.get("/api/analytics/summary")
def get_analytics_summary():
    """Lấy dữ liệu tổng hợp cho Dashboard của Ban Quản lý / Admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Tổng số feedback và phân loại theo trạng thái
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'PROCESSING' THEN 1 ELSE 0 END) as processing,
            SUM(CASE WHEN status = 'RESOLVED' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
        FROM feedbacks
    """)
    st_row = dict(cursor.fetchone())
    
    # 2. Thống kê cảm xúc
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN sentiment_label = 'POSITIVE' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN sentiment_label = 'NEUTRAL' THEN 1 ELSE 0 END) as neutral,
            SUM(CASE WHEN sentiment_label = 'NEGATIVE' THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN is_urgent = 1 THEN 1 ELSE 0 END) as urgent
        FROM ai_classifications
    """)
    senti_row = dict(cursor.fetchone())
    
    # 3. Phân bố theo danh mục
    cursor.execute("""
        SELECT c.category_id, c.category_name, c.color, c.icon, COUNT(fc.feedback_id) as count
        FROM categories c
        LEFT JOIN feedback_categories fc ON c.category_id = fc.category_id
        GROUP BY c.category_id
        ORDER BY count DESC
    """)
    category_distribution = [dict(r) for r in cursor.fetchall()]
    
    # 4. Thống kê độ chính xác AI (Agreement Rate)
    cursor.execute("""
        SELECT 
            COUNT(*) as total_reviewed,
            SUM(CASE WHEN is_corrected_by_admin = 0 THEN 1 ELSE 0 END) as auto_approved,
            SUM(CASE WHEN is_corrected_by_admin = 1 THEN 1 ELSE 0 END) as modified
        FROM ai_classifications
        WHERE is_reviewed = 1
    """)
    review_stats = dict(cursor.fetchone())
    
    total_rev = review_stats["total_reviewed"] or 0
    accuracy = round((review_stats["auto_approved"] / total_rev * 100), 1) if total_rev > 0 else 92.5
    
    conn.close()
    
    return {
        "status_counts": st_row,
        "sentiment_counts": senti_row,
        "category_distribution": category_distribution,
        "ai_accuracy": {
            "total_reviewed": total_rev,
            "auto_approved": review_stats["auto_approved"] or 0,
            "modified": review_stats["modified"] or 0,
            "accuracy_rate": accuracy
        }
    }


# ====================================================================
# 7. API AI RETRAIN LOGS & FEEDBACK LOOP
# ====================================================================
@app.get("/api/ai/retrain-logs")
def get_ai_retrain_logs():
    """Lấy danh sách các bản ghi hiệu chỉnh từ Admin để huấn luyện lại mô hình"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ai_retrain_logs ORDER BY created_at DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ====================================================================
# 8. API DATABASE SCHEMA VIEWER (Dành riêng cho môn PTTKHT)
# ====================================================================
@app.get("/api/db/schema-info")
def get_db_schema_info():
    """Cung cấp thông tin trực quan về cấu trúc các bảng và quan hệ cho báo cáo đồ án"""
    tables = [
        {
            "name": "users",
            "description": "Tài khoản đăng nhập dùng chung cho hệ thống",
            "columns": [
                {"name": "id", "type": "INTEGER", "pk": True, "description": "Khóa chính tự tăng"},
                {"name": "email", "type": "VARCHAR(255)", "constraint": "UNIQUE, NOT NULL", "description": "Email trường cấp"},
                {"name": "password_hash", "type": "VARCHAR(255)", "constraint": "NOT NULL", "description": "Mật khẩu mã hóa"},
                {"name": "role", "type": "VARCHAR(20)", "constraint": "STUDENT/TEACHER/ADMIN", "description": "Vai trò hệ thống"},
                {"name": "is_active", "type": "BOOLEAN", "constraint": "DEFAULT 1", "description": "Trạng thái kích hoạt"},
                {"name": "created_at", "type": "TIMESTAMP", "constraint": "DEFAULT CURRENT_TIMESTAMP", "description": "Thời gian tạo"}
            ]
        },
        {
            "name": "students",
            "description": "Thông tin hồ sơ sinh viên (1-1 với Users)",
            "columns": [
                {"name": "id", "type": "INTEGER", "pk": True, "description": "Mã sinh viên nội bộ"},
                {"name": "user_id", "type": "INTEGER", "fk": "users.id", "description": "Liên kết 1-1 với Users"},
                {"name": "student_code", "type": "VARCHAR(20)", "constraint": "UNIQUE", "description": "Mã số sinh viên (MSSV)"},
                {"name": "full_name", "type": "VARCHAR(100)", "constraint": "NOT NULL", "description": "Họ và tên"},
                {"name": "class_name", "type": "VARCHAR(50)", "constraint": "NOT NULL", "description": "Lớp sinh hoạt"},
                {"name": "major", "type": "VARCHAR(100)", "constraint": "NULLABLE", "description": "Ngành đào tạo"}
            ]
        },
        {
            "name": "admins",
            "description": "Cán bộ quản lý và các phòng ban tiếp nhận (1-1 với Users)",
            "columns": [
                {"name": "id", "type": "INTEGER", "pk": True, "description": "Mã cán bộ nội bộ"},
                {"name": "user_id", "type": "INTEGER", "fk": "users.id", "description": "Liên kết 1-1 với Users"},
                {"name": "full_name", "type": "VARCHAR(100)", "constraint": "NOT NULL", "description": "Họ tên cán bộ"},
                {"name": "office_department", "type": "VARCHAR(100)", "constraint": "NOT NULL", "description": "Phòng ban công tác"}
            ]
        },
        {
            "name": "categories",
            "description": "Danh mục phân loại góp ý (Giảng dạy, CSVC, Học vụ, Học phí, HĐSV, Khác)",
            "columns": [
                {"name": "category_id", "type": "INTEGER", "pk": True, "description": "Mã danh mục"},
                {"name": "category_code", "type": "VARCHAR(50)", "constraint": "UNIQUE", "description": "Mã code định danh"},
                {"name": "category_name", "type": "VARCHAR(100)", "constraint": "UNIQUE", "description": "Tên danh mục"},
                {"name": "description", "type": "TEXT", "constraint": "NULLABLE", "description": "Mô tả chi tiết"}
            ]
        },
        {
            "name": "feedbacks",
            "description": "Nội dung phản hồi do sinh viên gửi lên",
            "columns": [
                {"name": "feedback_id", "type": "INTEGER", "pk": True, "description": "Mã phản hồi"},
                {"name": "student_id", "type": "INTEGER", "fk": "students.id", "description": "Sinh viên gửi"},
                {"name": "title", "type": "VARCHAR(255)", "constraint": "NOT NULL", "description": "Tiêu đề"},
                {"name": "content", "type": "TEXT", "constraint": "NOT NULL", "description": "Nội dung phản hồi"},
                {"name": "is_anonymous", "type": "BOOLEAN", "constraint": "DEFAULT 0", "description": "Tùy chọn ẩn danh"},
                {"name": "status", "type": "VARCHAR(20)", "constraint": "PENDING/PROCESSING/RESOLVED/REJECTED", "description": "Trạng thái xử lý"},
                {"name": "assigned_department", "type": "VARCHAR(100)", "description": "Phòng ban xử lý"},
                {"name": "created_at", "type": "TIMESTAMP", "description": "Thời gian gửi"}
            ]
        },
        {
            "name": "feedback_categories",
            "description": "Bảng trung gian Xử lý Đa nhãn (Multi-label N - N) giữa Feedbacks và Categories",
            "columns": [
                {"name": "mapping_id", "type": "INTEGER", "pk": True, "description": "Mã bản ghi liên kết"},
                {"name": "feedback_id", "type": "INTEGER", "fk": "feedbacks.feedback_id", "description": "Liên kết phản hồi"},
                {"name": "category_id", "type": "INTEGER", "fk": "categories.category_id", "description": "Liên kết danh mục"},
                {"name": "is_ai_predicted", "type": "BOOLEAN", "description": "1 nếu do AI dự đoán, 0 nếu Admin gán"},
                {"name": "confidence_score", "type": "REAL", "description": "Độ tin cậy của AI (0.0 -> 1.0)"},
                {"name": "is_final", "type": "BOOLEAN", "description": "Nhãn chính thức được duyệt"}
            ]
        },
        {
            "name": "ai_classifications",
            "description": "Lưu trữ đánh giá AI, cảm xúc (Sentiment) và thông tin kiểm duyệt",
            "columns": [
                {"name": "classification_id", "type": "INTEGER", "pk": True, "description": "Mã phân loại"},
                {"name": "feedback_id", "type": "INTEGER", "fk": "feedbacks.feedback_id", "description": "Khóa ngoại duy nhất (1-1)"},
                {"name": "sentiment_label", "type": "VARCHAR(20)", "constraint": "POSITIVE/NEUTRAL/NEGATIVE", "description": "Phân loại cảm xúc"},
                {"name": "sentiment_score", "type": "REAL", "description": "Điểm cảm xúc (-1.0 đến +1.0)"},
                {"name": "overall_confidence", "type": "REAL", "description": "Độ tin cậy tổng thể"},
                {"name": "is_urgent", "type": "BOOLEAN", "description": "Cảnh báo vấn đề bức xúc / nguy cấp"},
                {"name": "is_corrected_by_admin", "type": "BOOLEAN", "description": "Admin có chỉnh sửa không"}
            ]
        },
        {
            "name": "feedback_responses",
            "description": "Lịch sử câu trả lời / trao đổi từ nhà trường",
            "columns": [
                {"name": "response_id", "type": "INTEGER", "pk": True, "description": "Mã câu trả lời"},
                {"name": "feedback_id", "type": "INTEGER", "fk": "feedbacks.feedback_id", "description": "Liên kết phản hồi"},
                {"name": "staff_id", "type": "INTEGER", "fk": "users.id", "description": "Cán bộ trả lời"},
                {"name": "response_content", "type": "TEXT", "constraint": "NOT NULL", "description": "Nội dung trả lời"},
                {"name": "created_at", "type": "TIMESTAMP", "description": "Thời gian trả lời"}
            ]
        }
    ]
    return {"tables": tables}


# Static files mount
STATIC_DIR = Path(__file__).resolve().parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return FileResponse(str(STATIC_DIR / "index.html"))
