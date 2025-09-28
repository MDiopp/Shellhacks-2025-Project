import { NavLink } from "react-router-dom";

const base =
  "flex items-center gap-2 px-4 py-2 rounded-xl transition";
const active =
  "bg-blue-600 text-white shadow-sm";
const idle =
  "text-slate-700 hover:bg-slate-50";

export default function Sidebar() {
  return (
    <div className="h-full flex flex-col p-5">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-slate-900">CivicLens</h1>
        <p className="text-sm text-slate-500 mt-1">
          Putting government activity into clearer focus
        </p>
      </div>

      <nav className="space-y-2">
        <NavLink to="/" end className={({ isActive }) => `${base} ${isActive ? active : idle}`}>
          <span>🏠</span> Home
        </NavLink>
        <NavLink to="/feed" className={({ isActive }) => `${base} ${isActive ? active : idle}`}>
          <span>🗂️</span> Feed
        </NavLink>
        <NavLink to="/about" className={({ isActive }) => `${base} ${isActive ? active : idle}`}>
          <span>ℹ️</span> About
        </NavLink>
      </nav>

      <div className="mt-auto text-[12px] text-slate-400">v0.1 • Hackathon build</div>
    </div>
  );
}

