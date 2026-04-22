import axiosInstance from "./axiosConfig";

export const projectService = {
    /**
     * Tạo dự án mới. User tạo sẽ tự động trở thành PM.
     * @param {Object} projectData - {project_code, name, description}
     * @returns {Promise<Object>} Thông tin project vừa tạo
     */
    createProject: async (projectData) => {
        const res = await axiosInstance.post('/projects', projectData);
        return res.data;
    },

    /**
     * Join dự án bằng project code.
     * @param {string} projectCode - Mã dự án
     * @returns {Promise<Object>} Thông tin project
     */
    joinProject: async (projectCode) => {
        const payload = { project_code: projectCode };
        const res = await axiosInstance.post('/projects/join', payload);
        return res.data;
    },

    /**
     * Lấy danh sách dự án của user hiện tại.
     * @returns {Promise<Object>} {total, projects[]}
     */
    getMyProjects: async () => {
        const res = await axiosInstance.get('/projects');
        return res.data;
    },

    /**
     * Lấy chi tiết dự án theo ID.
     * @param {number} projectId - ID dự án
     * @returns {Promise<Object>} Thông tin project
     */
    getProjectDetail: async (projectId) => {
        const res = await axiosInstance.get(`/projects/${projectId}`);
        return res.data;
    }
};