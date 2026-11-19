# ĐỒ ÁN MÔN: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (PTTKHT)
## Đề tài: Hệ Thống Phân Loại Phản Hồi Của Sinh Viên Bằng AI (Student Feedback AI Classification System)

---

### THÔNG TIN NHÓM THỰC HIỆN:
- **Thành viên 1:** Nguyễn Ngọc Phúc
- **Thành viên 2:** Hà Minh Diệu (Nhóm trưởng - C)

---

## 1. VẤN ĐỀ THỰC TẾ (PROBLEM STATEMENT)
Trong môi trường giáo dục đại học, mỗi học kỳ nhà trường tiếp nhận hàng ngàn góp ý/khiếu nại từ sinh viên dưới dạng văn bản tự do (*unstructured text*). 
- **Bất cập hiện tại:** Quản trị viên và các phòng ban phải đọc từng phản hồi, ghi chép và phân loại thủ công vào các danh mục (Giảng dạy, Cơ sở vật chất, Học vụ, Học phí, Hoạt động sinh viên, Ý kiến khác).
- **Hệ quả:** Rất tốn thời gian, dễ gây trễ hạn xử lý các phản hồi bức xúc, phụ thuộc cảm quan chủ quan của người duyệt, và thiếu số liệu thống kê trực quan để nâng cao chất lượng đào tạo.

---

## 2. GIẢI PHÁP ỨNG DỤNG AI (AI SOLUTION)
1. **Mô hình Phân loại Văn bản (Text Classification / NLP):** 
   - Tự động tiếp nhận, làm sạch văn bản tiếng Việt (*Unicode NFC, tiền xử lý, tách từ ngữ nghĩa*) và dự đoán danh mục phù hợp kèm **Độ tin cậy (Confidence Score)**.
2. **Xử lý Đa nhãn (Multi-label Classification):**
   - Giải quyết bài toán thực tế: Một câu góp ý của sinh viên có thể chứa nhiều vấn đề thuộc các phòng ban khác nhau:
     > *"Thầy cô giảng nhanh quá, phòng B102 lại bị hư máy lạnh"*
     > &rarr; AI tự động phân rã và gán **2 danh mục**:
     > - **Giảng dạy:** *Thầy cô giảng nhanh quá* (Confidence: ~86%)
     > - **Cơ sở vật chất:** *Phòng B102 bị hư máy lạnh* (Confidence: ~81%)
3. **Phân tích Cảm xúc (Sentiment Analysis & Urgency Detection):**
   - Phân lớp cảm xúc: **Tích cực (POSITIVE)**, **Trung tính (NEUTRAL)**, **Tiêu cực (NEGATIVE)**.
   - Kèm cơ chế cảnh báo **Khẩn cấp (is_urgent)** đối với các phản hồi bức xúc cao hoặc sự cố nghiêm trọng (máy lạnh hỏng, chập điện, cổng đăng ký môn quá tải) để nhà trường ưu tiên can thiệp tức thì.
4. **Vòng lặp Học máy (Active Learning / Feedback Loop):**
   - Quản trị viên có thể **Duyệt (Approve)** hoặc **Điều chỉnh nhãn (Override)**. Hệ thống lưu lại lịch sử vào bảng `ai_retrain_logs` làm tập dữ liệu *Ground Truth* để cải tiến mô hình định kỳ.

---

## 3. CÁC ĐỐI TƯỢNG SỬ DỤNG (ACTORS)
1. **Sinh viên (Student):** Người gửi phản hồi/góp ý/khiếu nại; theo dõi tiến độ xử lý và nhận phản hồi từ nhà trường. Có tùy chọn gửi ẩn danh.
2. **Quản trị viên / Ban Quản lý Trường (Admin / Department Officer):** Quản lý hệ thống, kiểm duyệt gợi ý phân loại của AI, điều chuyển phản hồi đến đúng phòng ban xử lý, trả lời sinh viên và theo dõi Dashboard báo cáo.
3. **Mô-đun AI (AI System Service):** Dịch vụ ngầm tự động tiền xử lý văn bản, trích xuất đặc trưng, dự đoán đa danh mục và đánh giá cảm xúc theo thời gian thực (*Live AI Assistant*).

---

## 4. YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

### A. Chức năng của Sinh viên:
- **Đăng nhập & Chuyển đổi vai trò:** Hỗ trợ mô phỏng nhiều tài khoản sinh viên với thông tin ngành, lớp.
- **Gửi phản hồi:**
  - Nhập tiêu đề, nội dung, đính kèm liên kết ảnh minh chứng.
  - Tùy chọn gửi ẩn danh (*Anonymous*) để bảo vệ quyền riêng tư.
  - **Trợ lý AI thời gian thực (Live Preview):** Hiển thị ngay nhãn danh mục, độ tin cậy và cảm xúc khi sinh viên đang gõ nội dung.
- **Hộp thư cá nhân (Theo dõi tiến độ):**
  - Xem danh sách các phản hồi đã gửi.
  - Tiến trình trạng thái: `Chờ tiếp nhận` &rarr; `Đang xử lý` &rarr; `Đã giải quyết` / `Từ chối`.
  - Xem nội dung giải đáp chính thức từ nhà trường.

