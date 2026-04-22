/**
 * Các component trạng thái được tái sử dụng cho tất cả các trang.
 * Giao diện thống nhất giữa WBS, PERT, Cost, Kanban, Gantt.
 */
import { Spin, Alert } from "antd";

/**
 * Loader toàn màn hình với spinner.
 */
export const PageLoading = ({ message = "Đang tải..." }) => (
    <div className="flex justify-center items-center h-[70vh]">
        <Spin size="large" tip={message} />
    </div>
);

/**
 * Thông báo lỗi toàn màn hình.
 */
export const PageError = ({ message = "Lỗi tải dữ liệu", details = null }) => (
    <Alert 
        message={message}
        description={details}
        type="error" 
        showIcon 
        className="m-4" 
    />
);

/**
 * Thông báo khi không có dữ liệu.
 */
export const EmptyState = ({ message = "Không có dữ liệu" }) => (
    <div className="py-12 text-center text-slate-400 text-sm">
        {message}
    </div>
);
