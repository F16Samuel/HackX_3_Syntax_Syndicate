import { Route, Routes } from "react-router-dom";
import Home from "@/Pages/Home"; // <-- MODIFIED PATH
import Login from "@/Pages/Login"; // <-- MODIFIED PATH
import SignUp from "@/Pages/SignUp"; // <-- MODIFIED PATH
import StudentDashboard from "@/Pages/StudentDashboard"; // <-- MODIFIED PATH
import Welcome from "../Pages/Welcome";
import StudentDashboardDummy from "@/Pages/StudentDashboardDummy"; // <-- MODIFIED PATH
import RecruiterDashboardDummy from "@/Pages/Dashboard"; // <-- MODIFIED PATH
import NewTestForm from "@/Pages/NewTestForm"; // <-- MODIFIED PATH
import TestTakingDummy from "@/Pages/TestResults"; // <-- MODIFIED PATH


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
            <Route path="/recruiter-dummy" element={<RecruiterDashboardDummy />} />
            <Route path="/new-test" element={<NewTestForm />} />
            <Route path="/test/:testId" element={<TestTakingDummy />} />
        </Routes>
    );
};

export default CustomRoutes;
