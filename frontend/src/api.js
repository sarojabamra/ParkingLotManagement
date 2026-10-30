const API_PREFIX = "http://127.0.0.1:8000/gw/parking-v2";

const TOKEN_KEY = "parking_token";
const USER_KEY = "parking_user";

export class AuthError extends Error {}

export function apiUrl(path) {
  return `${API_PREFIX}${path.startsWith("/") ? path : `/${path}`}`;
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || "null");
  } catch {
    return null;
  }
}

function decodeJwt(token) {
  const payload = token.split(".")[1];
  const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(normalized));
}

export function setSession(token, username) {
  const payload = decodeJwt(token);
  const user = {
    username,
    id: payload.sub,
    role: payload.role || "PUBLIC",
  };
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  return user;
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

async function readError(response) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
    }
    return JSON.stringify(data);
  } catch {
    return response.statusText || "Request failed";
  }
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (
    options.body &&
    !(options.body instanceof URLSearchParams) &&
    !headers["Content-Type"]
  ) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(apiUrl(path), { ...options, headers });
  if (response.status === 401) {
    if (token) {
      clearSession();
      throw new AuthError("Please log in again.");
    }
    throw new Error(await readError(response));
  }
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  if (response.status === 204) return null;
  return response.json();
}

export function toIstIso(value) {
  if (!value) return value;
  return value.length === 16 ? `${value}:00+05:30` : `${value}+05:30`;
}
