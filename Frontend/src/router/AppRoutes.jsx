import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import DashBoardLayout from '../components/layout/DashBoardLayout';

// Import các pages
import Login from '../page/Login';
import Register from '../page/Register';
import JoinProject from '../page/JoinProject';
import CreateProject from '../page/CreateProject';
import WbsDashBoard from '../page/WBS';
import KanbanBoard from '../page/Kanban';
import GanttChart from '../page/GanttChart';
import CostManagement from '../page/Cost';
import PERTCalculation from '../page/PERT';

export const AppRoutes = () => {
    return (
        <BrowserRouter>
            <Routes>
                {/* ================================================== */}
                {/* 1. KHU VỰC PUBLIC (AuthLayout: Không có menu)      */}
                {/* ================================================== */}
                <Route path="/login" element={<Login/>} />
                <Route path="/register" element={<Register/>} />

                {/* ================================================== */}
                {/* 2. KHU VỰC PRIVATE (Phải đi qua Lính gác ProtectedRoute) */}
                {/* ================================================== */}
                <Route element={<ProtectedRoute />}>
                    
                    {/* Trang chọn/tạo dự án */}
                    <Route path="/join-project" element={<JoinProject/>} />
                    <Route path="/create-project" element={<CreateProject/>} />

                    {/* Dashboard Layout với các sub-routes */}
                    <Route path="/dashboard/:projectCode" element={<DashBoardLayout/>}>
                        
                        {/* Các trang con nhét vào giữa Dashboard Layout (Outlet) */}
                        <Route path="wbs" element={<WbsDashBoard/>} />
                        <Route path="kanban" element={<KanbanBoard/>} />
                        <Route path="gantt" element={<GanttChart/>} />
                        <Route path="cost" element={<CostManagement/>} />
                        <Route path="pert" element={<PERTCalculation/>} />
                        
                        {/* Route mặc định cho dashboard */}
                        <Route index element={<Navigate to="wbs" replace />} />
                    </Route>
                </Route>

                {/* ================================================== */}
                {/* LỖI 404: Gõ bậy bạ tự động đá về Login             */}
                {/* ================================================== */}
                <Route path="/" element={<Navigate to="/join-project" replace />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default AppRoutes;