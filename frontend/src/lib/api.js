const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export function getAccessToken() {
  return localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
}

export function setAccessToken(token, remember = true) {
  if (remember) {
    localStorage.setItem("access_token", token);
    sessionStorage.removeItem("access_token");
  } else {
    sessionStorage.setItem("access_token", token);
    localStorage.removeItem("access_token");
  }
}

export function clearAccessToken() {
  localStorage.removeItem("access_token");
  sessionStorage.removeItem("access_token");
}

export async function apiRequest(path, options = {}) {
  const token = getAccessToken();
  const headers = new Headers(options.headers || {});

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || "The request could not be completed.");
  }

  return data;
}
