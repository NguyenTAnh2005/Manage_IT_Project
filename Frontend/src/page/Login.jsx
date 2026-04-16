import { useState, useEffect } from "react";
import {useAuth} from "../context/AuthContext"
import {authService} from "../services/authService"
import {useNavigate } from "react-router-dom";
import InputPassword from "../components/common/InputPassword"
import Input from "../components/common/Input"

import {Mail} from 'lucide-react'

const Login = () =>{
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const {login, isAuthenticated} = useAuth();


    const navigate = useNavigate();

    useEffect(()=>{
        if(isAuthenticated){
            navigate("/join-project");
        };
    },[isAuthenticated, navigate]);

    const handleLogin = async(e) =>{
        e.preventDefault();
        setError('');
        setLoading(true)

        try{
            const res = await authService.login(email, password);
            login(res.access_token);
            navigate("/join-project");
        }
        catch (err){
            console.error("Failed to login: ", err);
            setError("Failed to login!!");
        }
        finally{
            setLoading(false);
        }
    }

    return(
        <div className="flex flex-col relative items-center min-h-screen border justify-center text-light-text bg-light-bg dark:bg-dark-bg dark:text-dark-text">
            <form onSubmit={handleLogin} 
                className="flex gap-4 p-8 flex-col max-w-md items-center outline-none rounded-xl shadow-2xl dark:shadow-gray-400"
            >
                <p className="font-bold text-2xl text-wrap text-center text-primary">
                    👋 Chào mừng trở lại! 🗿
                </p>
                <p className="text-base">
                    Đăng nhập để quản lý dự án của bạn!
                </p>
                {
                    error&&(
                    <span className=" bg-red-50 border border-red-200 text-red-600 w-full text-sm italic px-2 py-2 rounded-sm">
                        ⚠️ {error}
                    </span>
                    )
                }
                
                <Input
                    placeholder={"abc...@...com"}
                    label={"Email"}
                    onChange={(e) => setEmail(e.target.value)}
                    isRequired={true}
                    icon={<Mail className="absolute top-[25%] left-[1%] text-dark-bg"/>}
                    value={email}
                />
                <InputPassword
                    placehoder={"...."}
                    label={"Mật khẩu"}
                    onChange={(e) => setPassword(e.target.value)}
                    value={password}
                />
                <button type="Submit" className={` w-full btn-primary ${loading&&'opacity-40 cursor-not-allowed '}`}>
                    {loading? "Waiting response ..... " : "Đăng nhập"}
                </button>
            </form>
        </div>
        
    )
};
export default Login;