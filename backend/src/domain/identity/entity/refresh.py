from pydantic import BaseModel


class RefreshResponse(BaseModel):
    accessToken: str
