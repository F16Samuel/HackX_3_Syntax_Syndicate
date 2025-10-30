import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Link } from "react-router-dom";

const SignUp = () => {
  const [role, setRole] = useState("candidate"); // Default to candidate

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Navbar on top */}
      <Navbar />

      {/* Signup content */}
      <div className="flex flex-col items-center justify-center flex-grow px-6 mt-16 relative z-10">
        <div className="bg-[#111] bg-opacity-60 backdrop-blur-md p-8 rounded-2xl shadow-[0_0_25px_rgba(255,80,40,0.3)] max-w-md w-full">
          <h2 className="text-4xl font-extrabold text-center mb-6 bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent">
            Create Account
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
          <form className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-gray-300 mb-1 text-sm">Email</label>
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full px-4 py-2 rounded-lg bg-[#1a1a1a] border border-gray-700 focus:outline-none focus:ring-2 focus:ring-[#ff2e2e] text-white placeholder-gray-500 transition"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-gray-300 mb-1 text-sm">
                Password
              </label>
              <input
                type="password"
                placeholder="Create a password"
                className="w-full px-4 py-2 rounded-lg bg-[#1a1a1a] border border-gray-700 focus:outline-none focus:ring-2 focus:ring-[#ff2e2e] text-white placeholder-gray-500 transition"
              />
            </div>

            {/* Register button */}
            <button
              type="submit"
              className="w-full py-2 mt-3 font-semibold rounded-lg bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] hover:shadow-[0_0_20px_rgba(255,80,40,0.6)] transition-transform duration-200 hover:scale-105"
            >
              Register as {role.charAt(0).toUpperCase() + role.slice(1)}
            </button>
          </form>

          {/* Login link */}
          <p className="text-center text-gray-400 mt-5 text-sm">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-[#ff6b00] hover:text-[#ff2e2e] font-semibold transition"
            >
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
