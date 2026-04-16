import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Input from "../components/common/Input";
import ThemeToggle from "../components/common/ThemeToggle";
import { LayoutGrid, ArrowRight } from "lucide-react";

const JoinProject = () => {
    const [code, setCode] = useState("");
    const { joinProject } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        if (code.trim()) {
            // Lưu mã dự án vào AuthContext (và localStorage)
            joinProject(code.trim());
            
            // Chuyển hướng thẳng vào Dashboard của dự án đó
            navigate(`/dashboard/${code.trim()}/wbs`);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-light-bg dark:bg-dark-bg transition-colors duration-300">
            {/* Nút đổi Theme ở góc màn hình */}
            <div className="absolute top-5 right-5">
                <ThemeToggle />
            </div>

            <form 
                onSubmit={handleSubmit}
                className="card w-full max-w-md flex flex-col gap-6 p-10 shadow-2xl"
            >
                <div className="text-center space-y-2">
                    <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <LayoutGrid className="text-primary" size={32} />
                    </div>
                    <h2 className="text-2xl font-bold text-light-text dark:text-dark-text">
                        Vào Không Gian Làm Việc
                    </h2>
                    <p className="text-sm text-light-muted dark:text-dark-muted">
                        Nhập mã dự án được cấp để bắt đầu quản lý công việc
                    </p>
                </div>

                <Input 
                    label="Mã dự án"
                    placeholder="Ví dụ: HABIT_01, PM_PROJ..."
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    isRequired={true}
                    icon={<LayoutGrid className="absolute top-[28%] left-[2%] text-slate-400" size={18}/>}
                />

                <button 
                    type="submit" 
                    className="btn-primary w-full flex items-center justify-center gap-2 py-3"
                >
                    Tiến vào dự án
                    <ArrowRight size={18} />
                </button>

                <p className="text-xs text-center text-light-muted dark:text-dark-muted italic">
                    * Lưu ý: Nếu chưa có mã, hãy liên hệ Trưởng dự án (PM) để được cấp quyền.
                </p>
            </form>
        </div>
    );
};

export default JoinProject;