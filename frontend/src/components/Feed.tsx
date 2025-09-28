import { useEffect, useState } from "react";
import CivicUpdateCard from "./CivicUpdateCard";

export default function Feed({ refreshKey }: { refreshKey?: number }) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadFeed() {
    try {
      setLoading(true);
      const resp = await fetch("http://127.0.0.1:8000/feed");
      const data = await resp.json();
      setItems(data.items || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadFeed(); }, [refreshKey]);

  if (loading) return <p className="text-slate-500">⏳ Loading feed…</p>;
  if (items.length === 0) return <p className="text-slate-500">No civic updates yet.</p>;

  return (
    <div className="grid gap-5">
      {items.map((it, i) => <CivicUpdateCard key={i} item={it} />)}
    </div>
  );
}
