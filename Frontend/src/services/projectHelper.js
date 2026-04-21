import { projectService } from "./projectService";

/**
 * Lấy project ID từ project code
 * @param {string} projectCode - Project code (e.g., "PRJMNG001")
 * @returns {Promise<number>} Project ID
 */
export const getProjectIdByCode = async (projectCode) => {
    try {
        // Lấy danh sách projects của user
        const response = await projectService.getMyProjects();
        // Tìm project có code match
        const project = response.projects.find(p => p.project_code === projectCode);
        if (!project) {
            throw new Error(`Project với code "${projectCode}" không tồn tại`);
        }
        return project.id;
    } catch (error) {
        console.error("Lỗi khi lấy project ID:", error);
        throw error;
    }
};

/**
 * Lấy danh sách tasks của project bằng project code
 * @param {string} projectCode - Project code
 * @returns {Promise<Object>} Tasks data
 */
export const getTasksByProjectCode = async (projectCode) => {
    try {
        const projectId = await getProjectIdByCode(projectCode);
        return await getTasksByProjectId(projectId);
    } catch (error) {
        console.error("Lỗi khi lấy tasks:", error);
        throw error;
    }
};

/**
 * Lấy danh sách tasks của project bằng project ID
 * @param {number} projectId - Project ID
 * @returns {Promise<Object>} Tasks data
 */
export const getTasksByProjectId = async (projectId) => {
    const { taskService } = await import("./taskService");
    return await taskService.getTasks(projectId);
};
