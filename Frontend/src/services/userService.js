import { authService } from "./authService";
import { projectService } from "./projectService";

/**
 * Lấy thông tin user hiện tại
 * @returns {Promise<Object>} User info {id, email, full_name, ...}
 */
export const getCurrentUser = async () => {
    try {
        const user = await authService.getMe();
        return user;
    } catch (error) {
        console.error("Lỗi khi lấy thông tin user:", error);
        throw error;
    }
};

/**
 * Lấy role của user hiện tại trong project
 * @param {number} projectId - Project ID
 * @returns {Promise<string>} Role ("PM" hoặc "MEMBER")
 */
export const getUserRoleInProject = async (projectId) => {
    try {
        const axiosInstance = (await import('./axiosConfig')).default;
        const response = await axiosInstance.get(`/projects/${projectId}/my-role`);
        return response.data.role;
    } catch (error) {
        console.error("Lỗi khi lấy role user:", error);
        throw error;
    }
};

/**
 * Lấy role của user hiện tại trong project bằng project code
 * @param {string} projectCode - Project code
 * @returns {Promise<{role: string, projectId: number}>} {role, projectId}
 */
export const getUserRoleByProjectCode = async (projectCode) => {
    try {
        const response = await projectService.getMyProjects();
        const project = response.projects.find(p => p.project_code === projectCode);
        
        if (!project) {
            throw new Error(`Project với code "${projectCode}" không tồn tại`);
        }
        
        const role = await getUserRoleInProject(project.id);
        
        return {
            role,
            projectId: project.id
        };
    } catch (error) {
        console.error("Lỗi khi lấy role user:", error);
        throw error;
    }
};

/**
 * Check nếu user có phải PM không, nếu không thì throw error
 * @param {number} projectId - Project ID
 * @param {string} actionName - Tên hành động (dùng cho error message)
 * @throws {Error} Nếu user không phải PM
 */
export const checkProjectManagerPermission = async (projectId, actionName = "thao tác này") => {
    try {
        const role = await getUserRoleInProject(projectId);
        if (role !== "PM") {
            throw new Error(`Chỉ Trưởng dự án mới có thể ${actionName}. Bạn hiện là thành viên thường.`);
        }
        return true;
    } catch (error) {
        if (error.message.includes("Chỉ Trưởng dự án")) {
            throw error;
        }
        console.error("Lỗi khi kiểm tra quyền:", error);
        throw error;
    }
};
