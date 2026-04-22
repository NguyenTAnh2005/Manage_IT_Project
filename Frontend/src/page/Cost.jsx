import { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { Table, Button, Spin, Alert, Form, InputNumber, Space, Tooltip, Card, Statistic, Tag, Typography } from "antd";
import { EditOutlined, CheckOutlined, CloseOutlined, DollarOutlined } from "@ant-design/icons";
import { taskService } from "../services/taskService";
import { projectService } from "../services/projectService";
import { showSuccess, showError } from "../utils/toast";
import axiosInstance from "../services/axiosConfig";

const { Text } = Typography;

const buildTree = (tasks, parentId = null) => {
    return tasks
        .filter((task) => task.parent_id === parentId)
        .map((task) => ({
            ...task,
            key: task.id,
            children: buildTree(tasks, task.id).length > 0 ? buildTree(tasks, task.id) : null,
        }));
};

export const Cost = () => {
    const { projectCode } = useParams();
    const [form] = Form.useForm();
    
    const [tasks, setTasks] = useState([]);
    const [projectId, setProjectId] = useState(null);
    const [role, setRole] = useState(null); 
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingKey, setEditingKey] = useState('');
    const [expandedRowKeys, setExpandedRowKeys] = useState([]);

    // Lấy dữ liệu dự án và công việc
    const fetchData = async () => {
        try {
            if (!projectId) setLoading(true);
            const projectRes = await projectService.joinProject(projectCode);
            const pId = projectRes.id;
            setProjectId(pId);

            const roleRes = await axiosInstance.get(`/projects/${pId}/my-role`);
            setRole(roleRes.data.role);

            const tasksRes = await taskService.getTasks(pId);
            setTasks(tasksRes.tasks || []);
        } catch (err) {
            setError(err?.response?.data?.detail || "Lỗi khi tải dữ liệu chi phí");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (projectCode) fetchData();
    }, [projectCode]);

    const treeData = useMemo(() => buildTree(tasks), [tasks]);

    useEffect(() => {
        if (tasks.length > 0) {
            const parentIds = tasks.filter(t => tasks.some(child => child.parent_id === t.id)).map(t => t.id);
            setExpandedRowKeys(parentIds);
        }
    }, [tasks]);

    // Calculate total project cost from root tasks only
    const totalProjectCost = useMemo(() => {
        const rootTasks = tasks.filter(t => t.parent_id === null);
        return rootTasks.reduce((sum, t) => sum + (parseFloat(t.cost_total) || 0), 0);
    }, [tasks]);

    // Permission check and inline editing handlers
    const checkPermission = () => {
        if (role !== "PM") {
            showError("Chỉ Trưởng dự án (PM) mới có quyền chỉnh sửa chi phí!");
            return false;
        }
        return true;
    };

    const isEditing = (record) => record.id === editingKey;

    const edit = (record) => {
        if (!checkPermission()) return;
        form.setFieldsValue({ cost_total: record.cost_total || 0 });
        setEditingKey(record.id);
    };

    const save = async (id) => {
        try {
            const row = await form.validateFields();
            await taskService.updateTask(id, { cost_total: row.cost_total });
            
            showSuccess("Đã cập nhật chi phí!");
            setEditingKey('');
            fetchData(); 
        } catch (errInfo) {
            if (errInfo?.response) showError(errInfo.response.data.detail);
        }
    };

    const columns = [
        {
            title: "Tên công việc",
            dataIndex: "name",
            key: "name",
            width: "50%",
            render: (text, record) => {
                const isParent = (record.children && record.children.length > 0) || record.parent_id === null;
                return <span className={isParent ? "font-bold text-blue-800" : "text-slate-700"}>{text}</span>;
            },
        },
        {
            title: "Chi phí (VNĐ)",
            dataIndex: "cost_total",
            width: "30%",
            align: "right",
            render: (_, record) => {
                if (isEditing(record)) {
                    return (
                        <Form.Item name="cost_total" style={{ margin: 0 }} rules={[{ required: true, message: 'Nhập số tiền' }]}>
                            <InputNumber 
                                min={0} 
                                step={100000} 
                                className="w-full" 
                                autoFocus
                                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                                parser={value => value.replace(/\$\s?|(,*)/g, '')}
                            />
                        </Form.Item>
                    );
                }
                const isParent = tasks.some(t => t.parent_id === record.id);
                return (
                    <Text className={isParent ? "font-bold text-orange-600" : "text-slate-600"}>
                        {record.cost_total ? record.cost_total.toLocaleString() : '0'} VNĐ
                    </Text>
                );
            }
        },
        {
            title: "Thao tác",
            width: "20%",
            align: "center",
            render: (_, record) => {
                const isParent = tasks.some(t => t.parent_id === record.id);
                if (isParent) return <Tag color="default" className="border-none bg-slate-100 text-slate-400">Tự động tổng</Tag>;

                if (role !== "PM") return <Text type="secondary" italic size="small">Chỉ xem</Text>;

                const editable = isEditing(record);
                return editable ? (
                    <Space size="small">
                        <Button type="primary" size="small" icon={<CheckOutlined />} className="bg-emerald-600" onClick={() => save(record.id)} />
                        <Button size="small" danger icon={<CloseOutlined />} onClick={() => setEditingKey('')} />
                    </Space>
                ) : (
                    <Button 
                        type="text" 
                        icon={<EditOutlined className="text-blue-600" />} 
                        onClick={() => edit(record)} 
                        disabled={editingKey !== ''}
                    >
                        Sửa tiền
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
                        <DollarOutlined className="text-orange-500" /> Quản Lý Chi Phí Dự Án
                    </h2>
                    <p className="text-gray-500 mt-1">
                        Dự án: <Tag color="blue">{projectCode}</Tag> | 
                        Quyền: <Tag color={role === 'PM' ? 'gold' : 'cyan'}>{role}</Tag>
                    </p>
                </div>

                <Card bordered={false} className="shadow-md border-l-4 border-l-orange-500 min-w-[300px]">
                    <Statistic 
                        title="TỔNG CHI PHÍ DỰ TOÁN" 
                        value={totalProjectCost} 
                        suffix="VNĐ" 
                        valueStyle={{ color: '#ea580c', fontWeight: '800' }} 
                    />
                </Card>
            </div>

            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
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

export default Cost;