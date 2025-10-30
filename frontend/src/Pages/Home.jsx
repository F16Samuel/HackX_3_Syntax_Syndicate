import { Link } from 'react-router-dom';
import Navbar from '../Components/Navbar';


function Home() {

  return (
    <div className="text-white min-h-screen flex flex-col justify-between relative overflow-hidden">
      {/* ===== Navbar ===== */}
      <Navbar/>


      {/* ===== Hero Section ===== */}
        <div className="flex flex-col items-center justify-center grow text-center px-6">
            <h2 className="h-17 text-5xl sm:text-6xl font-extrabold mb-2 bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(123,97,255,0.4)]">
            The Future Of Hiring
            </h2>
            <p className="text-xl sm:text-2xl text-gray-300 leading-relaxed font-serif ">
            We redefine hiring with AI - analyzing <br></br>how candidates reason, adapt, and think beyond the obvious.
            </p>
        </div>
    </div>
  );
}

export default Home;
