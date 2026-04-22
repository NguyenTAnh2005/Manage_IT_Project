// Frontend/src/page/CreateProject.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { projectService } from "../services/projectService";
import Input from "../components/common/Input";
import ThemeToggle from "../components/common/ThemeToggle";
import { ArrowLeft, Loader2, Rocket, Hash, Type, AlignLeft } from "lucide-react";

const CreateProject = () => {
    const navigate = useNavigate();
    const { joinProject } = useAuth();
    
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    
    const [formData, setFormData] = useState({
        project_code: "",
        name: "",
        description: ""
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name === "project_code") {
            // Chỉ cho phép A-Z, 0-9, underscore - tự động convert thành uppercase
            const cleanValue = value
                .toUpperCase()
                .replace(/[^A-Z0-9_]/g, "")
                .slice(0, 10); // Giới hạn 10 ký tự
            setFormData(prev => ({ ...prev, [name]: cleanValue }));
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        // Validate độ dài
        if (formData.project_code.length < 6 || formData.project_code.length > 10) {
            setError("Mã dự án phải từ 6 đến 10 ký tự.");
            return;
        }
        // Validate tên dự án
        if (formData.name.trim().length < 3) {
            setError("Tên dự án phải có ít nhất 3 ký tự.");
            return;
        }

        setLoading(true);
        try {
            // Gọi API tạo dự án (Backend sẽ tự set người tạo làm PM)
            await projectService.createProject({
                project_code: formData.project_code,
                name: formData.name.trim(),
                description: formData.description.trim()
            });

            // Lưu project_code vào context để ProtectedRoute cho phép vào
            joinProject(formData.project_code);
            
            // Chuyển vào Dashboard WBS
            navigate(`/dashboard/${formData.project_code}/wbs`);

        } catch (err) {
            const status = err.response?.status;
            const data = err.response?.data;

            // Handle lỗi theo status code
            if (status === 400) {
                setError("Mã dự án này đã tồn tại. Vui lòng chọn mã khác!");
            } else if (status === 422) {
                setError("Dữ liệu không hợp lệ. Kiểm tra lại mã hoặc tên dự án.");
            } else {
                setError(data?.detail || "Lỗi máy chủ. Không thể tạo dự án lúc này.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-light-bg dark:bg-dark-bg transition-colors duration-300 p-4">
            <div className="absolute top-5 right-5 flex gap-2">
                <ThemeToggle />
            </div>

            <div className="w-full max-w-lg">
                <form 
                    onSubmit={handleSubmit}
                    className="card flex flex-col gap-6 p-8 sm:p-10 shadow-2xl dark:shadow-gray-400 bg-white dark:bg-slate-800 rounded-2xl"
                >
                    <div className="flex items-center gap-4 mb-2">
                        <button 
                            type="button" 
                            onClick={() => navigate("/join-project")}
                            className="p-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 rounded-full transition-colors"
                        >
                            <ArrowLeft className="text-slate-600 dark:text-slate-300" size={20} />
                        </button>
                        <div>
                            <h2 className="text-2xl font-bold text-light-text dark:text-dark-text flex items-center gap-2">
                                <Rocket className="text-green-500" /> Khởi tạo Dự Án
                            </h2>
                            <p className="text-sm text-slate-500 dark:text-slate-400">Trở thành Trưởng dự án (PM) ngay hôm nay</p>
                        </div>
                    </div>

                    {error && (
                        <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-md">
                            <p className="text-sm text-red-600 font-medium">{error}</p>
                        </div>
                    )}

                    <div className="space-y-5">
                        <div className="relative">
                            <Input 
                                label="Mã Dự Án (Project Code)"
                                name="project_code"
                                placeholder="VD: BDU_APP_01"
                                value={formData.project_code}
                                onChange={handleChange}
                                isRequired={true}
                                icon={<Hash className="absolute top-[28%] left-[3%] text-slate-400" size={18} />}
                            />
                            <p className="text-xs text-slate-500 mt-1 italic">
                                * 6-10 ký tự, viết hoa, không dấu, không khoảng trắng. Mọi người sẽ dùng mã này để tham gia.
                            </p>
                        </div>

                        <Input 
                            label="Tên Dự Án"
                            name="name"
                            placeholder="VD: App Quản Lý Thói Quen"
                            value={formData.name}
                            onChange={handleChange}
                            isRequired={true}
                            icon={<Type className="absolute top-[28%] left-[3%] text-slate-400" size={18} />}
                        />

                        <div className="flex flex-col gap-1 relative">
                            <label className="text-sm font-semibold text-slate-700 dark:text-slate-200">Mô tả (Tùy chọn)</label>
                            <AlignLeft className="absolute top-[38%] left-[3%] text-slate-400" size={18} />
                            <textarea 
                                name="description"
                                rows="3"
                                placeholder="Mục tiêu dự án này là gì..."
                                value={formData.description}
                                onChange={handleChange}
                                className="pl-10 pr-4 py-2 border rounded-lg outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 bg-transparent text-light-text dark:text-dark-text border-slate-300 dark:border-slate-600 resize-none"
                            />
                        </div>
                    </div>

                    <button 
                        type="submit" 
                        disabled={loading}
                        className={`btn-primary w-full flex items-center justify-center gap-2 py-3 mt-4 bg-green-600 hover:bg-green-700 active:bg-green-800 text-white rounded-lg font-bold transition-all ${loading && 'opacity-60 cursor-not-allowed'}`}
                    >
                        {loading ? (
                            <><Loader2 className="animate-spin" size={18} /> Đang khởi tạo...</>
                        ) : (
                            <><Rocket size={18} /> Hoàn tất & Vào trang quản lý</>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreateProject;