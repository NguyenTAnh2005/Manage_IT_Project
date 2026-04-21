import { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { Table, Tag, Button, Spin, Alert, Avatar, Tooltip, Modal, Form, Input, Select, Space } from "antd";
import { PlusOutlined, UserOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { taskService } from "../services/taskService";
import { projectService } from "../services/projectService";
import { useAuth } from "../context/AuthContext";
import { showSuccess, showError } from "../utils/toast";
import axiosInstance from "../services/axiosConfig";

const buildTree = (tasks, parentId = null) => {
    return tasks
        .filter((task) => task.parent_id === parentId)
        .map((task) => ({
            ...task,
            key: task.id,
            children: buildTree(tasks, task.id).length > 0 ? buildTree(tasks, task.id) : null,
        }));
};

export const WbsDashBoard = () => {
    const { projectCode } = useParams();
    const { user } = useAuth();
    const [form] = Form.useForm();
    
    const [tasks, setTasks] = useState([]);
    const [projectId, setProjectId] = useState(null);
    const [role, setRole] = useState(null); // Lưu quyền user
    const [loading, setLoading] = useState(true);
    const [error, setPageError] = useState(null);
    const [expandedRowKeys, setExpandedRowKeys] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [submitLoading, setSubmitLoading] = useState(false);

    const fetchProjectAndTasks = async () => {
        try {
            if (!projectId) setLoading(true); 
            const projectRes = await projectService.joinProject(projectCode);
            const pId = projectRes.id;
            setProjectId(pId);

            // Lấy role của user
            const roleRes = await axiosInstance.get(`/projects/${pId}/my-role`);
            setRole(roleRes.data.role);

            const tasksRes = await taskService.getTasks(pId);
            setTasks(tasksRes.tasks || []);
        } catch (err) {
            setPageError(err?.response?.data?.detail || "Lỗi khi tải dữ liệu WBS");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (projectCode) fetchProjectAndTasks();
    }, [projectCode]);

    // ✅ HÀM CHECK QUYỀN TẠI CHỖ
    const checkPermission = () => {
        if (role !== "PM") {
            showError("Chỉ Trưởng dự án (PM) mới có quyền thực hiện hành động này!");
            return false;
        }
        return true;
    };

    const handleOpenModal = (task = null) => {
        // Bấm là check liền, không cho mở Form nếu là Member
        if (!checkPermission()) return;

        setEditingTask(task);
        if (task) {
            form.setFieldsValue({
                name: task.name,
                parent_id: task.parent_id || null,
                owner_id: task.owner_id || null,
            });
        } else {
            form.resetFields();
            form.setFieldsValue({ parent_id: null, owner_id: null });
        }
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingTask(null);
        form.resetFields();
    };

    const handleSubmit = async (values) => {
        try {
            setSubmitLoading(true);
            const payload = {
                ...values,
                parent_id: values.parent_id || null,
                owner_id: values.owner_id || null,
            };

            if (editingTask) {
                await taskService.updateTask(editingTask.id, payload);
                showSuccess("Đã cập nhật công việc!");
            } else {
                await taskService.createTask(projectId, payload);
                showSuccess("Đã tạo công việc mới!");
            }
            handleCloseModal();
            fetchProjectAndTasks();
        } catch (err) {
            showError(err?.response?.data?.detail || "Không thể lưu công việc");
        } finally {
            setSubmitLoading(false);
        }
    };

    const handleDeleteTask = () => {
        if (!checkPermission()) return; // Gác cổng thêm lần nữa cho chắc
        
        const isParent = editingTask.children && editingTask.children.length > 0;
        Modal.confirm({
            title: 'Xóa công việc này?',
            content: isParent 
                ? <div className="mt-2 text-red-600 font-medium">⚠️ CHÚ Ý: Đây là nhóm việc. Xóa nó sẽ xóa TẤT CẢ công việc con!</div>
                : 'Bạn có chắc chắn muốn xóa không?',
            okText: 'Xóa vĩnh viễn',
            okType: 'danger',
            cancelText: 'Hủy',
            onOk: async () => {
                try {
                    await taskService.deleteTask(editingTask.id);
                    showSuccess("Đã xóa thành công!");
                    handleCloseModal();
                    fetchProjectAndTasks();
                } catch (err) {
                    showError("Lỗi xóa: " + err?.response?.data?.detail);
                }
            }
        });
    };

    const treeData = useMemo(() => buildTree(tasks), [tasks]);
    
    useEffect(() => {
        if (tasks.length > 0) {
            const parentIds = tasks.filter(t => tasks.some(child => child.parent_id === t.id)).map(t => t.id);
            setExpandedRowKeys(parentIds);
        }
    }, [tasks]);

    const availableUsers = useMemo(() => {
        const usersMap = new Map();
        if (user) usersMap.set(user.id, user);
        tasks.forEach(t => { if (t.owner) usersMap.set(t.owner.id, t.owner); });
        return Array.from(usersMap.values());
    }, [tasks, user]);

    const columns = [
        {
            title: "Tên công việc",
            dataIndex: "name",
            key: "name",
            width: "45%",
            render: (text, record) => {
                const isParent = (record.children && record.children.length > 0) || record.parent_id === null;
                return <span className={isParent ? "font-bold text-blue-800 text-base" : "font-medium text-slate-700"}>{text}</span>;
            },
        },
        {
            title: "Người phụ trách",
            key: "owner",
            width: "25%",
            render: (_, record) => {
                if (!record.owner) return <span className="text-gray-400 italic text-xs">-- Nhóm việc --</span>;
                return (
                    <div className="flex items-center gap-2">
                        <Avatar size="small" className="bg-blue-500" icon={<UserOutlined />} />
                        <span className="text-sm font-medium truncate">{record.owner.full_name}</span>
                    </div>
                );
            },
        },
        {
            title: "Trạng thái",
            dataIndex: "status",
            key: "status",
            width: "15%",
            align: "center",
            render: (status) => {
                let color = status === "DONE" ? "green" : status === "DOING" ? "blue" : "default";
                return <Tag color={color}>{status}</Tag>;
            },
        },
        {
            title: "Tùy chỉnh",
            key: "action",
            width: "15%",
            align: "center",
            render: (_, record) => (
                <Button 
                    type="text" 
                    icon={<EditOutlined className={role === 'PM' ? "text-blue-600" : "text-gray-300"} />} 
                    onClick={() => handleOpenModal(record)} 
                >
                    Sửa
                </Button>
            ),
        },
    ];

    if (loading && tasks.length === 0) return <div className="flex justify-center items-center h-64"><Spin size="large" /></div>;

    return (
        <div className="p-6 bg-white rounded-lg shadow-md m-4 border border-slate-200">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 m-0">Quản trị WBS</h2>
                    <p className="text-gray-500 mt-1">Phân rã cấu trúc và giao việc <Tag color={role === 'PM' ? 'gold' : 'blue'}>{role}</Tag></p>
                </div>
                <Button type="primary" icon={<PlusOutlined />} className="bg-blue-600" onClick={() => handleOpenModal()}>
                    Thêm việc mới
                </Button>
            </div>

            <Table 
                columns={columns} dataSource={treeData} pagination={false} bordered size="middle"
                expandable={{ expandedRowKeys: expandedRowKeys, onExpandedRowsChange: (keys) => setExpandedRowKeys(keys) }}
            />

            <Modal
                title={<span className="text-lg text-blue-700">{editingTask ? "📝 Cập nhật công việc" : "✨ Thêm việc mới"}</span>}
                open={isModalOpen} onCancel={handleCloseModal} destroyOnClose
                footer={
                    <div className="flex justify-between items-center mt-6">
                        <div>
                            {editingTask && (
                                <Button danger icon={<DeleteOutlined />} onClick={handleDeleteTask}>Xóa công việc</Button>
                            )}
                        </div>
                        <Space>
                            <Button onClick={handleCloseModal}>Hủy</Button>
                            <Button type="primary" className="bg-blue-600" loading={submitLoading} onClick={() => form.submit()}>
                                {editingTask ? "Lưu thay đổi" : "Tạo công việc"}
                            </Button>
                        </Space>
                    </div>
                }
            >
                {/* Form giữ nguyên như cũ */}
                <Form form={form} layout="vertical" onFinish={handleSubmit} className="mt-4">
                    <Form.Item name="name" label="Tên công việc" rules={[{ required: true, message: "Nhập tên việc đi sếp!" }]}>
                        <Input placeholder="Vd: Viết API Login..." size="large" />
                    </Form.Item>
                    <div className="grid grid-cols-2 gap-4">
                        <Form.Item name="parent_id" label="Thuộc nhóm việc (Giai đoạn)">
                            <Select placeholder="Chọn nhóm" size="large">
                                <Select.Option value={null}>-- Để trống --</Select.Option>
                                {tasks.filter(t => t.id !== editingTask?.id && t.parent_id === null).map(t => (
                                    <Select.Option key={t.id} value={t.id}>{t.name}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                        <Form.Item name="owner_id" label="Giao cho ai?">
                            <Select placeholder="Chọn người làm" size="large">
                                <Select.Option value={null}>-- Để trống --</Select.Option>
                                {availableUsers.map(u => (
                                    <Select.Option key={u.id} value={u.id}>{u.full_name}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </div>
                </Form>
            </Modal>
        </div>
    );
};

export default WbsDashBoard;