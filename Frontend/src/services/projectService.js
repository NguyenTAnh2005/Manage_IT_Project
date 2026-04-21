import axiosInstance from "./axiosConfig";

export const projectService = {
    // Tạo dự án mới
    createProject: async (projectData) => {
        const res = await axiosInstance.post('/projects', projectData);
        return res.data;
    },

    // Gọi API để Join dự án
    joinProject: async (projectCode) => {
        const payload = {
            project_code: projectCode
        };
        const res = await axiosInstance.post('/projects/join', payload);
        return res.data;
    },

    // Lấy danh sách dự án của user
    getMyProjects: async () => {
        const res = await axiosInstance.get('/projects');
        return res.data;
    },

    // Lấy chi tiết dự án
    getProjectDetail: async (projectId) => {
        const res = await axiosInstance.get(`/projects/${projectId}`);
        return res.data;
    }
};