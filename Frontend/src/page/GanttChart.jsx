import { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { Spin, Alert, Empty, Radio, Tag, Card, Table, Button, Modal, DatePicker } from "antd";
import { EditOutlined } from "@ant-design/icons";
import { Gantt, ViewMode } from "gantt-task-react";
import "gantt-task-react/dist/index.css";
import dayjs from "dayjs";

import { taskService } from "../services/taskService";
import { getProjectIdByCode } from "../services/projectHelper";
import axiosInstance from "../services/axiosConfig";
import { showSuccess, showError } from "../utils/toast";

const { RangePicker } = DatePicker;

/**
 * GanttChart - Trực quan hóa lịch trình của các công việc.
 * Tính năng:
 * - Hiển thị công việc trên biểu đồ Gantt tương tác
 * - PM có thể kéo-thả để thay đổi ngày trực tiếp trên Gantt
 * - Tất cả người dùng có thể xem lịch trình
 * - View bảng để xem chi tiết và sửa ngày nhanh chóng
 */
const GanttChart = () => {
    const { projectCode } = useParams();
    const [tasks, setTasks] = useState([]);
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState(ViewMode.Day);

    // State cho Modal sửa ngày
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [selectedDates, setSelectedDates] = useState(null);
    const [submitLoading, setSubmitLoading] = useState(false);

    const fetchTasks = async () => {
        try {
            setLoading(true);
            const projectId = await getProjectIdByCode(projectCode);
            if (!projectId) {
                showError("Không tìm thấy dự án");
                return;
            }

            // Lấy quyền của user hiện tại
            const roleRes = await axiosInstance.get(`/projects/${projectId}/my-role`);
            setRole(roleRes.data.role);

            // Lấy danh sách công việc cho lịch trình
            const res = await taskService.getTasks(projectId);
            setTasks(res.tasks || res || []);
        } catch (err) {
            showError(err?.response?.data?.detail || err.message || "Lỗi tải dữ liệu lịch trình");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (projectCode) fetchTasks();
    }, [projectCode]);

    // Mở Modal để sửa ngày công việc
    const openEditModal = (task) => {
        setEditingTask(task);
        if (task.start_date && task.end_date) {
            setSelectedDates([dayjs(task.start_date), dayjs(task.end_date)]);
        } else {
            setSelectedDates(null);
        }
        setIsModalOpen(true);
    };

    // Lưu thay đổi ngày về backend
    const handleSaveDates = async () => {
        if (!selectedDates || !selectedDates[0] || !selectedDates[1]) {
            return showError("Vui lòng chọn đầy đủ Ngày bắt đầu và Kết thúc");
        }
        // Kiểm tra: ngày bắt đầu phải <= ngày kết thúc
        if (selectedDates[0].isAfter(selectedDates[1])) {
            return showError("Ngày bắt đầu không được sau ngày kết thúc");
        }
        try {
            setSubmitLoading(true);
            await taskService.updateTask(editingTask.id, {
                start_date: selectedDates[0].format('YYYY-MM-DD'),
                end_date: selectedDates[1].format('YYYY-MM-DD')
            });
            showSuccess("Cập nhật lịch trình thành công!");
            setIsModalOpen(false);
            fetchTasks();
        } catch (err) {
            showError(err?.response?.data?.detail || "Lỗi khi cập nhật");
        } finally {
            setSubmitLoading(false);
        }
    };

    // Xử lý kéo-thả thay đổi ngày trên Gantt (chỉ PM)
    const handleGanttDateChange = async (task) => {
        if (role !== "PM") {
            showError("Chỉ Trưởng dự án (PM) mới được dời lịch công việc");
            return;
        }
        try {
            await taskService.updateTask(task.id, {
                start_date: dayjs(task.start).format('YYYY-MM-DD'),
                end_date: dayjs(task.end).format('YYYY-MM-DD')
            });
            showSuccess("Đã dời lịch công việc!");
            fetchTasks();
        } catch (error) {
            showError("Lỗi khi dời lịch!");
            fetchTasks(); // Tải lại bảng nếu API lỗi
        }
    };

    const tableColumns = [
        { title: 'Tên công việc', dataIndex: 'name', key: 'name', render: (text) => <strong>{text}</strong> },
        { title: 'Bắt đầu', dataIndex: 'start_date', key: 'start_date', width: 120, render: d => d || <span className="text-gray-400 italic">Chưa set</span> },
        { title: 'Kết thúc', dataIndex: 'end_date', key: 'end_date', width: 120, render: d => d || <span className="text-gray-400 italic">Chưa set</span> },
        { 
            title: 'Trạng thái', 
            dataIndex: 'status', 
            key: 'status',
            width: 120,
            render: (s) => <Tag color={s === 'DONE' ? 'green' : s === 'DOING' ? 'blue' : 'default'}>{s}</Tag>
        },
        {
            title: 'Hành động',
            key: 'action',
            width: 120,
            render: (_, record) => {
                if (role !== "PM") return null;
                return (
                    <Button size="small" type="primary" ghost icon={<EditOutlined />} onClick={() => openEditModal(record)}>
                        Set ngày
                    </Button>
                );
            }
        }
    ];

    const ganttTasks = useMemo(() => {
        return tasks.filter(t => t.start_date && t.end_date).map(t => ({
            id: t.id.toString(),
            name: t.name,
            start: new Date(t.start_date),
            end: new Date(t.end_date),
            progress: t.status === "DONE" ? 100 : (t.status === "DOING" ? 50 : 0),
            type: tasks.some(child => child.parent_id === t.id) ? "project" : "task",
            project: t.parent_id?.toString(),
            isDisabled: role !== "PM", // Only PM can drag-drop tasks on Gantt
            styles: { progressColor: "#1890ff", progressSelectedColor: "#0050b3" }
        }));
    }, [tasks, role]);

    if (loading && tasks.length === 0) return <div className="flex justify-center p-20"><Spin size="large" tip="Đang tải..." /></div>;

    return (
        <div className="p-4 bg-slate-50 min-h-screen">
            <Card title={`Lịch trình chi tiết: ${projectCode}`} variant="outlined" className="mb-6 shadow-sm">
                <Table 
                    dataSource={tasks} // Show all tasks so PM can set dates for any task
                    columns={tableColumns} 
                    rowKey="id" 
                    pagination={false}
                    size="middle"
                    className="border rounded"
                    scroll={{ y: 300 }} 
                />
            </Card>

            <Card 
                title="Biểu đồ tiến độ (Gantt Chart)" 
                variant="outlined"
                className="shadow-sm"
                extra={
                    <Radio.Group value={viewMode} onChange={e => setViewMode(e.target.value)} size="small" buttonStyle="solid">
                        <Radio.Button value={ViewMode.Day}>Ngày</Radio.Button>
                        <Radio.Button value={ViewMode.Week}>Tuần</Radio.Button>
                        <Radio.Button value={ViewMode.Month}>Tháng</Radio.Button>
                    </Radio.Group>
                }
            >
                {ganttTasks.length > 0 ? (
                    <div style={{ border: '1px solid #f0f0f0', borderRadius: '8px' }}>
                        <Gantt
                            tasks={ganttTasks}
                            viewMode={viewMode}
                            onDateChange={handleGanttDateChange} // Update task dates when dragged
                            locale="vi"
                            listCellWidth="" 
                            TaskListHeader={() => null}
                            TaskListTable={() => null}
                            columnWidth={viewMode === ViewMode.Month ? 150 : 70}
                            rowHeight={45}
                            ganttHeight={400} 
                        />
                    </div>
                ) : (
                    <Empty description="Chưa có dữ liệu thời gian để vẽ biểu đồ" />
                )}
            </Card>

            <Modal
                title="⏱ Cập nhật thời gian công việc"
                open={isModalOpen}
                onCancel={() => setIsModalOpen(false)}
                onOk={handleSaveDates}
                confirmLoading={submitLoading}
                okText="Lưu lịch trình"
                cancelText="Hủy"
            >
                <div className="mt-4 mb-2">
                    <p className="mb-2 font-medium">Công việc: <span className="text-blue-600">{editingTask?.name}</span></p>
                    <RangePicker 
                        className="w-full"
                        value={selectedDates}
                        onChange={(dates) => setSelectedDates(dates)}
                        format="YYYY-MM-DD"
                    />
                </div>
            </Modal>

            <style>{`.gantt-task-react-list { display: none !important; }`}</style>
        </div>
    );
};

export default GanttChart;