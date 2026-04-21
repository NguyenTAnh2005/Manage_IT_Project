import axios from 'axios';

// Create Instance
const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{
        'Content-Type':'application/json',
    },
});

// ===================================================================
// REQUEST INTERCEPTOR: Hành động chặn lại TRƯỚC KHI gửi thư đi
// ===================================================================
// Thực chất là get access_token trên Localstorage, đính vào header để gửi Req

axiosInstance.interceptors.request.use(
    (config) =>{
        const token = localStorage.getItem('PM_access_token');
        if(token){
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config
    },
    (error)=>{
        return Promise.reject(error);
    }
);

// ===================================================================
// RESPONSE INTERCEPTOR: Hành động chặn lại SAU KHI nhận thư phản hồi về
// ===================================================================
axiosInstance.interceptors.response.use(
    (res)=>{
        return res ;
    },
    (err)=>{
        if(err.response && err.response.status == 401){
            console.error("Phiên đăng nhập hết hạn hoặc access token không hợp lệ!");
            localStorage.removeItem('PM_access_token');
            if(window.location.pathname != "/login"){
                window.location.href = '/login';
            }
        }
        return Promise.reject(err);
    }
);


export default axiosInstance;
