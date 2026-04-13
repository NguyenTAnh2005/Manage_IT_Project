import axiosInstance from "./axiosConfig";

export const authService = {
    login: async (email, password) =>{
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await axiosInstance.post('login', formData, {
            headers:{
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        return res.data;
    },

    getMe: async () =>{
        const res = await axiosInstance.get('/me');
        return res.data;
    }
}