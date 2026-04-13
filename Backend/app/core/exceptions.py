"""
Custom Exceptions và Error Handlers
Xử lý lỗi và trả response tiếng Việt
"""

from fastapi import HTTPException
from pydantic import ValidationError
from typing import Any


# ===== CUSTOM EXCEPTIONS =====

class APIException(HTTPException):
    """
    Base exception class cho API
    Được dùng cho tất cả custom errors
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class EmailAlreadyExistsException(APIException):
    """Exception khi email đã tồn tại"""
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Email đã được đăng ký. Vui lòng sử dụng email khác."
        )


class InvalidCredentialsException(APIException):
    """Exception khi email hoặc password sai"""
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Email hoặc password không chính xác"
        )


class UserNotFoundException(APIException):
    """Exception khi user không tồn tại"""
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="User không tồn tại"
        )


class InvalidTokenException(APIException):
    """Exception khi token không hợp lệ"""
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )


# ===== ERROR MESSAGE TRANSLATIONS =====
# Dictionary dịch lỗi validation từ tiếng Anh sang tiếng Việt

ERROR_MESSAGES_VI = {
    "value_error": {
        "email": "Email không hợp lệ. Vui lòng nhập email đúng định dạng.",
        "An email address cannot end with a period.": "Email không hợp lệ. Email không thể kết thúc bằng dấu chấm.",
        "value is not a valid email address": "Email không hợp lệ",
    },
    "string_too_short": "Giá trị quá ngắn",
    "string_too_long": "Giá trị quá dài",
    "greater_than_equal": "Giá trị phải lớn hơn hoặc bằng",
    "less_than_equal": "Giá trị phải nhỏ hơn hoặc bằng",
    "password_too_short": "Password tối thiểu 6 ký tự",
}


def translate_validation_error(error: dict) -> str:
    """
    Dịch lỗi validation sang tiếng Việt
    - Input: error dict từ Pydantic
    - Output: message tiếng Việt
    """
    error_type = error.get("type", "")
    msg = error.get("msg", "Dữ liệu không hợp lệ")
    field = None
    
    # Lấy tên field
    if error.get("loc") and len(error["loc"]) > 1:
        field = error["loc"][1]
    
    # Dịch theo field
    if field == "email":
        return "Email không hợp lệ. Vui lòng nhập email đúng định dạng."
    
    # Dịch lỗi full_name validation
    if field == "full_name":
        if "too short" in msg.lower() or "at least 1" in msg.lower() or "should have at least" in msg.lower():
            return "Tên không được để trống"
        if "too long" in msg.lower() or "less than or equal to 255" in msg.lower():
            return "Tên tối đa 255 ký tự"
        # Nếu msg tiếng Việt thì trả trực tiếp
        if any(char in msg for char in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"):
            return msg
    
    # Dịch lỗi password validation
    if field == "password":
        if "tối thiểu 6 ký tự" in msg.lower() or "6" in msg:
            return "Password tối thiểu 6 ký tự"
        if "chữ hoa" in msg.lower() or "uppercase" in msg.lower():
            return "Password phải chứa ít nhất 1 chữ hoa (A-Z)"
        if "chữ thường" in msg.lower() or "lowercase" in msg.lower():
            return "Password phải chứa ít nhất 1 chữ thường (a-z)"
        if "ký tự đặc biệt" in msg.lower() or "special" in msg.lower():
            return "Password phải chứa ít nhất 1 ký tự đặc biệt (!@#$%^&*...)"
        # Nếu msg tiếng Việt thì trả trực tiếp
        if any(char in msg for char in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"):
            return msg
    
    if "too short" in msg.lower():
        return f"Trường '{field}' quá ngắn"
    
    if "too long" in msg.lower():
        return f"Trường '{field}' quá dài"
    
    # Nếu không match, trả message gốc
    return msg


def format_validation_errors(errors: list) -> dict:
    """
    Format lỗi validation Pydantic thành response format
    - Input: errors list từ Pydantic
    - Output: dict format cho API response
    
    Ví dụ:
    {
        "detail": "Dữ liệu không hợp lệ",
        "errors": [
            {
                "field": "email",
                "message": "Email không hợp lệ. Vui lòng nhập email đúng định dạng."
            }
        ]
    }
    """
    formatted_errors = []
    
    for error in errors:
        field = error.get("loc")[1] if error.get("loc") and len(error["loc"]) > 1 else "unknown"
        message = translate_validation_error(error)
        
        formatted_errors.append({
            "field": field,
            "message": message
        })
    
    return {
        "detail": "Dữ liệu không hợp lệ",
        "errors": formatted_errors
    }
