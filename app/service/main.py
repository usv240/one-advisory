"""Cloud Run entry point for One Advisory."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from one_advisory.store import FirestoreIncidentStore,MemoryIncidentStore
from one_advisory.live_evidence import LiveEvidenceRunner
from one_advisory.managed_orchestrator import ManagedOrchestrator
from service.developer_routes import build_developer_router
from service.hardening_routes import build_hardening_router
from service.platform_routes import build_platform_router
from service.pilot_routes import build_pilot_router
from service.routes import build_router
from service.runtime import build_runtime
from service.scheduler_routes import build_scheduler_router
from spine.http_trace import install_http_tracing
from spine.developer_access import DeveloperAccessManager, FirestoreAccessStore, MemoryAccessStore, build_access_router

PROJECT=os.environ.get("GOOGLE_CLOUD_PROJECT","local")
USE_FIRESTORE=os.environ.get("USE_FIRESTORE","").lower() in {"1","true","yes"}
ALLOW_GLOBAL_RESET=os.environ.get("ALLOW_GLOBAL_RESET","").lower() in {"1","true","yes"}
ENABLE_LIVE_MODELS=os.environ.get("ENABLE_LIVE_MODELS","").lower() in {"1","true","yes"}
USE_MANAGED_AGENTS=os.environ.get("USE_MANAGED_AGENTS","").lower() in {"1","true","yes"}
GOOGLE_SERVICES=[
 {"name":"Gemini 3.5 Flash on Vertex AI","role":"Live fail-closed grounded advisory extraction"},
 {"name":"Google Gen AI SDK","role":"Required Google agent framework"},
 {"name":"Gemini Embedding 001","role":"Semantic facility-playbook routing; never authority decisions"},
 {"name":"Cloud Run","role":"Public orchestration service"},
 {"name":"Firestore","role":"Durable incidents, memory, and wake state"},
 {"name":"Cloud Scheduler","role":"OIDC-authenticated background wake scans"},
 {"name":"Cloud Trace","role":"End-to-end request observability"},
 {"name":"Secret Manager","role":"HMAC pepper for API-key and network-fingerprint protection"},
 {"name":"Agent Registry","role":"Discovery and versioning for four specialized agents"},
 {"name":"Agent Runtime","role":"Four scale-to-zero managed agent runtimes"},
 {"name":"Agent Identity","role":"Distinct zero-trust identity per managed agent"},
 {"name":"Agent Gateway","role":"Governed client-to-agent MCP access"},
 {"name":"Model Armor","role":"Regional prompt and response protection templates"},
]
if USE_FIRESTORE:
 from google.cloud import firestore
 firestore_client=firestore.Client(project=PROJECT)
 incident_store=FirestoreIncidentStore(firestore_client); persistence="firestore"
else:
 firestore_client=None
 incident_store=MemoryIncidentStore(); persistence="memory-local"
if USE_FIRESTORE and not os.environ.get("API_KEY_PEPPER"):
 raise RuntimeError("API_KEY_PEPPER must be provided by Secret Manager in deployed mode")
access_store=FirestoreAccessStore(firestore_client,"one_advisory") if USE_FIRESTORE else MemoryAccessStore()
access_manager=DeveloperAccessManager(access_store,"one_advisory","oa_live_",os.environ.get("API_KEY_PEPPER","local-development-only-pepper"))
clock,wake_scheduler=build_runtime(PROJECT,USE_FIRESTORE)
app=FastAPI(title="One Advisory",description="Critical-facility response fleet for authorized drinking-water advisories.",version="0.2.0")
trace_status=install_http_tracing(app,PROJECT,"one-advisory")
model_runner=LiveEvidenceRunner(PROJECT,Path(__file__).resolve().parent.parent/"web") if ENABLE_LIVE_MODELS else None
managed_orchestrator=ManagedOrchestrator(PROJECT) if USE_MANAGED_AGENTS else None
app.include_router(build_router(incident_store,wake_scheduler,allow_global_reset=ALLOW_GLOBAL_RESET,model_runner=model_runner,managed_orchestrator=managed_orchestrator)); app.include_router(build_pilot_router(incident_store,wake_scheduler)); app.include_router(build_hardening_router(incident_store,wake_scheduler,clock))
app.include_router(build_scheduler_router(incident_store,wake_scheduler))
app.include_router(build_platform_router(PROJECT))
app.include_router(build_access_router(access_manager,"One Advisory","/v1/incidents"))
app.include_router(build_developer_router(incident_store,access_manager,wake_scheduler,model_runner=model_runner,managed_orchestrator=managed_orchestrator))
WEB=Path(__file__).resolve().parent.parent/"web"; app.mount("/static",StaticFiles(directory=WEB),name="static")

@app.get("/health")
def health()->dict[str,Any]:
 return {"ok":True,"project":"one-advisory","google_cloud_project":PROJECT,"persistence":persistence,"synthetic_demo":True,"operating_mode":"public-synthetic-sandbox","public_data_policy":"synthetic-only","global_reset":ALLOW_GLOBAL_RESET,"advisory_authority":"human-only","resource_authority":"human-only","model":"gemini-3.5-flash","models":["gemini-3.5-flash","gemini-embedding-001"],"model_mode":"live-fail-closed" if ENABLE_LIVE_MODELS else "local-test-no-model","managed_runtime_mode":"required-fail-closed" if USE_MANAGED_AGENTS else "local-test-disabled","tracing":trace_status,"durable_wakes":"firestore-transactional" if USE_FIRESTORE else "memory-transactional","simulation_clock":True,"autonomy":"governed-managed-agent-auto-continuation" if USE_MANAGED_AGENTS else "governed-multi-agent-auto-continuation","developer_api":{"base":"/v1","key_issuance":"/api/developer/keys","daily_limit":50},"google_services":GOOGLE_SERVICES}
@app.get("/",include_in_schema=False)
def index()->FileResponse:return FileResponse(WEB/"index.html")
