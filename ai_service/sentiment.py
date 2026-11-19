from typing import Dict, Any
from .preprocessor import normalize_vietnamese_text

# Từ điển cảm xúc tiếng Việt (Lexicon-based with semantic intensity)
POSITIVE_KEYWORDS = {
    "tuyệt vời": 0.9, "rất tốt": 0.85, "tốt": 0.6, "hài lòng": 0.75, "rất hài lòng": 0.9,
    "nhiệt tình": 0.7, "cảm ơn": 0.65, "khen": 0.7, "nhanh chóng": 0.6, "chu đáo": 0.7,
    "tiến bộ": 0.5, "thông thoáng": 0.5, "mát mẻ": 0.5, "sạch sẽ": 0.6, "chất lượng": 0.6,
    "ủng hộ": 0.6, "thích": 0.55, "tận tâm": 0.75, "dễ hiểu": 0.65, "ổn định": 0.5,
    "thuận tiện": 0.6, "tiện lợi": 0.6, "hiện đại": 0.6, "chuẩn": 0.5, "rõ ràng": 0.55
}

NEGATIVE_KEYWORDS = {
    "bức xúc": 0.95, "quá tệ": 0.9, "rất tệ": 0.9, "tệ": 0.7, "hỏng": 0.8, "hư": 0.8,
    "hư hỏng": 0.85, "hư máy lạnh": 0.85, "thất vọng": 0.85, "chậm chạp": 0.75, "chậm": 0.6,
    "quá lâu": 0.75, "nóng quá": 0.8, "ngột ngạt": 0.75, "ức chế": 0.9, "khó chịu": 0.75,
    "thái độ kém": 0.85, "thái độ không tốt": 0.8, "bực mình": 0.8, "bất cập": 0.7, "vô lý": 0.8,
    "lag": 0.65, "chập chờn": 0.7, "mệt mỏi": 0.7, "dơ": 0.7, "bẩn": 0.7, "mùi hôi": 0.85,
    "ồn ào": 0.7, "không công bằng": 0.85, "thiếu sót": 0.6, "sai sót": 0.7, "áp lực": 0.65,
    "khó hiểu": 0.65, "nhanh quá": 0.6, "quá tải": 0.75, "nghẽn mạng": 0.75, "rớt mạng": 0.8,
    "rất chán": 0.8, "tồi tệ": 0.9, "phiền toái": 0.7, "khẩn cấp": 0.85
}

URGENT_KEYWORDS = [
    "bức xúc", "khẩn cấp", "nguy hiểm", "chập điện", "hỏng nặng", "sai điểm", "bị khóa",
    "mất đồ", "quấy rối", "hư hỏng nặng", "rơi rớt", "dột nặng", "không vào thi được"
]

NEGATION_WORDS = ["không", "chưa", "chẳng", "kém", "ít"]

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Phân tích cảm xúc văn bản:
    - Trả về label: POSITIVE / NEUTRAL / NEGATIVE
    - score: từ -1.0 đến +1.0
    - is_urgent: phát hiện các vấn đề bức xúc / nguy cấp cần xử lý ngay
    """
    normalized = normalize_vietnamese_text(text)
    words = normalized.split()
    
    pos_score = 0.0
    neg_score = 0.0
    matched_pos = []
    matched_neg = []
    
    # Check multi-word negative first
    for kw, val in NEGATIVE_KEYWORDS.items():
        if kw in normalized:
            neg_score += val
            matched_neg.append(kw)
            
    # Check multi-word positive
    for kw, val in POSITIVE_KEYWORDS.items():
        if kw in normalized:
            # Check if negated ("không tốt", "chưa hài lòng")
            pos_index = normalized.find(kw)
            preceding = normalized[max(0, pos_index - 10):pos_index]
            is_negated = any(neg in preceding.split() for neg in NEGATION_WORDS)
            if is_negated:
                neg_score += val * 0.9
                matched_neg.append(f"không {kw}")
            else:
                pos_score += val
                matched_pos.append(kw)
                
    # Normalize score between -1.0 and 1.0
    diff = pos_score - neg_score
    total = pos_score + neg_score
    
    if total == 0:
        score = 0.0
        label = "NEUTRAL"
    else:
        score = round(diff / (total + 0.5), 2)
        if score > 0.15:
            label = "POSITIVE"
        elif score < -0.15:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
            
    # Phát hiện tính cấp bách (Urgent)
    is_urgent = any(u in normalized for u in URGENT_KEYWORDS) or (label == "NEGATIVE" and score <= -0.55)
    
    return {
        "label": label,
        "score": score,
        "is_urgent": is_urgent,
        "matched_positive": matched_pos,
        "matched_negative": matched_neg
    }
