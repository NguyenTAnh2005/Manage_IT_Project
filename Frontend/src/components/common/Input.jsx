const Input = ({icon,label,placeholder, value, onChange, isRequired }) =>{
    return (
        <div className="flex flex-col w-full  ">
            {label !=""&&(
                <span className=" capitalize font-semibold">
                    {label}
                </span>
            )}
           
            <div className="flex relative ">
                <input 
                    className="indent-10 py-2 w-full focus:outline-none border border-light-muted rounded-md bg-light-bg dark:bg-dark-bg "
                    type="text" 
                    required = {isRequired}
                    placeholder={placeholder}
                    value={value}
                    onChange={onChange}
                />
                {icon}
            </div>
            
        </div>
    )
}
export default Input;