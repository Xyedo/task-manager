

import datetime
from typing import Optional
from pydantic import BaseModel

class UpdateGroupPayload(BaseModel):
    name: str
  
class UpdateGroupRequest(BaseModel):
    workspaceId: int
    groupId: int
    name: str


class UpdateGroupResponse(BaseModel):
    groupId: int
    name: str

    createdAt: datetime.datetime
    updatedAt: Optional[datetime.datetime]
    createdBy: int
    updatedBy: Optional[int]