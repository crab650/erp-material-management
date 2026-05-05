import router from "./router";
import { apiClient, clearAuthSession, getAuthToken } from "./api/http";

let verifiedToken = "";

router.beforeEach(async (to) => {
  const token = getAuthToken();

  if (to.path === "/login") {
    if (!token) {
      return true;
    }

    try {
      await apiClient.get("/api/auth/me");
      return { path: "/" };
    } catch {
      clearAuthSession();
      verifiedToken = "";
      return true;
    }
  }

  if (!token) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (token === verifiedToken) {
    return true;
  }

  try {
    await apiClient.get("/api/auth/me");
    verifiedToken = token;
    return true;
  } catch {
    clearAuthSession();
    verifiedToken = "";
    return { path: "/login", query: { redirect: to.fullPath } };
  }
});
