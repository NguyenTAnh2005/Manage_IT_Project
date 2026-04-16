# ========================================
# CUSTOM EXCEPTION HANDLERS
# ========================================
# Convert Pydantic validation errors sang tiếng Việt

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


# ========================================
# TRANSLATION MAP - LỖI TIẾNG VIỆT
# ========================================
VALIDATION_ERROR_MESSAGES = {
    # Độ dài string
    "string_too_short": "Quá ngắn (tối thiểu {min_length} ký tự)",
    "string_too_long": "Quá dài (tối đa {max_length} ký tự)",
    
    # Email
    "value_error": "Giá trị không hợp lệ",
    
    # Missing field
    "missing": "Trường này là bắt buộc",
    
    # Type errors
    "int_parsing": "Phải là số nguyên",
    "float_parsing": "Phải là số thực",
    
    # Custom validators
    "assertion_error": "Dữ liệu không hợp lệ",
}


def get_vietnamese_error_message(error: dict) -> str:
    """
    Convert Pydantic error sang tiếng Việt.
    
    Args:
        error: Dict error từ Pydantic validation
        
    Returns:
        str: Message tiếng Việt
    """
    error_type = error.get("type", "")
    ctx = error.get("ctx", {})
    msg = error.get("msg", "")
    
    # Nếu là custom validator error, dùng message gốc (đã tiếng Việt)
    if "Email không hợp lệ" in msg or "Mật khẩu phải chứa" in msg:
        return msg
    
    # Map error type sang message tiếng Việt
    if error_type in VALIDATION_ERROR_MESSAGES:
        template = VALIDATION_ERROR_MESSAGES[error_type]
        # Substitute placeholders từ context
        try:
            return template.format(**ctx)
        except KeyError:
            return template
    
    # Fallback: return original message
    return msg


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler cho RequestValidationError.
    Convert tất cả validation errors sang tiếng Việt.
    
    Args:
        request: HTTP request
        exc: RequestValidationError từ Pydantic
        
    Returns:
        JSONResponse với errors tiếng Việt
    """
    # Tạo list errors với message tiếng Việt
    errors = []
    
    for error in exc.errors():
        field = error.get("loc", [])[-1]  # Lấy tên field (loc[-1])
        message = get_vietnamese_error_message(error)
        
        errors.append({
            "field": field,
            "message": message,
            "type": error.get("type", "")
        })
    
    # Trả về response có format nhất quán
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Dữ liệu không hợp lệ",
            "errors": errors
        }
    )
