const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

export async function fetchHealth() {
  console.log("API_BASE_URL:", API_BASE_URL);

  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}