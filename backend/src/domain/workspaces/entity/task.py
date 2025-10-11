from typing import Optional, Union
from src.common.model import Model
import datetime


class CreateTask(Model):
    workspaceId: int
    groupId: int
    title: str
    description: Optional[str]
    dueDate: Optional[datetime.datetime]
    assignedToUserId: Optional[int]


class UpdateTask(Model):
    workspaceId: int
    groupId: int
    taskId: int
    toGroupId: Union[int, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None
    dueDate: Union[datetime.datetime, None] = None
    assignedToUserId: Union[int, None] = None

class DeleteTask(Model):
    taskId: int

class GetTaskById(Model):
    taskId: int