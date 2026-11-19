from typing import List, Dict, Any
from .preprocessor import normalize_vietnamese_text, split_sentences_or_clauses
from .sentiment import analyze_sentiment

# Định nghĩa từ khóa trọng số chuyên sâu cho từng danh mục đại học
CATEGORY_DEFINITIONS = {
    "TEACHING": {
        "id": 1,
        "name": "Giảng dạy",
        "code": "TEACHING",
        "description": "Chất lượng bài giảng, phương pháp giảng dạy, thái độ giảng viên, đề thi, chấm điểm",
        "icon": "bi-person-workspace",
        "color": "#3b82f6", # Blue
        "keywords": {
            "thầy": 0.8, "cô": 0.8, "thầy cô": 0.95, "giảng viên": 1.0, "gv": 0.8,
            "giảng nhanh": 0.95, "dạy nhanh": 0.95, "giảng chậm": 0.9, "dạy chậm": 0.9,
            "bài giảng": 0.9, "slide": 0.85, "khó hiểu": 0.85, "dễ hiểu": 0.85,
            "chấm điểm": 0.95, "điểm số": 0.8, "đề thi": 0.9, "đề kiểm tra": 0.9,
            "bài tập": 0.8, "thuyết trình": 0.8, "giáo trình": 0.85, "tài liệu học": 0.8,
            "thực hành": 0.75, "lab": 0.75, "kiến thức": 0.7, "tiết học": 0.75,
            "truyền đạt": 0.85, "chuyên cần": 0.75, "điểm danh": 0.75, "giảng bài": 0.9
        }
    },
    "FACILITIES": {
        "id": 2,
        "name": "Cơ sở vật chất",
        "code": "FACILITIES",
        "description": "Phòng học, máy lạnh, quạt, bàn ghế, thang máy, máy chiếu, wifi, nhà vệ sinh, nhà xe",
        "icon": "bi-buildings",
        "color": "#f59e0b", # Amber/Orange
        "keywords": {
            "máy lạnh": 1.0, "điều hòa": 1.0, "hư máy lạnh": 1.0, "máy lạnh hỏng": 1.0,
            "quạt": 0.85, "quạt trần": 0.9, "quạt hư": 0.9, "bàn ghế": 0.9, "bàn gãy": 0.95,
            "thang máy": 0.95, "kẹt thang máy": 1.0, "máy chiếu": 0.95, "projector": 0.9,
            "micro": 0.9, "mic rè": 0.95, "loa": 0.85, "âm thanh": 0.8, "bóng đèn": 0.85,
            "nhà vệ sinh": 0.95, "wc": 0.95, "toilet": 0.95, "nhà xe": 0.9, "bãi giữ xe": 0.95,
            "gửi xe": 0.9, "wifi": 0.95, "mạng internet": 0.9, "mạng yếu": 0.95,
            "phòng học": 0.8, "phòng b": 0.85, "phòng a": 0.85, "phòng c": 0.85, "phòng e": 0.85,
            "cơ sở vật chất": 1.0, "csvc": 1.0, "dột": 0.9, "thấm nước": 0.9, "rác": 0.8,
            "ổ điện": 0.9, "mất điện": 0.9, "nóng bức": 0.8
        }
    },
    "ACADEMIC": {
        "id": 3,
        "name": "Học vụ",
        "code": "ACADEMIC",
        "description": "Đăng ký môn học, thời khóa biểu, lịch thi, xét tốt nghiệp, bảng điểm, thủ tục phòng đào tạo",
        "icon": "bi-mortarboard",
        "color": "#10b981", # Green
        "keywords": {
            "đăng ký môn": 1.0, "dkmh": 1.0, "đăng ký học phần": 1.0, "hủy môn": 0.95,
            "rút môn": 0.95, "thời khóa biểu": 0.95, "tkb": 0.9, "lịch thi": 0.95,
            "hoãn thi": 0.95, "bảng điểm": 0.9, "phòng đào tạo": 0.95, "học vụ": 1.0,
            "tín chỉ": 0.85, "chứng chỉ": 0.8, "bằng tốt nghiệp": 0.9, "xét tốt nghiệp": 0.95,
            "chuẩn đầu ra": 0.9, "toeic": 0.8, "ielts": 0.8, "học lại": 0.85,
            "cải thiện điểm": 0.85, "phúc khảo": 0.95, "chuyển ngành": 0.9, "bảo lưu": 0.95,
            "điểm f": 0.85, "trùng lịch": 0.9
        }
    },
    "TUITION": {
        "id": 4,
        "name": "Học phí",
        "code": "TUITION",
        "description": "Mức thu học phí, gia hạn đóng tiền, học bổng, biên lai thanh toán, phòng tài chính kế toán",
        "icon": "bi-cash-coin",
        "color": "#ec4899", # Pink
        "keywords": {
            "học phí": 1.0, "tiền học": 0.95, "đóng tiền": 0.9, "thanh toán học phí": 1.0,
            "ngân hàng": 0.75, "gia hạn nợ": 0.95, "nợ học phí": 1.0, "học bổng": 0.95,
            "miễn giảm": 0.9, "biên lai": 0.9, "tài chính": 0.8, "kế toán": 0.8,
            "hóa đơn": 0.85, "chuyển khoản": 0.8, "tăng học phí": 0.95, "tiền tín chỉ": 0.9
        }
    },
    "ACTIVITIES": {
        "id": 5,
        "name": "Hoạt động sinh viên",
        "code": "ACTIVITIES",
        "description": "Đoàn thanh niên, Hội sinh viên, CLB đội nhóm, điểm rèn luyện, tình nguyện, phong trào",
        "icon": "bi-people",
        "color": "#8b5cf6", # Purple
        "keywords": {
            "đoàn hội": 1.0, "hội sinh viên": 1.0, "đoàn thanh niên": 1.0, "câu lạc bộ": 0.95,
            "clb": 0.95, "điểm rèn luyện": 1.0, "đrl": 1.0, "tình nguyện": 0.9,
            "mùa hè xanh": 0.95, "phong trào": 0.85, "ngày hội": 0.85, "ngoại khóa": 0.9,
            "văn nghệ": 0.85, "hội thao": 0.9, "hiến máu": 0.9, "sinh hoạt lớp": 0.8,
            "cán sự": 0.8, "bí thư": 0.85
        }
    },
    "OTHER": {
        "id": 6,
        "name": "Ý kiến khác",
        "code": "OTHER",
        "description": "Canteen, bảo vệ, an ninh, y tế, xe buýt, các vấn đề khác",
        "icon": "bi-chat-square-dots",
        "color": "#64748b", # Slate Gray
        "keywords": {
            "canteen": 0.95, "căn tin": 0.95, "đồ ăn": 0.85, "vệ sinh an toàn": 0.8,
            "bảo vệ": 0.9, "an ninh": 0.85, "thái độ bảo vệ": 0.95, "y tế": 0.85,
            "xe buýt": 0.9, "xe bus": 0.9, "trạm xe": 0.85, "khác": 0.5
        }
    }
}

