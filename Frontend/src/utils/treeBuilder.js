/**
 * Hàm tiện ích để xây dựng cấu trúc cây phân cấp từ danh sách task.
 * Được dùng bởi modules WBS, PERT, Cost.
 * Tránh trùng lặp code giữa các components.
 */
export const buildTree = (tasks, parentId = null) => {
    return tasks
        .filter((task) => task.parent_id === parentId)
        .map((task) => ({
            ...task,
            key: task.id,
            children: buildTree(tasks, task.id).length > 0 ? buildTree(tasks, task.id) : null,
        }));
};

/**
 * Lấy các task gốc (không có task cha) cho các tính toán cộng dồn.
 */
export const getRootTasks = (tasks) => {
    return tasks.filter(t => t.parent_id === null);
};

/**
 * Kiểm tra xem một task có phải là task cha (có task con) không.
 */
export const isParentTask = (task, allTasks) => {
    return allTasks.some(t => t.parent_id === task.id);
};

/**
 * Lọc để chỉ lấy task lá (không có task con).
 */
export const getLeafTasks = (tasks) => {
    return tasks.filter(t => !isParentTask(t, tasks));
};
