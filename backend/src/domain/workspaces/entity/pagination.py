from typing import Union
from src.common.model import Model

from src.domain.workspaces.entity.create import WorkspaceResponse


class WorkspacePagination(Model):
    limit: Union[int, None] = None
    lastId: Union[int, None] = None


class WorkspacePaginationResponse(Model):
    workspaces: list[WorkspaceResponse]
