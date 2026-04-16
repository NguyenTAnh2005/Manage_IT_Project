import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export const ProtectedRoute = () =>{
    const {isAuthenticated, projectCode} = useAuth();
    const location = useLocation();

    if(!isAuthenticated){
        return <Navigate to={'/login'} replace/>
    }
    if(!projectCode){
        if (location.pathname !== '/join-project'){
            return <Navigate to = {'/join-project'} replace/>
        }
    }
    if(projectCode){
        if(location.pathname === '/join-project'){
            return <Navigate to={`/dashboard/${projectCode}/wbs`} replace />
        }
    }
    return <Outlet/>
}