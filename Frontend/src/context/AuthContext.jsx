/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useContext, useEffect } from "react";
import axiosInstance from "../services/axiosConfig";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(() => localStorage.getItem("PM_access_token"));
    const [projectCode, setProjectCode] = useState(() => localStorage.getItem("PM_project_code"));
    
    // ✅ TRÁI TIM CỦA HỆ THỐNG: Lưu nguyên cục JSON API trả về vào đây
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // HÀM LẤY THÔNG TIN TỪ API
    const fetchUserProfile = async () => {
        try {
            // Gọi thẳng API /users/me mà sếp bảo nó đang trả về ngọt xớt ấy
            const res = await axiosInstance.get("/users/me");
            setUser(res.data); // Nhận đủ {id: 1, full_name: "Tuấn Anh"...}
        } catch (error) {
            console.error("Lỗi lấy thông tin user:", error);
            // Nếu lỗi (ví dụ token hết hạn), dọn dẹp luôn
            setToken(null);
            setUser(null);
            localStorage.removeItem("PM_access_token");
        } finally {
            setLoading(false);
        }
    };

    // F5 trang tự động load lại User
    useEffect(() => {
        if (token) {
            fetchUserProfile();
        } else {
            setLoading(false);
        }
    }, [token]);

    // KHI ĐĂNG NHẬP THÀNH CÔNG
    const logIn = async (newToken) => {
        setToken(newToken);
        localStorage.setItem("PM_access_token", newToken);
        
        // Cập nhật Profile ngay tắp lự
        try {
            // Interceptor của sếp tự lấy token mới từ localStorage rồi nên gọi vô tư
            const res = await axiosInstance.get("/users/me");
            setUser(res.data);
        } catch (error) {
            console.error("Không lấy được profile khi login", error);
        }
    };

    const logOut = () => {
        setToken(null);
        setUser(null); // Bay màu user
        localStorage.removeItem("PM_access_token");
        localStorage.removeItem("PM_project_code");
    };

    const joinProject = (newCode) => {
        setProjectCode(newCode);
        localStorage.setItem("PM_project_code", newCode);
    };

    const outProject = () => {
        setProjectCode(null);
        localStorage.removeItem("PM_project_code");
    };

    const value = {
        token,
        user, // ✅ Bây giờ biến này là cục vàng: {id: 1, full_name: "Tuấn Anh"}
        projectCode,
        isAuthenticated: !!token,
        authLoading: loading, // Trạng thái chờ load data
        logIn,
        logOut,
        joinProject,
        outProject
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};