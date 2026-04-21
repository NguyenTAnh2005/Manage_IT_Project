import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";

// Row hiển thị chi phí
const CostRow = ({ task, allTasks, level = 0, onUpdate }) => {
    const childTasks = allTasks.filter(t => t.parent_id === task.id || t.parentId === task.id);
    const hasChildren = childTasks.length > 0;
    const [isExpanded, setIsExpanded] = useState(true);

    const childrenCost = childTasks.reduce((sum, child) => sum + (child.cost_total || 0), 0);
    const totalCost = (task.cost_total || 0) + childrenCost;

    return (
        <>
            <div style={{ marginLeft: `${level * 20}px`, padding: "10px", borderBottom: "1px solid #ddd" }}>
                <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "8px" }}>
                    {hasChildren && (
                        <button 
                            onClick={() => setIsExpanded(!isExpanded)}
                            style={{ cursor: "pointer", background: "none", border: "none", fontSize: "12px" }}
                        >
                            {isExpanded ? "▼" : "▶"}
                        </button>
                    )}
                    <strong>{task.name}</strong>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "80px 150px 150px 150px", gap: "10px", fontSize: "13px" }}>
                    <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Thời gian</label>
                        <div>{task.duration} ngày</div>
                    </div>
                    <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Chi phí/ngày (₫)</label>
                        <input
                            type="number"
                            defaultValue={task.cost_total || 0}
                            onChange={(e) => onUpdate(task.id, parseFloat(e.target.value) || 0)}
                            style={{ width: "100%", padding: "4px", border: "1px solid #ddd", borderRadius: "3px", fontSize: "12px" }}
                        />
                    </div>
                    <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Tổng chi phí (₫)</label>
                        <div style={{ fontWeight: "bold", color: "#009900" }}>{totalCost.toLocaleString('vi-VN')} ₫</div>
                    </div>
                    <div>
                        <label style={{ fontSize: "11px", color: "#666" }}>Ngày x Chi phí</label>
                        <div style={{ fontWeight: "bold" }}>{(task.duration * (task.cost_total || 0)).toLocaleString('vi-VN')} ₫</div>
                    </div>
                </div>
            </div>

            {isExpanded && hasChildren && (
                childTasks.map(child => (
                    <CostRow
                        key={child.id}
                        task={child}
                        allTasks={allTasks}
                        level={level + 1}
                        onUpdate={onUpdate}
                    />
                ))
            )}
        </>
    );
};

