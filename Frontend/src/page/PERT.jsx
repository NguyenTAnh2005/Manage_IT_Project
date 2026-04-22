import { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { Table, Button, Spin, Alert, Form, InputNumber, Space, Tooltip, Card, Statistic, Tag } from "antd";
import { EditOutlined, CheckOutlined, CloseOutlined, CalculatorOutlined } from "@ant-design/icons";
import { taskService } from "../services/taskService";
import { projectService } from "../services/projectService";
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

export const PERTCalculation = () => {
    const { projectCode } = useParams();
    const [form] = Form.useForm();
    
    const [tasks, setTasks] = useState([]);
    const [projectId, setProjectId] = useState(null);
    const [role, setRole] = useState(null); // Lưu quyền user để kiểm tra quyền sửa
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingKey, setEditingKey] = useState('');
    const [expandedRowKeys, setExpandedRowKeys] = useState([]);

    // Fetch project data, user role, and tasks
    const fetchData = async () => {
        try {
            if (!projectId) setLoading(true);
            const projectRes = await projectService.joinProject(projectCode);
            const pId = projectRes.id;
            setProjectId(pId);

            // Get user's role in this project
            const roleRes = await axiosInstance.get(`/projects/${pId}/my-role`);
            setRole(roleRes.data.role);

            const tasksRes = await taskService.getTasks(pId);
            setTasks(tasksRes.tasks || []);
        } catch (err) {
            setError(err?.response?.data?.detail || "Lỗi khi tải dữ liệu PERT");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (projectCode) fetchData();
    }, [projectCode]);

    const treeData = useMemo(() => buildTree(tasks), [tasks]);

    // Tự động mở rộng các task cha khi có data
    useEffect(() => {
        if (tasks.length > 0) {
            const parentIds = tasks.filter(t => tasks.some(child => child.parent_id === t.id)).map(t => t.id);
            setExpandedRowKeys(parentIds);
        }
    }, [tasks]);

    // Calculate total EST from root tasks only
    const totalEST = useMemo(() => {
        const rootTasks = tasks.filter(t => t.parent_id === null);
        return rootTasks.reduce((sum, t) => sum + (parseFloat(t.est) || 0), 0).toFixed(2);
    }, [tasks]);

    // Permission check and inline editing handlers
    const checkPermission = () => {
        if (role !== "PM") {
            showError("Chỉ Trưởng dự án (PM) mới có quyền chỉnh sửa thông số PERT!");
            return false;
        }
        return true;
    };

    const isEditing = (record) => record.id === editingKey;

    const edit = (record) => {
        // Check permission before allowing edit
        if (!checkPermission()) return;

        form.setFieldsValue({
            mo: record.mo || 0.5,
            ml: record.ml || 0.5,
            mp: record.mp || 0.5,
        });
        setEditingKey(record.id);
    };

    const cancel = () => {
        setEditingKey('');
    };

    const save = async (id) => {
        try {
            const row = await form.validateFields();
            if (row.mo > row.ml || row.ml > row.mp) {
                showError("Lỗi: Lạc quan (O) ≤ Khả dĩ (M) ≤ Bi quan (P)");
                return;
            }

            await taskService.updateTask(id, {
                mo: row.mo,
                ml: row.ml,
                mp: row.mp
            });
            
            showSuccess("Đã cập nhật PERT!");
            setEditingKey('');
            fetchData(); // Refresh to get updated metrics
        } catch (errInfo) {
            if (errInfo?.response) showError(errInfo.response.data.detail);
        }
    };

    // ==========================================
    // CẤU HÌNH CỘT BẢNG
    // ==========================================
    const columns = [
        {
            title: "Tên công việc",
            dataIndex: "name",
            key: "name",
            width: "40%",
            render: (text, record) => {
                const isParent = (record.children && record.children.length > 0) || record.parent_id === null;
                return (
                    <span className={isParent ? "font-bold text-blue-800 text-base" : "font-medium text-slate-700"}>
                        {text}
                    </span>
                );
            },
        },
        {
            title: "Lạc quan (O)",
            dataIndex: "mo",
            width: "12%",
            align: "center",
            render: (_, record) => {
                if (isEditing(record)) {
                    return (
                        <Form.Item name="mo" style={{ margin: 0 }} rules={[{ required: true }]}>
                            <InputNumber min={0.5} step={0.5} size="small" className="w-16" />
                        </Form.Item>
                    );
                }
                return <span className="text-gray-600">{record.mo || '--'}</span>;
            }
        },
        {
            title: "Khả dĩ (M)",
            dataIndex: "ml",
            width: "12%",
            align: "center",
            render: (_, record) => {
                if (isEditing(record)) {
                    return (
                        <Form.Item name="ml" style={{ margin: 0 }} rules={[{ required: true }]}>
                            <InputNumber min={0.5} step={0.5} size="small" className="w-16" />
                        </Form.Item>
                    );
                }
                return <span className="font-medium text-blue-600">{record.ml || '--'}</span>;
            }
        },
        {
            title: "Bi quan (P)",
            dataIndex: "mp",
            width: "12%",
            align: "center",
            render: (_, record) => {
                if (isEditing(record)) {
                    return (
                        <Form.Item name="mp" style={{ margin: 0 }} rules={[{ required: true }]}>
                            <InputNumber min={0.5} step={0.5} size="small" className="w-16" />
                        </Form.Item>
                    );
                }
                return <span className="text-gray-600">{record.mp || '--'}</span>;
            }
        },
        {
            title: "EST (Dự kiến)",
            dataIndex: "est",
            width: "12%",
            align: "center",
            render: (est) => (
                <span className="font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
                    {est ? parseFloat(est).toFixed(2) : '--'}
                </span>
            ),
        },
        {
            title: "Thao tác",
            width: "12%",
            align: "center",
            render: (_, record) => {
                // Task cha không cho sửa (Backend tự cộng dồn)
                const isParent = tasks.some(t => t.parent_id === record.id);
                if (isParent) return <span className="text-gray-300 text-xs italic">Tự động</span>;

                const editable = isEditing(record);
                return editable ? (
                    <Space size="small">
                        <Button type="primary" size="small" icon={<CheckOutlined />} className="bg-blue-600" onClick={() => save(record.id)} />
                        <Button size="small" danger icon={<CloseOutlined />} onClick={cancel} />
                    </Space>
                ) : (
                    <Button 
                        type="text" 
                        // Icon mờ đi nếu không phải PM để ra hiệu "Chỉ xem"
                        icon={<EditOutlined className={role === 'PM' ? "text-blue-600" : "text-gray-300"} />} 
                        onClick={() => edit(record)} 
                        disabled={editingKey !== ''}
                    >
                        Sửa
                    </Button>
                );
            },
        },
    ];

    if (loading && tasks.length === 0) return <div className="flex justify-center items-center h-64"><Spin size="large" /></div>;

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            <div className="mb-6 flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 m-0 flex items-center gap-2">
                        <CalculatorOutlined className="text-blue-600" /> Ước Lượng Thời Gian PERT
                    </h2>
                    <p className="text-gray-500 mt-1">Dự án: <Tag color="blue">{projectCode}</Tag> | Vai trò: <Tag color={role === 'PM' ? 'gold' : 'cyan'}>{role}</Tag></p>
                </div>

                {/* Total EST statistics card */}
                <Card bordered={false} className="shadow-sm border-l-4 border-l-blue-600 min-w-[250px]">
                    <Statistic 
                        title="TỔNG THỜI GIAN DỰ KIẾN (EST)" 
                        value={totalEST} 
                        suffix="ngày" 
                        valueStyle={{ color: '#2563eb', fontWeight: '800' }} 
                    />
                </Card>
            </div>

            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-blue-800 text-sm flex items-center gap-2">
                    <span>💡</span>
                    <span>
                        <strong>Quy tắc:</strong> EST = (O + 4M + P) / 6. 
                        {role === 'PM' ? " Bạn có quyền chỉnh sửa các công việc nhỏ nhất." : " Bạn đang ở chế độ Chỉ xem."}
                    </span>
                </div>
                
                <Form form={form} component={false}>
                    <Table
                        columns={columns}
                        dataSource={treeData}
                        pagination={false}
                        bordered
                        size="middle"
                        expandable={{ 
                            expandedRowKeys: expandedRowKeys,
                            onExpandedRowsChange: (keys) => setExpandedRowKeys(keys)
                        }}
                        rowClassName={(record) => (tasks.some(t => t.parent_id === record.id) ? "bg-slate-50/50" : "")}
                    />
                </Form>
            </div>
        </div>
    );
};

export default PERTCalculation;