import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { marked } from "marked";
import { motion, AnimatePresence } from "framer-motion";
import PerformancePanel from "./components/PerformancePanel.jsx";
import Navbar from "./components/Navbar.jsx";
import LightRays from "./components/LightRays.jsx";
import "./components/LightRays.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("gemma3:12b");
  const [theme, setTheme] = useState("gradient");
  const [activeView, setActiveView] = useState("chat");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/models")
      .then((res) => setModels(res.data.models || []))
      .catch(() =>
        setModels([
          "gemma3:12b",
          "mistral:7b-instruct",
          "deepseek-coder-v2:latest",
          "codegemma:latest",
        ])
      );
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (customQuestion = null) => {
    const question = (customQuestion || input).trim();
    if (!question) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:5000/query", {
        question,
        model: selectedModel,
      });
      const { answer, sources } = res.data;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: answer, sources },
      ]);
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        "Error: Could not reach backend. Make sure Flask is running.";
      setMessages((prev) => [...prev, { role: "assistant", content: msg }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div
      className={`flex flex-col h-screen overflow-hidden relative ${
        theme === "gradient"
          ? "bg-gradient-animated text-gray-100"
          : "bg-black text-gray-100"
      }`}
    >
{theme === "gradient" && (
  <div className="absolute inset-0 bg-black">
    <LightRays
      raysOrigin="top-center"
      raysColor="#ffffff"        // bright white rays
      raysSpeed={1.2}
      lightSpread={0.9}
      rayLength={1.3}
      followMouse={true}
      mouseInfluence={0.1}
      noiseAmount={0.05}
      distortion={0.03}
      className="custom-rays"
    />
  </div>
)}


      <Navbar
        theme={theme}
        setTheme={setTheme}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        models={models}
        activeView={activeView}
        setActiveView={setActiveView}
      />

      {/* Main content area */}
      <main className="flex-1 overflow-y-auto p-6 space-y-6 relative z-10">
        {activeView === "chat" ? (
          <>
            {messages.length === 0 && !loading && (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 select-none">
                <motion.h2
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                  className="text-2xl font-semibold text-purple-300 mb-2"
                >
                  What’s on your mind today?
                </motion.h2>
                <p className="text-sm text-gray-500 mb-4">
                  Ask me anything related to VIT's Academics and Information
                </p>
                <div className="flex gap-2 flex-wrap justify-center">
                  {[
                    "Define Regulations",
                    "Summarize Curriculum",
                    "Compare Programs",
                    "Provide Guidelines",
                  ].map((tip, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(tip)}
                      disabled={loading}
                      className="bg-gray-800 border border-gray-700 text-gray-300 px-3 py-1 rounded-md text-sm hover:bg-gray-700 disabled:opacity-50"
                    >
                      {tip}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <AnimatePresence>
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex flex-col ${
                    msg.role === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-xl px-4 py-3 rounded-2xl shadow-md ${
                      msg.role === "user"
                        ? "bg-gray-700 text-gray-100"
                        : "bg-gray-800 text-gray-100"
                    }`}
                    dangerouslySetInnerHTML={{
                      __html: marked.parse(msg.content || ""),
                    }}
                  ></div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="text-sm mt-2 text-gray-400">
                      <p className="mb-1 font-semibold text-gray-300">
                        Sources:
                      </p>
                      <ul className="space-y-1">
                        {msg.sources.map((s, i) => (
                          <li key={i}>
                            {s.source} — page {s.page ?? "?"}
                            <a
                              href={`http://127.0.0.1:5000/files/${encodeURIComponent(
                                s.source
                              )}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-purple-400 hover:underline ml-2"
                            >
                              Download
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {loading && (
              <div className="text-gray-400 flex items-center gap-2 animate-pulse justify-center">
                <span>Thinking...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        ) : (
          <PerformancePanel />
        )}
      </main>

      {activeView === "chat" && (
        <footer className="border-t border-gray-700 p-4 flex relative z-10">
          <textarea
            rows="1"
            className="flex-1 resize-none bg-gray-800 text-gray-100 p-3 rounded-md outline-none"
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading}
            className="ml-3 px-5 py-2 bg-gray-700 rounded-md font-medium hover:bg-gray-600 disabled:opacity-50"
          >
            Send
          </button>
        </footer>
      )}
    </div>
  );
}
