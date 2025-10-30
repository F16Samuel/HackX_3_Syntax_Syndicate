import { useRef } from "react";
import WelcomeLeft from "../Components/WelcomeLeft";

const Welcome = ({ onContinue }) => {
  const rightSectionRef = useRef(null);

  const handleContinue = () => {
    if (rightSectionRef.current) {
      rightSectionRef.current.scrollBy({
        top: 180,
        behavior: "smooth",
      });
    }
    if (typeof onContinue === "function") {
      setTimeout(() => onContinue(), 300);
    }
  };

  return (
    <div className="flex w-screen h-screen text-white overflow-hidden relative">
      {/* Left section */}
      <WelcomeLeft />

      {/* Right section */}
      <div
        ref={rightSectionRef}
        className="w-3/5 flex flex-col justify-center items-start px-16 overflow-y-auto
        bg-white/10 backdrop-blur-lg border-l border-white/10 relative z-10"
      >
        <div className="text-5xl font-semibold mb-6 bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(255,0,100,0.6)]">
          Instructions
        </div>

        <div className="text-gray-300 leading-relaxed text-base mb-8 space-y-4">
          <p>
            1. This is a timed test. Please make sure you are not interrupted
            during the test, as the timer cannot be paused once started.
          </p>
          <p>
            2. Ensure you have a stable internet connection and avoid switching
            tabs during the assessment.
          </p>
          <p>
            3. Read each question carefully before submitting. Once submitted,
            you cannot revisit previous questions.
          </p>
        </div>

        {/* Continue Button */}
        <div className="flex gap-4 mt-4">
          <button
            className="px-6 py-3 rounded-lg text-white font-medium 
            bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] 
            shadow-[0_0_20px_rgba(255,0,106,0.5)] 
            hover:shadow-[0_0_30px_rgba(255,0,106,0.8)] 
            transition-all duration-300 border border-white/10"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
