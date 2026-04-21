import { useState } from "react";

export const InputPassword = ({ label, placeholder, value, onChange }) => {
    const [hidePass, setHidePass] = useState(true);

    const togglePasswordVisibility = () => {
        setHidePass(prev => !prev);
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", width: "100%", marginBottom: "15px" }}>
            <label style={{
                marginBottom: "5px",
                fontWeight: "600",
                fontSize: "14px",
                color: "#333",
                textTransform: "capitalize"
            }}>
                {label}
            </label>
            <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                <input
                    required
                    placeholder={placeholder}
                    onChange={onChange}
                    value={value}
                    style={{
                        width: "100%",
                        padding: "10px 40px 10px 40px",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        fontSize: "14px",
                        outline: "none",
                        boxSizing: "border-box"
                    }}
                    type={hidePass ? "password" : "text"}
                />
                <span style={{
                    position: "absolute",
                    left: "10px",
                    fontSize: "16px",
                    color: "#666"
                }}>
                    🔒
                </span>
                <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    style={{
                        position: "absolute",
                        right: "10px",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "18px",
                        padding: "0"
                    }}
                >
                    {hidePass ? "👁️" : "👁️‍🗨️"}
                </button>
            </div>
        </div>
    );
};

export default InputPassword;