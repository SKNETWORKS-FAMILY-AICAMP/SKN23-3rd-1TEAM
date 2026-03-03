from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

<<<<<<< HEAD
from backend.api.v1.endpoints import jobs_api, resume_api
from backend.db.base import Base
from backend.db.schema_patch import patch_user_table_columns
from backend.db.session import engine
from backend.models import refresh_token, user
from backend.routers import admin, auth, home, infer, social_auth, interview, attitude
=======
Modification History:
- 2026-02-15: 초기 생성
"""
>>>>>>> 3266b1e9f74b438985b9c6640f00b53ce80b4111


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(  # CORS는 반드시 특정 origin만
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
=======
    allow_origins=["http://localhost:8501","http://localhost:5173"],  # Vue 개발 서버 예시
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
>>>>>>> 3266b1e9f74b438985b9c6640f00b53ce80b4111
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    patch_user_table_columns()


app.include_router(auth.router)
app.include_router(social_auth.router)
app.add_api_route(
    "/api/v1/auth/kakao/start",
    social_auth.kakao_start,
    methods=["GET"],
    tags=["social-auth"],
)
app.add_api_route(
    "/api/v1/auth/kakao/callback",
    social_auth.kakao_callback,
    methods=["GET"],
    tags=["social-auth"],
)
app.add_api_route(
    "/api/v1/auth/google/start",
    social_auth.google_start,
    methods=["GET"],
    tags=["social-auth"],
)
app.add_api_route(
    "/api/v1/auth/google/callback",
    social_auth.google_callback,
    methods=["GET"],
    tags=["social-auth"],
)
app.include_router(admin.router)
app.include_router(home.router)
app.include_router(infer.router)
app.include_router(jobs_api.router)
app.include_router(resume_api.router, prefix="/api")
app.include_router(interview.router)
app.include_router(attitude.router)
