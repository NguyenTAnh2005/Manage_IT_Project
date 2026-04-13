/**
 * API Register - Tất cả các trường hợp lỗi có thể xảy ra
 * 
 * Endpoint: POST /auth/register
 */

// ===== CASE 1: Email không hợp lệ =====
// Request
{
  "email": "user@example.",
  "password": "Password@123",
  "full_name": "Nguyễn Văn A"
}

// Response (422 - Unprocessable Entity)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "email",
      "message": "Email không hợp lệ. Vui lòng nhập email đúng định dạng."
    }
  ]
}

// ===== CASE 2: Password quá ngắn (dưới 6 ký tự) =====
// Request
{
  "email": "user@example.com",
  "password": "Pass@1",
  "full_name": "Nguyễn Văn A"
}

// Response (422)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "password",
      "message": "Password tối thiểu 6 ký tự"
    }
  ]
}

// ===== CASE 3: Password không có chữ hoa =====
// Request
{
  "email": "user@example.com",
  "password": "password@123",
  "full_name": "Nguyễn Văn A"
}

// Response (422)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "password",
      "message": "Password phải chứa ít nhất 1 chữ hoa (A-Z)"
    }
  ]
}

// ===== CASE 4: Password không có chữ thường =====
// Request
{
  "email": "user@example.com",
  "password": "PASSWORD@123",
  "full_name": "Nguyễn Văn A"
}

// Response (422)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "password",
      "message": "Password phải chứa ít nhất 1 chữ thường (a-z)"
    }
  ]
}

// ===== CASE 5: Password không có ký tự đặc biệt =====
// Request
{
  "email": "user@example.com",
  "password": "Password123",
  "full_name": "Nguyễn Văn A"
}

// Response (422)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "password",
      "message": "Password phải chứa ít nhất 1 ký tự đặc biệt"
    }
  ]
}

// ===== CASE 6: Email rỗng =====
// Request
{
  "email": "",
  "password": "Password@123",
  "full_name": "Nguyễn Văn A"
}

// Response (422)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "email",
      "message": "Email không hợp lệ. Vui lòng nhập email đúng định dạng."
    }
  ]
}

// ===== CASE 7: Full name rỗng =====
// Request
{
  "email": "user@example.com",
  "password": "Password@123",
  "full_name": ""
}

// Response (422)
{
  "detail": "Dữ liệu không hợp lệ",
  "errors": [
    {
      "field": "full_name",
      "message": "Trường 'full_name' quá ngắn"
    }
  ]
}

// ===== CASE 8: Email đã tồn tại (đăng ký lần 2 với email tương tự) =====
// Request
{
  "email": "user@example.com",
  "password": "Password@123",
  "full_name": "Nguyễn Văn A"
}

// Response (400 - Bad Request)
{
  "detail": "Email đã được đăng ký. Vui lòng sử dụng email khác."
}

// ===== CASE 9: Đăng ký THÀNH CÔNG =====
// Request
{
  "email": "newuser@example.com",
  "password": "Password@123",
  "full_name": "Nguyễn Văn B"
}

// Response (201 - Created)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "newuser@example.com",
    "full_name": "Nguyễn Văn B",
    "created_at": "2026-04-13T02:24:31.715Z",
    "updated_at": null
  }
}

// ===== PASSWORD REQUIREMENTS =====
/*
Password phải đáp ứng TẤT CẢ điều kiện:
✅ Tối thiểu 6 ký tự
✅ Có ít nhất 1 chữ hoa (A-Z)
✅ Có ít nhất 1 chữ thường (a-z)
✅ Có ít nhất 1 ký tự đặc biệt (!@#$%^&*...)

Ví dụ password hợp lệ:
- Password@123
- Admin#2024
- MyPass!999
- Test@Pass1
*/

// ===== STATUS CODES =====
/*
201 - Created: Đăng ký thành công
400 - Bad Request: Email đã tồn tại
422 - Unprocessable Entity: Dữ liệu không hợp lệ (validation errors)
500 - Internal Server Error: Lỗi server (hiếm gặp)
*/
