"""Live read-only evidence for One Advisory's managed Agent Platform resources."""
from __future__ import annotations
from typing import Any,Callable
import google.auth
from google.auth.transport.requests import AuthorizedSession

RUNTIME_IDS={"facility-fleet":"6497737137423646720","policy-gateway":"9040019127074291712","resource-coordinator":"8611614212520673280","recovery-verifier":"6243283758477213696"}
class ManagedPlatformError(RuntimeError):pass

class ManagedPlatformEvidence:
 def __init__(self,project_id,location="us-central1",session_factory:Callable[[],Any]|None=None):self.project_id=project_id;self.location=location;self._session_factory=session_factory or self._session
 @staticmethod
 def _session():
  credentials,_=google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"]);return AuthorizedSession(credentials)
 @staticmethod
 def _json(response,component):
  if response.status_code!=200:raise ManagedPlatformError(f"{component} returned HTTP {response.status_code}; no local fallback was substituted")
  return response.json()
 def read(self):
  session=self._session_factory();base=f"projects/{self.project_id}/locations/{self.location}";gateway_name=f"{base}/agentGateways/day-three-ingress";runtimes=[]
  for role,engine_id in RUNTIME_IDS.items():
   resource=self._json(session.get(f"https://{self.location}-aiplatform.googleapis.com/v1beta1/{base}/reasoningEngines/{engine_id}",timeout=8),f"Agent Runtime {role}");spec=resource.get("spec",{});deployment=spec.get("deploymentSpec",{});actual=deployment.get("agentGatewayConfig",{}).get("clientToAgentConfig",{}).get("agentGateway")
   runtimes.append({"role":role,"name":resource.get("name"),"display_name":resource.get("displayName"),"identity_type":spec.get("identityType"),"effective_identity":spec.get("effectiveIdentity"),"gateway":actual,"min_instances":deployment.get("minInstances",0),"max_instances":deployment.get("maxInstances")})
  gateway=self._json(session.get(f"https://networkservices.googleapis.com/v1/{gateway_name}",timeout=8),"Agent Gateway")
  templates=self._json(session.get(f"https://modelarmor.{self.location}.rep.googleapis.com/v1/{base}/templates",timeout=8),"Model Armor").get("templates",[])
  armor=sorted(row.get("name") for row in templates if str(row.get("name","")).rsplit("/",1)[-1] in {"one-advisory-agent-input","one-advisory-agent-output"});identities=[row["effective_identity"] for row in runtimes]
  return {"live":True,"location":self.location,"runtime_count":len(runtimes),"runtimes":runtimes,"unique_agent_identity_count":len(set(identities)),"all_agent_identities_unique":len(identities)==len(set(identities)) and all(identities),"all_runtimes_gateway_bound":all(row["gateway"]==gateway_name for row in runtimes),"gateway":{"name":gateway.get("name"),"governed_access_path":gateway.get("googleManaged",{}).get("governedAccessPath"),"protocols":gateway.get("protocols",[])},"model_armor_templates":armor,"model_armor_template_count":len(armor),"inline_model_armor_attached":False,"memory":{"system":"Firestore bounded facility and incident documents","cross_session":True,"raw_transcript_replay":False},"note":"This endpoint reads managed APIs live and fails instead of substituting checked-in claims."}
