import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ResponsiveContainer
} from "recharts";

export default function PerformancePanel() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/performance")
      .then(res => setMetrics(res.data))
      .catch(() => setMetrics(null));
  }, []);

  if (!metrics) return (
    <div className="text-gray-400 text-sm">No performance data available.</div>
  );

  const { model, embedding, metrics: data, confusion_matrix, labels } = metrics;

  const chartData = data.accuracy.map((acc, i) => ({
    step: `E${i + 1}`,
    accuracy: acc,
    loss: data.loss[i],
  }));

  return (
    <div className="bg-gray-800 bg-opacity-70 rounded-xl p-5 mt-6 space-y-6 shadow-lg">
      <h2 className="text-lg font-semibold text-purple-300 mb-2">Model Performance</h2>
      <p className="text-sm text-gray-400 mb-2">
        Model <b>{model}</b> | Embedding <b>{embedding}</b>
      </p>

      {/* Accuracy / Loss Line Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="step" stroke="#aaa" />
          <YAxis stroke="#aaa" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="accuracy" stroke="#82ca9d" strokeWidth={2} />
          <Line type="monotone" dataKey="loss" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>

      {/* Confusion Matrix */}
      <div>
        <h3 className="text-sm font-semibold text-gray-300 mb-1">Confusion Matrix</h3>
        <div className="grid grid-cols-3 gap-1">
          {confusion_matrix.flat().map((val, idx) => {
            const intensity = Math.min(255, 60 + val * 2);
            return (
              <div
                key={idx}
                className="text-center text-xs font-medium p-2 rounded"
                style={{
                  backgroundColor: `rgba(138,43,226,${val / 100})`,
                  color: val > 50 ? "white" : "#ddd",
                }}
              >
                {val}
              </div>
            );
          })}
        </div>
        <div className="flex justify-around mt-1 text-xs text-gray-400">
          {labels.map((l) => <span key={l}>{l}</span>)}
        </div>
      </div>
    </div>
  );
}
