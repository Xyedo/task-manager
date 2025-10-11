

import datetime
from typing import Optional
from src.common.model import Model

class UpdateGroupPayload(Model):
    name: str
  
class UpdateGroupRequest(Model):
    workspaceId: int
    groupId: int
    name: str


class UpdateGroupResponse(Model):
    groupId: int
    name: str

    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]