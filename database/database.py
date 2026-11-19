import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "student_feedback.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Khởi tạo database từ file schema.sql nếu chưa có bảng"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Đọc schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    
    # Kiểm tra xem có categories chưa
    cursor.execute("SELECT COUNT(*) as cnt FROM categories")
    row = cursor.fetchone()
    if row["cnt"] == 0:
        seed_initial_data(conn)
        
    conn.close()

def seed_initial_data(conn):
    """Nạp dữ liệu mẫu ban đầu cho danh mục, tài khoản, phản hồi và AI classifications"""
    from ai_service.classifier import CATEGORY_DEFINITIONS, ai_classifier
    cursor = conn.cursor()
    
    # 1. Nạp Categories
    for code, info in CATEGORY_DEFINITIONS.items():
        cursor.execute(
            """
            INSERT OR IGNORE INTO categories (category_id, category_code, category_name, description, icon, color)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (info["id"], code, info["name"], info["description"], info["icon"], info["color"])
        )
    
    # 2. Nạp Users mẫu
    users_data = [
        ("admin@school.edu.vn", "admin123", "ADMIN"),
        ("student1@student.edu.vn", "student123", "STUDENT"),
        ("student2@student.edu.vn", "student123", "STUDENT"),
        ("dieuhm@student.edu.vn", "dieu123", "STUDENT"),
        ("phucnn@student.edu.vn", "phuc123", "STUDENT"),
        ("teacher1@school.edu.vn", "teacher123", "TEACHER")
    ]
    for email, pwd, role in users_data:
        cursor.execute(
            "INSERT OR IGNORE INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email, pwd, role)
        )
    
    # 3. Nạp Admins
    cursor.execute("SELECT id FROM users WHERE email = 'admin@school.edu.vn'")
    admin_u = cursor.fetchone()
    if admin_u:
        cursor.execute(
            "INSERT OR IGNORE INTO admins (user_id, full_name, office_department) VALUES (?, ?, ?)",
            (admin_u["id"], "ThS. Hoàng Thị Lan (Ban Giám Hiệu & Tiếp Nhận)", "Ban Quản Lý & Khảo Thí")
        )
        
    # 4. Nạp Students
    students_data = [
        ("student1@student.edu.vn", "SV21001", "Nguyễn Văn An", "SE1701", "Kỹ thuật phần mềm"),
        ("student2@student.edu.vn", "SV21002", "Trần Thị Bích", "IT1802", "Công nghệ thông tin"),
        ("dieuhm@student.edu.vn", "SV21010", "Hà Minh Diệu (Nhóm Trưởng)", "SE1701", "Kỹ thuật phần mềm"),
        ("phucnn@student.edu.vn", "SV21011", "Nguyễn Ngọc Phúc", "SE1701", "Kỹ thuật phần mềm")
    ]
    for email, code, name, cls, major in students_data:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        u = cursor.fetchone()
        if u:
            cursor.execute(
                "INSERT OR IGNORE INTO students (user_id, student_code, full_name, class_name, major) VALUES (?, ?, ?, ?, ?)",
                (u["id"], code, name, cls, major)
            )

    # 5. Nạp Teachers
    cursor.execute("SELECT id FROM users WHERE email = 'teacher1@school.edu.vn'")
    teacher_u = cursor.fetchone()
    if teacher_u:
        cursor.execute(
            "INSERT OR IGNORE INTO teachers (user_id, teacher_code, full_name, academic_title, department) VALUES (?, ?, ?, ?, ?)",
            (teacher_u["id"], "GV1001", "TS. Lê Hoàng Long", "Tiến sĩ", "Khoa Công nghệ thông tin")
        )

    conn.commit()

    # 6. Nạp danh sách Feedbacks thực tế phong phú
    cursor.execute("SELECT id FROM students WHERE student_code = 'SV21001'")
    st1 = cursor.fetchone()["id"]
    cursor.execute("SELECT id FROM students WHERE student_code = 'SV21002'")
    st2 = cursor.fetchone()["id"]
    cursor.execute("SELECT id FROM students WHERE student_code = 'SV21010'")
    st_dieu = cursor.fetchone()["id"]

    sample_feedbacks = [
        {
            "student_id": st1,
            "title": "Phòng B102 hư máy lạnh và thầy giảng quá nhanh",
            "content": "Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh cả tuần nay không ai sửa, rất ngột ngạt và khó tiếp thu bài giảng.",
            "is_anonymous": 0,
            "status": "PROCESSING",
            "assigned_dept": "Phòng Cơ sở vật chất & Khoa CNTT",
            "response": "Nhà trường đã tiếp nhận và cử đội kỹ thuật thay gas máy lạnh phòng B102 sáng mai, đồng thời trao đổi với giảng viên để điều chỉnh nhịp giảng."
        },
        {
            "student_id": st2,
            "title": "Hệ thống đăng ký môn học bị quá tải khi mở cổng",
            "content": "Sáng nay cổng ĐKMH mở lúc 9h thì bị nghẽn mạng liên tục, em không đăng ký được tín chỉ nào dù đã canh đúng giờ. Mong phòng đào tạo mở thêm lớp.",
            "is_anonymous": 1,
            "status": "PENDING",
            "assigned_dept": "Phòng Đào tạo",
            "response": None
        },
        {
            "student_id": st_dieu,
            "title": "Xin gia hạn thời gian nộp học phí học kỳ này",
            "content": "Gia đình em ở quê đang gặp khó khăn do mùa lũ, mong nhà trường và phòng tài chính hỗ trợ gia hạn đóng học phí thêm 3 tuần hoặc cho chia nhỏ đợt thanh toán.",
            "is_anonymous": 0,
            "status": "RESOLVED",
            "assigned_dept": "Phòng Kế hoạch Tài chính",
            "response": "Phòng Tài chính đã phê duyệt đơn gia hạn học phí của bạn đến ngày 15 tháng sau. Chúc bạn an tâm học tập tốt."
        },
        {
            "student_id": st1,
            "title": "Khen ngợi thầy Nam dạy môn Phân tích thiết kế hệ thống rất tận tâm",
            "content": "Thầy giảng bài cực kỳ dễ hiểu, slide bài giảng chi tiết và giải đáp thắc mắc nhiệt tình cả ngoài giờ. Em rất thích môn học này!",
            "is_anonymous": 0,
            "status": "RESOLVED",
            "assigned_dept": "Khoa CNTT",
            "response": "Cảm ơn em đã gửi lời khen ngợi. Khoa đã chuyển lời tri ân này đến giảng viên."
        },
        {
            "student_id": st2,
            "title": "Bãi gửi xe khu C quá đông đúc và trầy xước xe",
            "content": "Bãi giữ xe khu C giờ cao điểm từ 7h - 8h sáng kẹt cứng, bảo vệ dắt xe làm trầy xước xe sinh viên. Đề nghị bố trí thêm cổng phụ hoặc mở rộng nhà xe.",
            "is_anonymous": 1,
            "status": "PROCESSING",
            "assigned_dept": "Phòng Quản trị Thiết bị",
            "response": "BQL đã yêu cầu tổ bảo vệ tăng cường 3 nhân sự điều phối giờ cao điểm và dán biển phân luồng mới."
        },
        {
            "student_id": st_dieu,
            "title": "Đề xuất tổ chức thêm hoạt động thiện nguyện Mùa hè xanh và cộng điểm rèn luyện",
            "content": "Nhiều bạn sinh viên mong muốn tham gia chiến dịch tình nguyện Mùa hè xanh năm nay. Xin Đoàn trường công bố sớm kế hoạch và mức cộng ĐRL cụ thể.",
            "is_anonymous": 0,
            "status": "RESOLVED",
            "assigned_dept": "Đoàn Thanh niên - Hội Sinh viên",
            "response": "Đoàn trường đã đăng tải kế hoạch Mùa hè xanh trên Fanpage và cổng thông tin, các bạn tham gia sẽ được cộng 10 điểm ĐRL vào kỳ này."
        },
        {
            "student_id": st1,
            "title": "Đồ ăn căn tin buổi trưa nguội và giá tăng nhẹ",
            "content": "Canteen trường dạo này cơm trưa hơi nguội, đồ ăn một số món giá tăng thêm 5.000đ nhưng khẩu phần không đổi. Mong nhà trường kiểm tra vệ sinh và niêm yết giá.",
            "is_anonymous": 1,
            "status": "PENDING",
            "assigned_dept": "Ban Quản lý Dịch vụ Căn tin",
            "response": None
        }
    ]

    for item in sample_feedbacks:
        cursor.execute(
            """
            INSERT INTO feedbacks (student_id, title, content, is_anonymous, status, assigned_department)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item["student_id"], item["title"], item["content"], item["is_anonymous"], item["status"], item["assigned_dept"])
        )
        fb_id = cursor.lastrowid
        
        # Chạy AI Classifier tự động cho feedback này
        ai_res = ai_classifier.predict(item["content"], item["title"])
        
        # Lưu vào bảng ai_classifications
        cursor.execute(
            """
            INSERT INTO ai_classifications 
            (feedback_id, sentiment_label, sentiment_score, overall_confidence, is_urgent, is_reviewed, is_corrected_by_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fb_id, 
                ai_res["sentiment"]["label"], 
                ai_res["sentiment"]["score"], 
                ai_res["overall_confidence"],
                1 if ai_res["sentiment"]["is_urgent"] else 0,
                1 if item["status"] != "PENDING" else 0,
                0
            )
        )
        
        # Lưu danh sách đa nhãn vào feedback_categories
        for cat in ai_res["predicted_categories"]:
            cursor.execute(
                """
                INSERT OR IGNORE INTO feedback_categories 
                (feedback_id, category_id, is_ai_predicted, confidence_score, is_final)
                VALUES (?, ?, ?, ?, ?)
                """,
                (fb_id, cat["category_id"], 1, cat["confidence_score"], 1)
            )
            
        # Thêm câu trả lời nếu có
        if item["response"]:
            cursor.execute(
                """
                INSERT INTO feedback_responses (feedback_id, staff_id, response_content)
                VALUES (?, ?, ?)
                """,
                (fb_id, admin_u["id"], item["response"])
            )

    conn.commit()
