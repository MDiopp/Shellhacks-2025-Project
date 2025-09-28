import { useState } from "react";

export default function LocationForm({ onSaved }: { onSaved?: () => void }) {
  const [city, setCity] = useState("");
  const [region, setRegion] = useState("");
  const [status, setStatus] = useState("");

  async function saveLocation() {
    try {
      const resp = await fetch("http://127.0.0.1:8000/me/location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city, region, country: "US" }),
      });
      const data = await resp.json();
      if (data.ok) { setStatus("✅ Location saved"); onSaved?.(); }
      else setStatus("❌ " + (data.error || "Failed"));
    } catch { setStatus("❌ Network error"); }
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-pink-600">📍</span>
        <h3 className="font-semibold text-slate-900">Set Your Location</h3>
      </div>

      <div className="grid gap-3">
        <label className="text-sm text-slate-600">City</label>
        <input
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="border border-slate-300 bg-slate-50 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your city"
        />

        <label className="text-sm text-slate-600 mt-2">State</label>
        <input
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="border border-slate-300 bg-slate-50 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your state"
        />

        <button
          onClick={saveLocation}
          className="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-semibold"
        >
          Save Location
        </button>

        {status && <p className="text-sm text-slate-600">{status}</p>}
      </div>
    </div>
  );
}
