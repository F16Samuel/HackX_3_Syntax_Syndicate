import { Route, Routes } from "react-router-dom";
import Home from "../Pages/Home";
import Login from "../Pages/Login";
import SignUp from "../Pages/SignUp";
import StudentDashboard from "../Pages/StudentDashboard";


function CustomRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login/>} />
            <Route path="/signUp" element={<SignUp/>} />
            <Route path="/candidate" element={<StudentDashboard/>} />
        </Routes>
    );
};

export default CustomRoutes;
