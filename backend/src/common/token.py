from src.common.model import Model



class TokenPayload(Model):
    tenant_id: int
    id: int
    username: str
