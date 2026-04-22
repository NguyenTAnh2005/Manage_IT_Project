import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Spin, Alert, Avatar, Tooltip, Tag, Typography, Button } from "antd";
import { UserOutlined, ClockCircleOutlined, CheckCircleOutlined, LeftOutlined, RightOutlined, LockOutlined } from "@ant-design/icons";

import { taskService } from "../services/taskService";
import { projectService } from "../services/projectService";
import { useAuth } from "../context/AuthContext";
import { useCurrentUser } from "../hooks/useCurrentUser";
import axiosInstance from "../services/axiosConfig";
import { showSuccess, showError } from "../utils/toast";

const { Text } = Typography;

/**
 * TaskCard - Individual task card in Kanban column.
 * Shows task name, status, owner, and allows status updates for authorized users.
 */
const TaskCard = ({ task, currentUser, role, onMoveStatus }) => {
    // Extract user ID from various possible object structures
    const { id: currentUserId, name: currentUserName } = useCurrentUser(currentUser);
    const taskOwnerId = task?.owner_id || task?.owner?.id;
    const isOwner = currentUserId && taskOwnerId && String(taskOwnerId) === String(currentUserId);
    
    // Permission: task owner can move tasks, or PM can move unassigned tasks
    const canMove = taskOwnerId ? isOwner : role === 'PM';

    // Lock reason tooltip for unauthorized users
    const ownerName = task?.owner?.full_name || "người khác";
    const lockReason = taskOwnerId 
        ? `Việc này của [${ownerName}]. Bạn đăng nhập là: [${currentUserName}].` 
        : "Chỉ PM mới được nhận việc trống";

    const renderStatusTag = () => {
        if (task.status === 'DONE') return <Tag color="success" icon={<CheckCircleOutlined />}>Hoàn thành</Tag>;
        if (task.status === 'DOING') return <Tag color="processing" icon={<ClockCircleOutlined spin />}>Đang làm</Tag>;
        return <Tag color="default">Cần làm</Tag>;
    };

    return (
        <div className={`bg-white p-4 rounded-lg shadow-sm border mb-3 relative group border-slate-200 transition-shadow ${canMove ? 'hover:shadow-md' : 'opacity-90 bg-slate-50/50'}`}>
            <div className="flex justify-between items-start mb-2">
                <Text strong className="text-slate-800 text-sm block truncate w-3/4" title={task.name}>{task.name}</Text>
                {renderStatusTag()}
            </div>
            
            <div className="flex justify-between items-center mt-3 pt-3 border-t border-slate-100">
                <div className="flex items-center gap-2">
                    <Tooltip title={task.owner ? task.owner.full_name : "Chưa gán người"}>
                        <Avatar size="small" icon={<UserOutlined />} className={task.owner ? "bg-blue-500" : "bg-slate-300"} />
                    </Tooltip>
                    <Text type="secondary" className="text-xs truncate w-24">
                        {task.owner ? task.owner.full_name.split(' ').pop() : 'Chưa gán'}
                    </Text>
                </div>
                
                {/* Lock icon with reason tooltip - shown when user cannot move task */}
                {!canMove && (
                    <Tooltip title={lockReason} color="red" overlayInnerStyle={{ fontWeight: "bold" }}>
                        <LockOutlined className="text-red-400 text-lg cursor-help" />
                    </Tooltip>
                )}
            </div>

            {/* Move buttons only visible when user has permission */}
            {canMove && (
                <div className="flex justify-between mt-4 pt-2">
                    <Button size="small" icon={<LeftOutlined />} disabled={task.status === 'TODO'} onClick={() => onMoveStatus(task, 'prev')}>
                        Lùi
                    </Button>
                    <Button size="small" type="primary" className="bg-blue-600" disabled={task.status === 'DONE'} onClick={() => onMoveStatus(task, 'next')}>
                        Tiến <RightOutlined />
                    </Button>
                </div>
            )}
        </div>
    );
};

/**
 * KanbanColumn - Single column in Kanban board.
 * Displays tasks with count and allows scrolling.
 */
const KanbanColumn = ({ title, tasks, colorClass, currentUser, role, onMoveStatus }) => {
    return (
        <div className="flex-1 min-w-[300px] max-w-[350px] bg-slate-100/50 rounded-xl p-4 flex flex-col h-full border border-slate-200">
            <div className={`mb-4 pb-2 border-b-2 ${colorClass} flex justify-between items-center`}>
                <h3 className="font-bold text-slate-700 m-0 uppercase tracking-wide text-sm">{title}</h3>
                <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full text-xs font-bold">{tasks.length}</span>
            </div>
            <div className="flex-1 overflow-y-auto pr-1 pb-2 custom-scrollbar min-h-[50vh]">
                {tasks.map(task => (
                    <TaskCard key={task.id} task={task} currentUser={currentUser} role={role} onMoveStatus={onMoveStatus} />
                ))}
                {tasks.length === 0 && (
                    <div className="py-8 text-center text-slate-400 text-sm italic border-2 border-dashed border-slate-200 rounded-lg">Không có công việc nào</div>
                )}
            </div>
        </div>
    );
};

