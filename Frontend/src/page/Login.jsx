// Frontend/src/page/Login.jsx
import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { authService } from "../services/authService";
import { useNavigate, Link } from "react-router-dom";
import Input from "../components/common/Input";
import InputPassword from "../components/common/InputPassword";
import { Mail } from "lucide-react";

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
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

        // Validate input
        if (!email || !password) {
            setError("Vui lòng điền đầy đủ email và mật khẩu!");
            setLoading(false);
            return;
        }

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

    return (
        <div className="flex flex-col relative items-center min-h-screen justify-center text-light-text bg-light-bg dark:bg-dark-bg dark:text-dark-text">
            <form
                onSubmit={handleLogin}
                className="flex gap-4 p-8 flex-col w-full max-w-md items-center outline-none rounded-xl shadow-2xl dark:shadow-gray-400 bg-white dark:bg-slate-800"
            >
                <h1 className="font-bold text-3xl text-center text-primary mb-2">
                    👋 Đăng Nhập
                </h1>
                <p className="text-base text-center text-slate-500 mb-4">
                    Đăng nhập để quản lý dự án của bạn
                </p>

                {error && (
                    <span className="bg-red-50 border border-red-200 text-red-600 w-full text-sm italic px-3 py-2 rounded-md">
                        ⚠️ {error}
                    </span>
                )}

                <Input
                    label="Email"
                    type="email"
                    placeholder="abc@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    isRequired={true}
                    icon={<Mail size={18} className="text-slate-400" />}
                />

                <InputPassword
                    label="Mật khẩu"
                    placeholder="Nhập mật khẩu"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    isRequired={true}
                />

                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full mt-4 btn-primary py-3 ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                    {loading ? "Đang xử lý..." : "Đăng Nhập"}
                </button>

                <div className="w-full border-t border-slate-200 dark:border-slate-700 mt-6 pt-4 text-center">
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">
                        Chưa có tài khoản?
                    </p>
                    <Link
                        to="/register"
                        className="inline-block w-full py-2 border border-primary text-primary font-bold rounded-md hover:bg-primary hover:text-white transition-colors duration-300"
                    >
                        Đăng Ký Ngay
                    </Link>
                </div>
            </form>
        </div>
    );
};

export default Login;