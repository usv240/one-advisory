from fastapi import APIRouter,HTTPException
from one_advisory.managed_platform import ManagedPlatformError,ManagedPlatformEvidence
def build_platform_router(project_id):
 router=APIRouter(prefix="/api",tags=["managed-platform"])
 @router.get("/platform")
 def platform():
  try:return ManagedPlatformEvidence(project_id).read()
  except ManagedPlatformError as exc:raise HTTPException(status_code=503,detail=str(exc)) from exc
 return router
