import { Link } from "react-router-dom";
import "@/index.css"; // for the glow animation CSS (make sure this line exists if animation is in index.css)

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 w-full z-20 flex items-center justify-between px-8 py-6">
      {/* Logo - Left */}
      <Link
        to="/home"
        className="text-2xl font-bold tracking-wide bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent drop-shadow-[0_0_8px_rgba(255,80,40,0.4)] transition-transform duration-300 hover:scale-105 hover:drop-shadow-[0_0_15px_rgba(255,80,40,0.8)] animate-glow"
      >
        Advent
      </Link>

      {/* Nav Links - Right */}
      <div className="flex gap-8 text-gray-300 font-medium">
        <Link
          to="/recruiter"
          className="hover:text-white hover:drop-shadow-[0_0_10px_rgba(255,80,40,0.6)] transition duration-300"
        >
          Recruiter Demo
        </Link>
        <Link
          to="/candidate-dummy"
          className="hover:text-white hover:drop-shadow-[0_0_10px_rgba(255,80,40,0.6)] transition duration-300"
        >
          Candidate Demo
        </Link>
        <Link
          to="/login"
          className="hover:text-white hover:drop-shadow-[0_0_10px_rgba(255,80,40,0.6)] transition duration-300"
        >
          Login
        </Link>
        <Link
          to="/signUp"
          className="hover:text-white hover:drop-shadow-[0_0_10px_rgba(255,80,40,0.6)] transition duration-300"
        >
          Register
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
