const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function getHealth() {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(`L'API a répondu avec le statut ${response.status}`);
  }

  return response.json();
}

export default { API_URL, getHealth };
