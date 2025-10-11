import datetime
from typing import Optional

from src.common.model import Model


class WorkspaceRequest(Model):
    name: str


class WorkspaceResponse(Model):
    workspaceId: int
    name: str
    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]
