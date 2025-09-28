import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import HomePage from "./pages/HomePage";
import FeedPage from "./pages/FeedPage";
import AboutPage from "./pages/AboutPage";

export default function App() {
  return (
    <div className="min-h-screen grid grid-cols-[260px,1fr] bg-gray-50 text-slate-900">
      {/* Sidebar */}
      <aside className="border-r bg-white">
        <Sidebar />
      </aside>

      {/* Main content area */}
      <main className="min-h-screen px-8 py-6">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/feed" element={<FeedPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
    </div>
  );
}

