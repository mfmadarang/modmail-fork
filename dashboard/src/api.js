const BASE_URL = import.meta.env.VITE_API_URL;

export async function getLatestMetrics() {
    const res = await fetch(`${BASE_URL}/metrics/latest`);
    if (!res.ok) throw new Error(`Failed to fetch latest metrics: ${res.status}`);
    return res.json();
}

export async function getMetricsHistory(container, minutes = 60) {
    const params = new URLSearchParams({ minutes });
    if (container) params.set('container', container);
    const res = await fetch(`${BASE_URL}/metrics/history?${params}`);
    if (!res.ok) throw new Error(`Failed to fetch metrics history: ${res.status}`);
    return res.json();
}

export async function getIncidents(minutes = 1440) {
    const params = new URLSearchParams({ minutes });
    const res = await fetch(`${BASE_URL}/incidents?${params}`);
    if (!res.ok) throw new Error(`Failed to fetch incidents: ${res.status}`);
    return res.json();
}