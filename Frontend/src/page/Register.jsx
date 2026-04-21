import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { authService } from "../services/authService";
import { useNavigate, Link } from "react-router-dom";
import InputPassword from "../components/common/InputPassword";
import Input from "../components/common/Input";
import { Mail, User } from "lucide-react";

const Register = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [fullName, setFullName] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    const { logIn, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate("/join-project");
        }
    }, [isAuthenticated, navigate]);

    const handleRegister = async (e) => {
        e.preventDefault();
        setError("");
        setSuccessMessage("");
        setLoading(true);

        // Validation
        if (!email || !password || !confirmPassword || !fullName) {
            setError("Vui lòng điền đầy đủ thông tin!");
            setLoading(false);
            return;
        }

        if (password !== confirmPassword) {
            setError("Mật khẩu xác nhận không khớp!");
            setLoading(false);
            return;
        }

        if (password.length < 6) {
            setError("Mật khẩu phải có ít nhất 6 ký tự!");
            setLoading(false);
            return;
        }

        try {
            // Gọi API đăng ký từ service
            const res = await authService.register(email, password, fullName);
            setSuccessMessage("Đăng ký thành công! Vui lòng đăng nhập.");
            
            // Reset form
            setEmail("");
            setPassword("");
            setConfirmPassword("");
            setFullName("");

            // Chuyển hướng về Login sau 2 giây
            setTimeout(() => {
                navigate("/login");
            }, 2000);

        } catch (err) {
            console.error("Lỗi đăng ký: ", err);
            const errorDetail = err.response?.data?.detail || "Đăng ký thất bại. Vui lòng thử lại!";
            setError(errorDetail);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col relative items-center min-h-screen border justify-center text-light-text bg-light-bg dark:bg-dark-bg dark:text-dark-text">
            <form
                onSubmit={handleRegister}
                className="flex gap-4 p-8 flex-col max-w-md items-center outline-none rounded-xl shadow-2xl dark:shadow-gray-400"
            >
                <p className="font-bold text-2xl text-wrap text-center text-primary">
                    ✨ Tạo Tài Khoản Mới! 🚀
                </p>
                <p className="text-base text-center">
                    Đăng ký để bắt đầu quản lý dự án của bạn!
                </p>

                {/* Hiển thị thông báo lỗi */}
                {error && (
                    <span className="bg-red-50 border border-red-200 text-red-600 w-full text-sm italic px-2 py-2 rounded-sm">
                        ⚠️ {error}
                    </span>
                )}

                {/* Hiển thị thông báo thành công */}
                {successMessage && (
                    <span className="bg-green-50 border border-green-200 text-green-600 w-full text-sm italic px-2 py-2 rounded-sm">
                        ✅ {successMessage}
                    </span>
                )}

                {/* Trường Họ Tên */}
                <Input
                    placeholder="Nguyễn Tuấn Anh"
                    label="Họ và Tên"
                    onChange={(e) => setFullName(e.target.value)}
                    isRequired={true}
                    icon={<User className="absolute top-[25%] left-[1%] text-dark-bg" />}
                    value={fullName}
                />

                {/* Trường Email */}
                <Input
                    placeholder="abc...@...com"
                    label="Email"
                    type="email"
                    onChange={(e) => setEmail(e.target.value)}
                    isRequired={true}
                    icon={<Mail className="absolute top-[25%] left-[1%] text-dark-bg" />}
                    value={email}
                />

                {/* Trường Mật khẩu */}
                <InputPassword
                    placeholder="......."
                    label="Mật khẩu"
                    onChange={(e) => setPassword(e.target.value)}
                    value={password}
                    isRequired={true}
                />

                {/* Trường Xác nhận mật khẩu */}
                <InputPassword
                    placeholder="......."
                    label="Xác nhận mật khẩu"
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    value={confirmPassword}
                    isRequired={true}
                />

                {/* Nút Đăng ký */}
                <button
                    type="submit"
                    className={`w-full btn-primary ${loading && "opacity-40 cursor-not-allowed"}`}
                >
                    {loading ? "Đang xử lý....." : "Đăng ký"}
                </button>

                {/* Link tới trang Đăng nhập */}
                <p className="text-center text-sm">
                    Đã có tài khoản?{" "}
                    <Link to="/login" className="text-primary font-semibold hover:underline">
                        Đăng nhập ngay
                    </Link>
                </p>
            </form>
        </div>
    );
};

export default Register;
