/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useContext, useEffect } from "react";
import axiosInstance from "../services/axiosConfig";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(() => localStorage.getItem("PM_access_token"));
    const [projectCode, setProjectCode] = useState(() => localStorage.getItem("PM_project_code"));
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Lấy thông tin user từ API khi có token
    const fetchUserProfile = async () => {
        try {
            const res = await axiosInstance.get("/users/me");
            setUser(res.data);
        } catch (error) {
            console.error("Lỗi lấy thông tin user:", error);
            setToken(null);
            setUser(null);
            localStorage.removeItem("PM_access_token");
        } finally {
            setLoading(false);
        }
    };

    // Tự động fetch user khi F5 trang nếu có token
    useEffect(() => {
        if (token) {
            fetchUserProfile();
        } else {
            setLoading(false);
        }
    }, [token]);

    // Xử lý khi đăng nhập thành công
    const logIn = async (newToken) => {
        setToken(newToken);
        localStorage.setItem("PM_access_token", newToken);
        
        try {
            const res = await axiosInstance.get("/users/me");
            setUser(res.data);
        } catch (error) {
            console.error("Không lấy được profile khi login", error);
        }
    };

    const logOut = () => {
        setToken(null);
        setUser(null);
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
        user,
        projectCode,
        isAuthenticated: !!token,
        authLoading: loading,
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