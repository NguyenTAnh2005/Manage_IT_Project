import { useState, useEffect } from "react";
import {Moon, Sun} from 'lucide-react'

function ThemeToggle(){
    // ============== LƯU GIÁ TRỊ THEME VÀO LOCAL STORAGE
    const [theme, setTheme] = useState(()=>{
        // Mặc định set giá trị  theme là light nếu như chưa có theme
        return localStorage.getItem('theme') || 'light';
    });

    // ============== BẮT SỰ KIỆN KHI STATE THAY ĐỔI
    useEffect(()=>{
        // Lấy thẻ HTML cao nhất của html để set class dark
        const htmlElement = document.documentElement;
        if (theme === 'dark'){
            htmlElement.classList.add('dark')
            localStorage.setItem('theme','dark')
        }
        else{
            htmlElement.classList.remove('dark')
            localStorage.setItem('theme','light')
        }
    }, [theme]);

    // ============= HÀM XỬ LÝ KHI CLICK NÚT
    const toggleTheme = () =>{
        setTheme(theme === 'light' ? 'dark' : 'light')
    };
    return (
        <button onClick={toggleTheme} className="btn-primary flex items-center gap-2 transition-all ease-linear duration-500 ">
            {
                theme === 'light' 
                ? (
                    <>
                        Light <Sun className="text-xl" />
                    </>
                )
                : (
                    <>
                        Dark <Moon className="text-xl" />
                    </>
                )
            }
        </button>
    )
}
export default ThemeToggle;