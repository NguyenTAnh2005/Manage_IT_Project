/**
 * Toast notification utilities using Ant Design message component.
 * Displays success, error, info, and warning messages to the user.
 */

import { message } from "antd";

// Configure toast position, duration, and max count
message.config({
    top: 50,
    duration: 3,
    maxCount: 3,
});

/**
 * Show success notification.
 * @param {string} msg - Message to display
 */
export const showSuccess = (msg) => {
    message.success(msg);
};

/**
 * Show error notification.
 * @param {string} msg - Error message to display
 */
export const showError = (msg) => {
    message.error(msg || "Đã có lỗi xảy ra!");
};

/**
 * Show info notification.
 * @param {string} msg - Info message to display
 */
export const showInfo = (msg) => {
    message.info(msg);
};

/**
 * Show warning notification.
 * @param {string} msg - Warning message to display
 */
export const showWarning = (msg) => {
    message.warning(msg);
};