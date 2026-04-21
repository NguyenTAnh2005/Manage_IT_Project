import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";

// Hàm tính số ngày giữa 2 ngày
const getDaysBetween = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return Math.ceil((end - start) / (1000 * 60 * 60 * 24));
};

// Hàm tính vị trí bar trên timeline
const calculatePosition = (taskStart, minDate) => {
    const start = new Date(taskStart);
    const min = new Date(minDate);
    return Math.ceil((start - min) / (1000 * 60 * 60 * 24));
};

// Component hiển thị task trong Gantt
const GanttRow = ({ task, allTasks, level = 0 }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const childTasks = allTasks.filter(t => t.parent_id === task.id);
    const hasChildren = childTasks.length > 0;
    const duration = getDaysBetween(task.start_date, task.end_date);

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
                    {task.start_date} → {task.end_date} ({duration} ngày) | Trạng thái: {task.status} | Người làm: {task.assignee || "Chưa gán"}
                </div>
            </div>

            {isExpanded && hasChildren && (
                childTasks.map(child => (
                    <GanttRow key={child.id} task={child} allTasks={allTasks} level={level + 1} />
                ))
            )}
        </>
    );
};

const GanttChart = () => {
    const { projectCode } = useParams();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                setLoading(true);
                const projectId = await getProjectIdByCode(projectCode);
                if (projectId) {
                    const data = await taskService.getTasks(projectId);
                    setTasks(data || []);
                }
            } catch (err) {
                setError(err.message);
                setTasks([]);
            } finally {
                setLoading(false);
            }
        };

        if (projectCode) {
            fetchTasks();
        }
    }, [projectCode]);

    if (loading) return <div style={{ padding: "20px" }}>Đang tải...</div>;
    if (error) return <div style={{ padding: "20px", color: "red" }}>Lỗi: {error}</div>;
    if (!tasks.length) return <div style={{ padding: "20px", color: "#666" }}>Chưa có công việc nào</div>;

    const rootTasks = tasks.filter(t => !t.parent_id);
    const startDateMin = new Date(Math.min(...tasks.map(t => new Date(t.start_date))));
    const endDateMax = new Date(Math.max(...tasks.map(t => new Date(t.end_date))));

    return (
        <div style={{ padding: "20px" }}>
            <h2>Biểu Đồ Gantt</h2>
            <p>Dự án: {projectCode}</p>
            <p>Thời gian: {startDateMin.toLocaleDateString('vi-VN')} → {endDateMax.toLocaleDateString('vi-VN')} ({getDaysBetween(startDateMin, endDateMax)} ngày)</p>
            
            <div style={{ border: "1px solid #ddd", borderRadius: "4px", marginTop: "20px" }}>
                {rootTasks.map(task => (
                    <GanttRow key={task.id} task={task} allTasks={tasks} />
                ))}
            </div>
        </div>
    );
};

export default GanttChart;
