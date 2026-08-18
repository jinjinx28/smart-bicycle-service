import api from "../api/axios";

const MOCK_USER = {
  id: "mock-user-1",
  nickname: "김민준",
  handle: "@minzun_rides",
  email: "minjun@example.com",
};

// 향후 FastAPI: POST /api/auth/login
async function login({ email, password }) {
  try {
    const { data } = await api.post("/auth/login", { email, password });
    return data;
  } catch (error) {
    const message = error.response?.data?.detail || "이메일 또는 비밀번호가 틀렸습니다.";
    throw new Error(message);
  }
}

// 향후 FastAPI: POST /api/auth/signup
async function signup(payload) {
  const requestData = {
    email: payload.email,
    password: payload.password,
    username: payload.username || payload.nickname || "user" 
  };

  try {
    const { data } = await api.post("/auth/signup", requestData);
    return data;
  } catch (error) {
    const message = error.response?.data?.detail || "이미 등록된 이메일입니다.";
    throw new Error(message);
  }
}

// 향후 FastAPI OAuth 연동 지점 — 현재는 UI 전용
async function loginWithGoogle() {
  return login({ email: "google-user@example.com", password: "oauth" });
}

async function loginWithKakao() {
  return login({ email: "kakao-user@example.com", password: "oauth" });
}

function logout() {
  localStorage.removeItem("pedalup_access_token");
}

const authService = { login, signup, loginWithGoogle, loginWithKakao, logout };
export default authService;
