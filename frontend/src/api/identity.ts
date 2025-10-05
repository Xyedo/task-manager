import z from "zod";
import { api } from "@/api/api";

const identity = `${api}/identity`;

const loginResponse = z.object({
  accessToken: z.string(),
  refreshToken: z.string(),
});
export async function login(username: string, password: string) {
  const response = await fetch(`${identity}/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error(`Login failed with status ${response.status}`);
  }

  return loginResponse.parse(await response.json());
}

const refreshResponse = z.object({
  accessToken: z.string(),
});
export async function refreshToken() {
  const response = await fetch(`${identity}/refresh`, {
    method: "PUT",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Refresh token failed with status ${response.status}`);
  }

  return refreshResponse.parse(await response.json());
}

export async function logout() {
  const response = await fetch(`${identity}/logout`, {
    method: "delete",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Logout failed with status ${response.status}`);
  }
}

const userSchema = z.object({
  accountId: z.number(),
  username: z.string(),
  fullName: z.string(),
  email: z.email(),
});

export type User = z.infer<typeof userSchema>;

const usersResponse = z.object({
  users: z.array(userSchema),
});

export async function users(
  accessToken: string,
  limit: number,
  lastId?: number
) {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (lastId) {
    params.append("lastId", lastId.toString());
  }

  const response = await fetch(`${identity}/users?${params.toString()}`, {
    method: "GET",
    credentials: "include",
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch users: ${response.statusText}`);
  }

  return usersResponse.parse(await response.json());
}

export async function me(accessToken: string) {
  return fetch(`${identity}/me`, {
    method: "GET",
    credentials: "include",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}
