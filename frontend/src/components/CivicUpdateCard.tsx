export default function CivicUpdateCard({ item }: { item: any }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
      <h3 className="text-lg font-semibold text-slate-900">{item.title}</h3>
      {item.tl_dr && <p className="text-slate-600 mt-2">{item.tl_dr}</p>}
      {Array.isArray(item.what_changes) && item.what_changes.length > 0 && (
        <ul className="list-disc list-inside text-sm text-slate-700 mt-3 space-y-1">
          {item.what_changes.map((c: string, i: number) => <li key={i}>{c}</li>)}
        </ul>
      )}
      <p className="text-xs text-slate-400 mt-4">
        Source: <a className="underline" href={item.url} target="_blank" rel="noreferrer">{item.url}</a>
      </p>
    </div>
  );
}
