import { createContext, useContext, useState, useCallback } from "react";
import authService from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // 새로고침해도 localStorage에서 유저 정보와 인증 상태를 복원
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("pedalup_user");
    return saved ? JSON.parse(saved) : null;
  });
  
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("pedalup_access_token");
  });

  const applySession = useCallback(({ accessToken, user: nextUser }) => {
    localStorage.setItem("pedalup_access_token", accessToken);
    localStorage.setItem("pedalup_user", JSON.stringify(nextUser)); // 유저 정보도 저장
    setUser(nextUser);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    localStorage.removeItem("pedalup_user"); // 로그아웃 시 함께 삭제
    localStorage.removeItem("pedalup_access_token");
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const login = useCallback(
    async (credentials) => {
      const session = await authService.login(credentials);
      applySession(session);
      return session;
    },
    [applySession]
  );

  const signup = useCallback(
    async (payload) => {
      const session = await authService.signup(payload);
      applySession(session);
      return session;
    },
    [applySession]
  );

  const loginWithGoogle = useCallback(async () => {
    const session = await authService.loginWithGoogle();
    applySession(session);
    return session;
  }, [applySession]);

  const loginWithKakao = useCallback(async () => {
    const session = await authService.loginWithKakao();
    applySession(session);
    return session;
  }, [applySession]);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, login, signup, loginWithGoogle, loginWithKakao, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}