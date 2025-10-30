// Page: Login
// Route: /login

import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // Adjusted path

const Login = () => {
  const [role, setRole] = useState("candidate"); // Default to candidate
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password, role);
      // On successful login, navigate to a protected page
      navigate("/dashboard"); 
    } catch (err) {
      console.error("Login failed:", err);
      setError(err.response?.data?.detail || "An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Navbar on top */}
      <Navbar />

      {/* Login content */}
      <div className="flex flex-col items-center justify-center flex-grow px-6 mt-16 relative z-10">
        <div className="bg-[#111] bg-opacity-60 backdrop-blur-md p-8 rounded-2xl shadow-[0_0_25px_rgba(255,80,40,0.3)] max-w-md w-full">
          <h2 className="text-4xl font-extrabold text-center mb-6 bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent">
            Welcome Back
          </h2>

          {/* Toggle: Candidate / Recruiter */}
          <div className="flex justify-center mb-6">
            <div className="flex items-center bg-[#1a1a1a] rounded-full p-1 border border-gray-700">
              <button
                type="button"
                onClick={() => setRole("candidate")}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                  role === "candidate"
                    ? "bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                Candidate
              </button>
              <button
                type="button"
                onClick={() => setRole("recruiter")}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                  role === "recruiter"
                    ? "bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                Recruiter
              </button>
            </div>
          </div>

          {/* Form */}
          <form className="space-y-5" onSubmit={handleSubmit}>
            {/* Email */}
            <div>
              <label className="block text-gray-300 mb-1 text-sm">Email</label>
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full px-4 py-2 rounded-lg bg-[#1a1a1a] border border-gray-700 focus:outline-none focus:ring-2 focus:ring-[#ff2e2e] text-white placeholder-gray-500 transition"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-gray-300 mb-1 text-sm">
                Password
              </label>
              <input
                type="password"
                placeholder="Enter Your password"
                className="w-full px-4 py-2 rounded-lg bg-[#1a1a1a] border border-gray-700 focus:outline-none focus:ring-2 focus:ring-[#ff2e2e] text-white placeholder-gray-500 transition"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <p className="text-center text-red-400 text-sm">{error}</p>
            )}

            {/* Login button */}
            <button
              type="submit"
              className="w-full py-2 mt-3 font-semibold rounded-lg bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] hover:shadow-[0_0_20px_rgba(255,80,40,0.6)] transition-transform duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              {isLoading
                ? "Logging in..."
                : `Login as ${role.charAt(0).toUpperCase() + role.slice(1)}`}
            </button>
          </form>

          {/* Sign up link */}
          <p className="text-center text-gray-400 mt-5 text-sm">
            Don't have an account?{" "}
            <Link
              to="/signUp"
              className="text-[#ff6b00] hover:text-[#ff2e2e] font-semibold transition"
            >
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

