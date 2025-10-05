import { api } from "@/api/api";
import z from "zod";

const workspace = `${api}/workspaces`;

const workspaceSchema = z.object({
  workspaceId: z.number(),
  name: z.string(),

  createdBy: z.number(),
  createdAt: z.coerce.date(),
  updatedBy: z.number().nullable(),
  updatedAt: z.coerce.date().nullable(),
});

export type Workspace = z.infer<typeof workspaceSchema>;

const ListWorkspaceResponse = z.object({
  workspaces: z.array(workspaceSchema),
});

export type ListWorkspaceResponse = z.infer<typeof ListWorkspaceResponse>;

export async function listWorkspaces(
  accessToken: string,
  limit?: number,
  lastId?: number
): Promise<z.infer<typeof ListWorkspaceResponse>> {
  const params = new URLSearchParams();
  if (limit) {
    params.append("limit", limit.toString());
  }
  if (lastId) {
    params.append("lastId", lastId.toString());
  }

  const response = await fetch(`${workspace}?${params.toString()}`, {
    method: "GET",
    credentials: "include",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error("Failed to fetch workspaces", { cause: response });
  }

  return ListWorkspaceResponse.parse(await response.json());
}

export async function createWorkspace(accessToken: string, name: string) {
  const response = await fetch(`${workspace}/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    throw new Error("Failed to create workspace", { cause: response });
  }

  return workspaceSchema.parse(await response.json());
}

const taskSchema = z.object({
  taskId: z.number(),
  title: z.string(),
  description: z.string().nullable(),
  dueDate: z.coerce.date().nullable(),
  assignedToUserId: z.number().nullable(),
  assignedTo: z.string().nullable(),

  createdBy: z.number(),
  createdAt: z.coerce.date(),
  updatedBy: z.number().nullable(),
  updatedAt: z.coerce.date().nullable(),
});

export type Task = z.infer<typeof taskSchema>;

const groupWithTaskResponse = z.object({
  groupId: z.number(),
  name: z.string(),
  tasks: z.array(taskSchema),

  createdBy: z.number(),
  createdAt: z.coerce.date(),
  updatedBy: z.number().nullable(),
  updatedAt: z.coerce.date().nullable(),
});

export type Group = Omit<z.infer<typeof groupWithTaskResponse>, "tasks">;

const getWorkspaceByNameResponse = z.object({
  workspaceId: z.number(),
  groups: z.array(groupWithTaskResponse),
});

export type GetWorkspaceByNameResponse = z.infer<
  typeof getWorkspaceByNameResponse
>;

export async function getWorkspaceByName(accessToken: string, name: string) {
  const response = await fetch(`${workspace}/by-name/${name}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch workspace", { cause: response });
  }

  return getWorkspaceByNameResponse.parse(await response.json());
}

const updateGroupResponse = z.object({
  groupId: z.number(),
  name: z.string(),

  createdBy: z.number(),
  createdAt: z.coerce.date(),
  updatedBy: z.number().nullable(),
  updatedAt: z.coerce.date().nullable(),
});

export async function updateGroup(
  accessToken: string,
  workspaceId: number,
  groupId: number,
  name: string
) {
  const response = await fetch(
    `${workspace}/${workspaceId}/groups/${groupId}`,
    {
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ name }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update group", { cause: response });
  }

  return updateGroupResponse.parse(await response.json());
}

type CreateTask = {
  workspaceId: number;
  groupId: number;
  title: string;
  description?: string;
  dueDate?: Date;
  assignedToUserId?: number;
};

const createTaskResponse = z.object({
  taskId: z.number(),
  title: z.string(),
  description: z.string().nullable(),
  dueDate: z.coerce.date().nullable(),
  assignedToUserId: z.number().nullable(),

  createdBy: z.number(),
  createdAt: z.coerce.date(),
  updatedBy: z.number().nullable(),
  updatedAt: z.coerce.date().nullable(),
});
export async function createTask(accessToken: string, payload: CreateTask) {
  const response = await fetch(
    `${workspace}/${payload.workspaceId}/groups/${payload.groupId}/tasks`,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        title: payload.title,
        description: payload.description,
        dueDate: payload.dueDate,
        assignedToUserId: payload.assignedToUserId,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to create task", { cause: response });
  }

  return createTaskResponse.parse(await response.json());
}

type UpdateTask = {
  workspaceId: number;
  groupId: number;
  taskId: number;
  toGroupId?: number;
  title?: string | null;
  description?: string | null;
  dueDate?: Date | null;
  assignedToUserId?: number | null;
};
export async function updateTask(accessToken: string, payload: UpdateTask) {
  return fetch(
    `${workspace}/${payload.workspaceId}/groups/${payload.groupId}/tasks/${payload.taskId}`,
    {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        title: payload.title,
        description: payload.description,
        dueDate: payload.dueDate,
        assignedToUserId: payload.assignedToUserId,
        toGroupId: payload.toGroupId,
      }),
    }
  );
}

type TaskIdentifier = {
  workspaceId: number;
  groupId: number;
  taskId: number;
};

export async function getTask(accessToken: string, payload: TaskIdentifier) {
  const response = await fetch(
    `${workspace}/${payload.workspaceId}/groups/${payload.groupId}/tasks/${payload.taskId}`,
    {
      method: "GET",
      credentials: "include",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch task", { cause: response });
  }

  return taskSchema.parse(await response.json());
}

export async function deleteTask(accessToken: string, payload: TaskIdentifier) {
  return fetch(
    `${workspace}/${payload.workspaceId}/groups/${payload.groupId}/tasks/${payload.taskId}`,
    {
      method: "DELETE",
      credentials: "include",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );
}
