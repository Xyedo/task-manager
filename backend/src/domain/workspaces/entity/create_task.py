import datetime
from typing import Optional
from pydantic import BaseModel


class CreateTaskPayload(BaseModel):
    title: str
    description: Optional[str] = None
    dueDate: Optional[datetime.datetime] = None
    assignedToUserId: Optional[int] = None


class CreateTaskResponse(BaseModel):
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
