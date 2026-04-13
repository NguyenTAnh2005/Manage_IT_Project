import { useState } from "react";
import { Eye, EyeOff, Lock } from "lucide-react";

const InputPassword = ({label, placehoder, value, onChange}) =>{
    const [hidePass, setHidePass] = useState(true);
    const changeModeType = () =>{
        setHidePass(prev => !prev);
    };

    return (
        <div className="flex flex-col w-full">
            <span className="capitalize font-semibold">
                {label}
            </span>
            <div className="flex relative">
                <input 
                    required
                    placeholder={placehoder}
                    onChange={onChange}
                    value={value}
                    className="indent-10 w-full py-2 focus:outline-none border border-light-muted rounded-md "
                    type={hidePass? "password" : "text"}
                />
                <>
                    <Lock className="text-2xl absolute top-[25%] left-[1%] text-dark-bg"/>
                </>
                <div 
                    onClick={changeModeType} 
                    className="flex justify-center items-center absolute right-0 h-full px-2">
                    {hidePass
                        ?(
                            <>
                                <EyeOff className="text-2xl text-dark-bg"/>
                            </>
                        )
                        :(
                            <>
                                <Eye className="text-2xl text-dark-bg"/>
                            </>
                        )}
                </div>
            </div>
            
        </div>
    )
}
export default InputPassword;