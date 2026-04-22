import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export const ProtectedRoute = () => {
    const { isAuthenticated, projectCode } = useAuth();
    const location = useLocation();

    // 1. Chưa đăng nhập -> Đá về Login
    if (!isAuthenticated) {
        return <Navigate to={'/login'} replace />
    }

    // 2. Đã đăng nhập nhưng CHƯA CHỌN DỰ ÁN
    if (!projectCode) {
        // CHỈ cho phép ở lại trang Join hoặc trang Create
        if (location.pathname !== '/join-project' && location.pathname !== '/create-project') {
            return <Navigate to={'/join-project'} replace />
        }
    }

    // 3. ĐÃ CÓ DỰ ÁN (đang trong phiên làm việc)
    if (projectCode) {
        // Nếu cố tình quay lại trang Join hoặc Create thì tự động đẩy vào Dashboard
        if (location.pathname === '/join-project' || location.pathname === '/create-project') {
            return <Navigate to={`/dashboard/${projectCode}/wbs`} replace />
        }
    }

    // 4. Hợp lệ thì cho qua
    return <Outlet />
}