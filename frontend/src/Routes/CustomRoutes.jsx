import { Route, Routes } from "react-router-dom";
import Home from "@/Pages/Home"; // <-- MODIFIED PATH
import Login from "@/Pages/Login"; // <-- MODIFIED PATH
import SignUp from "@/Pages/SignUp"; // <-- MODIFIED PATH
import StudentDashboard from "@/Pages/StudentDashboard"; // <-- MODIFIED PATH
import Welcome from "../Pages/Welcome";
import StudentDashboardDummy from "@/Pages/StudentDashboardDummy"; // <-- MODIFIED PATH


function CustomRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login/>} />
            <Route path="/signUp" element={<SignUp/>} />
            <Route path="/candidate" element={<StudentDashboard/>} />
            <Route path="/candidate-dummy" element={<StudentDashboardDummy/>} />
            <Route path="/exam" element={<Welcome/>} />
        </Routes>
    );
};

export default CustomRoutes;
