import { Outlet, NavLink, useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { 
    ListTree, 
    KanbanSquare, 
    GanttChartSquare, 
    BadgeDollarSign, 
    LogOut, 
    Settings,
    Calculator,
    Menu,   // MỚI: Icon menu hamburger cho mobile
    X       // MỚI: Icon nút đóng
} from "lucide-react";
import ThemeToggle from "../common/ThemeToggle";
import { useAuth } from "../../context/AuthContext";
import { getCurrentUser, getUserRoleInProject } from "../../services/userService";
import { projectService } from "../../services/projectService";

// ==========================================
// COMPONENT SIDEBAR (THANH ĐIỀU HƯỚNG BÊN TRÁI)
// ==========================================
// Nhận thêm prop `onClose` để đóng sidebar trên mobile
const Sidebar = ({ onClose }) => {
    const { projectCode } = useParams();
    const navigate = useNavigate();
    const { outProject } = useAuth();
    const [user, setUser] = useState(null);
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Load user info và role
    useEffect(() => {
        const loadUserInfo = async () => {
            try {
                setLoading(true);
                setError(null);

                const currentUser = await getCurrentUser();
                setUser(currentUser);

                if (projectCode) {
                    const projectsResponse = await projectService.getMyProjects();
                    const project = projectsResponse.projects.find(p => p.project_code === projectCode);
                    
                    if (project) {
                        const userRole = await getUserRoleInProject(project.id);
                        setRole(userRole);
                    }
                }
            } catch (err) {
                console.error("Lỗi khi load thông tin user:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        loadUserInfo();
    }, [projectCode]);

    const navLinks = [
        { path: "wbs", name: "Bảng WBS", icon: <ListTree size={20} /> },
        { path: "kanban", name: "Bảng Kanban", icon: <KanbanSquare size={20} /> },
        { path: "gantt", name: "Biểu đồ Gantt", icon: <GanttChartSquare size={20} /> },
        { path: "cost", name: "Quản lý Chi phí", icon: <BadgeDollarSign size={20} /> },
        { path: "pert", name: "Tính PERT", icon: <Calculator size={20} /> },
    ];

    const handleExitProject = () => {
        outProject();
        navigate('/join-project');
    };

    const getInitials = (fullName) => {
        if (!fullName) return "?";
        return fullName.split(" ").map(word => word[0]).join("").toUpperCase().slice(0, 2);
    };

    return (
        <div className="w-64 h-full bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-colors duration-300 shadow-xl md:shadow-none">
            
            {/* 1. KHU VỰC TÊN DỰ ÁN (TOP) */}
            <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                <div className="min-w-0 flex-1">
                    <h1 className="text-xl font-bold text-slate-800 dark:text-white uppercase truncate">
                        {projectCode}
                    </h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        Trưởng dự án: {role === "PM" ? "Bạn" : "Khác"}
                    </p>
                </div>
                {/* Nút đóng Sidebar trên mobile */}
                <button 
                    onClick={onClose}
                    className="md:hidden p-1.5 text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <X size={20} />
                </button>
            </div>

            {/* 2. KHU VỰC MENU ĐIỀU HƯỚNG (MIDDLE) */}
            <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                {navLinks.map((link) => (
                    <NavLink
                        key={link.path}
                        to={link.path}
                        onClick={onClose} // MỚI: Bấm vào link thì tự động đóng menu trên mobile
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                                isActive
                                    ? "bg-blue-600 text-white shadow-md"
                                    : "text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800"
                            }`
                        }
                    >
                        {link.icon}
                        {link.name}
                    </NavLink>
                ))}
            </div>

            {/* 3. KHU VỰC BOTTOM (CHỨC NĂNG & PROFILE) */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
                <div className="flex flex-col gap-2">
                    <ThemeToggle />
                    <button 
                        onClick={handleExitProject}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-lg font-medium transition-colors"
                    >
                        <LogOut size={18} />
                        Thoát dự án
                    </button>
                </div>

                <div className="flex items-center gap-3 p-2 bg-slate-100 dark:bg-slate-800 rounded-xl">
                    <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold flex-shrink-0">
                        {loading ? "..." : getInitials(user?.full_name)}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-800 dark:text-white truncate">
                            {loading ? "Đang tải..." : user?.full_name || "User"}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                            {loading ? "-" : (role || "MEMBER")}
                        </p>
                    </div>
                    <button className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                        <Settings size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

// ==========================================
// LAYOUT TỔNG
// ==========================================
export const DashBoardLayout = () => {
    // State quản lý việc đóng/mở sidebar trên mobile
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <div className="flex h-screen bg-slate-100 dark:bg-slate-950 transition-colors duration-300 overflow-hidden">
            
            {/* LỚP MỜ (OVERLAY) CHO MOBILE */}
            {isSidebarOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* KHU VỰC SIDEBAR (FIXED TRÊN MOBILE, RELATIVE TRÊN PC) */}
            <div 
                className={`fixed inset-y-0 left-0 z-50 transform ${
                    isSidebarOpen ? "translate-x-0" : "-translate-x-full"
                } md:relative md:translate-x-0 transition-transform duration-300 ease-in-out h-full`}
            >
                <Sidebar onClose={() => setIsSidebarOpen(false)} />
            </div>

            {/* KHU VỰC NỘI DUNG CHÍNH (RIGHT SIDE) */}
            <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
                
                {/* HEADER RIÊNG CHO MOBILE (Chỉ hiện khi màn hình nhỏ) */}
                <div className="md:hidden flex items-center justify-between p-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm">
                    <div className="flex items-center gap-3">
                        <button 
                            onClick={() => setIsSidebarOpen(true)}
                            className="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                        >
                            <Menu size={24} />
                        </button>
                        <h1 className="text-lg font-bold text-slate-800 dark:text-white truncate uppercase">
                            Dự án WBS
                        </h1>
                    </div>
                </div>

                {/* CONTENT ĐỔ RA Ở ĐÂY */}
                <main className="flex-1 p-4 md:p-6 overflow-auto bg-slate-50 dark:bg-slate-950">
                    <div className="mx-auto max-w-7xl">
                        <Outlet />
                    </div>
                </main>
            </div>
            
        </div>
    );
};

export default DashBoardLayout;