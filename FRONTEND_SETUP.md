# 📚 HƯỚNG DẪN CÁCH SỬ DỤNG THƯ VIỆN - FRONTEND

## 🗂️ DANH SÁCH THƯ VIỆN FRONTEND

### **DEPENDENCIES (Thư viện chính)**

| Thư viện              | Phiên bản | Mục đích                                                                  |
| --------------------- | --------- | ------------------------------------------------------------------------- |
| **react**             | 19.2.4    | Library UI tạo components, state management, lifecycle hooks              |
| **react-dom**         | 19.2.4    | Render React components lên DOM, hydration SSR                            |
| **react-router-dom**  | 7.14.0    | Client-side routing, navigating giữa pages mà không reload toàn trang     |
| **axios**             | 1.15.0    | HTTP client gọi API. Interceptors cho auth tokens, error handling tự động |
| **antd**              | 6.3.6     | Ant Design - UI component library (Table, Button, Form, Modal, etc.)      |
| **@ant-design/icons** | 6.1.1     | Icon library dùng với Ant Design (UserOutlined, EditOutlined, etc.)       |
| **tailwindcss**       | 3.4.19    | Utility-first CSS framework (className="flex items-center gap-2")         |
| **lucide-react**      | 1.8.0     | Modern icon library (Mail, Lock, Edit, Plus, etc.)                        |
| **gantt-task-react**  | 0.3.9     | Gantt chart component cho timeline visualization các tasks                |
| **framer-motion**     | 12.38.0   | Animation library smooth transitions, page animations                     |

---

### **DEV DEPENDENCIES (Chỉ dùng khi develop)**

| Thư viện                        | Phiên bản | Mục đích                                                                    |
| ------------------------------- | --------- | --------------------------------------------------------------------------- |
| **vite**                        | 8.0.4     | Build tool tương tự Webpack nhưng nhanh hơn rất nhiều (dev server hiệu quả) |
| **@vitejs/plugin-react**        | 6.0.1     | Plugin Vite hỗ trợ React JSX                                                |
| **tailwindcss**                 | 3.4.19    | Utility CSS framework                                                       |
| **postcss**                     | 8.5.9     | CSS preprocessor, xử lý Tailwind directives                                 |
| **autoprefixer**                | 10.4.27   | Tự động thêm vendor prefixes cho CSS (Chrome, Firefox, Safari, IE)          |
| **eslint**                      | 9.39.4    | Linter kiểm tra code quality, syntax errors                                 |
| **@eslint/js**                  | 9.39.4    | ESLint rules chuẩn JavaScript                                               |
| **eslint-plugin-react-refresh** | 0.5.2     | ESLint rules cho React Fast Refresh (HMR)                                   |
| **eslint-plugin-react-hooks**   | 7.0.1     | ESLint rules kiểm tra React hooks usage (deps, rules of hooks)              |
| **@types/react**                | 19.2.14   | TypeScript type definitions cho React (optional, nếu dùng TS)               |
| **@types/react-dom**            | 19.2.3    | TypeScript type definitions cho ReactDOM                                    |
| **globals**                     | 17.4.0    | Global variables definitions cho ESLint                                     |

---

## 🚀 CÀI ĐẶT FRONTEND

### Yêu cầu tiên quyết:

- Node.js 16+ (có npm)

### Bước cài:

```bash
# 1. Vào thư mục frontend
cd Frontend

# 2. Cài đặt thư viện (tạo node_modules/)
npm install

# 3. Chạy development server
npm run dev

# 4. Build production
npm run build

# 5. Preview build
npm run preview

# 6. Lint check code quality
npm run lint
```

### Server dev chạy ở:

- Frontend: http://localhost:5173 (hoặc port khác nếu 5173 busy)

---

## 📝 TAILWINDCSS + POSTCSS

### File cấu hình:

- `tailwind.config.js` - Cấu hình Tailwind (colors, fonts, spacing)
- `postcss.config.js` - Cấu hình PostCSS (autoprefixer, tailwind)
- `src/index.css` - Import Tailwind directives: `@tailwind base`, `@tailwind components`, `@tailwind utilities`

### Dark mode:

- Sử dụng `dark:` prefix trong className
- Ví dụ: `<div className="bg-white dark:bg-slate-800">` → Trắng ở light mode, xám tối ở dark mode

---

## 🎨 ANT DESIGN + LUCIDE REACT

### Ant Design (antd):

- Component library chuyên nghiệp (Table, Form, Modal, Button, etc.)
- CSS tích hợp sẵn, không cần style thêm
- Ví dụ:

  ```jsx
  import { Table, Button, Modal } from "antd";
  import { EditOutlined } from "@ant-design/icons";

  <Button icon={<EditOutlined />}>Sửa</Button>;
  ```

### Lucide React:

- Lightweight icon library hơn Ant Design icons
- Smooth, modern design
- Ví dụ:

  ```jsx
  import { Mail, Lock, Edit } from "lucide-react";

  <Mail size={18} className="text-slate-400" />;
  ```

---

## 🔌 AXIOS INTERCEPTORS

File: `src/services/axiosConfig.js`

```javascript
import axiosInstance from "./axiosConfig";

// Request interceptor: thêm token vào mỗi request
// Response interceptor: nếu 401, clear token & redirect /login

// Dùng: axiosInstance.get('/users/me') thay vì axios.get()
```

---

## 🗂️ CẤU TRÚC THƯ MỤC FRONTEND

```
Frontend/
├── src/
│   ├── components/
│   │   ├── common/         # Reusable components (Input, Button, etc.)
│   │   └── layout/         # Layout components (Header, Sidebar)
│   ├── page/               # Pages (Login, WBS, PERT, Kanban, etc.)
│   ├── services/           # API calls (authService, taskService, etc.)
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Helper functions (toast, tree builder, etc.)
│   ├── context/            # React Context (AuthContext)
│   ├── assets/             # Static files (images, fonts)
│   ├── App.jsx             # Root component
│   ├── main.jsx            # Entry point
│   ├── index.css           # Global styles + Tailwind
│   └── App.css             # App-specific styles
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
├── eslint.config.js        # ESLint configuration
└── package.json            # Dependencies
```

---

## ✅ CHECKLIST SETUP HOÀN CHỈNH

Backend:

- [x] Cài Python 3.9+
- [x] `pip install -r requirements.txt`
- [x] Setup `.env` file
- [x] `alembic upgrade head` (migrations)
- [x] `uvicorn main:app --reload` (chạy server)

Frontend:

- [x] Cài Node.js 16+
- [x] `npm install`
- [x] `npm run dev` (chạy dev server)
- [x] Test API calls qua localhost:8000

---
