import React from "react";
import Navbar from "../components/Navbar"; // adjust path if needed
import { Link } from "react-router-dom";

const Login = () => {
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
                placeholder="Enter your password"
                className="w-full px-4 py-2 rounded-lg bg-[#1a1a1a] border border-gray-700 focus:outline-none focus:ring-2 focus:ring-[#ff2e2e] text-white placeholder-gray-500 transition"
              />
            </div>

            {/* Login button */}
            <button
              type="submit"
              className="w-full py-2 mt-3 font-semibold rounded-lg bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] hover:shadow-[0_0_20px_rgba(255,80,40,0.6)] transition-transform duration-200 hover:scale-105"
            >
              Login
            </button>
          </form>

          {/* Register link */}
          <p className="text-center text-gray-400 mt-5 text-sm">
            Don’t have an account?{" "}
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
