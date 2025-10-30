import React, { useState, useEffect } from "react";
import { FaRegCalendarAlt } from "react-icons/fa";
import { FiRadio, FiFilter } from "react-icons/fi";
import axios from "axios";
import { api } from '../lib/axios';

const DashBoard_body = () => {
  const [rounds, setRounds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // const fetchRounds = async () => {
  //   try {
  //     const res = await axios.get("http://127.0.0.1:8000/api/user/rounds");
  //     setRounds(res.data);
  //   } catch (err) {
  //     console.error("Error fetching rounds:", err);

  //     // 👇 fallback mock data to visualize UI
  //     setRounds([
  //       {
  //         _id: "1",
  //         title: "AI Code Contest",
  //         subtitle: "Round 1: Problem Solving + Debugging",
  //         thumbnailUrl: "https://picsum.photos/200/200?1",
  //         displayStartDate: "Oct 31, 2025",
  //         displayStartTime: "10:00 AM",
  //         displayEndTime: "12:00 PM",
  //         whoCanPlay: "Everyone",
  //         role: "Participant",
  //       },
  //       {
  //         _id: "2",
  //         title: "Simulation Game",
  //         subtitle: "HackX Challenge - Simulation Round",
  //         thumbnailUrl: "https://picsum.photos/200/200?2",
  //         displayStartDate: "Nov 1, 2025",
  //         displayStartTime: "2:00 PM",
  //         displayEndTime: "4:30 PM",
  //         whoCanPlay: "Top 50 Teams",
  //         role: "Team Lead",
  //       },
  //       {
  //         _id: "3",
  //         title: "Offline Round",
  //         subtitle: "On-site presentation and demo",
  //         thumbnailUrl: "https://picsum.photos/200/200?3",
  //         displayStartDate: "Nov 2, 2025",
  //         displayStartTime: "11:00 AM",
  //         displayEndTime: "1:30 PM",
  //         whoCanPlay: "Top 10 Teams",
  //         role: "Presenter",
  //       },
  //     ]);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const fetchRounds = async () => {
    try {
      // Using the api instance to make the GET request
      const res = await api.get("/api/v1/user/rounds");
      setRounds(res.data || []); // Set rounds data if the request is successful
      setError(null); // Clear any previous errors
    } catch (err) {
      console.error("Error fetching rounds:", err);
      setError("Unable to fetch rounds. Please try again later."); // Set an error message if something goes wrong
    } finally {
      setLoading(false); // Set loading to false once the request is completed
    }
  };
  
  useEffect(() => {
    fetchRounds();
    const interval = setInterval(fetchRounds, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <section className="min-h-screen flex items-center justify-center text-white text-lg tracking-wide relative z-10 pt-24">
        <div className="backdrop-blur-md bg-white/5 px-6 py-3 rounded-xl border border-white/10">
          Loading rounds...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="min-h-screen flex items-center justify-center text-white text-lg relative z-10 pt-24">
        <div className="bg-red-500/20 border border-red-500/30 px-6 py-4 rounded-xl backdrop-blur-md">
          {error}
        </div>
      </section>
    );
  }

  return (
    <section className="min-h-screen w-full text-white px-8 py-10 backdrop-blur-sm relative z-10 pt-24">
      {/* Header */}
      <h1 className="text-3xl font-semibold mb-8 tracking-wide drop-shadow-lg text-center">
        My Rounds
      </h1>

      {/* Filters Row */}
      <div className="flex flex-wrap items-center justify-between mb-6 gap-4">
        <div className="flex flex-wrap gap-3 text-sm">
          {[
            "All",
            "Aptitude Round",
            "DSA Round",
            "Interview",
          ].map((label) => (
            <button
              key={label}
              className="px-4 py-2 rounded-lg bg-white/10 border border-white/10 hover:bg-white/20 transition-all duration-300 backdrop-blur-sm"
            >
              {label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg hover:bg-white/20 border border-white/10 transition-all duration-300">
            <FiRadio /> Live
          </button>
          <button className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg hover:bg-white/20 border border-white/10 transition-all duration-300">
            <FaRegCalendarAlt /> Upcoming
          </button>
          <button className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg hover:bg-white/20 border border-white/10 transition-all duration-300">
            <FiFilter /> Sort By
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-8">
        <input
          type="text"
          placeholder="Search for rounds..."
          className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 backdrop-blur-sm transition"
        />
      </div>

      {/* Rounds List */}
      <div className="space-y-6">
        {rounds.length > 0 ? (
          rounds.map((r) => (
            <div
              key={r._id || r.title}
              className="flex flex-col sm:flex-row items-center sm:items-start bg-white/10 rounded-2xl border border-white/10 p-6 hover:bg-white/20 transition-all duration-300 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]"
            >
              <img
                src={r.thumbnailUrl}
                alt={r.title}
                className="w-24 h-24 object-cover rounded-xl mb-4 sm:mb-0 sm:mr-6 border border-white/10"
              />

              <div className="flex-1 w-full">
                <h2 className="text-xl font-semibold mb-1">{r.title}</h2>
                <p className="text-sm text-gray-300 mb-3">{r.subtitle}</p>

                <div className="flex flex-wrap text-xs text-gray-400 gap-3">
                  <span className="flex items-center gap-1">
                    <FaRegCalendarAlt /> {r.displayStartDate},{" "}
                    {r.displayStartTime} — {r.displayEndTime}
                  </span>
                  <span>| Who can play: {r.whoCanPlay}</span>
                  <span>| Your Role: {r.role}</span>
                </div>
              </div>

              <div className="flex gap-3 mt-4 sm:mt-0 sm:ml-auto">
              <button
                className="px-5 py-3 rounded-lg text-white font-medium 
                bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] 
                shadow-[0_0_20px_rgba(255,107,0,0.6)] 
                hover:shadow-[0_0_35px_rgba(255,0,106,0.8)] 
                transition-all duration-300 border border-white/10"
              >
                Start Exam
              </button>


              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-400 text-center">No rounds found</p>
        )}
      </div>
    </section>
  );
};

export default DashBoard_body;
