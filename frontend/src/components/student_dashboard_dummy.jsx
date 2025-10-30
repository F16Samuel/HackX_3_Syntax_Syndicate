import React, { useState, useMemo } from "react";
import { FaRegCalendarAlt } from "react-icons/fa";
import { FiRadio, FiFilter, FiClock } from "react-icons/fi";
import { Link } from "react-router-dom";

// Define filter categories
const CATEGORY_FILTERS = ["All", "Aptitude Round", "DSA Round", "Interview"];
const STATUS_FILTERS = [
  { key: "all", label: "All Status", icon: FiFilter },
  { key: "live", label: "Live", icon: FiRadio },
  { key: "upcoming", label: "Upcoming", icon: FiClock },
];

// --- 5 SAMPLE TESTS (MOCK DATA) ---
// Note: Dates are set relative to a hypothetical "now" to make filters work.
const mockRounds = [
  {
    _id: "1",
    title: "Cognizant Aptitude Round",
    subtitle: "Aptitude Round: Quantitative & Logical Reasoning",
    thumbnailUrl: "https://placehold.co/200x200/ff6b00/ffffff?text=Aptitude",
    role: "Software Engineer Trainee",
    whoCanPlay: "2025 Batch",
    dateTBA: false,
    // LIVE ROUND (e.g., set to be live for 2 hours)
    startDateTime: new Date(Date.now() - 60 * 60 * 1000).toISOString(), // Started 1 hour ago
    endDateTime: new Date(Date.now() + 60 * 60 * 1000).toISOString(), // Ends 1 hour from now
    displayStartDate: "Oct 31, 2025",
    displayStartTime: "03:00 AM",
    displayEndDate: "Oct 31, 2025",
    displayEndTime: "05:00 AM",
  },
  {
    _id: "2",
    title: "TCS DSA Round",
    subtitle: "DSA Round: Arrays, Strings, and Algorithms",
    thumbnailUrl: "https://placehold.co/200x200/ff2e2e/ffffff?text=DSA",
    role: "Backend Developer",
    whoCanPlay: "Everyone",
    dateTBA: false,
    // UPCOMING ROUND (e.g., starts in 1 day)
    startDateTime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    endDateTime: new Date(Date.now() + 26 * 60 * 60 * 1000).toISOString(),
    displayStartDate: "Nov 1, 2025",
    displayStartTime: "10:00 AM",
    displayEndDate: "Nov 1, 2025",
    displayEndTime: "12:00 PM",
  },
  {
    _id: "3",
    title: "Infosys HR Interview",
    subtitle: "Interview: Behavioral & Technical HR Round",
    thumbnailUrl: "https://placehold.co/200x200/ff006a/ffffff?text=HR",
    role: "Full-Stack Developer",
    whoCanPlay: "Shortlisted Candidates",
    dateTBA: false,
    // UPCOMING ROUND (e.g., starts in 2 days)
    startDateTime: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
    endDateTime: new Date(Date.now() + 50 * 60 * 60 * 1000).toISOString(),
    displayStartDate: "Nov 2, 2025",
    displayStartTime: "02:00 PM",
    displayEndDate: "Nov 2, 2025",
    displayEndTime: "04:00 PM",
  },
  {
    _id: "4",
    title: "Wipro Aptitude Challenge (Past)",
    subtitle: "Aptitude Round: Verbal Ability & Logic",
    thumbnailUrl: "https://placehold.co/200x200/1a1a1a/ffffff?text=Past",
    role: "Graduate Engineer",
    whoCanPlay: "2024 Batch",
    dateTBA: false,
    // PAST ROUND (e.g., ended 1 day ago)
    startDateTime: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
    endDateTime: new Date(Date.now() - 46 * 60 * 60 * 1000).toISOString(),
    displayStartDate: "Oct 30, 2025",
    displayStartTime: "10:00 AM",
    displayEndDate: "Oct 30, 2025",
    displayEndTime: "12:00 PM",
  },
  {
    _id: "5",
    title: "Google Coding Challenge",
    subtitle: "DSA Round: Advanced Algorithms & Data Structures",
    thumbnailUrl: "https://placehold.co/200x200/4285F4/ffffff?text=Coding",
    role: "SDE 1",
    whoCanPlay: "Everyone",
    dateTBA: false,
    // UPCOMING ROUND (e.g., starts in 5 days)
    startDateTime: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    endDateTime: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
    displayStartDate: "Nov 5, 2025",
    displayStartTime: "09:00 AM",
    displayEndDate: "Nov 5, 2025",
    displayEndTime: "11:00 AM",
  },
];

