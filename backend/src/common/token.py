from pydantic import BaseModel



class TokenPayload(BaseModel):
    tenant_id: int
    id: int
    username: str
