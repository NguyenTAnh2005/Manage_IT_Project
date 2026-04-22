/**
 * Utilities cho thiết kế responsive và các class sử dụng lại.
 * Dựa trên Tailwind CSS cho mobile-first design.
 * Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
 */

export const responsiveClasses = {
    // Độ rộng container
    container: "w-full sm:max-w-md md:max-w-2xl lg:max-w-4xl mx-auto px-4 sm:px-6",
    
    // Card/Form containers
    card: "bg-white dark:bg-slate-800 rounded-lg sm:rounded-xl shadow-sm sm:shadow-md hover:shadow-md transition-shadow duration-200 p-4 sm:p-6 md:p-8",
    
    // Kích thước button
    btnSmall: "px-3 py-2 text-xs sm:text-sm",
    btnMedium: "px-4 py-2 sm:py-3 text-sm sm:text-base",
    btnLarge: "px-6 py-3 sm:py-4 text-base sm:text-lg w-full sm:w-auto",
    
    // Layout lưới
    gridAuto: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6",
    gridDynamic: "flex flex-col sm:flex-row gap-4 sm:gap-6",
    
    // Kiểu chữ
    h1: "text-2xl sm:text-3xl md:text-4xl font-bold",
    h2: "text-xl sm:text-2xl md:text-3xl font-bold",
    h3: "text-lg sm:text-xl font-bold",
    
    // Khoảng cách
    spacingY: "space-y-3 sm:space-y-4 md:space-y-6",
    spacingX: "space-x-2 sm:space-x-3 md:space-x-4",
};

/**
 * Class cho bảng responsive.
 * Mobile: Lăn ngang, text nhỏ hơn
 * Tablet+: Layout bình thường
 */
export const responsiveTableClasses = {
    wrapper: "overflow-x-auto -mx-4 sm:mx-0",
    table: "w-full text-xs sm:text-sm md:text-base",
    scrollableBody: "max-h-[300px] sm:max-h-[500px] overflow-y-auto",
};

/**
 * Classes tương thích với chế độ tối.
 */
export const darkModeClasses = {
    bg: "bg-light-bg dark:bg-dark-bg",
    text: "text-light-text dark:text-dark-text",
    border: "border-slate-200 dark:border-slate-700",
    card: "bg-white dark:bg-slate-800",
    input: "bg-light-bg dark:bg-slate-700 border-light-border dark:border-slate-600 text-light-text dark:text-dark-text",
};
