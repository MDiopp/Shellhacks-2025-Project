import { useState } from "react";
import Feed from "../components/Feed";

export default function FeedPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-blue-700 text-center">Civic Updates Feed</h1>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 grid md:grid-cols-[1fr,240px] gap-3">
        <input
          placeholder="Search updates..."
          className="border border-slate-300 bg-slate-50 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select className="border border-slate-300 bg-slate-50 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Categories</option>
          <option>Budget</option>
          <option>Meetings</option>
          <option>Policy</option>
        </select>
      </div>

      <Feed refreshKey={refreshKey} />

      <div className="text-center">
        <button
          onClick={() => setRefreshKey(k => k + 1)}
          className="mt-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold"
        >
          Refresh Feed
        </button>
      </div>
    </div>
  );
}
