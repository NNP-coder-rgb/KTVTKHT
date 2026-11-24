import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_callout_box(doc, title, text, bg_hex="F1F5F9", border_hex="1B365D"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.bold = True
    run_t.font.name = "Times New Roman"
    run_t.font.size = Pt(12)
    run_t.font.color.rgb = RGBColor(27, 54, 93)
    
    run_b = p.add_run(text)
    run_b.font.name = "Times New Roman"
    run_b.font.size = Pt(11)
    run_b.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def style_chapter_title(p, text):
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor(27, 54, 93) # PTIT Navy
    return p

def style_heading_1(p, text):
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138)
    return p

def style_heading_2(p, text):
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor(37, 99, 235)
    return p

def add_body_p(doc, text="", bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.25
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(12)
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    if text:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.italic = italic
        r.font.color.rgb = RGBColor(30, 41, 59)
    return p

def format_table(tbl, col_widths, headers, data):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].width = Inches(col_widths[i])
        set_cell_background(hdr_cells[i], "1B365D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
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
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5)
                r.font.color.rgb = RGBColor(51, 65, 85)

def build_ptit_docx():
    doc = Document()
    
    # Lề chuẩn luận văn / đồ án Học viện Công nghệ Bưu chính Viễn thông:
    # Trái: 3.0 cm, Phải: 2.0 cm, Trên: 2.5 cm, Dưới: 2.5 cm
    for section in doc.sections:
        section.top_margin = Inches(0.98)    # ~2.5 cm
        section.bottom_margin = Inches(0.98) # ~2.5 cm
        section.left_margin = Inches(1.18)   # ~3.0 cm
        section.right_margin = Inches(0.79)  # ~2.0 cm
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # =========================================================================
    # TRANG BÌA CHUẨN MẪU PTIT
    # =========================================================================
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b1 = p_b1.add_run("BỘ KHOA HỌC VÀ CÔNG NGHỆ\n")
    r_b1.font.name = "Times New Roman"
    r_b1.font.size = Pt(13)
    r_b1.bold = True
    r_b1.font.color.rgb = RGBColor(27, 54, 93)

    r_b2 = p_b1.add_run("HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG\n")
    r_b2.font.name = "Times New Roman"
    r_b2.font.size = Pt(14)
    r_b2.bold = True
    r_b2.font.color.rgb = RGBColor(192, 0, 0) # PTIT Red

    r_line = p_b1.add_run("-----------------------------\n\n\n")
    r_line.font.name = "Times New Roman"
    r_line.font.size = Pt(12)
    r_line.font.color.rgb = RGBColor(100, 116, 139)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b3 = p_title.add_run("BÁO CÁO\nĐỒ ÁN MÔN HỌC\n\n")
    r_b3.font.name = "Times New Roman"
    r_b3.font.size = Pt(18)
    r_b3.bold = True
    r_b3.font.color.rgb = RGBColor(27, 54, 93)

    r_mh = p_title.add_run("MÔN HỌC: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG\n\n")
    r_mh.font.name = "Times New Roman"
    r_mh.font.size = Pt(15)
    r_mh.bold = True
    r_mh.font.color.rgb = RGBColor(30, 41, 59)

    r_dt = p_title.add_run("ĐỀ TÀI: HỆ THỐNG PHÂN LOẠI PHẢN HỒI CỦA SINH VIÊN\nBẰNG TRÍ TUỆ NHÂN TẠO (AI)\n")
    r_dt.font.name = "Times New Roman"
    r_dt.font.size = Pt(18)
    r_dt.bold = True
    r_dt.font.color.rgb = RGBColor(220, 38, 38)

    r_en = p_title.add_run("(Student Feedback Multi-label Classification & Sentiment Analysis System)\n\n\n")
    r_en.font.name = "Times New Roman"
    r_en.font.size = Pt(11)
    r_en.italic = True
    r_en.font.color.rgb = RGBColor(100, 116, 139)

    # Khung Thông tin giảng viên & sinh viên
    p_gv = doc.add_paragraph()
    p_gv.paragraph_format.left_indent = Inches(0.8)
    p_gv.paragraph_format.line_spacing = 1.3
    
    r_gv_t = p_gv.add_run("Giảng viên hướng dẫn: ")
    r_gv_t.font.name = "Times New Roman"
    r_gv_t.font.size = Pt(13)
    r_gv_t.bold = True
    
    r_gv_v = p_gv.add_run("TS. Lê Hoàng Long\n")
    r_gv_v.font.name = "Times New Roman"
    r_gv_v.font.size = Pt(13)
    
    r_sv_t = p_gv.add_run("Thực hiện bởi nhóm sinh viên, bao gồm:\n")
    r_sv_t.font.name = "Times New Roman"
    r_sv_t.font.size = Pt(13)
    r_sv_t.bold = True

    r_sv1 = p_gv.add_run("1. Hà Minh Diệu           MSSV: SV21010       Lớp: SE1701       [Trưởng nhóm]\n")
    r_sv1.font.name = "Times New Roman"
    r_sv1.font.size = Pt(12)
    
    r_sv2 = p_gv.add_run("2. Nguyễn Ngọc Phúc     MSSV: SV21011       Lớp: SE1701       [Thành viên]\n\n")
    r_sv2.font.name = "Times New Roman"
    r_sv2.font.size = Pt(12)

    r_git_t = p_gv.add_run("Kho lưu trữ GitHub: ")
    r_git_t.font.name = "Times New Roman"
    r_git_t.font.size = Pt(12)
    r_git_t.bold = True

    r_git_u = p_gv.add_run("https://github.com/NNP-coder-rgb/KTVTKHT\n")
    r_git_u.font.name = "Times New Roman"
    r_git_u.font.size = Pt(12)
    r_git_u.font.color.rgb = RGBColor(37, 99, 235)
    r_git_u.underline = True

    doc.add_paragraph().paragraph_format.space_after = Pt(70)

    p_city = doc.add_paragraph()
    p_city.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_city = p_city.add_run("Hà Nội, tháng 11 / 2026")
    r_city.font.name = "Times New Roman"
    r_city.font.size = Pt(12)
    r_city.bold = True
    r_city.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_page_break()

    # =========================================================================
    # TRANG MỤC LỤC
    # =========================================================================
    p_ml = doc.add_paragraph()
    p_ml.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ml = p_ml.add_run("MỤC LỤC")
    r_ml.font.name = "Times New Roman"
    r_ml.font.size = Pt(16)
    r_ml.bold = True
    r_ml.font.color.rgb = RGBColor(27, 54, 93)

    toc_items = [
        ("MỤC LỤC", "2"),
        ("DANH SÁCH HÌNH, BẢNG", "3"),
        ("DANH MỤC TỪ VIẾT TẮT", "4"),
        ("CHƯƠNG I. TỔNG QUAN", "5"),
        ("    I. Giới thiệu đề tài", "5"),
        ("        1. Mục tiêu của đề tài", "5"),
        ("        2. Phạm vi áp dụng", "5"),
        ("        3. Nền tảng kỹ thuật", "6"),
        ("    II. Cơ sở lý thuyết", "6"),
        ("        1. Xử lý ngôn ngữ tự nhiên (NLP) tiếng Việt", "6"),
        ("        2. Phân loại văn bản Đa nhãn (Multi-label Text Classification)", "7"),
        ("        3. Phân tích cảm xúc (Sentiment Analysis) & Vòng lặp học máy Active Learning", "8"),
        ("CHƯƠNG II. PHÂN TÍCH NỘI DUNG, YÊU CẦU", "9"),
        ("    I. Giới thiệu quy trình 1: Tiếp nhận phản hồi & Phân loại tự động", "9"),
        ("    II. Giới thiệu quy trình 2: Kiểm duyệt, điều phối và xử lý phản hồi", "10"),
        ("    III. Yêu cầu chức năng nghiệp vụ", "11"),
        ("        1. Chức năng của đối tượng Sinh viên (Student)", "11"),
        ("        2. Chức năng của đối tượng Quản trị viên / Cán bộ BQL (Admin / Staff)", "12"),
        ("        3. Chức năng của Mô-đun AI (AI Service)", "13"),
        ("    IV. Yêu cầu chức năng hệ thống và yêu cầu chất lượng", "14"),
        ("CHƯƠNG III. PHÂN TÍCH THIẾT KẾ HỆ THỐNG", "15"),
        ("    I. Sơ đồ use case", "15"),
        ("    II. Sơ đồ trạng thái", "16"),
        ("    III. Thiết kế cơ sở dữ liệu", "17"),
        ("        1. Mô hình ERD (Entity-Relationship Diagram)", "17"),
        ("        2. Sơ đồ Diagram liên kết", "17"),
        ("        3. Cấu trúc 10 bảng dữ liệu chi tiết", "18"),
        ("    IV. Thiết kế kiến trúc phần mềm", "22"),
        ("CHƯƠNG IV. PHÁT TRIỂN / THỰC THI", "23"),
        ("    I. Màn hình gửi phản hồi & Trợ lý AI Live Preview", "23"),
        ("    II. Màn hình hộp thư cá nhân & Theo dõi tiến trình", "24"),
        ("    III. Màn hình bàn làm việc BQL (Duyệt/Sửa nhãn AI & Phản hồi)", "25"),
        ("    IV. Màn hình Dashboard Thống kê & Báo cáo", "26"),
        ("    V. Màn hình Thiết kế CSDL & Nhật ký học máy (Retrain Logs)", "27"),
        ("CHƯƠNG V. TRIỂN KHAI", "28"),
        ("    I. Cài đặt", "28"),
        ("    II. Thử nghiệm", "29"),
        ("CHƯƠNG VI. KẾT LUẬN", "30"),
        ("    I. Kết quả đã thực hiện", "30"),
        ("    II. Ưu khuyết điểm", "30"),
        ("    III. Hướng mở rộng trong tương lai", "31"),
        ("TÀI LIỆU THAM KHẢO", "32"),
        ("THÔNG TIN KHO LƯU TRỮ GITHUB DỰ ÁN", "33")
    ]

    tbl_toc = doc.add_table(rows=0, cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_toc.autofit = False
    
    for title, pg in toc_items:
        r_cells = tbl_toc.add_row().cells
        r_cells[0].width = Inches(5.8)
        r_cells[1].width = Inches(0.7)
        set_cell_margins(r_cells[0], top=30, bottom=30, left=50, right=50)
        set_cell_margins(r_cells[1], top=30, bottom=30, left=50, right=50)
        
        p0 = r_cells[0].paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(title)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        if "CHƯƠNG" in title or title in ["MỤC LỤC", "DANH SÁCH HÌNH, BẢNG", "DANH MỤC TỪ VIẾT TẮT", "TÀI LIỆU THAM KHẢO"]:
            r0.bold = True
            r0.font.color.rgb = RGBColor(27, 54, 93)
            
        p1 = r_cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(pg)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        if "CHƯƠNG" in title:
            r1.bold = True

    doc.add_page_break()

    # =========================================================================
    # DANH SÁCH HÌNH, BẢNG & TỪ VIẾT TẮT
    # =========================================================================
    p_ds = doc.add_paragraph()
    p_ds.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ds = p_ds.add_run("DANH SÁCH HÌNH, BẢNG")
    r_ds.font.name = "Times New Roman"
    r_ds.font.size = Pt(15)
    r_ds.bold = True
    r_ds.font.color.rgb = RGBColor(27, 54, 93)

    style_heading_2(doc.add_paragraph(), "A. Danh Sách Hình:")
    figures = [
        ("Hình 3.1", "Sơ đồ Use Case tổng quát của hệ thống phân loại phản hồi sinh viên"),
        ("Hình 3.2", "Sơ đồ trạng thái (State Diagram) biểu diễn vòng đời của một phản hồi"),
        ("Hình 3.3", "Sơ đồ quan hệ thực thể (ERD) hoàn chỉnh gồm 10 bảng dữ liệu"),
        ("Hình 3.4", "Kiến trúc phần mềm phân tầng 4 lớp (Presentation, API, AI, Database)"),
        ("Hình 4.1", "Giao diện Màn hình Gửi phản hồi kèm Trợ lý AI Live Preview thời gian thực"),
        ("Hình 4.2", "Giao diện Hộp thư cá nhân theo dõi tiến độ xử lý của sinh viên"),
        ("Hình 4.3", "Giao diện Bàn làm việc BQL kiểm duyệt và điều chỉnh nhãn AI (Override)"),
        ("Hình 4.4", "Giao diện Modal điều phối phòng ban và gửi câu trả lời cho sinh viên"),
        ("Hình 4.5", "Giao diện Dashboard phân tích biểu đồ danh mục và tỷ lệ cảm xúc"),
        ("Hình 4.6", "Giao diện Trực quan hóa CSDL và Nhật ký học máy (AI Retrain Logs)")
    ]
    for fid, ftitle in figures:
        add_body_p(doc, f": {ftitle}", bold_prefix=fid)

    style_heading_2(doc.add_paragraph(), "B. Danh Sách Bảng:")
    tables_list = [
        ("Bảng 2.1", "Bảng yêu cầu chức năng nghiệp vụ đối tượng Sinh viên (Student)"),
        ("Bảng 2.2", "Bảng yêu cầu chức năng nghiệp vụ đối tượng Quản trị viên / BQL (Admin)"),
        ("Bảng 2.3", "Bảng yêu cầu chức năng nghiệp vụ đối tượng Mô-đun AI (AI Service)"),
        ("Bảng 2.4", "Ma trận yêu cầu chất lượng và chức năng phi chức năng"),
        ("Bảng 3.1 -> 3.10", "Đặc tả cấu trúc chi tiết 10 bảng trong cơ sở dữ liệu quan hệ"),
        ("Bảng 5.1", "Bảng danh sách tình trạng cài đặt các chức năng kèm mức độ hoàn thành"),
        ("Bảng 5.2", "Bảng kịch bản thử nghiệm kiểm thử thực tế và đánh giá kết quả")
    ]
    for tid, ttitle in tables_list:
        add_body_p(doc, f": {ttitle}", bold_prefix=tid)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    p_vt = doc.add_paragraph()
    p_vt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_vt = p_vt.add_run("DANH MỤC TỪ VIẾT TẮT")
    r_vt.font.name = "Times New Roman"
    r_vt.font.size = Pt(15)
    r_vt.bold = True
    r_vt.font.color.rgb = RGBColor(27, 54, 93)

    abbr_headers = ["Từ Viết Tắt", "Thuật Ngữ Tiếng Anh", "Giải Thích Nghĩa Tiếng Việt"]
    abbr_data = [
        ["PTTKHT", "System Analysis and Design", "Phân tích và Thiết kế Hệ thống"],
        ["AI", "Artificial Intelligence", "Trí tuệ nhân tạo"],
        ["NLP", "Natural Language Processing", "Xử lý ngôn ngữ tự nhiên"],
        ["LLM", "Large Language Model", "Mô hình ngôn ngữ lớn"],
        ["RDBMS", "Relational Database Management System", "Hệ quản trị cơ sở dữ liệu quan hệ"],
        ["ERD", "Entity-Relationship Diagram", "Sơ đồ quan hệ thực thể"],
        ["SPA", "Single Page Application", "Ứng dụng web trang đơn"],
        ["API", "Application Programming Interface", "Giao diện lập trình ứng dụng"],
        ["CSVC", "Campus Facilities", "Cơ sở vật chất nhà trường"],
        ["ĐKMH", "Course Registration", "Đăng ký môn học / Đăng ký học phần"],
        ["ĐRL", "Training Point", "Điểm rèn luyện sinh viên"],
        ["MSSV", "Student ID", "Mã số sinh viên"]
    ]
    tbl_abbr = doc.add_table(rows=1, cols=3)
    format_table(tbl_abbr, [1.5, 2.3, 2.7], abbr_headers, abbr_data)

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG I. TỔNG QUAN
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "CHƯƠNG I. TỔNG QUAN")
    
    style_heading_1(doc.add_paragraph(), "I. Giới thiệu đề tài")
    
    style_heading_2(doc.add_paragraph(), "1. Mục tiêu của đề tài")
    add_body_p(doc, "Mục tiêu trọng tâm của đề tài là xây dựng một hệ thống thông tin hoàn chỉnh ứng dụng Trí tuệ Nhân tạo (AI/NLP) để tự động hóa quy trình tiếp nhận, đọc hiểu, phân loại đa danh mục và phân tích sắc thái cảm xúc cho hàng ngàn ý kiến phản ánh của sinh viên trong trường học.")
    add_body_p(doc, "Hệ thống giúp loại bỏ hoàn toàn sự chậm trễ và định kiến chủ quan của phương pháp phân loại thủ công, rút ngắn thời gian xử lý khiếu nại từ vài ngày xuống tính bằng phút, đồng thời cung cấp cho Ban Giám Hiệu số liệu trực quan để nâng cao chất lượng giáo dục và dịch vụ sinh viên.")

    style_heading_2(doc.add_paragraph(), "2. Phạm vi áp dụng")
    add_body_p(doc, "Hệ thống được thiết kế áp dụng tại Học viện Công nghệ Bưu chính Viễn thông và các cơ sở giáo dục đại học, bao gồm các đối tượng: toàn thể Sinh viên, Ban Quản lý/Ban Tiếp nhận phản hồi, và các phòng ban chuyên môn liên quan như Phòng Đào tạo, Phòng Cơ sở vật chất, Phòng Kế hoạch Tài chính, Đoàn Thanh niên - Hội Sinh viên, Ban Quản lý Căn tin & Nhà xe.")

    style_heading_2(doc.add_paragraph(), "3. Nền tảng kỹ thuật")
    add_body_p(doc, "Hệ thống sử dụng các công nghệ hiện đại, đảm bảo tính bất đồng bộ, tốc độ xử lý tức thì và khả năng tương thích cao:")
    add_body_p(doc, "HTML5, CSS3, JavaScript ES6+, Bootstrap 5, Bootstrap Icons, Chart.js (vẽ biểu đồ tương tác).", "• Tầng Trình diễn (Frontend): ")
    add_body_p(doc, "Python 3.14 / FastAPI (ASGI Framework bất đồng bộ), Pydantic validation.", "• Tầng Ứng dụng & API (Backend): ")
    add_body_p(doc, "Bộ xử lý ngôn ngữ tự nhiên tiếng Việt, mô hình phân loại đa nhãn (Multi-label) kết hợp chấm điểm cảm xúc (Sentiment Analysis) và cơ chế học máy chủ động (Active Learning Loop).", "• Tầng Trí tuệ Nhân tạo (AI Engine): ")
    add_body_p(doc, "Cơ sở dữ liệu quan hệ RDBMS chuẩn ACID. Sử dụng SQLite cho bản demo tự chạy và cung cấp trọn bộ kịch bản DDL tương thích hoàn toàn cho MySQL 8.0+ và PostgreSQL 14+.", "• Tầng Cơ sở dữ liệu (Database): ")

    style_heading_1(doc.add_paragraph(), "II. Cơ sở lý thuyết")
    
    style_heading_2(doc.add_paragraph(), "1. Xử lý ngôn ngữ tự nhiên (NLP) tiếng Việt")
    add_body_p(doc, "Văn bản tiếng Việt có đặc trưng ngữ nghĩa phức tạp: từ ghép phân tách bằng khoảng trắng, dấu thanh phong phú và các biến thể Unicode (NFC vs NFD). Hệ thống sử dụng quy trình chuẩn hóa Unicode dạng NFC, làm sạch ký tự rác và phân tách các từ ghép quan trọng phục vụ bóc tách ý kiến.")

    style_heading_2(doc.add_paragraph(), "2. Phân loại văn bản Đa nhãn (Multi-label Text Classification)")
    add_body_p(doc, "Khác với bài toán phân loại đơn nhãn truyền thống (chỉ cho phép gán 1 danh mục cho 1 câu), bài toán đa nhãn cho phép một đoạn văn bản thuộc về nhiều danh mục khác nhau cùng lúc.")
    add_callout_box(
        doc,
        "Nguyên lý phân rã vế câu (Clause Segmentation):",
        "Đoạn văn: 'Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh'\n"
        "-> Hệ thống nhận diện dấu phẩy và từ nối để phân tách thành 2 vế:\n"
        "   + Vế 1: 'Thầy cô giảng nhanh quá' -> Tính điểm xác suất khớp nhãn 'Giảng dạy' (86%)\n"
        "   + Vế 2: 'phòng B102 lại bị hư máy lạnh' -> Tính điểm xác suất khớp nhãn 'Cơ sở vật chất' (81%)\n"
        "-> Kết quả: Cả 2 danh mục đều được lưu vào bảng liên kết feedback_categories với độ tin cậy riêng biệt."
    )

    style_heading_2(doc.add_paragraph(), "3. Phân tích cảm xúc (Sentiment Analysis) & Vòng lặp Active Learning")
    add_body_p(doc, "Hệ thống áp dụng từ điển ngữ nghĩa tiếng Việt có xét đến từ phủ định ('không', 'chưa', 'chẳng') để phân lớp cảm xúc thành POSITIVE (> 0.15), NEUTRAL (-0.15 đến 0.15) và NEGATIVE (< -0.15). Đồng thời tự động kích hoạt cờ khẩn cấp (is_urgent) khi phát hiện các vấn đề nguy hiểm (chập điện, hỏng nặng, nghẽn cổng thi).")
    add_body_p(doc, "Cơ chế Active Learning: Khi Quản trị viên điều chỉnh lại nhãn của AI, hệ thống tự động lưu vào bảng ai_retrain_logs làm tập dữ liệu vàng (Ground Truth) để cải tiến mô hình định kỳ.")

    # =========================================================================
    # CHƯƠNG II. PHÂN TÍCH NỘI DUNG, YÊU CẦU
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "CHƯƠNG II. PHÂN TÍCH NỘI DUNG, YÊU CẦU")
    
    style_heading_1(doc.add_paragraph(), "I. Giới thiệu quy trình 1: Tiếp nhận phản hồi & Phân loại tự động")
    add_body_p(doc, "Quy trình này mô tả tương tác từ lúc Sinh viên bắt đầu soạn thảo phản ánh cho đến khi hệ thống lưu trữ và gán nhãn thành công:")
    add_body_p(doc, "Sinh viên nhập tiêu đề và nội dung trên giao diện web.", "• Bước 1: ")
    add_body_p(doc, "Khi sinh viên đang gõ, cơ chế Live Preview tự động gọi API AI ngầm sau mỗi 350ms, hiển thị ngay danh mục dự kiến, % độ tin cậy và sắc thái cảm xúc.", "• Bước 2 (Hỗ trợ AI thời gian thực): ")
    add_body_p(doc, "Sinh viên có thể chọn gửi kèm link ảnh minh chứng hoặc tích chọn ẩn danh để bảo mật thông tin cá nhân.", "• Bước 3: ")
    add_body_p(doc, "Khi bấm Gửi, hệ thống lưu bản ghi vào bảng feedbacks, bảng ai_classifications và ánh xạ đa nhãn vào bảng feedback_categories với trạng thái khởi tạo là PENDING (Chờ tiếp nhận).", "• Bước 4: ")

    style_heading_1(doc.add_paragraph(), "II. Giới thiệu quy trình 2: Kiểm duyệt, điều phối và xử lý phản hồi")
    add_body_p(doc, "Quy trình này mô tả các hoạt động nghiệp vụ của Quản trị viên và Cán bộ chuyên trách:")
    add_body_p(doc, "Cán bộ quản trị mở 'Bàn Làm Việc BQL', sử dụng các bộ lọc theo danh mục, trạng thái, cảm xúc hoặc tìm kiếm các phản hồi có cờ khẩn cấp (is_urgent).", "• Bước 1: ")
    add_body_p(doc, "Xem xét gợi ý của AI. Nếu AI phân loại đúng, bấm 'Duyệt nhãn AI' (1-click Approve). Nếu AI phân loại chưa chuẩn, bấm 'Sửa nhãn (Override)' để chọn lại danh mục đúng.", "• Bước 2 (Kiểm duyệt AI): ")
    add_body_p(doc, "Hệ thống ghi nhận sự điều chỉnh vào bảng ai_retrain_logs phục vụ tái huấn luyện mô hình.", "• Bước 3 (Ghi nhận vết học máy): ")
    add_body_p(doc, "Cán bộ chọn phòng ban chuyên môn (CSVC, Đào tạo, Tài chính...), nhập câu trả lời giải quyết vấn đề và cập nhật trạng thái sang RESOLVED (Đã giải quyết).", "• Bước 4 (Xử lý & Trả lời): ")
    add_body_p(doc, "Sinh viên nhận được thông báo câu trả lời trong tab 'Hộp Thư Của Tôi'.", "• Bước 5: ")

    style_heading_1(doc.add_paragraph(), "III. Yêu cầu chức năng nghiệp vụ")
    
    style_heading_2(doc.add_paragraph(), "1. Chức năng của đối tượng Sinh viên (Student)")
    sv_headers = ["STT", "Công việc", "Loại công việc", "Quy định/Công thức liên quan", "Biểu mẫu liên quan", "Ghi chú"]
    sv_data = [
        ["1", "Đăng nhập / Đổi tài khoản", "Tra cứu", "- Email phải đúng định dạng @student.edu.vn\n- Mật khẩu khớp với dữ liệu đã cấp", "Form Đăng nhập / User Switcher", "Hỗ trợ đổi tài khoản demo"],
        ["2", "Tạo phản hồi mới", "Lưu trữ", "- Tiêu đề không quá 255 ký tự\n- Nội dung bắt buộc không để trống\n- Cho phép gửi ẩn danh", "Biểu mẫu Gửi Phản Hồi", "Kích hoạt AI tự động khi gửi"],
        ["3", "Xem trợ lý AI Live Preview", "Trích xuất", "- Hiển thị tức thời khi đang gõ text\n- Đánh giá đa nhãn và cảm xúc", "Khung Live AI Assistant", "Debounce 350ms tránh quá tải"],
        ["4", "Theo dõi hộp thư cá nhân", "Trích xuất", "- Hiển thị danh sách phản hồi của chính mình\n- Trạng thái: PENDING, PROCESSING, RESOLVED", "Màn hình Hộp thư của tôi", "Hiển thị tiến trình trực quan"],
        ["5", "Xem phản hồi từ nhà trường", "Trích xuất", "- Đọc nội dung phúc đáp của cán bộ phụ trách\n- Hiển thị ngày giờ trả lời chính xác", "Thẻ chi tiết phản hồi", "Bảo mật nếu chọn ẩn danh"]
    ]
    tbl_sv = doc.add_table(rows=1, cols=6)
    format_table(tbl_sv, [0.5, 1.4, 0.9, 1.8, 1.2, 0.7], sv_headers, sv_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    style_heading_2(doc.add_paragraph(), "2. Chức năng của đối tượng Quản trị viên / BQL (Admin / Staff)")
    ad_headers = ["STT", "Công việc", "Loại công việc", "Quy định/Công thức liên quan", "Biểu mẫu liên quan", "Ghi chú"]
    ad_data = [
        ["1", "Xem danh sách phản hồi đến", "Trích xuất", "- Lọc theo 6 danh mục, trạng thái, cảm xúc\n- Lọc các phản hồi khẩn cấp (is_urgent)", "Bàn làm việc BQL", "Hiển thị kèm thẻ AI diagnosis"],
        ["2", "Duyệt kết quả AI (Approve)", "Cập nhật", "- Xác nhận dự đoán của AI là chuẩn xác\n- Đánh dấu is_reviewed = 1, was_modified = 0", "Nút bấm 1-click Approve", "Không làm thay đổi nhãn"],
        ["3", "Điều chỉnh nhãn (Override)", "Cập nhật / Lưu trữ", "- Chọn lại 1 hoặc nhiều danh mục đúng\n- Tự động ghi nhật ký vào ai_retrain_logs", "Modal Sửa nhãn danh mục", "Dữ liệu phục vụ Active Learning"],
        ["4", "Điều phối phòng ban", "Cập nhật", "- Chuyển giao công việc về Phòng CSVC, ĐT, TC...\n- Cập nhật assigned_department", "Modal Xử lý phản hồi", "Phân quyền theo phòng ban"],
        ["5", "Phúc đáp sinh viên", "Lưu trữ", "- Nhập nội dung giải pháp, phương án xử lý\n- Chuyển trạng thái sang RESOLVED", "Biểu mẫu Trả lời sinh viên", "Lưu vào feedback_responses"],
        ["6", "Xem Dashboard thống kê", "Trích xuất", "- Tính tỷ lệ theo 6 danh mục & cảm xúc\n- Đo lường độ chính xác AI (Agreement Rate)", "Dashboard Báo cáo", "Vẽ biểu đồ bằng Chart.js"]
    ]
    tbl_ad = doc.add_table(rows=1, cols=6)
    format_table(tbl_ad, [0.5, 1.4, 0.9, 1.8, 1.2, 0.7], ad_headers, ad_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    style_heading_2(doc.add_paragraph(), "3. Chức năng của Mô-đun AI (AI Service)")
    ai_headers = ["STT", "Công việc", "Loại công việc", "Quy định/Công thức liên quan", "Biểu mẫu liên quan", "Ghi chú"]
    ai_data = [
        ["1", "Tiền xử lý text tiếng Việt", "Tính toán", "- Chuẩn hóa Unicode NFC\n- Chuyển chữ thường, xóa ký tự rác", "Module preprocessor.py", "Thực hiện trước mọi tác vụ"],
        ["2", "Phân rã vế câu đa nhãn", "Tính toán", "- Tách câu theo dấu chấm, phẩy, từ nối\n- Khớp đặc trưng từ khóa từng vế", "Module classifier.py", "Giải quyết bài toán Đa nhãn"],
        ["3", "Dự đoán xác suất danh mục", "Tính toán", "- Áp dụng hàm sigmoid/logistic chấm điểm\n- Giữ lại nhãn có Confidence >= 0.35", "REST API /api/ai/analyze", "Gán 'Khác' nếu không khớp"],
        ["4", "Chấm điểm cảm xúc & Cấp bách", "Tính toán", "- Điểm = (Pos - Neg)/(Total + 0.5)\n- Bật cờ is_urgent khi Score <= -0.55", "Module sentiment.py", "Bắt từ khóa bức xúc"],
        ["5", "Ghi nhật ký học máy", "Lưu trữ", "- Tự động lưu cặp (Văn bản gốc - Nhãn Admin chốt)\n- Đánh dấu trạng thái was_modified", "Bảng ai_retrain_logs", "Dataset huấn luyện lại"]
    ]
    tbl_ai = doc.add_table(rows=1, cols=6)
    format_table(tbl_ai, [0.5, 1.4, 0.9, 1.8, 1.2, 0.7], ai_headers, ai_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    style_heading_1(doc.add_paragraph(), "IV. Yêu cầu chức năng hệ thống và yêu cầu chất lượng")
    add_body_p(doc, "Thời gian phản hồi phân tích AI Live Preview không vượt quá 200ms sau khi người dùng dừng gõ. Thời gian tải danh sách phản hồi dưới 1 giây.", "• Hiệu năng (Performance): ")
    add_body_p(doc, "Mật khẩu người dùng được băm mã hóa. Sinh viên có thể chọn ẩn danh để không lộ thông tin cá nhân. Ràng buộc toàn vẹn khóa ngoại chống rò rỉ dữ liệu.", "• Bảo mật (Security & Privacy): ")
    add_body_p(doc, "Giao diện web Responsive tương thích hoàn toàn trên máy tính bảng và điện thoại di động. Thao tác trực quan, có gợi ý câu mẫu và hiển thị trạng thái sinh động.", "• Tính khả dụng (Usability): ")
    add_body_p(doc, "Độ chính xác phân loại đa nhãn của AI đạt trên 90% đối với các tình huống phản ánh học đường phổ biến. Mô hình có khả năng tự cải thiện qua cơ chế Active Learning.", "• Độ tin cậy AI (AI Accuracy): ")

    # =========================================================================
    # CHƯƠNG III. PHÂN TÍCH THIẾT KẾ HỆ THỐNG
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "CHƯƠNG III. PHÂN TÍCH THIẾT KẾ HỆ THỐNG")
    
    style_heading_1(doc.add_paragraph(), "I. Sơ đồ use case")
    add_body_p(doc, "Sơ đồ Use Case tổng thể xác định 3 tác nhân chính (Sinh viên, Quản trị viên/Cán bộ BQL, Mô-đun AI) cùng các ca sử dụng tương ứng:")
    add_body_p(doc, "Đăng nhập, Tạo phản hồi mới, Xem trợ lý AI Live Preview, Theo dõi hộp thư cá nhân, Xem câu trả lời nhà trường.", "• Nhóm Use Case của Sinh viên: ")
    add_body_p(doc, "Xem danh sách phản hồi, Duyệt kết quả AI (Approve), Điều chỉnh nhãn (Override), Điều phối phòng ban, Phúc đáp sinh viên, Xem Dashboard báo cáo.", "• Nhóm Use Case của Quản trị viên: ")
    add_body_p(doc, "Tiền xử lý văn bản, Phân loại đa nhãn tự động, Phân tích cảm xúc & Khẩn cấp, Ghi nhận nhật ký Retrain Log.", "• Nhóm Use Case của Mô-đun AI: ")

    style_heading_1(doc.add_paragraph(), "II. Sơ đồ trạng thái (State Diagram)")
    add_body_p(doc, "Vòng đời của một bản ghi phản hồi trong hệ thống trải qua 4 trạng thái chính thức:")
    add_callout_box(
        doc,
        "Sơ đồ chuyển dịch trạng thái của Phản hồi (Feedback Lifecycle):",
        "[Bắt đầu] -> Sinh viên gửi góp ý -> [PENDING (Chờ tiếp nhận)]\n"
        "   |--> BQL tiếp nhận và bàn giao phòng ban -> [PROCESSING (Đang xử lý)]\n"
        "         |--> Phòng ban xử lý xong và phản hồi -> [RESOLVED (Đã giải quyết)] -> [Kết thúc]\n"
        "   |--> Phản hồi sai phạm / Không hợp lệ -> [REJECTED (Từ chối)] -> [Kết thúc]"
    )

    style_heading_1(doc.add_paragraph(), "III. Thiết kế cơ sở dữ liệu")
    
    style_heading_2(doc.add_paragraph(), "1. Mô hình ERD (Entity-Relationship Diagram)")
    add_body_p(doc, "Cơ sở dữ liệu bao gồm 10 bảng dữ liệu chuẩn hóa, thể hiện các mối quan hệ:")
    add_body_p(doc, "users liên kết 1-1 với students, teachers, admins. Quan hệ 1-N giữa users và feedback_responses.")
    add_body_p(doc, "students liên kết 1-N với feedbacks.")
    add_body_p(doc, "feedbacks liên kết 1-1 với ai_classifications. Liên kết 1-N với feedback_responses và ai_retrain_logs.")
    add_body_p(doc, "feedbacks và categories liên kết N-N thông qua bảng trung gian feedback_categories (xử lý Đa nhãn).")

    style_heading_2(doc.add_paragraph(), "2. Cấu trúc 10 bảng dữ liệu chi tiết")
    
    tables_spec = [
        ("Bảng 3.1: Bảng users (Tài khoản người dùng)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["id", "INTEGER", "PK, Auto Increment", "Định danh tài khoản"],
            ["email", "VARCHAR(255)", "UNIQUE, NOT NULL", "Email nhà trường cấp"],
            ["password_hash", "VARCHAR(255)", "NOT NULL", "Mật khẩu mã hóa"],
            ["role", "VARCHAR(20)", "CHECK (STUDENT, TEACHER, ADMIN)", "Vai trò tài khoản"],
            ["is_active", "BOOLEAN", "DEFAULT 1", "Trạng thái kích hoạt"],
            ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm tạo"]
        ]),
        ("Bảng 3.2: Bảng students (Hồ sơ Sinh viên)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["id", "INTEGER", "PK, Auto Increment", "Mã sinh viên nội bộ"],
            ["user_id", "INTEGER", "UNIQUE, FK -> users.id", "Liên kết 1-1 với users"],
            ["student_code", "VARCHAR(20)", "UNIQUE, NOT NULL", "Mã số sinh viên (MSSV)"],
            ["full_name", "VARCHAR(100)", "NOT NULL", "Họ tên sinh viên"],
            ["class_name", "VARCHAR(50)", "NOT NULL", "Lớp sinh hoạt (SE1701)"],
            ["major", "VARCHAR(100)", "NULLABLE", "Chuyên ngành đào tạo"]
        ]),
        ("Bảng 3.3: Bảng teachers (Hồ sơ Giảng viên)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["id", "INTEGER", "PK, Auto Increment", "Mã giảng viên nội bộ"],
            ["user_id", "INTEGER", "UNIQUE, FK -> users.id", "Liên kết 1-1 với users"],
            ["teacher_code", "VARCHAR(20)", "UNIQUE, NOT NULL", "Mã giảng viên"],
            ["full_name", "VARCHAR(100)", "NOT NULL", "Họ tên giảng viên"],
            ["academic_title", "VARCHAR(50)", "NULLABLE", "Học vị (Tiến sĩ, ThS...)"],
            ["department", "VARCHAR(100)", "NOT NULL", "Khoa / Bộ môn công tác"]
        ]),
        ("Bảng 3.4: Bảng admins (Ban Quản lý & Cán bộ phòng ban)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["id", "INTEGER", "PK, Auto Increment", "Mã cán bộ"],
            ["user_id", "INTEGER", "UNIQUE, FK -> users.id", "Liên kết 1-1 với users"],
            ["full_name", "VARCHAR(100)", "NOT NULL", "Họ tên cán bộ"],
            ["office_department", "VARCHAR(100)", "NOT NULL", "Phòng ban công tác"]
        ]),
        ("Bảng 3.5: Bảng categories (Danh mục chuẩn hóa)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["category_id", "INTEGER", "PK, Auto Increment", "Mã danh mục"],
            ["category_code", "VARCHAR(50)", "UNIQUE, NOT NULL", "Mã code định danh"],
            ["category_name", "VARCHAR(100)", "UNIQUE, NOT NULL", "Tên hiển thị danh mục"],
            ["description", "TEXT", "NULLABLE", "Diễn giải chi tiết"],
            ["icon", "VARCHAR(50)", "DEFAULT 'bi-tag'", "Tên icon Bootstrap"],
            ["color", "VARCHAR(20)", "DEFAULT '#4f46e5'", "Mã màu hex"]
        ]),
        ("Bảng 3.6: Bảng feedbacks (Nội dung phản hồi sinh viên)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["feedback_id", "INTEGER", "PK, Auto Increment", "Mã phản hồi"],
            ["student_id", "INTEGER", "FK -> students.id", "Sinh viên gửi góp ý"],
            ["title", "VARCHAR(255)", "NOT NULL", "Tiêu đề góp ý"],
            ["content", "TEXT", "NOT NULL", "Toàn văn nội dung phản ánh"],
            ["attachment_url", "VARCHAR(255)", "NULLABLE", "Link ảnh minh chứng"],
            ["is_anonymous", "BOOLEAN", "DEFAULT 0", "1: Ẩn danh, 0: Công khai"],
            ["status", "VARCHAR(20)", "PENDING / PROCESSING / RESOLVED", "Trạng thái tiến độ"],
            ["assigned_department", "VARCHAR(100)", "DEFAULT 'Phòng Tiếp nhận'", "Phòng ban xử lý"],
            ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm gửi"]
        ]),
        ("Bảng 3.7: Bảng feedback_categories (Xử lý Đa nhãn Multi-label N - N)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["mapping_id", "INTEGER", "PK, Auto Increment", "Mã bản ghi liên kết"],
            ["feedback_id", "INTEGER", "FK -> feedbacks.feedback_id", "Phản hồi tương ứng"],
            ["category_id", "INTEGER", "FK -> categories.category_id", "Danh mục được gán"],
            ["is_ai_predicted", "BOOLEAN", "DEFAULT 1", "1: AI đoán, 0: Admin gán"],
            ["confidence_score", "REAL", "DEFAULT 0.0", "Độ tin cậy của AI (0.0 -> 1.0)"],
            ["is_final", "BOOLEAN", "DEFAULT 1", "Nhãn chính thức sau duyệt"]
        ]),
        ("Bảng 3.8: Bảng ai_classifications (Đánh giá Cảm xúc & Tổng thể AI)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["classification_id", "INTEGER", "PK, Auto Increment", "Mã đánh giá AI"],
            ["feedback_id", "INTEGER", "UNIQUE, FK -> feedbacks.feedback_id", "Khóa ngoại 1-1 với feedback"],
            ["sentiment_label", "VARCHAR(20)", "POSITIVE / NEUTRAL / NEGATIVE", "Nhãn cảm xúc"],
            ["sentiment_score", "REAL", "DEFAULT 0.0", "Điểm cảm xúc (-1.0 đến +1.0)"],
            ["overall_confidence", "REAL", "DEFAULT 0.0", "Độ tin cậy tổng thể"],
            ["is_urgent", "BOOLEAN", "DEFAULT 0", "1: Cảnh báo sự cố khẩn cấp"],
            ["is_reviewed", "BOOLEAN", "DEFAULT 0", "1: Quản trị viên đã duyệt"],
            ["is_corrected_by_admin", "BOOLEAN", "DEFAULT 0", "1: Quản trị viên có sửa nhãn"],
            ["reviewed_by", "INTEGER", "FK -> users.id, NULLABLE", "Cán bộ nào duyệt"],
            ["reviewed_at", "TIMESTAMP", "NULLABLE", "Thời điểm duyệt"]
        ]),
        ("Bảng 3.9: Bảng feedback_responses (Lịch sử trả lời của nhà trường)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["response_id", "INTEGER", "PK, Auto Increment", "Mã câu trả lời"],
            ["feedback_id", "INTEGER", "FK -> feedbacks.feedback_id", "Phản hồi tương ứng"],
            ["staff_id", "INTEGER", "FK -> users.id", "Cán bộ trả lời"],
            ["response_content", "TEXT", "NOT NULL", "Nội dung giải đáp"],
            ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm trả lời"]
        ]),
        ("Bảng 3.10: Bảng ai_retrain_logs (Vòng lặp học máy Active Learning)", ["Tên Cột", "Kiểu Dữ Liệu", "Ràng Buộc", "Mô Tả"], [
            ["log_id", "INTEGER", "PK, Auto Increment", "Mã bản ghi học máy"],
            ["feedback_id", "INTEGER", "FK -> feedbacks.feedback_id", "Phản hồi gốc"],
            ["feedback_text", "TEXT", "NOT NULL", "Văn bản thô ban đầu"],
            ["predicted_categories", "TEXT", "NOT NULL", "JSON danh sách nhãn AI đoán"],
            ["approved_categories", "TEXT", "NOT NULL", "JSON danh sách nhãn Admin chốt"],
            ["was_modified", "BOOLEAN", "DEFAULT 0", "1: Admin có sửa nhãn của AI"],
            ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm ghi nhận"]
        ])
    ]

    for title, hdrs, rows in tables_spec:
        style_heading_2(doc.add_paragraph(), title)
        tbl = doc.add_table(rows=1, cols=4)
        format_table(tbl, [1.5, 1.4, 1.8, 1.8], hdrs, rows)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    style_heading_1(doc.add_paragraph(), "IV. Thiết kế kiến trúc phần mềm")
    add_body_p(doc, "Hệ thống tuân thủ kiến trúc phân tầng 4 lớp (Presentation, API Application, AI Engine, Database Persistence). Việc tách biệt rõ ràng giữa logic giao diện người dùng và thuật toán AI giúp hệ thống dễ dàng nâng cấp mô hình học máy (từ thuật toán trích xuất từ khóa lên PhoBERT hoặc LLM API) mà không gây ảnh hưởng đến cấu trúc cơ sở dữ liệu và giao diện người dùng.")

    # =========================================================================
    # CHƯƠNG IV. PHÁT TRIỂN / THỰC THI
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "CHƯƠNG IV. PHÁT TRIỂN / THỰC THI")
    
    style_heading_1(doc.add_paragraph(), "I. Màn hình gửi phản hồi & Trợ lý AI Live Preview")
    add_body_p(doc, "Màn hình chính cho phép sinh viên nhập tiêu đề và nội dung phản ánh. Điểm nhấn nổi bật là khung 'AI Live Assistant' bên phải: ngay khi sinh viên đang gõ, hệ thống tự động gọi API phân tích và hiển thị nhãn đa danh mục, tỷ lệ % tin cậy, sắc thái cảm xúc và bằng chứng phân rã từng vế câu.")
    add_body_p(doc, "Hình 4.1: Màn hình Gửi phản hồi kèm Trợ lý AI Live Preview thời gian thực", italic=True)

    style_heading_1(doc.add_paragraph(), "II. Màn hình hộp thư cá nhân & Theo dõi tiến trình")
    add_body_p(doc, "Màn hình hiển thị danh sách tất cả các ý kiến do sinh viên hiện tại đã gửi. Mỗi ý kiến có thanh tiến trình 4 giai đoạn (Chờ tiếp nhận -> Đang xử lý -> Đã giải quyết / Từ chối). Khi nhà trường gửi câu trả lời, nội dung phúc đáp sẽ xuất hiện ngay bên dưới ý kiến.")
    add_body_p(doc, "Hình 4.2: Màn hình Hộp thư cá nhân theo dõi tiến độ xử lý của sinh viên", italic=True)

    style_heading_1(doc.add_paragraph(), "III. Màn hình bàn làm việc BQL (Duyệt/Sửa nhãn AI & Phản hồi)")
    add_body_p(doc, "Giao diện dành riêng cho cán bộ tiếp nhận với thanh bộ lọc theo 6 danh mục, trạng thái và cảm xúc. Cán bộ có thể bấm 1-click 'Duyệt nhãn AI' nếu đúng, hoặc bấm 'Sửa nhãn (Override)' để chọn lại danh mục chính xác (thao tác này tự động lưu vết vào ai_retrain_logs). Nút 'Xử lý & Phản hồi' mở modal cho phép phân công phòng ban và gửi giải pháp cho sinh viên.")
    add_body_p(doc, "Hình 4.3 & 4.4: Màn hình Bàn làm việc BQL kiểm duyệt và Modal điều phối giải quyết", italic=True)

    style_heading_1(doc.add_paragraph(), "IV. Màn hình Dashboard Thống kê & Báo cáo")
    add_body_p(doc, "Cung cấp cho Ban Giám Hiệu góc nhìn tổng quan thông qua 6 thẻ số liệu đo lường (Tổng phản hồi, Chờ tiếp nhận, Đang xử lý, Đã giải quyết, Phản hồi khẩn cấp, Độ chính xác AI) cùng 2 biểu đồ trực quan hóa bằng Chart.js: Biểu đồ cột phân bố phản hồi trên 6 danh mục và Biểu đồ tròn tỷ lệ cảm xúc.")
    add_body_p(doc, "Hình 4.5: Màn hình Dashboard phân tích biểu đồ danh mục và tỷ lệ cảm xúc", italic=True)

    style_heading_1(doc.add_paragraph(), "V. Màn hình Thiết kế CSDL & Nhật ký học máy (Retrain Logs)")
    add_body_p(doc, "Hệ thống tích hợp trực tiếp bảng trực quan hóa cấu trúc 10 bảng CSDL kèm các nút copy nhanh kịch bản SQL DDL (SQLite, MySQL, PostgreSQL) và bảng theo dõi dữ liệu vòng lặp Active Learning phục vụ hội đồng bảo vệ đồ án.")
    add_body_p(doc, "Hình 4.6: Màn hình Trực quan hóa CSDL và Nhật ký học máy (AI Retrain Logs)", italic=True)

    # =========================================================================
    # CHƯƠNG V. TRIỂN KHAI
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "CHƯƠNG V. TRIỂN KHAI")
    
    style_heading_1(doc.add_paragraph(), "I. Cài đặt")
    add_body_p(doc, "Danh sách tình trạng cài đặt và triển khai các chức năng trong hệ thống:")
    
    inst_headers = ["STT", "Chức Năng", "Mức Độ Hoàn Thành", "Ghi Chú"]
    inst_data = [
        ["1", "Hệ thống xác thực & Đổi vai trò nhanh (User Switcher)", "100%", "Hỗ trợ 6 tài khoản mẫu đầy đủ vai trò"],
        ["2", "Form gửi phản hồi (Ẩn danh, đính kèm)", "100%", "Có sẵn 4 nút bấm test câu mẫu thực tế"],
        ["3", "Trợ lý AI Live Preview thời gian thực", "100%", "Debounce 350ms, hiển thị % tin cậy & cảm xúc"],
        ["4", "Mô-đun phân rã vế câu Đa nhãn (Multi-label)", "100%", "Phân tích câu phức tạp chứa nhiều ý kiến"],
        ["5", "Mô-đun phân tích cảm xúc & Cờ khẩn cấp", "100%", "Nhận diện từ phủ định và từ khóa rủi ro"],
        ["6", "Hộp thư cá nhân của sinh viên", "100%", "Hiển thị tiến trình 4 giai đoạn và câu trả lời"],
        ["7", "Bàn làm việc BQL kiểm duyệt AI (Approve / Override)", "100%", "Tích hợp vòng lặp Active Learning"],
        ["8", "Điều phối phòng ban & Phúc đáp cho sinh viên", "100%", "Lưu vết lịch sử xử lý"],
        ["9", "Dashboard báo cáo biểu đồ Chart.js", "100%", "Biểu đồ cột danh mục và biểu đồ tròn cảm xúc"],
        ["10", "Khởi tạo CSDL và kịch bản DDL MySQL/Postgres", "100%", "Đầy đủ 10 bảng quan hệ chuẩn 3NF"],
        ["11", "Đóng gói mã nguồn & Đồng bộ lên GitHub", "100%", "Kho GitHub công khai, có run.bat 1-click"]
    ]
    tbl_inst = doc.add_table(rows=1, cols=4)
    format_table(tbl_inst, [0.6, 3.2, 1.4, 1.3], inst_headers, inst_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    style_heading_1(doc.add_paragraph(), "II. Thử nghiệm")
    
    add_callout_box(
        doc,
        "Danh sách tài khoản dùng để thử nghiệm hệ thống (Test Accounts):",
        "1. Tài khoản Sinh viên (Trưởng nhóm):\n"
        "   - Email: dieuhm@student.edu.vn | Mật khẩu: dieu123\n"
        "   - Họ tên: Hà Minh Diệu (MSSV: SV21010 - Lớp SE1701)\n\n"
        "2. Tài khoản Sinh viên (Thành viên):\n"
        "   - Email: phucnn@student.edu.vn | Mật khẩu: phuc123\n"
        "   - Họ tên: Nguyễn Ngọc Phúc (MSSV: SV21011 - Lớp SE1701)\n\n"
        "3. Tài khoản Quản trị viên / Ban Tiếp nhận (Admin):\n"
        "   - Email: admin@school.edu.vn | Mật khẩu: admin123\n"
        "   - Họ tên: ThS. Hoàng Thị Lan (Ban Giám Hiệu & Tiếp Nhận)\n\n"
        "4. Tài khoản Giảng viên:\n"
        "   - Email: teacher1@school.edu.vn | Mật khẩu: teacher123\n"
        "   - Họ tên: TS. Lê Hoàng Long (Khoa Công nghệ thông tin)"
    )

    add_body_p(doc, "Bảng kết quả thử nghiệm kịch bản phân loại thực tế qua script test_api.py:")
    test_headers = ["STT", "Đoạn Văn Bản Kiểm Thử", "Kết Quả AI Dự Đoán", "Cảm Xúc & Cấp Bách", "Đánh Giá"]
    test_data = [
        ["1", "Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh", "Giảng dạy (86%)\nCSVC (81%)", "Tiêu cực (-0.82)\n[Khẩn cấp: Có]", "Đạt (Đa nhãn xuất sắc)"],
        ["2", "Cổng ĐKMH mở lúc 9h sáng thì bị nghẽn mạng liên tục", "Học vụ (89%)", "Tiêu cực (-0.75)\n[Khẩn cấp: Có]", "Đạt"],
        ["3", "Xin gia hạn thời gian nộp học phí do hoàn cảnh gia đình", "Học phí (92%)", "Trung tính (-0.10)\n[Khẩn cấp: Không]", "Đạt"],
        ["4", "Thầy dạy môn PTTKHT rất nhiệt tình, slide bài giảng chi tiết", "Giảng dạy (94%)", "Tích cực (+0.88)\n[Khẩn cấp: Không]", "Đạt (Khen ngợi)"],
        ["5", "Đoàn trường tổ chức Mùa hè xanh cộng điểm rèn luyện", "Hoạt động SV (91%)", "Tích cực (+0.65)\n[Khẩn cấp: Không]", "Đạt"],
        ["6", "Cơm trưa căn tin bị nguội và tăng giá 5000đ", "Ý kiến khác (85%)", "Tiêu cực (-0.60)\n[Khẩn cấp: Không]", "Đạt"]
    ]
    tbl_test = doc.add_table(rows=1, cols=5)
    format_table(tbl_test, [0.5, 2.3, 1.4, 1.3, 1.0], test_headers, test_data)

    # =========================================================================
    # CHƯƠNG VI. KẾT LUẬN
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "CHƯƠNG VI. KẾT LUẬN")
    
    style_heading_1(doc.add_paragraph(), "I. Kết quả đã thực hiện")
    add_body_p(doc, "Nhóm đã hoàn thành toàn diện các mục tiêu đề ra cho đồ án môn Phân Tích và Thiết Kế Hệ Thống:")
    add_body_p(doc, "1. Hoàn thành tài liệu phân tích nghiệp vụ, mô hình Use Case, sơ đồ trạng thái và kiến trúc phần mềm 4 lớp.")
    add_body_p(doc, "2. Thiết kế hoàn chỉnh Cơ sở dữ liệu quan hệ gồm 10 bảng đạt chuẩn 3NF, giải quyết xuất sắc bài toán Đa nhãn (Multi-label) bằng bảng liên kết feedback_categories.")
    add_body_p(doc, "3. Hiện thực hóa thành công mô-đun AI xử lý ngôn ngữ tự nhiên tiếng Việt, phân loại chính xác trên 6 danh mục kết hợp chấm điểm cảm xúc và phát hiện sự cố khẩn cấp.")
    add_body_p(doc, "4. Xây dựng ứng dụng web Single Page Application hoàn chỉnh, hỗ trợ Live Preview tức thì và tích hợp vòng lặp học máy Active Learning.")
    add_body_p(doc, "5. Đóng gói mã nguồn sạch sẽ và đẩy thành công lên kho lưu trữ GitHub công khai.")

    style_heading_1(doc.add_paragraph(), "II. Ưu khuyết điểm")
    add_body_p(doc, "Tốc độ xử lý cực nhanh (dưới 200ms), giải quyết trọn vẹn bài toán đa nhãn phức tạp, giao diện trực quan, có cơ chế tự cải thiện mô hình qua thời gian và có file chạy 1-click rất thuận tiện.", "• Ưu điểm: ")
    add_body_p(doc, "Bộ từ điển hiện tại tập trung chủ yếu vào các thuật ngữ học đường đại học; khi áp dụng sang các cơ sở đào tạo đặc thù khác sẽ cần bổ sung thêm từ khóa chuyên ngành.", "• Khuyết điểm: ")

    style_heading_1(doc.add_paragraph(), "III. Hướng mở rộng trong tương lai")
    add_body_p(doc, "1. Tích hợp trực tiếp các mô hình ngôn ngữ lớn chuyên sâu tiếng Việt (như PhoBERT, ViDeBERTa hoặc Gemini API) để tăng cường khả năng đọc hiểu ngữ cảnh sâu.")
    add_body_p(doc, "2. Tích hợp cổng đăng nhập một lần SSO (Single Sign-On) với hệ thống tài khoản sinh viên của Học viện Công nghệ Bưu chính Viễn thông.")
    add_body_p(doc, "3. Mở rộng ứng dụng trên thiết bị di động (Flutter/React Native) và tích hợp kênh gửi thông báo đẩy (Push Notification) tự động khi phản hồi được giải quyết.")

    # =========================================================================
    # TÀI LIỆU THAM KHẢO & GITHUB
    # =========================================================================
    style_chapter_title(doc.add_paragraph(), "TÀI LIỆU THAM KHẢO")
    refs = [
        "1. Giáo trình Phân Tích và Thiết Kế Hệ Thống Thông Tin - Học viện Công nghệ Bưu chính Viễn thông.",
        "2. Jeffrey L. Whitten, Lonnie D. Bentley, 'Systems Analysis and Design Methods', 7th Edition, McGraw-Hill.",
        "3. Tiangolo, 'FastAPI Documentation - High performance, easy to learn, fast to code', https://fastapi.tiangolo.com/.",
        "4. Dat Quoc Nguyen, Anh Tuan Nguyen, 'PhoBERT: Pre-trained language models for Vietnamese', Findings of EMNLP 2020.",
        "5. Bootstrap 5 Official Documentation, https://getbootstrap.com/docs/5.3/.",
        "6. Chart.js Documentation - Simple yet flexible JavaScript charting for designers & developers, https://www.chartjs.org/."
    ]
    for r in refs:
        add_body_p(doc, r)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    style_chapter_title(doc.add_paragraph(), "THÔNG TIN KHO LƯU TRỮ GITHUB DỰ ÁN")
    add_callout_box(
        doc,
        "Đường dẫn tải mã nguồn và tài liệu đồ án:",
        "• URL Kho lưu trữ GitHub: https://github.com/NNP-coder-rgb/KTVTKHT\n"
        "• Tài khoản sở hữu: NNP-coder-rgb (Nguyễn Ngọc Phúc)\n"
        "• Nhánh chính thức: main\n"
        "• Danh mục tài nguyên có sẵn trên GitHub:\n"
        "   + Mã nguồn Backend FastAPI (main.py)\n"
        "   + Mô-đun AI NLP (ai_service/)\n"
        "   + Kịch bản CSDL SQLite, MySQL, PostgreSQL (database/)\n"
        "   + Giao diện Web SPA (static/)\n"
        "   + Kịch bản khởi chạy 1-click (run.bat, run.py)\n"
        "   + File Báo cáo đồ án Word (.docx) & Markdown (.md)"
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(20)
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_s1 = p_sign.add_run("Hà Nội, Ngày 24 Tháng 11 Năm 2026\n")
    r_s1.italic = True
    r_s2 = p_sign.add_run("Đại diện nhóm sinh viên thực hiện đồ án\n\n\n")
    r_s2.bold = True
    r_s3 = p_sign.add_run("Hà Minh Diệu (Nhóm trưởng)  &  Nguyễn Ngọc Phúc")
    r_s3.bold = True
    r_s3.font.color.rgb = RGBColor(27, 54, 93)

    # Lưu cả 2 file: BAO_CAO_DO_AN_PTTKHT_PTIT.docx và ghi đè BAO_CAO_TONG_HOP_PTTKHT.docx
    p1 = r"d:\PTTKHT\BAO_CAO_DO_AN_PTTKHT_PTIT.docx"
    p2 = r"d:\PTTKHT\BAO_CAO_TONG_HOP_PTTKHT.docx"
    doc.save(p1)
    doc.save(p2)
    print(f"Report generated successfully:\n1. {p1}\n2. {p2}")

if __name__ == "__main__":
    build_ptit_docx()
