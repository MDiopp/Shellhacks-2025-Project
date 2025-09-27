// api.js
const API = "http://127.0.0.1:8000";

export async function getFeed() {
  const r = await fetch(`${API}/feed`);
  return r.json();
}

export async function summarizeText(text) {
  const r = await fetch(`${API}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return r.json();
}

export async function summarizeUrl(url) {
  const r = await fetch(`${API}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return r.json();
}

export async function uploadPdf(file) {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`${API}/summarize/upload`, { method: "POST", body: fd });
  return r.json();
}
