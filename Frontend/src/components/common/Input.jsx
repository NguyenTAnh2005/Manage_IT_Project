const Input = ({ icon, label, placeholder, value, onChange, isRequired, type = "text" }) => {
    return (
        <div style={{ display: "flex", flexDirection: "column", width: "100%", marginBottom: "15px" }}>
            {label && (
                <label style={{
                    marginBottom: "5px",
                    fontWeight: "600",
                    fontSize: "14px",
                    color: "#333",
                    textTransform: "capitalize"
                }}>
                    {label}
                </label>
            )}
            <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                <input
                    style={{
                        width: "100%",
                        padding: "10px 10px 10px 40px",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        fontSize: "14px",
                        outline: "none",
                        boxSizing: "border-box"
                    }}
                    type={type}
                    required={isRequired}
                    placeholder={placeholder}
                    value={value}
                    onChange={onChange}
                />
                {icon && <span style={{ position: "absolute", left: "10px", fontSize: "16px" }}>{icon}</span>}
            </div>
        </div>
    );
};

export default Input;