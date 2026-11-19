import re
import unicodedata

def normalize_vietnamese_text(text: str) -> str:
    """
    Tiền xử lý văn bản tiếng Việt:
    - Chuẩn hóa Unicode dạng NFC
    - Chuyển về chữ thường
    - Làm sạch khoảng trắng thừa và ký tự đặc biệt không cần thiết
    """
    if not text:
        return ""
    
    # 1. Unicode NFC normalization
    text = unicodedata.normalize('NFC', text)
    
    # 2. Lowercase
    text = text.lower()
    
    # 3. Chuẩn hóa khoảng trắng và dấu câu
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^\w\s\.,!\?àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def split_sentences_or_clauses(text: str) -> list[str]:
    """
    Tách đoạn văn bản thành các vế / câu độc lập dựa trên dấu câu hoặc từ nối (nhưng, còn, mà, và, ngoài ra)
    để phân tích đa danh mục (Multi-label) chính xác hơn.
    """
    clean = normalize_vietnamese_text(text)
    # Tách theo dấu câu . , ; ! ? hoặc từ nối thông dụng
    clauses = re.split(r'[\.,;!\?]+|\bnhưng\b|\bcòn\b|\bngoài ra\b|\bđồng thời\b', clean)
    clauses = [c.strip() for c in clauses if len(c.strip()) > 3]
    if not clauses:
        clauses = [clean]
    return clauses
