import { useState } from "react";
import LocationForm from "./LocationForm";
import Feed from "./Feed";

export default function Dashboard() {
  const [status, setStatus] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const [hasLocation, setHasLocation] = useState(false);

  async function runAgent() {
    try {
      setStatus("⏳ Fetching updates…");
      const resp = await fetch("http://127.0.0.1:8000/agent/run-for-me", { method: "POST" });
      const data = await resp.json();
      if (typeof data.ok === "number") {
        setStatus(data.ok > 0 ? `✅ Got ${data.ok} new updates` : "ℹ️ No new updates found");
        if (data.ok > 0) setRefreshKey(k => k + 1);
      } else if (data.error) setStatus(`❌ ${data.error}`);
      else setStatus("⚠️ Unexpected response");
    } catch {
      setStatus("❌ Network error");
    }
  }

  return (
    <div className="space-y-10">
      {/* Hero */}
      <div className="text-center">
        <div className="inline-block rounded-full px-3 py-1 text-sm bg-emerald-100 text-emerald-700 mb-4">
          Stay informed about your local government
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-slate-900">CivicLens</h1>
        <p className="text-slate-600 mt-3 max-w-3xl mx-auto text-lg">
          Putting government activity into clearer focus. Track local decisions, meetings, and initiatives that matter to your community.
        </p>
      </div>

      {/* Controls */}
      <div className="grid md:grid-cols-2 gap-6 items-start">
        <LocationForm onSaved={() => { setHasLocation(true); setStatus("📍 Location saved"); }} />

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-semibold text-slate-900 mb-4">Updates</h3>
          <button
            onClick={runAgent}
            disabled={!hasLocation}
            className={`w-full px-5 py-3 rounded-xl font-semibold text-white transition
              ${hasLocation ? "bg-blue-600 hover:bg-blue-700" : "bg-blue-300 cursor-not-allowed"}`}
          >
            Fetch Updates
          </button>
          <p className="text-sm text-slate-500 mt-3">
            {hasLocation ? "Fetch the latest local updates" : "Set your location first to fetch local updates"}
          </p>
          {status && <p className="text-sm mt-3">{status}</p>}
        </div>
      </div>

      {/* Feed */}
      <div className="space-y-3">
        <h2 className="text-xl font-semibold text-slate-900">Latest updates</h2>
        <Feed refreshKey={refreshKey} />
      </div>
    </div>
  );
}