const DashBoard_dummy = () => {
  // --- SET INITIAL STATE WITH MOCK DATA ---
  const [rounds, setRounds] = useState(mockRounds);

  // --- NEW STATE FOR FILTERS ---
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState(CATEGORY_FILTERS[0]); // "All"
  const [statusFilter, setStatusFilter] = useState(STATUS_FILTERS[0].key); // "all"

  // --- FILTERING LOGIC (No changes needed here) ---
  const filteredRounds = useMemo(() => {
    const now = new Date();

    return rounds.filter(round => {
      // 1. Filter by Search Term (Title or Subtitle)
      const searchMatch =
        round.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        round.subtitle.toLowerCase().includes(searchTerm.toLowerCase());

      // 2. Filter by Category (Title or Subtitle)
      const categoryMatch =
        categoryFilter === "All" ||
        round.title.toLowerCase().includes(categoryFilter.toLowerCase()) ||
        round.subtitle.toLowerCase().includes(categoryFilter.toLowerCase());

      // 3. Filter by Status (Live, Upcoming)
      let statusMatch = true;
      if (statusFilter !== "all") {
        try {
          const startTime = new Date(round.startDateTime);
          const endTime = new Date(round.endDateTime);

          if (statusFilter === "live") {
            statusMatch = now >= startTime && now <= endTime;
          } else if (statusFilter === "upcoming") {
            statusMatch = now < startTime;
          }
        } catch (e) {
          console.error("Error parsing round dates:", e);
          statusMatch = false; // Exclude if dates are invalid
        }
      }

      // Return true only if all filters match
      return searchMatch && categoryMatch && statusMatch;
    });
  }, [rounds, searchTerm, categoryFilter, statusFilter]);

  // --- MAIN RENDER (Removed Loading/Error states) ---
  return (
    <section className="h-screen w-full text-white px-8 py-10 backdrop-blur-sm relative z-10 pt-24 flex flex-col">
      {/* Header */}
      <h1 className="text-3xl font-semibold mb-8 tracking-wide drop-shadow-lg text-center">
        My Rounds
      </h1>

      {/* Search Bar */}
      <div className="mb-8 max-w-2xl mx-auto w-full">
        <input
          type="text"
          placeholder="Search for rounds by title or subtitle..."
          className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Filters Row */}
      <div className="flex flex-col sm:flex-row items-center justify-between mb-6 gap-4">
        {/* Category Filters */}
        <div className="flex flex-wrap justify-center sm:justify-start gap-3 text-sm">
          {CATEGORY_FILTERS.map((label) => (
            <button
              key={label}
              onClick={() => setCategoryFilter(label)}
              className={`px-4 py-2 rounded-lg border border-white/10 transition-all duration-300 backdrop-blur-sm ${
                categoryFilter === label
                  ? "bg-gradient-to-r from-[#ff6b00] to-[#ff006a] text-white font-semibold shadow-[0_0_15px_rgba(255,80,40,0.5)]"
                  : "bg-white/10 hover:bg-white/20"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-3 text-sm">
          {STATUS_FILTERS.map(status => {
            const Icon = status.icon;
            return (
              <button
                key={status.key}
                onClick={() => setStatusFilter(status.key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-white/10 transition-all duration-300 ${
                  statusFilter === status.key
                    ? "bg-white text-black font-semibold"
                    : "bg-white/10 hover:bg-white/20"
                }`}
              >
                <Icon className="w-4 h-4" />
                {status.label}
              </button>
            )
          })}

          {/* Sort By button - logic not implemented yet */}
          <button className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg hover:bg-white/20 border border-white/10 transition-all duration-300 text-sm">
            <FiFilter /> Sort By
          </button>
        </div>
      </div>

      {/* Rounds List (Now Scrollable) */}
      <div className="space-y-6 flex-1 overflow-y-auto pt-6 pb-10">
        {filteredRounds.length > 0 ? (
          filteredRounds.map((r) => (
            <div
              key={r._id}
              className="flex flex-col sm:flex-row items-center sm:items-start bg-white/10 rounded-2xl border border-white/10 p-6 hover:bg-white/20 transition-all duration-300 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]"
            >
              <img
                src={r.thumbnailUrl}
                alt={r.title}
                className="w-24 h-24 object-cover rounded-xl mb-4 sm:mb-0 sm:mr-6 border border-white/10"
                onError={(e) => { e.target.src = "https://placehold.co/200x200/1a1a1a/ffffff?text=Image"; }} // Fallback
              />

              <div className="flex-1 w-full">
                <h2 className="text-xl font-semibold mb-1">{r.title}</h2>
                <p className="text-sm text-gray-300 mb-3">{r.subtitle}</p>

                <div className="flex flex-wrap text-xs text-gray-400 gap-x-3 gap-y-1">
                  <span className="flex items-center gap-1.5">
                    <FaRegCalendarAlt /> {r.displayStartDate},{" "}
                    {r.displayStartTime} — {r.displayEndTime}
                  </span>
                  <span>| Who can play: {r.whoCanPlay}</span>
                  <span>| Your Role: {r.role}</span>
                </div>
              </div>

              <div className="flex gap-3 mt-4 sm:mt-0 sm:ml-auto">
                <Link to='/exam'>
                  <button
                    className="px-5 py-3 rounded-lg text-white font-medium 
                    bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] 
                    shadow-[0_0_20px_rgba(255,107,0,0.6)] 
                    hover:shadow-[0_0_35px_rgba(255,0,106,0.8)] 
                    transition-all duration-300 border border-white/10"
                  >
                    Start Exam
                  </button>
                </Link>
              </div>
            </div>
          ))
        ) : (
          <div className="text-gray-400 text-center py-10 bg-white/5 rounded-lg border border-white/10 backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-white mb-2">No Rounds Found</h3>
            <p>Try adjusting your search or filter criteria.</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default DashBoard_dummy;

