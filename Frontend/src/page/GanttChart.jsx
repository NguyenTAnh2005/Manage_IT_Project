import { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { Spin, Alert, Empty, Radio, Tag, Card, Table } from "antd";
import { Gantt, ViewMode } from "gantt-task-react";
import "gantt-task-react/dist/index.css";

import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";

const GanttChart = () => {
    const { projectCode } = useParams();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState(ViewMode.Day);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                setLoading(true);
                const projectId = await getProjectIdByCode(projectCode);
                if (projectId) {
                    const res = await taskService.getTasks(projectId);
                    const rawData = res.tasks || res || [];
                    setTasks(rawData);
                }
            } catch (err) {
                console.error("Lỗi:", err);
            } finally {
                setLoading(false);
            }
        };
        if (projectCode) fetchTasks();
    }, [projectCode]);

    const tableColumns = [
        { title: 'Tên công việc', dataIndex: 'name', key: 'name', render: (text) => <strong>{text}</strong> },
        { title: 'Bắt đầu', dataIndex: 'start_date', key: 'start_date', width: 120 },
        { title: 'Kết thúc', dataIndex: 'end_date', key: 'end_date', width: 120 },
        { 
            title: 'Trạng thái', 
            dataIndex: 'status', 
            key: 'status',
            width: 120,
            render: (s) => <Tag color={s === 'DONE' ? 'green' : 'blue'}>{s}</Tag>
        },
    ];

    const tasksWithDates = useMemo(() => tasks.filter(t => t.start_date && t.end_date), [tasks]);

    const ganttTasks = useMemo(() => {
        return tasksWithDates.map(t => ({
            id: t.id.toString(),
            name: t.name,
            start: new Date(t.start_date),
            end: new Date(t.end_date),
            progress: t.status === "DONE" ? 100 : (t.status === "DOING" ? 50 : 0),
            type: tasks.some(child => child.parent_id === t.id) ? "project" : "task",
            project: t.parent_id?.toString(),
            styles: { progressColor: "#1890ff", progressSelectedColor: "#0050b3" }
        }));
    }, [tasksWithDates, tasks]);

    if (loading) return <div className="p-20 text-center"><Spin size="large" tip="Đang tải..." /></div>;

    return (
        <div className="p-4 bg-slate-50 min-h-screen">
            {/* BẢNG THÔNG TIN CÓ HEADER GHIM (STICKY) */}
            <Card title={`Lịch trình chi tiết: ${projectCode}`} variant="outlined" className="mb-4 shadow-sm">
                <Table 
                    dataSource={tasksWithDates} 
                    columns={tableColumns} 
                    rowKey="id" 
                    pagination={false}
                    // ✅ GHIM HEADER LẠI ĐÂY SẾP ƠI
                    sticky={true} 
                    size="middle"
                    className="border rounded"
                />
            </Card>

            {/* BIỂU ĐỒ GANTT CÓ THANH CUỘN BÊN TRÊN */}
            <Card 
                title="Biểu đồ Gantt (Cuộn ngang ở trên)" 
                variant="outlined"
                extra={
                    <Radio.Group value={viewMode} onChange={e => setViewMode(e.target.value)} size="small" buttonStyle="solid">
                        <Radio.Button value={ViewMode.Day}>Ngày</Radio.Button>
                        <Radio.Button value={ViewMode.Week}>Tuần</Radio.Button>
                        <Radio.Button value={ViewMode.Month}>Tháng</Radio.Button>
                    </Radio.Group>
                }
            >
                {ganttTasks.length > 0 ? (
                    <div className="gantt-top-scroll-container">
                        <div className="gantt-flip-back">
                            <Gantt
                                tasks={ganttTasks}
                                viewMode={viewMode}
                                locale="vi"
                                listCellWidth="" // Xóa sổ cột danh sách
                                TaskListHeader={() => null}
                                TaskListTable={() => null}
                                columnWidth={viewMode === ViewMode.Month ? 150 : 70}
                                rowHeight={45}
                            />
                        </div>
                    </div>
                ) : (
                    <Empty description="Thiếu dữ liệu thời gian" />
                )}
            </Card>

            <style>{`
                /* Kỹ thuật lật ngược Container để ép scrollbar lên đầu */
                .gantt-top-scroll-container {
                    overflow-x: auto;
                    transform: rotateX(180deg); 
                    border: 1px solid #f0f0f0;
                }
                .gantt-flip-back {
                    transform: rotateX(180deg);
                }

                /* Custom thanh cuộn nhìn cho nó pro */
                .gantt-top-scroll-container::-webkit-scrollbar { height: 10px; }
                .gantt-top-scroll-container::-webkit-scrollbar-track { background: #f8fafc; }
                .gantt-top-scroll-container::-webkit-scrollbar-thumb { 
                    background: #cbd5e1; 
                    border-radius: 5px;
                    border: 2px solid #f8fafc;
                }
                .gantt-top-scroll-container::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

                /* Ẩn triệt để list bên trái của Gantt */
                .gantt-task-react-list { display: none !important; }
            `}</style>
        </div>
    );
};

export default GanttChart;