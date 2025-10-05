import datetime
from typing import Optional
from pydantic import BaseModel


class GroupByWorkspaceRequest(
    BaseModel,
):
    name: str



class TaskResponse(BaseModel):
    taskId: int
    title: str
    description: Optional[str]
    dueDate: Optional[datetime.datetime]
    assignedToUserId: Optional[int]
    assignedTo: Optional[str]

    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]


class GroupResponse(BaseModel):
    groupId: int
    name: str
    tasks: list[TaskResponse]

    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]


class GroupByWorkspaceResponse(BaseModel):
    workspaceId: int
    groups: list[GroupResponse]
