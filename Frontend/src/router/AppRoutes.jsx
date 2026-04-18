import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import DashBoardLayout from '../components/layout/DashBoardLayout';

// Giả lập import các Layout và Page
// import AuthLayout from '../layouts/AuthLayout';
// import DashboardLayout from '../layouts/DashboardLayout';
import Login from '../page/Login';
import JoinProject from '../page/JoinProject';
import WbsDashBoard from '../page/WBS'

export const AppRoutes = () => {
    return (
        <BrowserRouter>
            <Routes>
                {/* ================================================== */}
                {/* 1. KHU VỰC PUBLIC (AuthLayout: Không có menu)      */}
                {/* ================================================== */}
                <Route path="/login" element={<Login/>} />

                {/* ================================================== */}
                {/* 2. KHU VỰC PRIVATE (Phải đi qua Lính gác ProtectedRoute) */}
                {/* ================================================== */}
                <Route element={<ProtectedRoute />}>
                    
                    {/* Vượt qua Login thì được vào trang Nhập mã */}
                    <Route path="/join-project" element={<JoinProject/>} />

                    {/* Vượt qua Nhập mã thì được vào Dashboard Layout */}
                    {/* Chú ý: Có chữ :projectCode để bắt cái mã HABIT_01 từ URL */}
                    <Route path="/dashboard/:projectCode" element={<DashBoardLayout/>}>
                        
                        {/* Đây là các trang con nhét vào giữa Dashboard Layout (Outlet) */}
                        <Route path="wbs" element={<WbsDashBoard/>} />
                        <Route path="kanban" element={<div>Bảng Kanban</div>} />
                        <Route path="gantt" element={<div>Biểu đồ Gantt</div>} />
                        <Route path="cost" element={<div>Bảng Chi Phí</div>} />
                        

                    </Route>
                    {/* Nếu user chỉ gõ /dashboard/HABIT_01 -> Tự động đá sang wbs */}
                    <Route index element={<Navigate to="/dashboard/:projectCode/wbs" replace />} />
                </Route>

                {/* ================================================== */}
                {/* LỖI 404: Gõ bậy bạ tự động đá về Login             */}
                {/* ================================================== */}
                <Route path="*" element={<h1>Lỗi 404: Đường dẫn không tồn tại!</h1>} />
            </Routes>
        </BrowserRouter>
    );
}

export default AppRoutes;