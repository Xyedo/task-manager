from typing import Union
from pydantic import BaseModel

from src.domain.workspaces.entity.create import WorkspaceResponse


class WorkspacePagination(BaseModel):
    limit: Union[int, None] = None
    lastId: Union[int, None] = None


class WorkspacePaginationResponse(BaseModel):
    workspaces: list[WorkspaceResponse]
