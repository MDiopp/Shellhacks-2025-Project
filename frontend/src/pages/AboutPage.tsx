export default function AboutPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-sm text-blue-700 font-semibold">About CivicLens</h2>
        <h1 className="text-3xl font-bold text-slate-900 mt-2">
          Making local government more accessible and transparent for everyone
        </h1>
      </div>

      <section className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <h3 className="font-semibold text-slate-900 mb-2">Our Mission</h3>
        <p className="text-slate-700 leading-relaxed">
          CivicLens bridges the gap between local government and citizens. This tool can summarize agendas, policies,
          and budget updates so residents can quickly understand what’s changing and why it matters.
        </p>
      </section>

      <h3 className="text-center text-blue-700 font-semibold">How CivicLens Helps</h3>
      <div className="grid md:grid-cols-2 gap-5">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
          <div className="text-2xl mb-2">🔔</div>
          <h4 className="font-semibold">Stay Informed</h4>
          <p className="text-slate-700">Timely updates about meetings, decisions, and initiatives that affect your community.</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
          <div className="text-2xl mb-2">📍</div>
          <h4 className="font-semibold">Local Focus</h4>
          <p className="text-slate-700">Filter by your city and state to see only relevant civic information.</p>
        </div>
      </div>
    </div>
  );
}
