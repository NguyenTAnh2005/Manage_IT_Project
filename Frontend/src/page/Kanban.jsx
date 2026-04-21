import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";

// Card hiển thị task
const KanbanCard = ({ task, onDelete, onEdit, onChangeStatus, currentStatus }) => {
    const canMovePrev = currentStatus !== "TODO";
    const canMoveNext = currentStatus !== "DONE";

    const handlePrevStatus = () => {
        const statusMap = { DOING: "TODO", DONE: "DOING" };
        onChangeStatus(task.id, statusMap[currentStatus]);
    };

    const handleNextStatus = () => {
        const statusMap = { TODO: "DOING", DOING: "DONE" };
        onChangeStatus(task.id, statusMap[currentStatus]);
    };

    return (
        <div style={{ border: "1px solid #ddd", padding: "10px", marginBottom: "10px", borderRadius: "4px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <strong>{task.name}</strong>
                <div>
                    <button onClick={() => onEdit(task)} style={{ marginRight: "5px", cursor: "pointer" }}>✏️</button>
                    <button onClick={() => onDelete(task.id)} style={{ cursor: "pointer" }}>🗑️</button>
                </div>
            </div>
            <div style={{ fontSize: "13px", color: "#666", marginBottom: "8px" }}>
                Người làm: {task.assignee || "Chưa gán"} | Thời gian: {task.duration}d | Ưu tiên: {task.priority}
            </div>
            <div style={{ display: "flex", gap: "5px" }}>
                {canMovePrev && (
                    <button onClick={handlePrevStatus} style={{ padding: "5px 10px", fontSize: "12px", cursor: "pointer" }}>← Lùi</button>
                )}
                {canMoveNext && (
                    <button onClick={handleNextStatus} style={{ padding: "5px 10px", fontSize: "12px", cursor: "pointer", background: "#0066cc", color: "white", border: "none", borderRadius: "3px" }}>Tiến →</button>
                )}
            </div>
        </div>
    );
};

// Column hiển thị task theo status
const KanbanColumn = ({ title, status, tasks, onDelete, onEdit, onAddTask, onChangeStatus }) => {
    return (
        <div style={{ flex: 1, minWidth: "250px", border: "1px solid #ddd", borderRadius: "4px", padding: "15px" }}>
            <div style={{ marginBottom: "15px" }}>
                <h3 style={{ fontSize: "16px", fontWeight: "bold", margin: "0 0 5px 0" }}>{title}</h3>
                <p style={{ fontSize: "12px", color: "#666", margin: 0 }}>{tasks.length} công việc</p>
            </div>

            <div style={{ maxHeight: "500px", overflowY: "auto" }}>
                {tasks.length > 0 ? (
                    tasks.map((task) => (
                        <KanbanCard
                            key={task.id}
                            task={task}
                            onDelete={onDelete}
                            onEdit={onEdit}
                            onChangeStatus={onChangeStatus}
                            currentStatus={status}
                        />
                    ))
                ) : (
                    <div style={{ padding: "20px", textAlign: "center", color: "#999", fontSize: "12px" }}>Chưa có công việc</div>
                )}
            </div>

            <button
                onClick={() => onAddTask(status)}
                style={{ width: "100%", marginTop: "10px", padding: "8px", border: "1px dashed #ddd", borderRadius: "4px", background: "#f9f9f9", cursor: "pointer", fontSize: "12px" }}
            >
                + Thêm công việc
            </button>
        </div>
    );
};

const KanbanBoard = () => {
    const { projectCode } = useParams();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedTask, setSelectedTask] = useState(null);
    const [showModal, setShowModal] = useState(false);

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

    const todoTasks = tasks.filter(t => t.status === "TODO" && !t.parent_id);
    const doingTasks = tasks.filter(t => t.status === "DOING" && !t.parent_id);
    const doneTasks = tasks.filter(t => t.status === "DONE" && !t.parent_id);

    if (loading) return <div style={{ padding: "20px" }}>Đang tải...</div>;
    if (error) return <div style={{ padding: "20px", color: "red" }}>Lỗi: {error}</div>;

    const handleDeleteTask = (taskId) => {
        if (confirm("Bạn chắc chắn muốn xóa?")) {
            setTasks(tasks.filter(t => t.id !== taskId));
        }
    };

    const handleEditTask = (task) => {
        setSelectedTask(task);
        setShowModal(true);
    };

    const handleAddTask = (status) => {
        setSelectedTask({ status, id: null });
        setShowModal(true);
    };

    const handleChangeStatus = (taskId, newStatus) => {
        setTasks(tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    };

    const handleSaveTask = (taskData) => {
        if (selectedTask?.id) {
            setTasks(tasks.map(t => t.id === selectedTask.id ? { ...t, ...taskData } : t));
        } else {
            const newTask = { id: `T${Date.now()}`, ...taskData, parent_id: null };
            setTasks([...tasks, newTask]);
        }
        setShowModal(false);
        setSelectedTask(null);
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Bảng Kanban</h2>
            <p>Dự án: {projectCode}</p>

            <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
                <KanbanColumn
                    title="TO DO"
                    status="TODO"
                    tasks={todoTasks}
                    onDelete={handleDeleteTask}
                    onEdit={handleEditTask}
                    onAddTask={handleAddTask}
                    onChangeStatus={handleChangeStatus}
                />

                <KanbanColumn
                    title="DOING"
                    status="DOING"
                    tasks={doingTasks}
                    onDelete={handleDeleteTask}
                    onEdit={handleEditTask}
                    onAddTask={handleAddTask}
                    onChangeStatus={handleChangeStatus}
                />

                <KanbanColumn
                    title="DONE"
                    status="DONE"
                    tasks={doneTasks}
                    onDelete={handleDeleteTask}
                    onEdit={handleEditTask}
                    onAddTask={handleAddTask}
                    onChangeStatus={handleChangeStatus}
                />
            </div>

            {showModal && (
                <TaskModal
                    task={selectedTask}
                    onSave={handleSaveTask}
                    onClose={() => {
                        setShowModal(false);
                        setSelectedTask(null);
                    }}
                />
            )}
        </div>
    );
};

// Modal Component
const TaskModal = ({ task, onSave, onClose }) => {
    const [formData, setFormData] = useState(
        task || {
            name: "",
            assignee: "",
            priority: "Medium",
            duration: 1
        }
    );

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.name.trim()) {
            alert("Vui lòng nhập tên công việc!");
            return;
        }
        onSave(formData);
    };

    return (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 50, padding: "20px" }}>
            <div style={{ background: "white", borderRadius: "8px", width: "100%", maxWidth: "400px", boxShadow: "0 10px 25px rgba(0,0,0,0.2)" }}>
                <div style={{ padding: "20px", borderBottom: "1px solid #ddd", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <h3 style={{ margin: 0, fontSize: "18px", fontWeight: "bold" }}>
                        {task?.id ? "Chỉnh sửa" : "Thêm"} Công Việc
                    </h3>
                    <button onClick={onClose} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>✕</button>
                </div>

                <form onSubmit={handleSubmit} style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "15px" }}>
                    <div>
                        <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "5px" }}>Tên Công Việc *</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Nhập tên công việc..."
                            style={{ width: "100%", padding: "8px", border: "1px solid #ddd", borderRadius: "4px", boxSizing: "border-box" }}
                        />
                    </div>

                    <div>
                        <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "5px" }}>Người phụ trách</label>
                        <input
                            type="text"
                            name="assignee"
                            value={formData.assignee}
                            onChange={handleChange}
                            placeholder="Nhập tên người..."
                            style={{ width: "100%", padding: "8px", border: "1px solid #ddd", borderRadius: "4px", boxSizing: "border-box" }}
                        />
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                        <div>
                            <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "5px" }}>Ưu Tiên</label>
                            <select
                                name="priority"
                                value={formData.priority}
                                onChange={handleChange}
                                style={{ width: "100%", padding: "8px", border: "1px solid #ddd", borderRadius: "4px", boxSizing: "border-box" }}
                            >
                                <option value="Low">Thấp</option>
                                <option value="Medium">Trung bình</option>
                                <option value="High">Cao</option>
                            </select>
                        </div>

                        <div>
                            <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "5px" }}>Thời Lượng (ngày)</label>
                            <input
                                type="number"
                                name="duration"
                                value={formData.duration}
                                onChange={handleChange}
                                min="1"
                                style={{ width: "100%", padding: "8px", border: "1px solid #ddd", borderRadius: "4px", boxSizing: "border-box" }}
                            />
                        </div>
                    </div>

                    <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                        <button
                            type="button"
                            onClick={onClose}
                            style={{ flex: 1, padding: "10px", border: "1px solid #ddd", borderRadius: "4px", background: "#fff", cursor: "pointer" }}
                        >
                            Hủy
                        </button>
                        <button
                            type="submit"
                            style={{ flex: 1, padding: "10px", background: "#0066cc", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}
                        >
                            Lưu
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default KanbanBoard;
