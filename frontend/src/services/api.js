const API_BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

export async function listActivities(type, limit = 50) {
  const q = new URLSearchParams();
  if (type) q.set('type', type);
  if (limit) q.set('limit', String(limit));
  return request(`/activities?${q.toString()}`);
}

export async function createActivity(payload) {
  return request(`/activities`, { method: 'POST', body: JSON.stringify(payload) });
}

export async function updateActivity(id, payload) {
  return request(`/activities/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

export async function deleteActivity(id) {
  return request(`/activities/${id}`, { method: 'DELETE' });
}
