import { useState } from "react";
import { ChevronRight, ChevronDown, User, Calendar, AlertCircle, Plus } from "lucide-react";


import {project_1} from "../mock_data"


const WbsRow = ({task, allTasks, level = 0})=>{
    const [isExpanded, setIsExpanded] = useState(true)
    const childTasks = allTasks.filter(t => t.parentId === task.id);
    console.log(task.id);
    console.log(childTasks);
    const hasChildren = childTasks.length > 0;
    return (
        <>
            <tr className="border-b border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors">
                <td className="py-3 px-4">
                    <div className="flex items-center" style={{ paddingLeft: `${level * 24}px` }}>
                        {hasChildren ? (
                            <button 
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded mr-1"
                            >
                                {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </button>
                        ) : (
                            <span className="w-6" /> // Khoảng trống nếu không có con
                        )}
                        <span className={`text-sm ${level === 0 ? 'font-bold' : 'font-medium'}`}>
                            {task.name}
                        </span>
                    </div>
                </td>
                <td className="py-3 px-4">
                    <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <User size={14} /> {task.assignee}
                    </div>
                </td>
                <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        task.status === 'DONE' ? 'bg-green-100 text-green-700' : 
                        task.status === 'DOING' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-700'
                    }`}>
                        {task.status}
                    </span>
                </td>
                <td className="py-3 px-4 text-sm text-slate-600 dark:text-slate-400">
                    <div className="flex items-center gap-2">
                        <Calendar size={14} /> {task.duration} ngày
                    </div>
                </td>
                <td className="py-3 px-4">
                    <div className="flex items-center gap-1 text-xs">
                        <AlertCircle size={14} className={task.priority === 'High' ? 'text-red-500' : 'text-yellow-500'} />
                        {task.priority}
                    </div>
                </td>
            </tr>
            
            {/* ĐỆ QUY: Nếu đang mở và có con, vẽ tiếp các hàng con */}
            {isExpanded && hasChildren && (
                childTasks.map(child => (
                    <WbsRow key={child.id} task={child} allTasks={allTasks} level={level + 1} />
                ))
            )}
            
        </>
    );
};
const WbsDashBoard = () =>{
    const rootTasks = project_1.filter( t => t.parentId == null);
    return(
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Cấu trúc phân rã công việc (WBS)</h2>
                    <p className="text-slate-500 text-sm">Quản lý danh sách và phân cấp các hạng mục dự án</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Plus size={18} /> Thêm công việc
                </button>
            </div>

            <div className="card overflow-hidden !p-0">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200">
                        <tr>
                            <th className="py-3 px-4 font-semibold text-sm">Tên công việc</th>
                            <th className="py-3 px-4 font-semibold text-sm">Người phụ trách</th>
                            <th className="py-3 px-4 font-semibold text-sm">Trạng thái</th>
                            <th className="py-3 px-4 font-semibold text-sm">Thời lượng</th>
                            <th className="py-3 px-4 font-semibold text-sm">Ưu tiên</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rootTasks.map(task => (
                            <WbsRow key={task.id} task={task} allTasks={project_1} />
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
export default WbsDashBoard;