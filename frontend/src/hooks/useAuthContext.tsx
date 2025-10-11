import { createContext, useContext } from "react";

export type DecodedAccessToken = {
  tenant_id: string;
  id: number;
  username: string;
  iat: number;
  exp?: number;
};

export type Auth = {
  session: {
    accessToken: string | null;
    user: DecodedAccessToken | null;
  };
  setAccessToken: (token: string | null) => void;
};

export const AuthContext = createContext<Auth | null>(null);

export function useAuth() {
  const auth = useContext(AuthContext);
  if (!auth) {
    throw new Error("useAuthToken must be used within an AuthProvider");
  }

  return auth;
}
