import React, { useEffect } from "react";

const ParticlesBackground = () => {
  useEffect(() => {
    const numStars = 1000; // reduced for performance, you can tweak
    const starfield = document.createElement("div");
    starfield.classList.add("starfield");

    for (let i = 0; i < numStars; i++) {
      const star = document.createElement("div");
      star.classList.add("star");

      const x = Math.random() * window.innerWidth;
      const y = Math.random() * window.innerHeight;
      const size = Math.random() * 1 + 0.5;
      const depth = Math.random() * 1000;

      star.style.left = `${x}px`;
      star.style.top = `${y}px`;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      star.style.transform = `translateZ(${depth}px)`;

      starfield.appendChild(star);
    }

    document.body.appendChild(starfield);

    return () => document.body.removeChild(starfield);
  }, []);

  return null;
};

export default ParticlesBackground;
