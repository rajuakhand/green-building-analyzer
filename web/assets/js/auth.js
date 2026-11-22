/**
 * Authentication scaffolding for Green Building Analyzer.
 * Supports email/password and mobile + SMS code (common in China).
 * Stores users in localStorage. For production, replace with a backend API.
 */

const USERS_KEY = "gba.users.v1";
const SESSION_KEY = "gba.session.v1";

export function getUsers() {
  try {
    const raw = localStorage.getItem(USERS_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error) {
    console.warn("Could not read users", error);
    return {};
  }
}

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch (error) {
    return null;
  }
}

export function registerUser(email, password, mobile) {
  const users = getUsers();
  if (users[email]) {
    return { success: false, error: "User already exists." };
  }

  users[email] = {
    email,
    password, // In production, hash this
    mobile: mobile || "",
    createdAt: new Date().toISOString(),
    role: "user",
  };

  try {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  } catch (error) {
    console.warn("Could not save user", error);
    return { success: false, error: "Storage failed." };
  }

  return { success: true };
}

export function loginUser(email, password) {
  const users = getUsers();
  const user = users[email];

  if (!user || user.password !== password) {
    return { success: false, error: "Invalid email or password." };
  }

  const session = {
    email,
    role: user.role,
    loggedInAt: new Date().toISOString(),
  };

  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  } catch (error) {
    console.warn("Could not save session", error);
    return { success: false, error: "Storage failed." };
  }

  return { success: true, user };
}

export function loginWithMobile(mobile, smsCode) {
  // In production, verify SMS code via a gateway.
  // For now, accept any 6-digit code.
  if (!/^\d{6}$/.test(smsCode)) {
    return { success: false, error: "Invalid SMS code." };
  }

  const users = getUsers();
  const user = Object.values(users).find((u) => u.mobile === mobile);

  if (!user) {
    return { success: false, error: "Mobile not registered." };
  }

  const session = {
    email: user.email,
    role: user.role,
    loggedInAt: new Date().toISOString(),
    mobile,
  };

  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  } catch (error) {
    console.warn("Could not save session", error);
    return { success: false, error: "Storage failed." };
  }

  return { success: true, user };
}

export function logout() {
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch (error) {
    console.warn("Could not clear session", error);
  }
}

export function isAuthenticated() {
  return getSession() !== null;
}

export function getCurrentUser() {
  const session = getSession();
  if (!session) return null;
  const users = getUsers();
  return users[session.email] || null;
}
