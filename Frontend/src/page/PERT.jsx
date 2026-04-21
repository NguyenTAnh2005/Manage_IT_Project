import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";

// Hàm tính EST: (MO + 4*ML + MP) / 6
const calculateEST = (mo, ml, mp) => {
    if (!mo || !ml || !mp) return 0;
    return ((mo + 4 * ml + mp) / 6).toFixed(2);
};

// Row cho mỗi task
const PERTRow = ({ task, allTasks, level = 0, onUpdatePERT }) => {
    const childTasks = allTasks.filter(t => t.parent_id === task.id || t.parentId === task.id);
    const hasChildren = childTasks.length > 0;
    const [isExpanded, setIsExpanded] = useState(true);
    const [formData, setFormData] = useState({
        mo: task.mo || 1,
        ml: task.ml || 2,
        mp: task.mp || 3
    });

    let displayEST;
    if (hasChildren) {
        displayEST = childTasks.reduce((sum, child) => sum + parseFloat(child.est || 0), 0).toFixed(2);
    } else {
        displayEST = calculateEST(formData.mo, formData.ml, formData.mp);
    }

    const handleChange = (field, value) => {
        const numValue = parseFloat(value) || 0;
        if (numValue < 0.5) {
            alert("Giá trị phải >= 0.5");
            return;
        }
        setFormData(prev => ({ ...prev, [field]: numValue }));
        onUpdatePERT(task.id, { ...formData, [field]: numValue, est: parseFloat(displayEST) });
    };

    return (
        <>
            <div style={{ marginLeft: `${level * 20}px`, padding: "10px", borderBottom: "1px solid #ddd", background: hasChildren ? "#f0f3ff" : "white" }}>
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
                    {hasChildren && <span style={{ fontSize: "11px", color: "#666" }}>({childTasks.length} con)</span>}
                </div>
                
                {!hasChildren ? (
                    <div style={{ display: "grid", gridTemplateColumns: "80px 80px 80px 100px", gap: "10px", fontSize: "13px" }}>
                        <div>
                            <label style={{ fontSize: "11px", color: "#666" }}>MO</label>
                            <input
                                type="number"
                                step="0.5"
                                min="0.5"
                                value={formData.mo}
                                onChange={(e) => handleChange("mo", e.target.value)}
                                style={{ width: "100%", padding: "4px", border: "1px solid #ddd", borderRadius: "3px", fontSize: "12px" }}
                            />
                        </div>
                        <div>
                            <label style={{ fontSize: "11px", color: "#666" }}>ML</label>
                            <input
                                type="number"
                                step="0.5"
                                min="0.5"
                                value={formData.ml}
                                onChange={(e) => handleChange("ml", e.target.value)}
                                style={{ width: "100%", padding: "4px", border: "1px solid #ddd", borderRadius: "3px", fontSize: "12px" }}
                            />
                        </div>
                        <div>
                            <label style={{ fontSize: "11px", color: "#666" }}>MP</label>
                            <input
                                type="number"
                                step="0.5"
                                min="0.5"
                                value={formData.mp}
                                onChange={(e) => handleChange("mp", e.target.value)}
                                style={{ width: "100%", padding: "4px", border: "1px solid #ddd", borderRadius: "3px", fontSize: "12px" }}
                            />
                        </div>
                        <div>
                            <label style={{ fontSize: "11px", color: "#666" }}>EST</label>
                            <div style={{ padding: "4px", fontWeight: "bold", color: "#0066cc" }}>{displayEST} ngày</div>
                        </div>
                    </div>
                ) : (
                    <div style={{ fontSize: "13px", fontWeight: "bold", color: "#0066cc" }}>
                        Tổng EST: {displayEST} ngày
                    </div>
                )}
            </div>

            {isExpanded && hasChildren && (
                childTasks.map(child => (
                    <PERTRow
                        key={child.id}
                        task={child}
                        allTasks={allTasks}
                        level={level + 1}
                        onUpdatePERT={onUpdatePERT}
                    />
                ))
            )}
        </>
    );
};

