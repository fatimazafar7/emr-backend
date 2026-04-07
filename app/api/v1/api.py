from app.api.v1.endpoints import login, ai, patients

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
# We will add other routers here (patients, clinics, ai-agents)
