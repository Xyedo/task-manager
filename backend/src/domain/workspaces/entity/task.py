from typing import Optional, Union
from pydantic import BaseModel
import datetime


class CreateTask(BaseModel):
    workspaceId: int
    groupId: int
    title: str
    description: Optional[str]
    dueDate: Optional[datetime.datetime]
    assignedToUserId: Optional[int]


class UpdateTask(BaseModel):
    workspaceId: int
    groupId: int
    taskId: int
    toGroupId: Union[int, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None
    dueDate: Union[datetime.datetime, None] = None
    assignedToUserId: Union[int, None] = None

class DeleteTask(BaseModel):
    taskId: int

class GetTaskById(BaseModel):
    taskId: int