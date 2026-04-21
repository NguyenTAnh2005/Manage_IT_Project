import axiosInstance from "./axiosConfig";

export const taskService = {
    // Lấy danh sách công việc (WBS) của dự án
    getTasks: async (projectId) => {
        const res = await axiosInstance.get(`/projects/${projectId}/tasks`);
        return res.data;
    },

    // Tạo công việc mới
    createTask: async (projectId, taskData) => {
        const res = await axiosInstance.post(`/projects/${projectId}/tasks`, taskData);
        return res.data;
    },

    // Lấy chi tiết công việc
    getTaskDetail: async (taskId) => {
        const res = await axiosInstance.get(`/tasks/${taskId}`);
        return res.data;
    },

    // Cập nhật công việc
    updateTask: async (taskId, taskData) => {
        const res = await axiosInstance.put(`/tasks/${taskId}`, taskData);
        return res.data;
    },

    // Xóa công việc
    deleteTask: async (taskId) => {
        const res = await axiosInstance.delete(`/tasks/${taskId}`);
        return res.data;
    },

    // ✅ ĐÃ SỬA: Lấy dữ liệu cho bảng Kanban (Trả về 1 cục 3 cột)
    getTasksByStatus: async (projectId) => {
        const res = await axiosInstance.get(`/projects/${projectId}/tasks/kanban`);
        return res.data;
    },

    // Lấy công việc trong khoảng thời gian (cho Gantt sau này)
    getTasksByDateRange: async (projectId, startDate, endDate) => {
        const res = await axiosInstance.get(`/projects/${projectId}/tasks?start_date=${startDate}&end_date=${endDate}`);
        return res.data;
    }
};