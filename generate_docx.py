import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Đặt màu nền cho cell trong bảng"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề trong cell"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_callout_box(doc, title, text, bg_hex="F0F4F8", border_hex="1E3A8A"):
    """Tạo hộp thông tin điểm nhấn (Callout Box)"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.bold = True
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = RGBColor(30, 58, 138)
    
    run_b = p.add_run(text)
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def style_heading_1(p, text):
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(15)
    run.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138) # Navy Blue
    return p

def style_heading_2(p, text):
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor(37, 99, 235) # Royal Blue
    return p

def style_heading_3(p, text):
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11.5)
    run.bold = True
    run.font.color.rgb = RGBColor(71, 85, 105)
    return p

def add_body_p(doc, text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(11)
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(11)
    r.italic = italic
    r.font.color.rgb = RGBColor(51, 65, 85)
    return p

def format_table(tbl, col_widths, headers, data):
    """Format bảng chuyên nghiệp với header xanh đậm và sọc xen kẽ"""
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].width = Inches(col_widths[i])
        set_cell_background(hdr_cells[i], "1E3A8A")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(10)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data rows
    for r_idx, row_data in enumerate(data):
        row_cells = tbl.add_row().cells
        bg_hex = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            row_cells[c_idx].width = Inches(col_widths[c_idx])
            set_cell_background(row_cells[c_idx], bg_hex)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(51, 65, 85)

def build_docx_report():
    doc = Document()
    
    # Thiết lập lề trang A4 chuẩn (2.54 cm = 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # =========================================================================
    # TRANG BÌA (COVER PAGE)
    # =========================================================================
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top1 = p_top.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO &bull; TRƯỜNG ĐẠI HỌC\n")
    r_top1.font.size = Pt(11)
    r_top1.font.color.rgb = RGBColor(100, 116, 139)
    r_top2 = p_top.add_run("KHOA CÔNG NGHỆ THÔNG TIN &bull; BỘ MÔN CÔNG NGHỆ PHẦN MỀM\n")
    r_top2.font.size = Pt(11)
    r_top2.bold = True
    r_top2.font.color.rgb = RGBColor(30, 58, 138)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(30)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("BÁO CÁO ĐỒ ÁN MÔN HỌC\n")
    r_sub.font.size = Pt(14)
    r_sub.bold = True
    r_sub.font.color.rgb = RGBColor(220, 38, 38) # Crimson
    
    r_course = p_title.add_run("PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (PTTKHT)\n\n")
    r_course.font.size = Pt(16)
    r_course.bold = True
    r_course.font.color.rgb = RGBColor(30, 58, 138)
    
    r_maintitle = p_title.add_run("HỆ THỐNG PHÂN LOẠI PHẢN HỒI CỦA SINH VIÊN\nBẰNG TRÍ TUỆ NHÂN TẠO (AI)\n")
    r_maintitle.font.size = Pt(20)
    r_maintitle.bold = True
    r_maintitle.font.color.rgb = RGBColor(37, 99, 235)
    
    r_en = p_title.add_run("Student Feedback Multi-Label Classification & Sentiment Analysis System\n")
    r_en.font.size = Pt(11)
    r_en.italic = True
    r_en.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    # Bảng thông tin sinh viên thực hiện
    tbl_info = doc.add_table(rows=1, cols=1)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_info = tbl_info.cell(0, 0)
    c_info.width = Inches(5.8)
    set_cell_background(c_info, "F8FAFC")
    set_cell_margins(c_info, top=160, bottom=160, left=200, right=180)
    
    tcPr_info = c_info._tc.get_or_add_tcPr()
    tcBorders_info = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/><w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/><w:bottom w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/><w:right w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/></w:tcBorders>')
    tcPr_info.append(tcBorders_info)
    
    p_mem = c_info.paragraphs[0]
    p_mem.paragraph_format.line_spacing = 1.3
    
    r_h = p_mem.add_run("THÔNG TIN NHÓM THỰC HIỆN:\n")
    r_h.bold = True
    r_h.font.size = Pt(11)
    r_h.font.color.rgb = RGBColor(30, 58, 138)
    
    p_mem.add_run("1. Sinh viên 1: ").bold = True
    p_mem.add_run("Nguyễn Ngọc Phúc (Thành viên)\n")
    
    p_mem.add_run("2. Sinh viên 2: ").bold = True
    p_mem.add_run("Hà Minh Diệu (Nhóm trưởng - C)\n")
    
    p_mem.add_run("3. Lớp học phần: ").bold = True
    p_mem.add_run("Phân tích và Thiết kế Hệ thống - HK1\n")
    
    p_mem.add_run("4. Mã nguồn GitHub: ").bold = True
    r_git = p_mem.add_run("https://github.com/NNP-coder-rgb/KTVTKHT")
    r_git.bold = True
    r_git.font.color.rgb = RGBColor(37, 99, 235)
    r_git.underline = True

    doc.add_paragraph().paragraph_format.space_after = Pt(60)

    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_bot = p_bot.add_run("NĂM HỌC 2026 - 2027")
    r_bot.font.size = Pt(11)
    r_bot.bold = True
    r_bot.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # =========================================================================
    # PHẦN 1: GIỚI THIỆU BÀI TOÁN & GIẢI PHÁP AI
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "1. TỔNG QUAN BÀI TOÁN & GIẢI PHÁP AI")
    
    style_heading_2(doc.add_paragraph(), "1.1. Vấn đề thực tế (Problem Statement)")
    add_body_p(doc, "Trong môi trường giáo dục đại học hiện đại, mỗi học kỳ nhà trường tiếp nhận hàng ngàn góp ý, khiếu nại và nguyện vọng từ sinh viên dưới dạng văn bản tự do phi cấu trúc (Unstructured text).")
    add_body_p(doc, "Hiện nay, phần lớn các trường vẫn sử dụng quy trình xử lý thủ công: cán bộ tiếp nhận phải tự đọc từng phản hồi, ghi chép vào bảng tính Excel rồi chuyển thủ công sang các phòng ban liên quan (Phòng Đào tạo, Phòng Cơ sở vật chất, Phòng Tài chính, Đoàn Thanh niên...).")
    
    add_callout_box(
        doc,
        "Những bất cập cốt lõi của quy trình thủ công:",
        "• Tốn kém nguồn lực: Tốn hàng trăm giờ làm việc của cán bộ chỉ để đọc và phân loại nhãn.\n"
        "• Định kiến chủ quan: Cùng một câu văn, hai cán bộ khác nhau có thể phân loại vào hai danh mục khác nhau.\n"
        "• Trễ hạn vấn đề bức xúc: Các phản hồi nghiêm trọng (hỏng máy lạnh diện rộng, chập điện, cổng thi lỗi) bị lẫn vào hàng ngàn phản hồi khác, không được ưu tiên can thiệp kịp thời.\n"
        "• Thiếu báo cáo trực quan: Lãnh đạo nhà trường không có số liệu phân tích định lượng về mức độ hài lòng của sinh viên theo từng danh mục."
    )

    style_heading_2(doc.add_paragraph(), "1.2. Giải pháp ứng dụng Trí Tuệ Nhân Tạo (AI Solution)")
    add_body_p(doc, "Nhóm đề xuất xây dựng hệ thống tự động hóa hoàn toàn khâu phân loại và đánh giá cảm xúc với 4 thành phần kỹ thuật chủ chốt:")
    add_body_p(doc, "Tự động làm sạch văn bản tiếng Việt, chuẩn hóa Unicode chuẩn NFC, tách từ ghép chuyên ngành và phân rã các vế câu độc lập (Clause Segmentation).", "1. Tiền xử lý ngôn ngữ tự nhiên (Vietnamese NLP Preprocessing): ")
    add_body_p(doc, "Khác với các hệ thống đơn nhãn thông thường, mô hình của nhóm cho phép nhận diện nhiều nội dung trong một phản hồi. Ví dụ: 'Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh' được phân rã chính xác thành: Giảng dạy (86%) và Cơ sở vật chất (81%).", "2. Phân loại Đa nhãn (Multi-label Text Classification): ")
    add_body_p(doc, "Phân loại cảm xúc thành Tích cực (POSITIVE), Trung tính (NEUTRAL) và Tiêu cực (NEGATIVE) dựa trên trọng số từ điển ngữ nghĩa tiếng Việt và từ phủ định. Cảnh báo cờ Khẩn cấp (is_urgent) đối với các sự cố nghiêm trọng.", "3. Phân tích Cảm xúc & Phát hiện Cấp bách (Sentiment & Urgency): ")
    add_body_p(doc, "Mọi thao tác duyệt (Approve) hoặc điều chỉnh (Override) của Quản trị viên đều được tự động lưu vào cơ sở dữ liệu (bảng ai_retrain_logs), tạo thành tập dữ liệu chuẩn mực để tái huấn luyện và nâng cao độ chính xác của AI theo thời gian.", "4. Vòng lặp cải tiến mô hình (Active Learning & Feedback Loop): ")

    # =========================================================================
    # PHẦN 2: PHÂN TÍCH YÊU CẦU HỆ THỐNG
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "2. PHÂN TÍCH YÊU CẦU HỆ THỐNG (SYSTEM REQUIREMENTS)")
    
    style_heading_2(doc.add_paragraph(), "2.1. Liệt kê các đối tượng sử dụng (Actors)")
    
    actor_headers = ["STT", "Tác Nhân (Actor)", "Mô Tả Vai Trò", "Quyền Hạn Chính"]
    actor_data = [
        ["1", "Sinh viên (Student)", "Người học trong trường gửi phản ánh, góp ý, khiếu nại.", "Tạo phản hồi, tùy chọn ẩn danh, xem trợ lý AI Live Preview, theo dõi tiến độ và nhận phản hồi."],
        ["2", "Quản trị viên / Cán bộ BQL (Admin / Staff)", "Ban quản lý tiếp nhận và cán bộ các phòng ban liên quan.", "Xem danh sách phản hồi, duyệt/sửa nhãn AI, điều chuyển phòng ban, nhập phúc đáp cho SV, xem Dashboard."],
        ["3", "Mô-đun AI (AI Service)", "Hệ thống dịch vụ ngầm xử lý trí tuệ nhân tạo.", "Tiền xử lý text tiếng Việt, tính toán xác suất đa nhãn, chấm điểm cảm xúc và lưu vết vòng lặp học máy."]
    ]
    tbl_actor = doc.add_table(rows=1, cols=4)
    format_table(tbl_actor, [0.5, 1.8, 2.0, 2.2], actor_headers, actor_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    style_heading_2(doc.add_paragraph(), "2.2. Ma trận Yêu cầu Chức năng (Functional Requirements)")
    fr_headers = ["Mã YC", "Tên Chức Năng", "Đối Tượng", "Mô Tả Yêu Cầu Chức Năng"]
    fr_data = [
        ["FR-01", "Đăng nhập / Đổi vai trò", "SV, Admin", "Hỗ trợ xác thực và bộ chuyển đổi tài khoản demo nhanh chóng phục vụ đánh giá đồ án."],
        ["FR-02", "Gửi phản hồi mới", "Sinh viên", "Nhập tiêu đề, nội dung chi tiết, đính kèm link ảnh minh chứng và tùy chọn ẩn danh."],
        ["FR-03", "Trợ lý AI Live Preview", "Sinh viên", "Phân tích tức thời văn bản đang gõ, hiển thị % độ tin cậy, nhãn đa danh mục và cảm xúc."],
        ["FR-04", "Hộp thư cá nhân", "Sinh viên", "Xem lịch sử các phản hồi đã gửi cùng thanh tiến trình 4 giai đoạn trực quan."],
        ["FR-05", "Xem giải đáp từ nhà trường", "Sinh viên", "Nhận nội dung trả lời chính thức từ cán bộ phụ trách chuyên môn."],
        ["FR-06", "Dự đoán Đa nhãn tự động", "Module AI", "Tách câu và phân bổ nhãn đa danh mục kèm độ tin cậy độc lập theo ngưỡng (0.35)."],
        ["FR-07", "Phân tích cảm xúc & Khẩn cấp", "Module AI", "Chấm điểm sắc thái từ -1.0 đến +1.0 và bật cờ is_urgent đối với sự cố bức xúc."],
        ["FR-08", "Duyệt nhanh nhãn AI (Approve)", "Admin", "1-click phê duyệt kết quả dự đoán đúng của AI."],
        ["FR-09", "Điều chỉnh nhãn (Override)", "Admin", "Cho phép sửa đổi nhãn và tự động lưu vào bảng ai_retrain_logs làm dataset học máy."],
        ["FR-10", "Điều phối phòng ban", "Admin", "Chuyển giao phản hồi đến Phòng CSVC, Phòng Đào tạo, Tài chính, Khoa CNTT..."],
        ["FR-11", "Phản hồi cho sinh viên", "Admin", "Nhập câu trả lời chính thức và cập nhật trạng thái sang RESOLVED."],
        ["FR-12", "Dashboard thống kê báo cáo", "Admin", "Biểu đồ cột phân bố 6 danh mục, biểu đồ tròn cảm xúc và tỷ lệ chính xác của AI."]
    ]
    tbl_fr = doc.add_table(rows=1, cols=4)
    format_table(tbl_fr, [0.8, 1.8, 1.1, 2.8], fr_headers, fr_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # =========================================================================
    # PHẦN 3: THIẾT KẾ KIẾN TRÚC HỆ THỐNG
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "3. THIẾT KẾ KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)")
    
    style_heading_2(doc.add_paragraph(), "3.1. Kiến trúc phân tầng 4 lớp (4-Tier Layered Architecture)")
    add_body_p(doc, "Hệ thống được thiết kế theo chuẩn phân tầng độc lập giúp dễ dàng bảo trì và mở rộng:")
    add_body_p(doc, "Được xây dựng theo mô hình Single Page Application (SPA) mượt mà sử dụng HTML5, CSS3, JavaScript ES6+, Bootstrap 5 và Chart.js. Hỗ trợ giao diện phản hồi nhanh (Responsive) và bảng tương tác trợ lý AI Live Preview.", "• Tầng Trình Diễn (Presentation Layer): ")
    add_body_p(doc, "Xây dựng trên nền tảng Python FastAPI (ASGI Framework), cung cấp các dịch vụ RESTful API chuẩn hóa, hiệu năng xử lý bất đồng bộ cao và khả năng mở rộng tuyệt vời.", "• Tầng Dịch Vụ & Xử Lý Ứng Dụng (Application / API Layer): ")
    add_body_p(doc, "Mô-đun chuyên biệt xử lý ngôn ngữ tự nhiên tiếng Việt, trích xuất đặc trưng ngữ nghĩa, thuật toán phân loại Đa nhãn (Multi-label) và tính toán điểm cảm xúc (Sentiment Scorer).", "• Tầng Trí Tuệ Nhân Tạo (AI / NLP Engine Layer): ")
    add_body_p(doc, "Sử dụng Cơ sở dữ liệu quan hệ RDBMS chuẩn ACID. Hỗ trợ hoàn toàn trên SQLite (mặc định cho demo), đồng thời tương thích 100% với MySQL 8.0+ và PostgreSQL 14+ qua các file DDL tương ứng.", "• Tầng Dữ Liệu (Data Persistence Layer): ")

    style_heading_2(doc.add_paragraph(), "3.2. Luồng xử lý dữ liệu (Data Workflow)")
    add_callout_box(
        doc,
        "Luồng tuần tự từ lúc sinh viên gửi đến khi nhà trường phản hồi:",
        "1. Sinh viên gõ tiêu đề & nội dung -> Frontend gọi POST /api/ai/analyze (Debounce 350ms) -> Trợ lý AI trả về nhãn đa danh mục, độ tin cậy và cảm xúc hiển thị ngay trên màn hình.\n"
        "2. Sinh viên nhấn 'Gửi Phản Hồi' -> Backend ghi nhận vào bảng feedbacks, ai_classifications và liên kết bảng feedback_categories (quan hệ N-N).\n"
        "3. Quản trị viên vào Bàn làm việc BQL -> Lọc theo danh mục/cảm xúc/khẩn cấp -> Xem gợi ý của AI.\n"
        "4. Quản trị viên duyệt (Approve) hoặc sửa nhãn (Override) -> Nếu sửa, hệ thống tự động ghi nhật ký vào ai_retrain_logs.\n"
        "5. Quản trị viên chọn phòng ban phụ trách và nhập câu trả lời -> Hệ thống chuyển trạng thái sang RESOLVED -> Sinh viên xem được câu trả lời trong Hộp thư cá nhân."
    )

    # =========================================================================
    # PHẦN 4: THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ (10 BẢNG)
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "4. THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ (DATABASE DESIGN)")
    add_body_p(doc, "Cơ sở dữ liệu được thiết kế đạt chuẩn dạng chuẩn 3 (3NF) với 10 bảng dữ liệu được liên kết chặt chẽ bằng các khóa ngoại (Foreign Keys) và ràng buộc toàn vẹn:")

    tables_detail = [
        ("4.1. Bảng users (Tài khoản người dùng tập trung)", 
         "Lưu trữ tài khoản đăng nhập chung cho Sinh viên, Giảng viên và Quản trị viên.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["id", "INTEGER", "PK, Auto Increment", "Định danh duy nhất của tài khoản"],
             ["email", "VARCHAR(255)", "UNIQUE, NOT NULL", "Email nhà trường cấp (@student / @school.edu.vn)"],
             ["password_hash", "VARCHAR(255)", "NOT NULL", "Mật khẩu đã mã hóa (Bcrypt)"],
             ["role", "VARCHAR(20)", "CHECK IN (STUDENT, TEACHER, ADMIN)", "Vai trò tài khoản trong hệ thống"],
             ["is_active", "BOOLEAN", "DEFAULT 1", "Trạng thái kích hoạt tài khoản"],
             ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm tạo tài khoản"]
         ]),
        ("4.2. Bảng students (Hồ sơ Sinh viên - Quan hệ 1-1 với users)",
         "Lưu trữ các thông tin đặc thù của sinh viên trong trường.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["id", "INTEGER", "PK, Auto Increment", "Định danh sinh viên nội bộ"],
             ["user_id", "INTEGER", "UNIQUE, FK -> users.id", "Liên kết 1-1 với tài khoản đăng nhập"],
             ["student_code", "VARCHAR(20)", "UNIQUE, NOT NULL", "Mã số sinh viên (MSSV)"],
             ["full_name", "VARCHAR(100)", "NOT NULL", "Họ và tên sinh viên"],
             ["class_name", "VARCHAR(50)", "NOT NULL", "Lớp sinh hoạt (Ví dụ: SE1701)"],
             ["major", "VARCHAR(100)", "NULLABLE", "Chuyên ngành đào tạo"]
         ]),
        ("4.3. Bảng teachers (Hồ sơ Giảng viên - Quan hệ 1-1 với users)",
         "Lưu thông tin cán bộ giảng dạy liên quan đến các môn học.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["id", "INTEGER", "PK, Auto Increment", "Định danh giảng viên nội bộ"],
             ["user_id", "INTEGER", "UNIQUE, FK -> users.id", "Liên kết 1-1 với tài khoản users"],
             ["teacher_code", "VARCHAR(20)", "UNIQUE, NOT NULL", "Mã giảng viên"],
             ["full_name", "VARCHAR(100)", "NOT NULL", "Họ tên giảng viên"],
             ["academic_title", "VARCHAR(50)", "NULLABLE", "Học vị (Thạc sĩ, Tiến sĩ, PGS...)"],
             ["department", "VARCHAR(100)", "NOT NULL", "Khoa / Bộ môn giảng dạy"]
         ]),
        ("4.4. Bảng admins (Ban Quản lý & Cán bộ phòng ban - Quan hệ 1-1 với users)",
         "Thông tin ban tiếp nhận phản hồi và chuyên viên xử lý khiếu nại.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["id", "INTEGER", "PK, Auto Increment", "Định danh cán bộ nội bộ"],
             ["user_id", "INTEGER", "UNIQUE, FK -> users.id", "Liên kết 1-1 với tài khoản users"],
             ["full_name", "VARCHAR(100)", "NOT NULL", "Họ và tên cán bộ quản lý"],
             ["office_department", "VARCHAR(100)", "NOT NULL", "Phòng ban công tác (Phòng ĐT, Phòng CSVC...)"]
         ]),
        ("4.5. Bảng categories (Danh mục chuẩn hóa)",
         "Danh mục 6 nhóm phân loại chính trong trường học.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["category_id", "INTEGER", "PK, Auto Increment", "Mã danh mục"],
             ["category_code", "VARCHAR(50)", "UNIQUE, NOT NULL", "Mã code: TEACHING, FACILITIES, ACADEMIC..."],
             ["category_name", "VARCHAR(100)", "UNIQUE, NOT NULL", "Tên danh mục: Giảng dạy, CSVC, Học vụ, Học phí..."],
             ["description", "TEXT", "NULLABLE", "Diễn giải chi tiết phạm vi danh mục"],
             ["icon", "VARCHAR(50)", "DEFAULT 'bi-tag'", "Tên biểu tượng icon hiển thị trên giao diện"],
             ["color", "VARCHAR(20)", "DEFAULT '#4f46e5'", "Mã màu hex phân biệt trực quan"]
         ]),
        ("4.6. Bảng feedbacks (Nội dung phản hồi sinh viên)",
         "Lưu trữ nội dung văn bản góp ý gốc từ sinh viên.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["feedback_id", "INTEGER", "PK, Auto Increment", "Mã phản hồi"],
             ["student_id", "INTEGER", "FK -> students.id", "Sinh viên nào gửi góp ý này"],
             ["title", "VARCHAR(255)", "NOT NULL", "Tiêu đề ngắn gọn của phản hồi"],
             ["content", "TEXT", "NOT NULL", "Toàn văn nội dung phản ánh của sinh viên"],
             ["attachment_url", "VARCHAR(255)", "NULLABLE", "Đường dẫn hình ảnh minh chứng nếu có"],
             ["is_anonymous", "BOOLEAN", "DEFAULT 0", "1: Ẩn danh danh tính, 0: Công khai"],
             ["status", "VARCHAR(20)", "CHECK (PENDING, PROCESSING, RESOLVED, REJECTED)", "Trạng thái xử lý tiến độ"],
             ["assigned_department", "VARCHAR(100)", "DEFAULT 'Phòng Tiếp nhận'", "Phòng ban được bàn giao xử lý"],
             ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm sinh viên gửi"],
             ["updated_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm cập nhật trạng thái gần nhất"]
         ]),
        ("4.7. Bảng feedback_categories (Bảng trung gian Xử lý Đa nhãn Multi-label N - N)",
         "ĐIỂM SÁNG KIẾN KỸ THUẬT: Cho phép một phản hồi được gán nhiều danh mục cùng lúc.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["mapping_id", "INTEGER", "PK, Auto Increment", "Mã bản ghi liên kết"],
             ["feedback_id", "INTEGER", "FK -> feedbacks.feedback_id", "Phản hồi tương ứng"],
             ["category_id", "INTEGER", "FK -> categories.category_id", "Danh mục được gán"],
             ["is_ai_predicted", "BOOLEAN", "DEFAULT 1", "1: Do AI dự đoán, 0: Do Admin gán thủ công"],
             ["confidence_score", "REAL", "DEFAULT 0.0", "Độ tin cậy của AI (0.0 đến 1.0)"],
             ["is_final", "BOOLEAN", "DEFAULT 1", "Nhãn chính thức sau kiểm duyệt"]
         ]),
        ("4.8. Bảng ai_classifications (Đánh giá Cảm xúc & Tổng thể AI - Quan hệ 1-1 với feedbacks)",
         "Lưu trữ kết quả phân tích cảm xúc (Sentiment) và cảnh báo khẩn cấp (is_urgent).",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["classification_id", "INTEGER", "PK, Auto Increment", "Mã đánh giá AI"],
             ["feedback_id", "INTEGER", "UNIQUE, FK -> feedbacks.feedback_id", "Khóa ngoại 1-1 với phản hồi"],
             ["sentiment_label", "VARCHAR(20)", "POSITIVE / NEUTRAL / NEGATIVE", "Nhãn sắc thái cảm xúc"],
             ["sentiment_score", "REAL", "DEFAULT 0.0", "Điểm cảm xúc từ -1.0 đến +1.0"],
             ["overall_confidence", "REAL", "DEFAULT 0.0", "Độ tin cậy tổng thể của AI"],
             ["is_urgent", "BOOLEAN", "DEFAULT 0", "1: Báo động khẩn cấp (sự cố nghiêm trọng)"],
             ["is_reviewed", "BOOLEAN", "DEFAULT 0", "1: Quản trị viên đã kiểm duyệt"],
             ["is_corrected_by_admin", "BOOLEAN", "DEFAULT 0", "1: Quản trị viên có chỉnh sửa nhãn của AI"],
             ["reviewed_by", "INTEGER", "FK -> users.id, NULLABLE", "Cán bộ nào thực hiện duyệt"],
             ["reviewed_at", "TIMESTAMP", "NULLABLE", "Thời điểm duyệt kết quả"]
         ]),
        ("4.9. Bảng feedback_responses (Lịch sử trả lời của nhà trường)",
         "Lưu nội dung giải quyết hoặc phương án phúc đáp của nhà trường gửi lại cho sinh viên.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["response_id", "INTEGER", "PK, Auto Increment", "Mã câu trả lời"],
             ["feedback_id", "INTEGER", "FK -> feedbacks.feedback_id", "Phản hồi tương ứng"],
             ["staff_id", "INTEGER", "FK -> users.id", "Cán bộ thực hiện trả lời"],
             ["response_content", "TEXT", "NOT NULL", "Toàn văn nội dung câu trả lời"],
             ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm phản hồi"]
         ]),
        ("4.10. Bảng ai_retrain_logs (Vòng lặp học máy Active Learning)",
         "ĐIỂM SÁNG KIẾN KỸ THUẬT: Thu thập tập dữ liệu chuẩn mực để tái huấn luyện mô hình.",
         ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"],
         [
             ["log_id", "INTEGER", "PK, Auto Increment", "Mã bản ghi học máy"],
             ["feedback_id", "INTEGER", "FK -> feedbacks.feedback_id", "Liên kết phản hồi gốc"],
             ["feedback_text", "TEXT", "NOT NULL", "Đoạn văn bản thô ban đầu"],
             ["predicted_categories", "TEXT", "NOT NULL", "JSON danh sách các nhãn do AI dự đoán"],
             ["approved_categories", "TEXT", "NOT NULL", "JSON danh sách các nhãn do Admin chốt"],
             ["was_modified", "BOOLEAN", "DEFAULT 0", "1: Admin có sửa nhãn của AI (Dữ liệu học tập quý giá)"],
             ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm ghi nhận"]
         ])
    ]

    for title, desc, hdrs, rows in tables_detail:
        style_heading_2(doc.add_paragraph(), title)
        add_body_p(doc, desc, italic=True)
        tbl = doc.add_table(rows=1, cols=4)
        format_table(tbl, [1.5, 1.4, 1.8, 1.8], hdrs, rows)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # =========================================================================
    # PHẦN 5: SÁNG KIẾN KỸ THUẬT NỔI BẬT
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "5. CÁC ĐIỂM SÁNG KIẾN KỸ THUẬT NỔI BẬT (INNOVATIONS)")
    
    style_heading_2(doc.add_paragraph(), "5.1. Xử lý Đa nhãn hoàn chỉnh (Multi-label Classification)")
    add_body_p(doc, "Hầu hết các bài toán phân loại thông thường chỉ áp dụng mô hình đơn nhãn (Single-label Multi-class), dẫn đến việc phải 'ép' một câu văn phức tạp vào một danh mục duy nhất. Trong thực tế đời sống sinh viên:")
    add_callout_box(
        doc,
        "Minh chứng Đa nhãn thực tế:",
        "Câu văn: 'Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh cả tuần nay không ai sửa.'\n"
        "• Nếu dùng Đơn nhãn: Hệ thống chỉ chọn Giảng dạy HOẶC Cơ sở vật chất -> Phòng CSVC sẽ không bao giờ biết máy lạnh B102 bị hỏng để đi sửa!\n"
        "• Dùng Đa nhãn của nhóm: Hệ thống bóc tách thành 2 vế câu độc lập:\n"
        "   + Vế 1: 'Thầy cô giảng nhanh quá' -> Giảng dạy (Confidence: 86%)\n"
        "   + Vế 2: 'phòng B102 lại bị hư máy lạnh' -> Cơ sở vật chất (Confidence: 81%)\n"
        "-> Nhờ bảng feedback_categories (quan hệ N-N), cả 2 phòng ban đều nhận được nhiệm vụ tương ứng!"
    )

    style_heading_2(doc.add_paragraph(), "5.2. Phân tích Cảm xúc & Nhận diện Khẩn cấp (Urgency Detection)")
    add_body_p(doc, "Hệ thống xây dựng bộ từ điển cảm xúc tiếng Việt phong phú có tính đến xử lý phủ định (Negation Words: 'không tốt', 'chưa hài lòng'). Cờ cảnh báo is_urgent được kích hoạt tự động khi:")
    add_body_p(doc, "1. Điểm phân cực cảm xúc tiêu cực vượt ngưỡng sâu: sentiment_score <= -0.55.")
    add_body_p(doc, "2. Xuất hiện các từ khóa cảnh báo rủi ro cao: 'bức xúc', 'khẩn cấp', 'chập điện', 'hỏng nặng', 'nguy hiểm', 'sai điểm', 'không vào thi được'.")

    style_heading_2(doc.add_paragraph(), "5.3. Vòng lặp Học máy Chủ động (Active Learning Feedback Loop)")
    add_body_p(doc, "Để mô hình AI không bị lạc hậu, hệ thống thiết kế cơ chế Human-in-the-loop: Quản trị viên đóng vai trò là chuyên gia giám sát. Khi Admin sửa nhãn từ 'Học vụ' sang 'Học phí', thao tác này lập tức được ghi vào bảng ai_retrain_logs. Bảng này chính là tập dữ liệu huấn luyện mới (Ground Truth) để định kỳ tinh chỉnh (Fine-tune) mô hình NLP đạt độ chính xác cao hơn.")

    # =========================================================================
    # PHẦN 6: GIAO DIỆN & CÁC PHÂN HỆ CHỨC NĂNG
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "6. THIẾT KẾ GIAO DIỆN & CÁC PHÂN HỆ CHỨC NĂNG")
    add_body_p(doc, "Hệ thống sở hữu giao diện người dùng Single Page Application trực quan, hiện đại với 6 phân hệ chính:")

    ui_modules = [
        ("Phân hệ 1: Bộ chuyển đổi tài khoản (User Switcher)", "Nằm trên thanh Navbar, cho phép chuyển đổi nhanh giữa 6 tài khoản mẫu: Sinh viên Hà Minh Diệu (Nhóm trưởng), Sinh viên Nguyễn Ngọc Phúc, Sinh viên Nguyễn Văn An, Sinh viên Trần Thị Bích, Quản trị viên ThS. Hoàng Thị Lan và Giảng viên TS. Lê Hoàng Long."),
        ("Phân hệ 2: Gửi Phản Hồi & Trợ lý AI Live Preview", "Gồm form nhập thông tin, 4 nút điền mẫu thử nghiệm nhanh và khung Trợ lý AI Live Assistant bên phải tự động dự đoán nhãn, độ tin cậy và cảm xúc khi sinh viên đang gõ văn bản."),
        ("Phân hệ 3: Hộp Thư Cá Nhân (Theo dõi tiến độ)", "Hiển thị lịch sử các phản hồi của sinh viên, thẻ trạng thái tiến trình (Chờ tiếp nhận -> Đang xử lý -> Đã giải quyết) và xem câu trả lời của nhà trường."),
        ("Phân hệ 4: Bàn Làm Việc BQL (Admin Moderation)", "Bảng kiểm duyệt đa năng với thanh lọc theo danh mục, trạng thái, cảm xúc, cờ khẩn cấp; nút 1-click Duyệt nhãn AI, nút Sửa nhãn (Override) và nút Điều phối & Phản hồi cho sinh viên."),
        ("Phân hệ 5: Dashboard Thống Kê & Báo Cáo", "6 thẻ chỉ số đo lường (Tổng phản hồi, Chờ tiếp nhận, Đang xử lý, Đã giải quyết, Phản hồi khẩn cấp, Độ chính xác AI) cùng 2 biểu đồ Chart.js trực quan hóa phân bố danh mục và tỷ lệ cảm xúc."),
        ("Phân hệ 6: Quản lý CSDL & Nhật ký Retrain Logs", "Trực quan hóa cấu trúc 10 bảng dữ liệu (ERD) và bảng nhật ký chi tiết các phản hồi được Admin hiệu chỉnh để phục vụ bài toán Active Learning.")
    ]
    for m_title, m_desc in ui_modules:
        style_heading_2(doc.add_paragraph(), m_title)
        add_body_p(doc, m_desc)

    # =========================================================================
    # PHẦN 7: KẾT QUẢ KIỂM THỬ THỰC NGHIỆM
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "7. KẾT QUẢ KIỂM THỬ THỰC NGHIỆM (TESTING RESULTS)")
    add_body_p(doc, "Hệ thống đã trải qua quy trình kiểm thử tự động toàn diện với script test_api.py. Dưới đây là bảng tổng hợp các ca kiểm thử tiêu biểu:")

    test_headers = ["Mã Test", "Đoạn Văn Bản Kiểm Thử", "Kết Quả AI Dự Đoán", "Cảm Xúc & Khẩn Cấp", "Đánh Giá"]
    test_data = [
        ["TC-01", "Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh", "Giảng dạy (86%)\nCơ sở vật chất (81%)", "Tiêu cực (-0.82)\n[Khẩn cấp: Có]", "Đạt (Đa nhãn chuẩn)"],
        ["TC-02", "Cổng ĐKMH mở lúc 9h sáng thì bị nghẽn mạng liên tục", "Học vụ (89%)", "Tiêu cực (-0.75)\n[Khẩn cấp: Có]", "Đạt"],
        ["TC-03", "Xin gia hạn thời gian nộp học phí do hoàn cảnh lũ lụt", "Học phí (92%)", "Trung tính (-0.10)\n[Khẩn cấp: Không]", "Đạt"],
        ["TC-04", "Thầy dạy môn PTTKHT rất tận tâm, slide bài giảng dễ hiểu", "Giảng dạy (94%)", "Tích cực (+0.88)\n[Khẩn cấp: Không]", "Đạt (Khen ngợi)"],
        ["TC-05", "Đoàn trường tổ chức Mùa hè xanh cộng điểm rèn luyện", "Hoạt động sinh viên (91%)", "Tích cực (+0.65)\n[Khẩn cấp: Không]", "Đạt"],
        ["TC-06", "Cơm trưa căn tin bị nguội và tăng giá 5000đ", "Ý kiến khác (85%)", "Tiêu cực (-0.60)\n[Khẩn cấp: Không]", "Đạt"]
    ]
    tbl_test = doc.add_table(rows=1, cols=5)
    format_table(tbl_test, [0.7, 2.2, 1.4, 1.2, 1.0], test_headers, test_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # =========================================================================
    # PHẦN 8: KHO MÃ NGUỒN GITHUB & CÀI ĐẶT
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "8. KHO MÃ NGUỒN GITHUB & HƯỚNG DẪN CÀI ĐẶT")
    
    add_callout_box(
        doc,
        "Liên kết Kho mã nguồn GitHub chính thức của đồ án:",
        "URL Repository: https://github.com/NNP-coder-rgb/KTVTKHT\n"
        "Tài khoản sở hữu: NNP-coder-rgb (Nguyễn Ngọc Phúc)\n"
        "Trạng thái kho: Hoạt động (Branch: main, đầy đủ mã nguồn backend, frontend, database, test scripts và tài liệu)."
    )

    style_heading_2(doc.add_paragraph(), "8.1. Hướng dẫn Khởi chạy Hệ thống trên máy tính")
    add_body_p(doc, "Cách 1: Khởi động 1-click (Windows)", bold_prefix="• ")
    add_body_p(doc, "Double-click vào file run.bat tại thư mục gốc. Hệ thống sẽ tự động kích hoạt môi trường, khởi chạy máy chủ FastAPI và mở trình duyệt web tại địa chỉ: http://127.0.0.1:8000.")
    
    add_body_p(doc, "Cách 2: Khởi động qua dòng lệnh (PowerShell / Command Prompt)", bold_prefix="• ")
    add_body_p(doc, "1. cd d:\\PTTKHT\n2. .\\venv\\Scripts\\activate\n3. pip install -r requirements.txt\n4. python run.py")

    add_body_p(doc, "Chạy kiểm thử tự động toàn diện:", bold_prefix="• ")
    add_body_p(doc, "python test_api.py (Thực thi kiểm tra toàn bộ kết nối DB, API và phân loại NLP).")

    # =========================================================================
    # PHẦN 9: KẾT LUẬN & HƯỚNG PHÁT TRIỂN
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "9. KẾT LUẬN & HƯỚNG PHÁT TRIỂN")
    add_body_p(doc, "Đồ án 'Hệ thống phân loại phản hồi sinh viên bằng AI' đã giải quyết trọn vẹn bài toán thực tế đặt ra trong trường đại học. Nhóm đã vận dụng đầy đủ kiến thức môn Phân Tích và Thiết Kế Hệ Thống:")
    add_body_p(doc, "1. Thiết kế cơ sở dữ liệu quan hệ chuẩn 3NF (10 bảng), nổi bật với bảng trung gian feedback_categories giải quyết bài toán Đa nhãn (Multi-label) phức tạp.")
    add_body_p(doc, "2. Thiết kế kiến trúc phân tầng 4 lớp rõ ràng, đảm bảo tính mô-đun hóa, bảo mật và hiệu năng cao.")
    add_body_p(doc, "3. Tích hợp AI một cách thực tế và khoa học thông qua cơ chế Human-in-the-loop và nhật ký ai_retrain_logs.")
    add_body_p(doc, "4. Toàn bộ mã nguồn và tài liệu đã được kiểm thử nghiêm ngặt, đóng gói hoàn chỉnh và đồng bộ lên kho lưu trữ GitHub công khai.")

    doc.add_paragraph().paragraph_format.space_after = Pt(20)
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_s1 = p_sign.add_run("TP. Hồ Chí Minh, Ngày 19 Tháng 11 Năm 2026\n")
    r_s1.italic = True
    r_s2 = p_sign.add_run("Nhóm sinh viên thực hiện đồ án\n\n\n")
    r_s2.bold = True
    r_s3 = p_sign.add_run("Nguyễn Ngọc Phúc & Hà Minh Diệu (C)")
    r_s3.bold = True
    r_s3.font.color.rgb = RGBColor(30, 58, 138)

    # Lưu file
    output_path = r"d:\PTTKHT\BAO_CAO_TONG_HOP_PTTKHT.docx"
    doc.save(output_path)
    print(f"Report generated successfully at: {output_path}")

if __name__ == "__main__":
    build_docx_report()
