export const project_1 = [
    // ===== 1. KHỞI TẠO & PHÂN QUYỀN =====
    {
        id: "T1",
        name: "Khởi tạo & Phân quyền (Login)",
        assignee: "Tuấn Anh + Vũ",
        status: "DOING",
        startDate: "2024-05-01",
        duration: 6,
        priority: "High",
        parentId: null
    },
    {
        id: "T1.10",
        name: "Setup base project",
        assignee: "Tuấn Anh + Vũ",
        status: "DONE",
        startDate: "2024-05-01",
        duration: 1,
        priority: "High",
        parentId: "T1"
    },
    {
        id: "T1.20",
        name: "Thiết kế Database",
        assignee: "Vũ",
        status: "DONE",
        startDate: "2024-05-02",
        duration: 1,
        priority: "High",
        parentId: "T1"
    },
    {
        id: "T1.30",
        name: "Chức năng Đăng nhập & Auth",
        assignee: "Tuấn Anh + Vũ",
        status: "DOING",
        startDate: "2024-05-03",
        duration: 2,
        priority: "High",
        parentId: "T1"
    },
    {
        id: "T1.40",
        name: "Join dự án bằng mã",
        assignee: "Tuấn Anh + Vũ",
        status: "TODO",
        startDate: "2024-05-05",
        duration: 2,
        priority: "Medium",
        parentId: "T1"
    },

    // ===== 2. QUẢN LÝ WBS & PERT =====
    {
        id: "T2",
        name: "Quản lý WBS & PERT",
        assignee: "Tuấn Anh + Vũ",
        status: "TODO",
        startDate: "2024-05-07",
        duration: 5,
        priority: "High",
        parentId: null
    },
    {
        id: "T2.10",
        name: "Giao diện bảng công việc (WBS)",
        assignee: "Tuấn Anh",
        status: "TODO",
        startDate: "2024-05-07",
        duration: 2,
        priority: "High",
        parentId: "T2"
    },
    {
        id: "T2.20",
        name: "Tính toán PERT",
        assignee: "Vũ",
        status: "TODO",
        startDate: "2024-05-09",
        duration: 2,
        priority: "High",
        parentId: "T2"
    },
    {
        id: "T2.30",
        name: "Quản lý chi phí",
        assignee: "Tuấn Anh + Vũ",
        status: "TODO",
        startDate: "2024-05-10",
        duration: 1,
        priority: "Medium",
        parentId: "T2"
    },

    // ===== 3. TRỰC QUAN HÓA =====
    {
        id: "T3",
        name: "Trực quan hóa (Kanban & Gantt)",
        assignee: "Tuấn Anh + Vũ",
        status: "TODO",
        startDate: "2024-05-12",
        duration: 6,
        priority: "High",
        parentId: null
    },
    {
        id: "T3.10",
        name: "Bảng Kanban",
        assignee: "Tuấn Anh",
        status: "TODO",
        startDate: "2024-05-12",
        duration: 2,
        priority: "High",
        parentId: "T3"
    },
    {
        id: "T3.20",
        name: "Biểu đồ Gantt",
        assignee: "Tuấn Anh",
        status: "TODO",
        startDate: "2024-05-14",
        duration: 2,
        priority: "High",
        parentId: "T3"
    },
    {
        id: "T3.30",
        name: "Tổng duyệt & báo cáo",
        assignee: "Tuấn Anh + Vũ",
        status: "TODO",
        startDate: "2024-05-16",
        duration: 2,
        priority: "Medium",
        parentId: "T3"
    }
];