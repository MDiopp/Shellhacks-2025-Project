import { NavLink, Outlet } from "react-router-dom";

function NavItem({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        [
          "flex items-center gap-3 w-full rounded-xl px-4 py-3 text-sm font-medium transition",
          isActive ? "bg-blue-600 text-white shadow-sm" : "text-slate-700 hover:bg-slate-100",
        ].join(" ")
      }
    >
      <span className="text-lg">{icon}</span>
      <span>{label}</span>
    </NavLink>
  );
}

export default function Shell() {
  return (
    <div className="min-h-screen bg-slate-50 grid grid-cols-[260px,1fr]">
      {/* Sidebar */}
      <aside className="h-screen sticky top-0 bg-white border-r border-slate-200 p-6 flex flex-col">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">
            <span className="text-emerald-500">Civic</span>Lens
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Putting government activity into clearer focus
          </p>
        </div>

        <nav className="flex flex-col gap-2">
          <NavItem to="/" icon={"🏠"} label="Home" />
          <NavItem to="/feed" icon={"🗂️"} label="Feed" />
          <NavItem to="/about" icon={"ℹ️"} label="About" />
        </nav>

        <div className="mt-auto pt-6 text-xs text-slate-400">v0.1 • Hackathon build</div>
      </aside>

      {/* Main content */}
      <main className="p-8">
        <Outlet />
      </main>
    </div>
  );
}
