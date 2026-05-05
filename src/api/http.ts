import axios from "axios";

export type AuthUser = {
  username: string;
  role: string;
};

export const API_BASE = import.meta.env.VITE_API_BASE || "";

export const apiClient = axios.create({
  baseURL: API_BASE,
});

export const getAuthToken = () => localStorage.getItem("token");

export const getStoredUser = (): AuthUser | null => {
  const userJson = localStorage.getItem("user");

  if (!userJson) {
    return null;
  }

  try {
    return JSON.parse(userJson) as AuthUser;
  } catch {
    return null;
  }
};

export const saveAuthSession = (token: string, user: AuthUser) => {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
};

export const clearAuthSession = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});
