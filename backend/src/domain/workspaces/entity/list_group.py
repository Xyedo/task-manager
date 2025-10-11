import datetime
from typing import Optional
from src.common.model import Model


class GroupByWorkspaceRequest(
    Model,
):
    name: str



class TaskResponse(Model):
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


class GroupResponse(Model):
    groupId: int
    name: str
    tasks: list[TaskResponse]

    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]


class GroupByWorkspaceResponse(Model):
    workspaceId: int
    groups: list[GroupResponse]