class VietnameseFeedbackClassifier:
    """
    Module AI phân loại văn bản tiếng Việt hỗ trợ Multi-label và Sentiment Analysis
    """
    def __init__(self):
        self.categories = CATEGORY_DEFINITIONS
        self.confidence_threshold = 0.35 # Ngưỡng để giữ nhãn dự đoán

    def predict(self, text: str, title: str = "") -> Dict[str, Any]:
        """
        Dự đoán danh mục (Multi-label) và cảm xúc cho phản hồi.
        """
        full_text = f"{title} {text}".strip()
        normalized_full = normalize_vietnamese_text(full_text)
        clauses = split_sentences_or_clauses(full_text)
        
        # 1. Tính điểm từng danh mục
        category_scores: Dict[str, float] = {code: 0.0 for code in self.categories}
        category_matched_tokens: Dict[str, List[str]] = {code: [] for code in self.categories}
        clause_evidence: List[Dict[str, Any]] = []

        # Phân tích từng vế câu để tìm bằng chứng đa nhãn
        for clause in clauses:
            clause_hits = {}
            for code, cat_info in self.categories.items():
                if code == "OTHER":
                    continue
                score_for_cat = 0.0
                matched = []
                for kw, weight in cat_info["keywords"].items():
                    if kw in clause:
                        score_for_cat += weight
                        matched.append(kw)
                if score_for_cat > 0:
                    clause_hits[code] = {
                        "score": score_for_cat,
                        "matched": matched,
                        "cat_name": cat_info["name"]
                    }
                    category_scores[code] += score_for_cat
                    category_matched_tokens[code].extend(matched)
            if clause_hits:
                clause_evidence.append({
                    "clause": clause,
                    "matches": clause_hits
                })

        # Xử lý từ khóa trên toàn bộ văn bản để tránh sót
        for code, cat_info in self.categories.items():
            if code == "OTHER":
                continue
            for kw, weight in cat_info["keywords"].items():
                if kw in normalized_full and kw not in category_matched_tokens[code]:
                    category_scores[code] += weight * 0.7
                    category_matched_tokens[code].append(kw)

        # Chuyển đổi điểm thô thành điểm xác suất / độ tin cậy (Confidence Score) từ 0.0 -> 0.99
        predictions = []
        max_score = max(category_scores.values()) if category_scores else 0

        for code, cat_info in self.categories.items():
            if code == "OTHER":
                continue
            raw_score = category_scores[code]
            if raw_score > 0:
                # Tính confidence bằng hàm logistic-like
                # 1 hit = ~0.65, 2 hits = ~0.85, 3+ hits = ~0.94-0.98
                confidence = round(1.0 - (1.0 / (1.0 + raw_score * 1.5)), 2)
                # Đảm bảo điểm nằm trong khoảng 0.40 - 0.98
                confidence = min(0.98, max(0.40, confidence))
                
                if confidence >= self.confidence_threshold:
                    predictions.append({
                        "category_id": cat_info["id"],
                        "category_code": code,
                        "category_name": cat_info["name"],
                        "description": cat_info["description"],
                        "icon": cat_info["icon"],
                        "color": cat_info["color"],
                        "confidence_score": confidence,
                        "matched_keywords": list(set(category_matched_tokens[code]))
                    })

        # Sắp xếp danh mục theo độ tin cậy giảm dần
        predictions.sort(key=lambda x: x["confidence_score"], reverse=True)

        # Nếu không khớp danh mục nào, gán "Ý kiến khác"
        if not predictions:
            other_cat = self.categories["OTHER"]
            predictions.append({
                "category_id": other_cat["id"],
                "category_code": "OTHER",
                "category_name": other_cat["name"],
                "description": other_cat["description"],
                "icon": other_cat["icon"],
                "color": other_cat["color"],
                "confidence_score": 0.50,
                "matched_keywords": ["ý kiến chung"]
            })

        # 2. Phân tích cảm xúc
        sentiment_res = analyze_sentiment(full_text)

        # 3. Overall confidence score
        overall_conf = predictions[0]["confidence_score"] if predictions else 0.5

        return {
            "text": full_text,
            "normalized_text": normalized_full,
            "is_multi_label": len(predictions) > 1,
            "predicted_categories": predictions,
            "sentiment": sentiment_res,
            "overall_confidence": overall_conf,
            "clause_evidence": clause_evidence
        }

# Global singleton classifier instance
ai_classifier = VietnameseFeedbackClassifier()
