import datetime
from typing import Optional
from pydantic import BaseModel


class WorkspaceRequest(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    workspaceId: int
    name: str
    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]
