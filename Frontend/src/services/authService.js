import axiosInstance from "./axiosConfig";

export const authService = {
    // Đăng ký tài khoản mới
    register: async (email, password, fullName) => {
        const payload = {
            email: email,
            password: password,
            full_name: fullName
        };
        const res = await axiosInstance.post('/auth/register', payload);
        return res.data;
    },

    //  Đăng nhập (form OAuth2PasswordRequestForm)
    login: async (email, password) =>{
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await axiosInstance.post('/auth/login', formData, {
            headers:{
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        return res.data;
    },

    // Lấy thông tin user hiện tại
    getMe: async () =>{
        const res = await axiosInstance.get('/users/me');
        return res.data;
    }
}