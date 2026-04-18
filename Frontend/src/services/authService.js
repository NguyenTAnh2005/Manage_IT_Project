import axiosInstance from "./axiosConfig";

export const authService = {
    // Bỏ do này dành cho form2OAuth
    // login: async (email, password) =>{
    //     const formData = new URLSearchParams();
    //     formData.append('username', email);
    //     formData.append('password', password);

    //     const res = await axiosInstance.post('auth/login', formData, {
    //         headers:{
    //             'Content-Type': 'application/x-www-form-urlencoded'
    //         }
    //     });
    //     return res.data;
    // },
    login: async (email, password) => {
        const payload = {
            email: email,
            password: password
        };
        const res = await axiosInstance.post('/auth/login', payload);
        return res.data
    },

    getMe: async () =>{
        const res = await axiosInstance.get('/me');
        return res.data;
    }
}