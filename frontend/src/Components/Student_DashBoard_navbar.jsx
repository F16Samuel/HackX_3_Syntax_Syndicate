import React from "react";

const DashBoard_navbar = () => {
  return (
    <nav className="flex items-center justify-between bg-black text-slate-100 px-6 py-3 shadow-sm">
      {/* Left Section - Logo + Search */}
      <div className="flex items-center gap-6">
        <div className="text-xl font-bold tracking-tight">
          hackX<span className="text-blue-400">3.0</span>
        </div>

        {/* Search bar */}
        <div className="flex items-center bg-gray-800 px-3 py-1 rounded-lg">
          <input
            type="text"
            placeholder="Search rounds..."
            className="bg-transparent focus:outline-none text-sm placeholder-gray-400"
          />
        </div>
      </div>

      {/* Center - Nav Links */}
      <div className="hidden md:flex items-center gap-6 text-sm font-serif">
        <a href="#" className="hover:text-blue-400 transition">Rounds</a>
        <a href="#" className="hover:text-blue-400 transition">Quizzes</a>
        <a href="#" className="hover:text-blue-400 transition">Events</a>
        <a href="#" className="hover:text-blue-400 transition">Practice</a>
        <a href="#" className="hover:text-blue-400 transition">More</a>
      </div>

      {/* Right - Buttons / Icons */}
      <div className="flex items-center gap-4">
        <button className="bg-gray-800 hover:bg-gray-700 px-3 py-1 rounded-lg text-sm font-medium">
          For Business
        </button>
        <div className="w-8 h-8 rounded-full bg-blue-400"></div>
      </div>
    </nav>
  );
};

export default DashBoard_navbar;
