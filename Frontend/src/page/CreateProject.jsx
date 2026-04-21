import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { projectService } from "../services/projectService";
import Input from "../components/common/Input";
import ThemeToggle from "../components/common/ThemeToggle";
import { FolderPlus, ArrowLeft, Loader2 } from "lucide-react";

const CreateProject = () => {
    const [projectCode, setProjectCode] = useState("");
    const [projectName, setProjectName] = useState("");
    const [projectDescription, setProjectDescription] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const cleanCode = projectCode.trim();
        const cleanName = projectName.trim();
        
        if (!cleanCode || !cleanName) {
            setError("Vui lòng điền mã và tên dự án!");
            return;
        }

        // Kiểm tra định dạng mã dự án (A-Z, 0-9, _)
        const codeRegex = /^[A-Z0-9_]{6,10}$/;
        if (!codeRegex.test(cleanCode)) {
            setError("Mã dự án phải: 6-10 ký tự, chỉ A-Z, 0-9, _. VD: HABIT_01");
            return;
        }

        setError("");
        setLoading(true);

        try {
            const projectData = {
                project_code: cleanCode,
                name: cleanName,
                description: projectDescription || null
            };
            
            const res = await projectService.createProject(projectData);
            
            // Sau khi tạo dự án thành công, chuyển đến WBS
            navigate(`/dashboard/${cleanCode}/wbs`);

        } catch (err) {
            console.error("Lỗi tạo dự án:", err);
            const status = err.response?.status;
            const detail = err.response?.data?.detail;

            if (status === 400) {
                setError(`Lỗi: ${detail || "Mã dự án có thể đã tồn tại!"}`);
            } else if (status === 401) {
                setError("Bạn phải đăng nhập trước!");
                navigate("/login");
            } else {
                setError("Có lỗi xảy ra từ máy chủ. Vui lòng thử lại sau.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-light-bg dark:bg-dark-bg transition-colors duration-300">
            <div className="absolute top-5 right-5">
                <ThemeToggle />
            </div>

            <div className="absolute top-5 left-5">
                <button
                    onClick={() => navigate("/join-project")}
                    className="flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <ArrowLeft size={18} />
                    Quay lại
                </button>
            </div>

            <form 
                onSubmit={handleSubmit}
                className="card w-full max-w-md flex flex-col gap-6 p-10 shadow-2xl dark:shadow-gray-400"
            >
                <div className="text-center space-y-2">
                    <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <FolderPlus className="text-primary" size={32} />
                    </div>
                    <h2 className="text-2xl font-bold text-light-text dark:text-dark-text">
                        Tạo Dự Án Mới
                    </h2>
                    <p className="text-sm text-light-muted dark:text-dark-muted">
                        Tạo không gian làm việc mới cho dự án của bạn
                    </p>
                </div>

                {/* Khung hiển thị lỗi */}
                {error && (
                    <span className="bg-red-50 border border-red-200 text-red-600 w-full text-sm italic px-3 py-2 rounded-md">
                        ⚠️ {error}
                    </span>
                )}

                {/* Mã Dự Án */}
                <Input 
                    label="Mã Dự Án"
                    placeholder="Ví dụ: HABIT_01, PM_PRJ_2024..."
                    value={projectCode}
                    onChange={(e) => setProjectCode(e.target.value.toUpperCase())}
                    isRequired={true}
                    icon={<FolderPlus className="absolute top-[28%] left-[2%] text-slate-400" size={18}/>}
                />
                <p className="text-xs text-slate-500 -mt-4">
                    (6-10 ký tự: A-Z, 0-9, _)
                </p>

                {/* Tên Dự Án */}
                <Input 
                    label="Tên Dự Án"
                    placeholder="Ví dụ: Hệ Thống Quản Lý Dự Án..."
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    isRequired={true}
                />

                {/* Mô Tả Dự Án (Optional) */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                        Mô Tả (Tùy chọn)
                    </label>
                    <textarea
                        placeholder="Mô tả ngắn về dự án của bạn..."
                        value={projectDescription}
                        onChange={(e) => setProjectDescription(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary"
                        rows="3"
                    />
                </div>

                {/* Nút Tạo Dự Án */}
                <button 
                    type="submit" 
                    disabled={loading}
                    className={`btn-primary w-full flex items-center justify-center gap-2 py-3 ${loading && "opacity-60 cursor-not-allowed"}`}
                >
                    {loading ? (
                        <>
                            <Loader2 className="animate-spin" size={18} />
                            Đang tạo...
                        </>
                    ) : (
                        <>
                            <FolderPlus size={18} />
                            Tạo Dự Án
                        </>
                    )}
                </button>

                {/* Hướng dẫn */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
                    <p className="text-xs text-blue-700 dark:text-blue-300">
                        💡 <strong>Mẹo:</strong> Sau khi tạo dự án, bạn sẽ tự động trở thành Trưởng Dự Án (PM).
                    </p>
                </div>
            </form>
        </div>
    );
};

export default CreateProject;
