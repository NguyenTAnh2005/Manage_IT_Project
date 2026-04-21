import axios from 'axios';

// Create Instance
const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{'Content-Type':'application/json',},
});

// ===================================================================
// REQUEST INTERCEPTOR: Hành động chặn lại TRƯỚC KHI gửi thư đi
// ===================================================================
// Thực chất là get access_token trên Localstorage, đính vào header để gửi Req

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('PM_access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ===================================================================
// RESPONSE INTERCEPTOR: Hành động chặn lại SAU KHI nhận thư phản hồi về
// ===================================================================
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('PM_access_token');
      window.location.href = '/login'; // Đẩy về login ngay lập tức
    }
    return Promise.reject(error);
  }
);


export default axiosInstance;
