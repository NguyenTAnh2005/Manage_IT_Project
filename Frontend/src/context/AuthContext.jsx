/* eslint-disable react-refresh/only-export-components */

import { createContext, useState, useContext } from "react";

// COntext 
const AuthContext = createContext();
export const AuthProvider = ({children}) =>{
    const [token, setToken] = useState(()=> localStorage.getItem("PM_access_token"));
    const [projectCode , setProjectCode] = useState(()=> localStorage.getItem("PM_project_code"));


    // If Login Successed 
    const logIn = (newToken) =>{
        setToken(newToken);
        localStorage.setItem("PM_access_token", newToken);
    }

    // If Logout 
    const logOut = () =>{
        setToken(null);
        localStorage.removeItem("PM_access_token");
        localStorage.removeItem("PM_project_code");
    }

    // If Join Project 
    const joinProject = (newCode) =>{
        setProjectCode(newCode);
        localStorage.setItem("PM_project_code", newCode);
    }

    // If out the Project 
    const outProject = () =>{
        setProjectCode(null);
        localStorage.removeItem("PM_project_code");
    }


    // Save all data in value 
    const value = {
        token,
        projectCode, 
        isAuthenticated: !!token,
        logIn,
        logOut,
        joinProject,
        outProject
    };
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
};

export const useAuth = () =>{
    return useContext(AuthContext);
}