/**
 * Main Kanban board component.
 * Displays tasks grouped by status (TODO, DOING, DONE) with drag-and-drop functionality.
 */
export const Kanban = () => {
    const { projectCode } = useParams();
    
    // Get user from context or localStorage fallback
    const authContext = useAuth() || {};
    const contextUser = authContext.user || authContext.userInfo || authContext.currentUser;
    const [localUser, setLocalUser] = useState(null);

    useEffect(() => {
        try {
            const stored = localStorage.getItem('user');
            if (stored) setLocalUser(JSON.parse(stored));
        } catch (e) {}
    }, []);

    const activeUser = contextUser || localUser;

    const [tasksByStatus, setTasksByStatus] = useState({ TODO: [], DOING: [], DONE: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [role, setRole] = useState(null);

    const fetchKanbanData = async () => {
        try {
            setLoading(true);
            const projectRes = await projectService.joinProject(projectCode);
            const pId = projectRes.id;

            const roleRes = await axiosInstance.get(`/projects/${pId}/my-role`);
            setRole(roleRes.data.role);

            const kanbanRes = await taskService.getTasksByStatus(pId);
            
            // Filter to exclude parent tasks (show only leaf tasks)
            const isNotParent = (task, allTasks) => !allTasks.some(t => t.parent_id === task.id);
            const allTasks = [...(kanbanRes.todo || []), ...(kanbanRes.doing || []), ...(kanbanRes.done || [])];

            setTasksByStatus({
                TODO: (kanbanRes.todo || []).filter(t => isNotParent(t, allTasks)),
                DOING: (kanbanRes.doing || []).filter(t => isNotParent(t, allTasks)),
                DONE: (kanbanRes.done || []).filter(t => isNotParent(t, allTasks)),
            });
        } catch (err) {
            setError("Lỗi tải bảng Kanban");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { if (projectCode) fetchKanbanData(); }, [projectCode]);

    const handleMoveStatus = async (task, direction) => {
        let newStatus = '';
        if (direction === 'next') {
            newStatus = task.status === 'TODO' ? 'DOING' : 'DONE';
        } else {
            newStatus = task.status === 'DONE' ? 'DOING' : 'TODO';
        }

        const sourceTasks = tasksByStatus[task.status].filter(t => t.id !== task.id);
        const destTasks = [...tasksByStatus[newStatus], { ...task, status: newStatus }]
            .sort((a, b) => a.name.localeCompare(b.name));

        setTasksByStatus(prev => ({
            ...prev,
            [task.status]: sourceTasks,
            [newStatus]: destTasks
        }));

        try {
            await taskService.updateTask(task.id, { status: newStatus });
            showSuccess(`Đã chuyển sang ${newStatus}`);
        } catch (error) {
            showError(error?.response?.data?.detail || "Không có quyền chuyển việc này!");
            fetchKanbanData(); 
        }
    };

    if (loading) return <div className="flex justify-center items-center h-[70vh]"><Spin size="large" /></div>;
    if (error) return <Alert message="Lỗi" description={error} type="error" showIcon className="m-4" />;

    return (
        <div className="p-6 bg-white min-h-[80vh] rounded-lg shadow-sm m-4 overflow-hidden">
            <div className="mb-6 flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800 m-0">Bảng Kanban</h2>
                    <p className="text-slate-500 mt-1">Dự án: <Tag color="blue">{projectCode}</Tag> | Quyền: <Tag color={role === 'PM' ? 'gold' : 'cyan'}>{role}</Tag></p>
                </div>
                <div className="text-sm text-slate-500 italic bg-slate-50 px-3 py-1 rounded">
                    💡 Việc của ai, người nấy chuyển!
                </div>
            </div>

            <div className="overflow-x-auto pb-4">
                <div className="flex gap-6 items-stretch h-[60vh] min-w-[950px] justify-center">
                    {/* Pass active user to columns for permission checks */}
                    <KanbanColumn title="📌 Cần làm (TODO)" tasks={tasksByStatus.TODO} colorClass="border-slate-400" currentUser={activeUser} role={role} onMoveStatus={handleMoveStatus} />
                    <KanbanColumn title="⏳ Đang làm (DOING)" tasks={tasksByStatus.DOING} colorClass="border-blue-500" currentUser={activeUser} role={role} onMoveStatus={handleMoveStatus} />
                    <KanbanColumn title="✅ Hoàn thành (DONE)" tasks={tasksByStatus.DONE} colorClass="border-emerald-500" currentUser={activeUser} role={role} onMoveStatus={handleMoveStatus} />
                </div>
            </div>
            
            <style>{`
                .custom-scrollbar::-webkit-scrollbar { width: 4px; height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
            `}</style>
        </div>
    );
};

export default Kanban;