from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import settings
from app.routers import auth, contracts, agent, audit, reports

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="律盾（LawShield）—— 基于 Agent Loop 架构、弹性路由与决策溯源的跨企业级数字法务专家系统",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics setup
Instrumentator().instrument(app).expose(app)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(contracts.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to LawShield API. Go to /docs for Swagger documentation."}
