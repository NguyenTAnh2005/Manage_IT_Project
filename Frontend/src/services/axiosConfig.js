import axios from 'axios';

// Tạo axios instance với cấu hình chung
const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{'Content-Type':'application/json'},
});

// Request interceptor: Thêm token vào header trước khi gửi request
axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('PM_access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor: Xử lý lỗi 401 (token hết hạn)
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Xóa token và redirect về login
            localStorage.removeItem('PM_access_token');
            localStorage.removeItem('PM_project_code');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
