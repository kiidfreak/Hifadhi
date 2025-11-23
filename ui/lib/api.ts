export const HR_API = 'http://localhost:8000/api';
export const AGENT_API = 'http://localhost:8001/api/v2';

export async function fetchDashboardData() {
  const res = await fetch(`${HR_API}/analytics/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch dashboard data');
  return res.json();
}

export async function fetchAgents() {
  const res = await fetch(`${AGENT_API}/agents`);
  if (!res.ok) throw new Error('Failed to fetch agents');
  return res.json();
}

export async function fetchEvents() {
  const res = await fetch(`${AGENT_API}/events`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function startMission(mission: string) {
  const res = await fetch(`${AGENT_API}/mission`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mission }),
  });
  if (!res.ok) throw new Error('Failed to start mission');
  return res.json();
}

export async function fetchCandidates() {
  const res = await fetch(`${HR_API}/candidates`);
  if (!res.ok) throw new Error('Failed to fetch candidates');
  return res.json();
}

export async function fetchApplications() {
  const res = await fetch(`${HR_API}/applications`);
  if (!res.ok) throw new Error('Failed to fetch applications');
  return res.json();
}

export async function fetchJobs() {
  const res = await fetch(`${HR_API}/jobs`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}
