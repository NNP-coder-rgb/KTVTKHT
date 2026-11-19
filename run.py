import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n[INFO] Đang mở trình duyệt tại: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 70)
    print(" HỆ THỐNG PHÂN LOẠI PHẢN HỒI SINH VIÊN BẰNG AI (PTTKHT)")
    print(" Đề tài: Phân loại phản hồi của sinh viên")
    print(" Thành viên: Nguyễn Ngọc Phúc, Hà Minh Diệu (C)")
    print(" Server đang khởi động tại: http://127.0.0.1:8000")
    print("=" * 70)
    
    # Mở trình duyệt tự động
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Khởi chạy server FastAPI
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
