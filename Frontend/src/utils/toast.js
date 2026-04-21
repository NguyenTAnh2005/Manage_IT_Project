/**
 * Toast notification utility
 * Hiển thị thông báo tạm thời cho user
 */

export const showToast = (message, type = "info", duration = 3000) => {
    // Tạo container nếu chưa tồn tại
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    // Tạo toast element
    const toast = document.createElement("div");
    const bgColor = {
        success: "bg-green-500",
        error: "bg-red-500",
        info: "bg-blue-500",
        warning: "bg-yellow-500",
    }[type] || "bg-blue-500";

    toast.style.cssText = `
        padding: 12px 16px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        font-size: 14px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
        pointer-events: auto;
    `;
    toast.className = bgColor;
    toast.textContent = message;

    // Thêm animation style nếu chưa tồn tại
    if (!document.getElementById("toast-styles")) {
        const style = document.createElement("style");
        style.id = "toast-styles";
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    container.appendChild(toast);

    // Tự động xóa sau duration
    setTimeout(() => {
        toast.style.animation = "slideOut 0.3s ease-out";
        setTimeout(() => toast.remove(), 300);
    }, duration);
};

/**
 * Show error toast
 */
export const showError = (message) => {
    showToast(message, "error", 4000);
};

/**
 * Show success toast
 */
export const showSuccess = (message) => {
    showToast(message, "success", 3000);
};

/**
 * Show info toast
 */
export const showInfo = (message) => {
    showToast(message, "info", 3000);
};

/**
 * Show warning toast
 */
export const showWarning = (message) => {
    showToast(message, "warning", 3000);
};
