import { useState, useEffect } from "react";
import * as identity from "@/api/identity";
import { useNavigate } from "react-router";

type DecodedAccessToken = {
  tenant_id: string;
  id: number;
  username: string;
  iat: number;
  exp?: number;
};

export function useAuthToken() {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  let session: DecodedAccessToken | null = null;
  if (accessToken) {
    const [, payloadBase64] = accessToken.split(".");
    session = JSON.parse(atob(payloadBase64));
  }


  useEffect(() => {
    if (!accessToken) return;

    if (accessToken) {
      navigate("/");
    }
  }, [accessToken, navigate]);

  

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

  return [accessToken, setAccessToken, session] as const;
}
