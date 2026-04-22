import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { projectService } from "../services/projectService"; // Import service mới
import Input from "../components/common/Input";
import ThemeToggle from "../components/common/ThemeToggle";
import { LayoutGrid, ArrowRight, Loader2, FolderPlus, LogOut } from "lucide-react";

const JoinProject = () => {
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    
    const { joinProject, logOut } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const cleanCode = code.trim();
        
        // Validate format: 6-10 ký tự, chỉ A-Z, 0-9, underscore
        const codeRegex = /^[A-Z0-9_]{6,10}$/;
        
        if (!cleanCode) {
            setError("Vui lòng nhập mã dự án!");
            return;
        }

        if (!codeRegex.test(cleanCode)) {
            setError("Mã dự án phải chứa 6-10 ký tự (A-Z, 0-9, _). Ví dụ: HABIT_01");
            return;
        }

        setError("");
        setLoading(true);

        try {
            // Join project bằng project code
            await projectService.joinProject(cleanCode);
            
            // Lưu project_code vào context
            joinProject(cleanCode);
            
            // Redirect vào dashboard
            navigate(`/dashboard/${cleanCode}/wbs`);

        } catch (err) {
            const status = err.response?.status;
            const data = err.response?.data;

            // Handle lỗi theo status code từ backend
            if (status === 404) {
                setError("Mã dự án không tồn tại! Vui lòng kiểm tra lại.");
            } 
            else if (status === 422) {
                const validationMsg = data?.errors?.[0]?.message || "Định dạng mã không hợp lệ";
                setError(`Lỗi validation: ${validationMsg}`);
            }
            else {
                setError(data?.detail || data?.message || "Lỗi máy chủ. Thử lại sau.");
                console.error("Join Project error:", err);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logOut();
        navigate("/login");
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-light-bg dark:bg-dark-bg transition-colors duration-300">
            <div className="absolute top-5 right-5 flex gap-2">
                <ThemeToggle />
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-lg font-medium transition-colors"
                >
                    <LogOut size={18} />
                    Đăng xuất
                </button>
            </div>

            <div className="w-full max-w-2xl flex gap-8 px-4 flex-col sm:flex-row">
                {/* Form Tham gia dự án */}
                <form 
                    onSubmit={handleSubmit}
                    className="card flex-1 flex flex-col gap-6 p-10 shadow-2xl dark:shadow-gray-400"
                >
                    <div className="text-center space-y-2">
                        <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <LayoutGrid className="text-primary" size={32} />
                        </div>
                        <h2 className="text-2xl font-bold text-light-text dark:text-dark-text">
                            Tham gia Dự Án
                        </h2>
                        <p className="text-sm text-light-muted dark:text-dark-muted">
                            Nhập mã dự án để bắt đầu quản lý công việc
                        </p>
                    </div>

                    {/* Khung hiển thị lỗi */}
                    {error && (
                        <span className="bg-red-50 border border-red-200 text-red-600 w-full text-sm italic px-3 py-2 rounded-md">
                            ⚠️ {error}
                        </span>
                    )}

                    <Input 
                        label="Mã dự án"
                        placeholder="Ví dụ: HABIT_01, PM_PROJ..."
                        value={code}
                        onChange={(e) => setCode(e.target.value.toUpperCase())}
                        isRequired={true}
                        icon={<LayoutGrid className="absolute top-[28%] left-[2%] text-slate-400" size={18}/>}
                    />

                    <button 
                        type="submit" 
                        disabled={loading}
                        className={`btn-primary w-full flex items-center justify-center gap-2 py-3 ${loading && 'opacity-60 cursor-not-allowed'}`}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="animate-spin" size={18} /> Đang kiểm tra...
                            </>
                        ) : (
                            <>
                                Tiến vào dự án <ArrowRight size={18} />
                            </>
                        )}
                    </button>

                    <p className="text-xs text-center text-light-muted dark:text-dark-muted italic">
                        * Nếu chưa có mã, hãy liên hệ Trưởng dự án (PM)
                    </p>
                </form>

                {/* Form Tạo dự án */}
                <div className="card flex-1 flex flex-col gap-6 p-10 shadow-2xl dark:shadow-gray-400">
                    <div className="text-center space-y-2">
                        <div className="bg-green-100/50 dark:bg-green-900/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FolderPlus className="text-green-600 dark:text-green-400" size={32} />
                        </div>
                        <h2 className="text-2xl font-bold text-light-text dark:text-dark-text">
                            Tạo Dự Án Mới
                        </h2>
                        <p className="text-sm text-light-muted dark:text-dark-muted">
                            Bạn muốn làm chủ dự án?
                        </p>
                    </div>

                    <p className="text-sm text-slate-600 dark:text-slate-300">
                        Nếu bạn là Trưởng Dự Án (PM), hãy tạo dự án mới để bắt đầu quản lý.
                    </p>

                    <button 
                        onClick={() => navigate("/create-project")}
                        className={`btn-primary w-full flex items-center justify-center gap-2 py-3 bg-green-600 hover:bg-green-700 active:bg-green-800`}
                    >
                        <FolderPlus size={18} />
                        Tạo Dự Án Ngay
                    </button>

                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-3">
                        <p className="text-xs text-green-700 dark:text-green-300">
                            ✨ <strong>Lợi ích PM:</strong> Quản lý toàn bộ công việc, thành viên, và tiến độ dự án.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default JoinProject;