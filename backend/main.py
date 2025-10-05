from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.domain.identity.interfaces.http.route import router as identity_router
from src.domain.workspaces.interfaces.http.route import router as workspace_router
from src.infrastructure.http.exception_handler import register_error_handlers
import dotenv
import os

dotenv.load_dotenv(".env")



api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(identity_router)
api_v1.include_router(workspace_router)



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_v1)

register_error_handlers(app)