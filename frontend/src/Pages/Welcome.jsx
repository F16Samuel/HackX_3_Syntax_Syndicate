import React, { useRef } from 'react';

/**
 * A placeholder component for the left section.
 * In a real app, this would be imported from "../components/WelcomeLeft"
 */
const WelcomeLeft = () => (
  <div className="w-2/5 bg-gray-900 p-16 flex flex-col justify-center items-center relative z-0">
    <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-black opacity-50"></div>
    <div className="relative z-10 text-center">
      <h1 className="text-5xl font-bold mb-4 text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
        Welcome
      </h1>
      <p className="text-lg text-gray-300">
        Prepare for your assessment.
      </p>
    </div>
  </div>
);

/**
 * The main Welcome component.
 * It shows instructions and a continue button that navigates to an external site.
 */
const Welcome = () => {
  const rightSectionRef = useRef(null);

  // This function handles the button click
  const handleContinue = () => {
    // 1. This is the external URL you want to navigate to.
    const externalWebsiteUrl = "https://advent-hackx-sampletest.vercel.app/";

    // 2. Scroll the local section first (optional cosmetic effect)
    if (rightSectionRef.current) {
      rightSectionRef.current.scrollBy({
        top: 180,
        behavior: "smooth",
      });
    }

    // 3. Navigate to the external site after a short delay
    setTimeout(() => {
      // This line is what makes you "travel to the other site"
      window.location.href = externalWebsiteUrl;
    }, 300); // 300ms delay
  };

  return (
    <div className="flex w-screen h-screen text-white overflow-hidden relative font-sans">
      {/* Left section */}
      <WelcomeLeft />

      {/* Right section (Scrollable) */}
      <div
        ref={rightSectionRef}
        className="w-3/5 flex flex-col justify-center items-start px-16 overflow-y-auto
         bg-white/5 backdrop-blur-lg border-l border-white/10 relative z-10"
        style={{
          background: 'rgba(20, 20, 30, 0.7)', // Darker glass effect
        }}
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
            onClick={handleContinue} // This button triggers the navigation
            className="px-6 py-3 rounded-lg text-white font-medium 
             bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] 
             shadow-[0_0_20px_rgba(255,0,106,0.5)] 
             hover:shadow-[0_0_30px_rgba(255,0,106,0.8)] 
             transition-all duration-300 border border-white/10
             transform hover:scale-105"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
