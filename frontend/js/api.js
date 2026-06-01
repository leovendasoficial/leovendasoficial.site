const API_BASE = "http://127.0.0.1:8000";

async function apiGet(path, token=null) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { "Authorization": `Bearer ${token}` } : {}
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function apiSend(method, path, body, token=null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {})
    },
    body: body ? JSON.stringify(body) : null
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = { raw: text }; }
  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) ? (data.detail || data.message) : `API error ${res.status}`;
    throw new Error(msg);
  }
  return data;
}
