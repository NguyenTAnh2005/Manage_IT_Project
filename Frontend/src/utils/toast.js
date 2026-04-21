// Frontend/src/utils/toast.js
import { message } from "antd";

// Cấu hình vị trí và thời gian hiển thị mặc định
message.config({
    top: 50,
    duration: 3,
    maxCount: 3,
});

export const showSuccess = (msg) => {
    message.success(msg);
};

export const showError = (msg) => {
    message.error(msg || "Đã có lỗi xảy ra!");
};

export const showInfo = (msg) => {
    message.info(msg);
};

export const showWarning = (msg) => {
    message.warning(msg);
};