/**
 * Task service - API calls for task management (WBS, PERT, Cost, Kanban, Gantt).
 */

import axiosInstance from "./axiosConfig";

export const taskService = {
    /**
     * Lấy danh sách công việc (WBS) của dự án.
     * @param {number} projectId - ID dự án
     * @returns {Promise<Object>} {total, tasks[]}
     */
    getTasks: async (projectId) => {
        const res = await axiosInstance.get(`/projects/${projectId}/tasks`);
        return res.data;
    },

    /**
     * Tạo công việc mới.
     * @param {number} projectId - ID dự án
     * @param {Object} taskData - {name, parent_id, owner_id, mo, ml, mp, start_date, end_date, cost_total}
     * @returns {Promise<Object>} Thông tin task vừa tạo
     */
    createTask: async (projectId, taskData) => {
        const res = await axiosInstance.post(`/projects/${projectId}/tasks`, taskData);
        return res.data;
    },

    /**
     * Lấy chi tiết công việc.
     * @param {number} taskId - ID công việc
     * @returns {Promise<Object>} Thông tin task
     */
    getTaskDetail: async (taskId) => {
        const res = await axiosInstance.get(`/tasks/${taskId}`);
        return res.data;
    },

    /**
     * Cập nhật công việc.
     * @param {number} taskId - ID công việc
     * @param {Object} taskData - Dữ liệu cập nhật (name, status, owner_id, mo, ml, mp, cost_total, etc.)
     * @returns {Promise<Object>} Thông tin task sau cập nhật
     */
    updateTask: async (taskId, taskData) => {
        const res = await axiosInstance.put(`/tasks/${taskId}`, taskData);
        return res.data;
    },

    /**
     * Xóa công việc.
     * @param {number} taskId - ID công việc
     * @returns {Promise<Object>} Kết quả xóa
     */
    deleteTask: async (taskId) => {
        const res = await axiosInstance.delete(`/tasks/${taskId}`);
        return res.data;
    },

    /**
     * Lấy dữ liệu Kanban - tasks grouped by status (TODO, DOING, DONE).
     * @param {number} projectId - ID dự án
     * @returns {Promise<Object>} {todo[], doing[], done[]}
     */
    getTasksByStatus: async (projectId) => {
        const res = await axiosInstance.get(`/projects/${projectId}/tasks/kanban`);
        return res.data;
    },

    /**
     * Lấy công việc trong khoảng thời gian (cho Gantt Chart).
     * @param {number} projectId - ID dự án
     * @param {string} startDate - Ngày bắt đầu (YYYY-MM-DD)
     * @param {string} endDate - Ngày kết thúc (YYYY-MM-DD)
     * @returns {Promise<Object>} Danh sách tasks trong khoảng thời gian
     */
    getTasksByDateRange: async (projectId, startDate, endDate) => {
        const res = await axiosInstance.get(`/projects/${projectId}/tasks?start_date=${startDate}&end_date=${endDate}`);
        return res.data;
    }
};