const PERTCalculation = () => {
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
                const taskList = response.tasks || response;
                setTasks(taskList.map(t => ({
                    ...t,
                    mo: t.mo || 1,
                    ml: t.ml || 2,
                    mp: t.mp || 3,
                    est: calculateEST(t.mo || 1, t.ml || 2, t.mp || 3)
                })));
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
    const totalEST = tasks.reduce((sum, task) => sum + parseFloat(task.est || 0), 0);

    const taskVariances = tasks.map(task => {
        if (!task.mo || !task.ml || !task.mp) return 0;
        return Math.pow((task.mp - task.mo) / 6, 2);
    });
    const totalVariance = taskVariances.reduce((sum, v) => sum + v, 0);
    const standardDeviation = Math.sqrt(totalVariance);

    const confidenceInterval68 = {
        low: (totalEST - standardDeviation).toFixed(2),
        high: (totalEST + standardDeviation).toFixed(2)
    };

    const confidenceInterval95 = {
        low: (totalEST - 2 * standardDeviation).toFixed(2),
        high: (totalEST + 2 * standardDeviation).toFixed(2)
    };

    const handleUpdatePERT = (taskId, newData) => {
        setTasks(tasks.map(t =>
            t.id === taskId
                ? { ...t, mo: newData.mo, ml: newData.ml, mp: newData.mp, est: newData.est }
                : t
        ));
    };

    if (loading) return <div style={{ padding: "20px" }}>Đang tải...</div>;
    if (error) return <div style={{ padding: "20px", color: "red" }}>Lỗi: {error}</div>;

    return (
        <div style={{ padding: "20px" }}>
            <h2>Ước Lượng Thời Gian PERT</h2>
            <p>Dự án: {projectCode}</p>

            <div style={{ marginTop: "20px", padding: "15px", background: "#f0f3ff", border: "1px solid #ddd", borderRadius: "4px", marginBottom: "20px" }}>
                <strong>Công thức PERT:</strong>
                <div style={{ marginTop: "8px", fontSize: "14px", fontFamily: "monospace" }}>
                    EST = (MO + 4×ML + MP) / 6
                </div>
                <div style={{ marginTop: "10px", fontSize: "13px", color: "#666" }}>
                    <div>• MO: Thời gian lạc quan (tốt nhất)</div>
                    <div>• ML: Thời gian khả dĩ (nhiều khả năng)</div>
                    <div>• MP: Thời gian bi quan (xấu nhất)</div>
                    <div>• EST: Thời gian ước lượng (Kỳ vọng)</div>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", marginBottom: "20px" }}>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>Tổng EST</div>
                    <div style={{ fontSize: "20px", fontWeight: "bold", color: "#0066cc" }}>{totalEST.toFixed(1)} ngày</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>Độ Lệch Chuẩn</div>
                    <div style={{ fontSize: "20px", fontWeight: "bold", color: "#ff9900" }}>±{standardDeviation.toFixed(2)} ngày</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>68% Tin Cây</div>
                    <div style={{ fontSize: "14px", fontWeight: "bold", color: "#009900" }}>{confidenceInterval68.low} - {confidenceInterval68.high}</div>
                </div>
                <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "5px" }}>95% Tin Cây</div>
                    <div style={{ fontSize: "14px", fontWeight: "bold", color: "#cc0000" }}>{confidenceInterval95.low} - {confidenceInterval95.high}</div>
                </div>
            </div>

            <h3 style={{ marginTop: "20px", marginBottom: "15px" }}>Tính Toán PERT Cho Từng Công Việc</h3>
            <div style={{ border: "1px solid #ddd", borderRadius: "4px" }}>
                {rootTasks.length > 0 ? (
                    rootTasks.map(task => (
                        <PERTRow
                            key={task.id}
                            task={task}
                            allTasks={tasks}
                            level={0}
                            onUpdatePERT={handleUpdatePERT}
                        />
                    ))
                ) : (
                    <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>Chưa có công việc nào</div>
                )}
            </div>

            <div style={{ marginTop: "20px", padding: "15px", background: "#e8f5e9", border: "1px solid #4caf50", borderRadius: "4px", color: "#2e7d32" }}>
                💡 <strong>Mẹo:</strong> Nhập các giá trị lạc quan (MO), khả dĩ (ML) và bi quan (MP) cho mỗi công việc. Hệ thống sẽ tự động tính EST.
            </div>
        </div>
    );
};

export default PERTCalculation;
