import React from "react";
import { MoonIcon, SunIcon, SparklesIcon, ChartBarIcon, ChatBubbleLeftIcon } from "@heroicons/react/24/solid";

export default function Navbar({ theme, setTheme, selectedModel, setSelectedModel, models, activeView, setActiveView }) {
  return (
    <header className="flex justify-between items-center p-4 border-b border-gray-700 relative z-10 bg-gray-900/80 backdrop-blur">
      <div className="flex items-center gap-2">
        <SparklesIcon className="w-5 h-5 text-purple-400" />
        <h1 className="text-xl font-semibold">Viora</h1>
      </div>

      <div className="flex items-center gap-4">
        {/* Navigation Buttons */}
        <nav className="flex gap-2">
          <button
            onClick={() => setActiveView("chat")}
            className={`flex items-center gap-1 px-3 py-1 rounded-md text-sm ${
              activeView === "chat"
                ? "bg-purple-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            <ChatBubbleLeftIcon className="w-4 h-4" /> Chat
          </button>
          <button
            onClick={() => setActiveView("performance")}
            className={`flex items-center gap-1 px-3 py-1 rounded-md text-sm ${
              activeView === "performance"
                ? "bg-purple-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            <ChartBarIcon className="w-4 h-4" /> Performance
          </button>
        </nav>

        {/* Model Selector */}
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="bg-gray-800 text-gray-200 border border-gray-600 rounded-md px-3 py-1"
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>

        {/* Theme toggle */}
        <button
          onClick={() => setTheme(theme === "gradient" ? "minimal" : "gradient")}
          className="p-2 bg-gray-800 rounded-md hover:bg-gray-700"
        >
          {theme === "gradient" ? (
            <MoonIcon className="w-5 h-5 text-gray-300" />
          ) : (
            <SunIcon className="w-5 h-5 text-yellow-400" />
          )}
        </button>
      </div>
    </header>
  );
}