const CostManagement = () => {
    const { projectCode } = useParams();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                setLoading(true);
                setError(null);
                const projectId = await getProjectIdByCode(projectCode);
                const response = await taskService.getTasks(projectId);
                setTasks(response.tasks || response);
            } catch (err) {
                setError(err?.response?.data?.detail || err.message || "Lỗi khi tải dữ liệu");
            } finally {
                setLoading(false);
            }
        };

        if (projectCode) {
            fetchTasks();
        }
    }, [projectCode]);

    const rootTasks = tasks.filter(t => !t.parent_id && !t.parentId);

    const totalProjectCost = tasks.reduce((sum, task) => sum + (task.cost_total || 0), 0);
    const estimatedCostByDuration = tasks.reduce((sum, task) => sum + (task.duration * (task.cost_total || 0)), 0);

    const costByStatus = {
        TODO: tasks.filter(t => t.status === "TODO").reduce((sum, t) => sum + (t.cost_total || 0), 0),
        DOING: tasks.filter(t => t.status === "DOING").reduce((sum, t) => sum + (t.cost_total || 0), 0),
        DONE: tasks.filter(t => t.status === "DONE").reduce((sum, t) => sum + (t.cost_total || 0), 0),
    };

    const costByPriority = {
        High: tasks.filter(t => t.priority === "High").reduce((sum, t) => sum + (t.cost_total || 0), 0),
        Medium: tasks.filter(t => t.priority === "Medium").reduce((sum, t) => sum + (t.cost_total || 0), 0),
        Low: tasks.filter(t => t.priority === "Low").reduce((sum, t) => sum + (t.cost_total || 0), 0),
    };

    const handleUpdateCost = (taskId, newCost) => {
        setTasks(tasks.map(t => t.id === taskId ? { ...t, cost_total: newCost } : t));
    };

    if (loading) return <div style={{ padding: "20px" }}>Đang tải...</div>;
    if (error) return <div style={{ padding: "20px", color: "red" }}>Lỗi: {error}</div>;

    return (
        <div style={{ padding: "20px" }}>
            <h2>Quản Lý Chi Phí</h2>
            <p>Dự án: {projectCode}</p>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", marginTop: "20px", marginBottom: "20px" }}>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>Tổng Chi Phí</div>
                    <div style={{ fontSize: "20px", fontWeight: "bold", color: "#009900" }}>{(totalProjectCost / 1000000).toFixed(1)}M ₫</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>Chi Phí Ước Lượng</div>
                    <div style={{ fontSize: "20px", fontWeight: "bold", color: "#0066cc" }}>{(estimatedCostByDuration / 1000000).toFixed(1)}M ₫</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>Tổng Công Việc</div>
                    <div style={{ fontSize: "20px", fontWeight: "bold", color: "#cc0066" }}>{tasks.length}</div>
                </div>
            </div>

            <h3 style={{ marginTop: "20px", marginBottom: "15px" }}>Chi Phí Theo Trạng Thái</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "15px", marginBottom: "20px" }}>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>TO DO</div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#cc9900" }}>{(costByStatus.TODO / 1000000).toFixed(2)}M ₫</div>
                    <div style={{ fontSize: "11px", color: "#999", marginTop: "5px" }}>{tasks.filter(t => t.status === "TODO").length} công việc</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>DOING</div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#0066cc" }}>{(costByStatus.DOING / 1000000).toFixed(2)}M ₫</div>
                    <div style={{ fontSize: "11px", color: "#999", marginTop: "5px" }}>{tasks.filter(t => t.status === "DOING").length} công việc</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>DONE</div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#009900" }}>{(costByStatus.DONE / 1000000).toFixed(2)}M ₫</div>
                    <div style={{ fontSize: "11px", color: "#999", marginTop: "5px" }}>{tasks.filter(t => t.status === "DONE").length} công việc</div>
                </div>
            </div>

            <h3 style={{ marginTop: "20px", marginBottom: "15px" }}>Chi Phí Theo Ưu Tiên</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "15px", marginBottom: "20px" }}>
                <div style={{ padding: "15px", border: "1px solid #ff6666", borderRadius: "4px", background: "#ffe6e6" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>🔴 Cao</div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#cc0000" }}>{(costByPriority.High / 1000000).toFixed(2)}M ₫</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ffcc66", borderRadius: "4px", background: "#fff5e6" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>🟡 Trung bình</div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#cc9900" }}>{(costByPriority.Medium / 1000000).toFixed(2)}M ₫</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #66cc66", borderRadius: "4px", background: "#e6ffe6" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>🟢 Thấp</div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#009900" }}>{(costByPriority.Low / 1000000).toFixed(2)}M ₫</div>
                </div>
            </div>

            <h3 style={{ marginTop: "20px", marginBottom: "15px" }}>Chi Phí Theo Công Việc</h3>
            <div style={{ border: "1px solid #ddd", borderRadius: "4px" }}>
                {rootTasks.length > 0 ? (
                    rootTasks.map(task => (
                        <CostRow key={task.id} task={task} allTasks={tasks} level={0} onUpdate={handleUpdateCost} />
                    ))
                ) : (
                    <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>Chưa có công việc nào</div>
                )}
            </div>

            <div style={{ marginTop: "20px", padding: "15px", background: "#fff8e6", border: "1px solid #ffcc99", borderRadius: "4px", color: "#cc8800" }}>
                💡 <strong>Mẹo:</strong> Nhập chi phí ước lượng cho mỗi công việc. Tổng chi phí ước lượng được tính bằng chi phí × số ngày.
            </div>
        </div>
    );
};

export default CostManagement;
