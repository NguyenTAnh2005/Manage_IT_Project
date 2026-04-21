import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";
import { getUserRoleInProject } from "../services/userService";
import { showError, showInfo } from "../utils/toast";


// Hàm tính số ngày
const calculateDays = (startDate, endDate) => {
    if (!startDate || !endDate) return 0;
    const start = new Date(startDate);
    const end = new Date(endDate);
    return Math.ceil((end - start) / (1000 * 60 * 60 * 24));
};

const WbsRow = ({ task, allTasks, level = 0 }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const childTasks = allTasks.filter(t => t.parent_id === task.id || t.parentId === task.id);
    const hasChildren = childTasks.length > 0;
    const duration = calculateDays(task.start_date || task.startDate, task.end_date || task.endDate);

    return (
        <>
            <div style={{ marginLeft: `${level * 20}px`, padding: "10px", borderBottom: "1px solid #ddd" }}>
                <div>
                    {hasChildren && (
                        <button 
                            onClick={() => setIsExpanded(!isExpanded)}
                            style={{ marginRight: "10px", cursor: "pointer", background: "none", border: "none", fontSize: "12px" }}
                        >
                            {isExpanded ? "▼" : "▶"}
                        </button>
                    )}
                    <strong>{task.name}</strong>
                </div>
                <div style={{ marginTop: "5px", fontSize: "13px", color: "#666" }}>
                    Người làm: {task.assignee || "Chưa gán"} | 
                    Trạng thái: {task.status || "TODO"} | 
                    Thời gian: {duration} ngày | 
                    Ưu tiên: {task.priority || "Normal"}
                </div>
            </div>

            {isExpanded && hasChildren && (
                childTasks.map(child => (
                    <WbsRow key={child.id} task={child} allTasks={allTasks} level={level + 1} />
                ))
            )}
        </>
    );
};
const WbsDashBoard = () => {
    const { projectCode } = useParams();
    const [tasks, setTasks] = useState([]);
    const [projectId, setProjectId] = useState(null);
    const [userRole, setUserRole] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);
                const pId = await getProjectIdByCode(projectCode);
                setProjectId(pId);
                
                const response = await taskService.getTasks(pId);
                setTasks(response.tasks || response);
                
                const role = await getUserRoleInProject(pId);
                setUserRole(role);
            } catch (err) {
                setError(err?.response?.data?.detail || err.message || "Lỗi khi tải dữ liệu");
                console.error("Lỗi:", err);
            } finally {
                setLoading(false);
            }
        };

        if (projectCode) {
            fetchData();
        }
    }, [projectCode]);

    const handleAddTask = () => {
        if (userRole !== "PM") {
            showError("Chỉ Trưởng dự án mới có thể thêm công việc");
            return;
        }
        showInfo("Chức năng thêm công việc sẽ được triển khai sớm");
    };

    const rootTasks = tasks.filter(t => !t.parent_id && !t.parentId);

    if (loading) return <div style={{ padding: "20px" }}>Đang tải dữ liệu...</div>;
    if (error) return <div style={{ padding: "20px", color: "red" }}>Lỗi: {error}</div>;

    return (
        <div style={{ padding: "20px" }}>
            <h2>Cấu Trúc Phân Rã Công Việc (WBS)</h2>
            <p>Dự án: {projectCode} | Role: {userRole}</p>
            
            <button onClick={handleAddTask} style={{ padding: "8px 16px", marginBottom: "20px", cursor: "pointer", background: "#0066cc", color: "white", border: "none", borderRadius: "4px" }}>
                + Thêm công việc
            </button>

            <div style={{ border: "1px solid #ddd", borderRadius: "4px" }}>
                {rootTasks.length > 0 ? (
                    rootTasks.map(task => (
                        <WbsRow key={task.id} task={task} allTasks={tasks} />
                    ))
                ) : (
                    <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
                        Chưa có công việc nào
                    </div>
                )}
            </div>
        </div>
    );
};
export default WbsDashBoard;