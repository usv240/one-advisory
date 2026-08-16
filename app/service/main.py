"""Cloud Run entry point for One Advisory."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from one_advisory.store import FirestoreIncidentStore,MemoryIncidentStore
from service.hardening_routes import build_hardening_router
from service.platform_routes import build_platform_router
from service.routes import build_router
from service.runtime import build_runtime
from service.scheduler_routes import build_scheduler_router
from spine.http_trace import install_http_tracing

PROJECT=os.environ.get("GOOGLE_CLOUD_PROJECT","local")
USE_FIRESTORE=os.environ.get("USE_FIRESTORE","").lower() in {"1","true","yes"}
if USE_FIRESTORE:
 from google.cloud import firestore
 incident_store=FirestoreIncidentStore(firestore.Client(project=PROJECT)); persistence="firestore"
else: incident_store=MemoryIncidentStore(); persistence="memory-local"
clock,wake_scheduler=build_runtime(PROJECT,USE_FIRESTORE)
app=FastAPI(title="One Advisory",description="Critical-facility response fleet for authorized drinking-water advisories.",version="0.2.0")
trace_status=install_http_tracing(app,PROJECT,"one-advisory")
app.include_router(build_router(incident_store)); app.include_router(build_hardening_router(incident_store,wake_scheduler,clock))
app.include_router(build_scheduler_router(incident_store,wake_scheduler))
app.include_router(build_platform_router(PROJECT))
WEB=Path(__file__).resolve().parent.parent/"web"; app.mount("/static",StaticFiles(directory=WEB),name="static")

@app.get("/health")
def health()->dict[str,Any]:
 return {"ok":True,"project":"one-advisory","google_cloud_project":PROJECT,"persistence":persistence,"synthetic_demo":True,"advisory_authority":"human-only","resource_authority":"human-only","model":"gemini-3.5-flash","tracing":trace_status,"durable_wakes":"firestore-transactional" if USE_FIRESTORE else "memory-transactional","simulation_clock":True}
@app.get("/",include_in_schema=False)
def index()->FileResponse:return FileResponse(WEB/"index.html")
@app.get("/judges",include_in_schema=False)
def judges()->FileResponse:return FileResponse(WEB/"hardening.html")
@app.get("/judges/architecture",include_in_schema=False)
def architecture_brief()->FileResponse:return FileResponse(WEB/"judges.html")
