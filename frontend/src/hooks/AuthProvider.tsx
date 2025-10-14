import { useEffect, useState } from "react";
import * as identity from "@/api/identity";
import { useNavigate } from "react-router";
import { AuthContext, type DecodedAccessToken } from "@/hooks/useAuthContext";

export type AuthProviderProps = {
  children: React.ReactNode;
};

export function Auth({ children }: AuthProviderProps) {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useState<string | null>(
    localStorage.getItem("accessToken")
  );
  let session: DecodedAccessToken | null = null;
  if (accessToken) {
    const [, payloadBase64] = accessToken.split(".");
    session = JSON.parse(atob(payloadBase64));
  }

  //manage localStorage
  useEffect(() => {
    if (accessToken) {
      localStorage.setItem("accessToken", accessToken);
    }
  }, [accessToken]);

  // manage auth
  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
    }
  }, [accessToken, navigate]);

  //manage refreshToken
  useEffect(() => {
    const refreshToken = async () => {
      try {
        const res = await identity.refreshToken();
        setAccessToken(res.accessToken);
      } catch (err) {
        console.error("Refresh failed:", err);
        setAccessToken(null);
      }
    };

    if (!session) return;

    const expiresAt = session.exp ? session.exp * 1000 : 0;
    const now = Date.now();
    const refreshTime = expiresAt - now - 5000;

    if (refreshTime > 0) {
      const id = setTimeout(() => refreshToken(), refreshTime);
      return () => clearTimeout(id);
    }
  }, [session]);

  return (
    <AuthContext
      value={{
        session: { accessToken, user: session },
        setAccessToken,
      }}
    >
      {children}
    </AuthContext>
  );
}
