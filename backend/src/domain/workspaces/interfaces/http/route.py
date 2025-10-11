import datetime
from typing import Annotated, Union
from src.common.model import Model
from fastapi import APIRouter, Depends
from src.domain.workspaces.entity.update_group import (
    UpdateGroupPayload,
    UpdateGroupRequest,
    UpdateGroupResponse,
)
from src.domain.workspaces.entity.create_task import (
    CreateTaskPayload,
    TaskResponse,
)
from src.domain.workspaces.entity.create import WorkspaceRequest, WorkspaceResponse
from src.domain.workspaces.entity.list_group import (
    GroupByWorkspaceRequest,
    GroupByWorkspaceResponse,
)
from src.domain.workspaces.entity.task import (
    CreateTask,
    DeleteTask,
    GetTaskById,
    UpdateTask,
)
from src.domain.workspaces.entity.pagination import (
    WorkspacePagination,
    WorkspacePaginationResponse,
)
from src.infrastructure.http.guarded import get_current_user
from src.common.token import TokenPayload
from src.domain.workspaces.usecase.workspace import WorkspaceUsecase

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("/")
def list_workspaces(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    pagination: Annotated[WorkspacePagination, Depends()],
) -> WorkspacePaginationResponse:
    return workspace_usecase.list_workspaces(auth, pagination)


@router.post("/")
def create_workspace(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspace: WorkspaceRequest,
) -> WorkspaceResponse:
    return workspace_usecase.create_workspace(auth, workspace)


@router.get("/by-name/{workspace}")
def get_workspace_by_name(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspace: str,
) -> GroupByWorkspaceResponse:
    return workspace_usecase.workspace_detail(
        auth, GroupByWorkspaceRequest(name=workspace)
    )


@router.put("/{workspaceId}/groups/{groupId}")
def update_group(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspaceId: int,
    groupId: int,
    group: UpdateGroupPayload,
) -> UpdateGroupResponse:
    return workspace_usecase.update_group(
        auth,
        UpdateGroupRequest(
            workspaceId=workspaceId, groupId=groupId, **group.model_dump()
        ),
    )


@router.post("/{workspaceId}/groups/{groupId}/tasks")
def create_task(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspaceId: int,
    groupId: int,
    task: CreateTaskPayload,
) -> TaskResponse:

    return workspace_usecase.create_task(
        auth,
        CreateTask(workspaceId=workspaceId, groupId=groupId, **task.model_dump()),
    )


class UpdateTaskPayload(Model):
    title: Union[str, None] = None
    description: Union[str, None] = None
    dueDate: Union[datetime.datetime, None] = None
    assignedToUserId: Union[int, None] = None
    toGroupId: Union[int, None] = None


@router.patch("/{workspaceId}/groups/{groupId}/tasks/{taskId}")
def update_task(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspaceId: int,
    groupId: int,
    taskId: int,
    payload: UpdateTaskPayload,
) -> None:

    workspace_usecase.update_task(
        auth,
        UpdateTask(
            workspaceId=workspaceId,
            groupId=groupId,
            taskId=taskId,
            **payload.model_dump(exclude_unset=True),
        ),
    )


@router.get("/{workspaceId}/groups/{groupId}/tasks/{taskId}")
def get_task(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspaceId: int,
    groupId: int,
    taskId: int,
) -> TaskResponse:
    return workspace_usecase.get_task(auth, GetTaskById(taskId=taskId))


@router.delete("/{workspaceId}/groups/{groupId}/tasks/{taskId}", status_code=204)
def delete_task(
    workspace_usecase: Annotated[WorkspaceUsecase, Depends(WorkspaceUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    workspaceId: int,
    groupId: int,
    taskId: int,
):
    workspace_usecase.delete_task(auth, DeleteTask(taskId=taskId))
