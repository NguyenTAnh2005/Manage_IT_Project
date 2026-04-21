import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { authService } from "../services/authService";
import { useNavigate } from "react-router-dom";
import Input from "../components/common/Input";
import InputPassword from "../components/common/InputPassword";

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [fullName, setFullName] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const { logIn, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate("/join-project");
        }
    }, [isAuthenticated, navigate]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const res = await authService.login(email, password);
            logIn(res.access_token);
            navigate("/join-project");
        } catch (err) {
            setError(err?.response?.data?.detail || "Đăng nhập thất bại!");
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError("");

        if (password !== confirmPassword) {
            setError("Mật khẩu không trùng khớp!");
            return;
        }

        if (password.length < 6) {
            setError("Mật khẩu phải có ít nhất 6 ký tự!");
            return;
        }

        setLoading(true);

        try {
            await authService.register(email, password, fullName);
            setError("");
            setEmail("");
            setPassword("");
            setConfirmPassword("");
            setFullName("");
            setIsLogin(true);
            alert("Đăng ký thành công! Vui lòng đăng nhập.");
        } catch (err) {
            setError(err?.response?.data?.detail || "Đăng ký thất bại!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
            background: "#f5f5f5",
            padding: "20px"
        }}>
            <div style={{
                background: "white",
                padding: "40px",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                width: "100%",
                maxWidth: "400px"
            }}>
                <h1 style={{
                    textAlign: "center",
                    fontSize: "28px",
                    fontWeight: "bold",
                    marginBottom: "10px",
                    color: "#333"
                }}>
                    {isLogin ? "👋 Đăng Nhập" : "📝 Đăng Ký"}
                </h1>

                <p style={{
                    textAlign: "center",
                    color: "#666",
                    marginBottom: "30px",
                    fontSize: "14px"
                }}>
                    {isLogin ? "Đăng nhập để quản lý dự án của bạn" : "Tạo tài khoản mới để bắt đầu"}
                </p>

                {error && (
                    <div style={{
                        background: "#ffe6e6",
                        border: "1px solid #ff6666",
                        color: "#cc0000",
                        padding: "12px",
                        borderRadius: "4px",
                        marginBottom: "20px",
                        fontSize: "13px"
                    }}>
                        ⚠️ {error}
                    </div>
                )}

                <form onSubmit={isLogin ? handleLogin : handleRegister} style={{ display: "flex", flexDirection: "column", gap: "0" }}>
                    {!isLogin && (
                        <Input
                            label="Họ và Tên"
                            placeholder="Nhập họ và tên"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            isRequired={true}
                            icon="👤"
                        />
                    )}

                    <Input
                        label="Email"
                        type="email"
                        placeholder="abc@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        isRequired={true}
                        icon="📧"
                    />

                    <InputPassword
                        label="Mật khẩu"
                        placeholder="Nhập mật khẩu"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    {!isLogin && (
                        <InputPassword
                            label="Xác nhận mật khẩu"
                            placeholder="Nhập lại mật khẩu"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            width: "100%",
                            padding: "12px",
                            background: loading ? "#ccc" : "#0066cc",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            fontSize: "16px",
                            fontWeight: "bold",
                            cursor: loading ? "not-allowed" : "pointer",
                            marginTop: "10px"
                        }}
                    >
                        {loading ? "Đang xử lý..." : (isLogin ? "Đăng Nhập" : "Đăng Ký")}
                    </button>
                </form>

                <div style={{
                    textAlign: "center",
                    marginTop: "20px",
                    paddingTop: "20px",
                    borderTop: "1px solid #eee"
                }}>
                    <p style={{ color: "#666", fontSize: "14px", marginBottom: "10px" }}>
                        {isLogin ? "Chưa có tài khoản?" : "Đã có tài khoản?"}
                    </p>
                    <button
                        type="button"
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError("");
                            setEmail("");
                            setPassword("");
                            setConfirmPassword("");
                            setFullName("");
                        }}
                        style={{
                            background: "white",
                            color: "#0066cc",
                            border: "1px solid #0066cc",
                            padding: "10px 20px",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontSize: "14px",
                            fontWeight: "bold"
                        }}
                    >
                        {isLogin ? "Đăng Ký Ngay" : "Quay Lại Đăng Nhập"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;