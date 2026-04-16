"""
Validators - Các hàm validate dữ liệu custom.

Dùng để kiểm tra tính hợp lệ của dữ liệu trước khi lưu vào database.
"""

import re
from typing import Optional


# ============= PASSWORD VALIDATORS =============

def is_strong_password(password: str) -> bool:
    """
    Kiểm tra mật khẩu mạnh.
    
    Yêu cầu:
    - Tối thiểu 8 ký tự
    - Ít nhất 1 chữ hoa (A-Z)
    - Ít nhất 1 chữ thường (a-z)
    - Ít nhất 1 ký tự đặc biệt (!@#$%^&*...)
    
    Args:
        password (str): Mật khẩu cần kiểm tra
    
    Returns:
        bool: True nếu mạnh, False nếu yếu
    
    Example:
        >>> is_strong_password("WeakPass")
        False
        >>> is_strong_password("SecurePass!")
        True
    """
    # Kiểm tra độ dài
    if len(password) < 8:
        return False
    
    # Kiểm tra có chữ hoa
    if not re.search(r'[A-Z]', password):
        return False
    
    # Kiểm tra có chữ thường
    if not re.search(r'[a-z]', password):
        return False
    
    # Kiểm tra có ký tự đặc biệt
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False
    
    return True


def get_password_error_message() -> str:
    """
    Trả về message lỗi chi tiết khi mật khẩu yếu.
    Dùng trong field_validator để thông báo cho user.
    
    Returns:
        str: Message lỗi tiếng Việt
    """
    return (
        "Mật khẩu phải chứa: "
        "- Tối thiểu 8 ký tự, "
        "- Ít nhất 1 chữ hoa (A-Z), "
        "- Ít nhất 1 chữ thường (a-z), "
        "- Ít nhất 1 ký tự đặc biệt (!@#$%^&*)"
    )


# ============= EMAIL VALIDATORS =============

def is_valid_email(email: str) -> bool:
    """
    Validate định dạng email.
    
    Args:
        email (str): Email cần kiểm tra
    
    Returns:
        bool: True nếu hợp lệ, False nếu không
    
    Example:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid.email@")
        False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ============= TEXT VALIDATORS =============

def is_valid_full_name(name: str) -> bool:
    """
    Validate tên người dùng.
    Cho phép: chữ cái (cả tiếng Anh và tiếng Việt), space, dấu gạch ngang, dấu chấm, dấu nháy
    
    Args:
        name (str): Tên cần kiểm tra
    
    Returns:
        bool: True nếu hợp lệ, False nếu không
    
    Example:
        >>> is_valid_full_name("Nguyễn Tuấn Anh")
        True
        >>> is_valid_full_name("Name123")
        False
    """
    # Cho phép: chữ cái (ASCII + Unicode Việt), space, dấu gạch, dấu chấm, dấu nháy
    pattern = r'^[a-zA-ZÀ-ỿ\s\-\.\']+$'
    return re.match(pattern, name) is not None