### B. Chức năng của Quản trị viên / BQL:
- **Tiếp nhận & Kiểm duyệt AI (AI-assisted Moderation):**
  - Xem danh sách phản hồi mới gửi đến.
  - Xem kết quả gợi ý đa nhãn của AI (kèm Confidence score & từ khóa nhận diện).
  - Phê duyệt nhanh (*1-click Approve*) hoặc Điều chỉnh (*Override*) danh mục.
- **Điều phối & Trả lời sinh viên:**
  - Chuyển tiếp đến các đơn vị phụ trách (Phòng CSVC, Phòng Đào tạo, Phòng Tài chính, Khoa CNTT, Đoàn trường...).
  - Nhập nội dung phản hồi trực tiếp cho sinh viên và cập nhật trạng thái.
- **Thống kê & Dashboard phân tích:**
  - Biểu đồ cột phân bố số lượng theo 6 danh mục.
  - Biểu đồ tròn tỷ lệ cảm xúc (Tích cực / Tiêu cực / Trung tính).
  - Thống kê tỷ lệ đồng thuận của AI (*AI Accuracy / Agreement Rate*).

---

## 5. THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE DESIGN)

Hệ thống được thiết kế theo chuẩn RDBMS (sử dụng được trên **SQLite, MySQL 8.0+, PostgreSQL 14+**).

### Danh Sách Các Bảng (Tables):

| STT | Tên Bảng | Mục Đích |
|---|---|---|
| 1 | `users` | Tài khoản & Xác thực chung (email, password_hash, role: STUDENT/TEACHER/ADMIN) |
| 2 | `students` | Thông tin chi tiết sinh viên (MSSV, Họ tên, Lớp, Ngành) &bull; Quan hệ 1 - 1 với `users` |
| 3 | `teachers` | Thông tin chi tiết giảng viên &bull; Quan hệ 1 - 1 với `users` |
| 4 | `admins` | Ban quản trị & các phòng ban &bull; Quan hệ 1 - 1 với `users` |
| 5 | `categories` | Danh sách 6 danh mục chuẩn (Giảng dạy, CSVC, Học vụ, Học phí, HĐSV, Ý kiến khác) |
| 6 | `feedbacks` | Thông tin phản hồi do sinh viên gửi (tiêu đề, nội dung, ẩn danh, trạng thái, phòng ban) |
| 7 | **`feedback_categories`** | **Xử lý Đa nhãn (Multi-label N - N):** Lưu các danh mục tương ứng cho mỗi phản hồi kèm độ tin cậy AI và nhãn duyệt |
| 8 | **`ai_classifications`** | Kết quả phân tích AI (cảm xúc `sentiment_label`, điểm `sentiment_score`, cảnh báo `is_urgent`, kiểm duyệt) |
| 9 | `feedback_responses` | Câu trả lời/giải pháp từ nhà trường gửi cho sinh viên |
| 10 | **`ai_retrain_logs`** | Ghi nhận Feedback loop khi Admin điều chỉnh nhãn để làm dữ liệu tái huấn luyện mô hình |

---

## 6. ĐIỂM SÁNG KIẾN TRONG BÀI TOÁN PTTKHT
1. **Xử lý Đa nhãn hoàn chỉnh (Multi-label):**
   - Đạt trọn vẹn điểm đồ án nhờ chuyển quan hệ `feedbacks` và `categories` sang liên kết N - N qua bảng `feedback_categories`. 
   - Không bị giới hạn 1 nhãn duy nhất như các thiết kế thông thường.
2. **Tích hợp vòng lặp cải thiện AI (Human-in-the-loop):**
   - Dữ liệu do Admin hiệu chỉnh được lưu vào `ai_retrain_logs` phục vụ bài toán Active Learning.
3. **Kiến trúc phân tầng rõ ràng:**
   - **Data Layer:** SQLite / MySQL / PostgreSQL DDL scripts.
   - **AI/NLP Layer:** Phân rã vế câu tiếng Việt, khớp đặc trưng ngữ nghĩa, chấm điểm cảm xúc.
   - **Service Layer (API):** FastAPI xử lý bất đồng bộ, tốc độ cao.
   - **Presentation Layer:** Giao diện trực quan, responsive với Bootstrap 5, Chart.js và Vanilla JavaScript.

---

## 7. HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

### Cách 1: Khởi động nhanh bằng file Batch (Windows)
Double-click vào file **`run.bat`** tại thư mục gốc của dự án. Trình duyệt sẽ tự động mở tại địa chỉ `http://127.0.0.1:8000`.

### Cách 2: Khởi động bằng dòng lệnh
```powershell
# 1. Kích hoạt môi trường ảo
.\venv\Scripts\activate

# 2. Cài đặt thư viện (nếu cần)
pip install -r requirements.txt

# 3. Chạy ứng dụng
python run.py
```

Ứng dụng sẽ hoạt động tại: **`http://127.0.0.1:8000`**

### Kiểm thử hệ thống:
```powershell
.\venv\Scripts\python.exe test_api.py
```
Toàn bộ kịch bản kiểm thử API, AI Multi-label và CSDL sẽ được thực thi tự động.
