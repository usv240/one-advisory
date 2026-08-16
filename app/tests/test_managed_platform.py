from one_advisory.managed_platform import ManagedPlatformEvidence,RUNTIME_IDS
class Response:
 def __init__(self,data,status_code=200):self.data=data;self.status_code=status_code
 def json(self):return self.data
class Session:
 def get(self,url,timeout):
  if "reasoningEngines" in url:
   engine=url.rsplit("/",1)[-1];role=next(k for k,v in RUNTIME_IDS.items() if v==engine)
   return Response({"name":url.rsplit("/v1beta1/",1)[-1],"displayName":f"One Advisory Runtime {role}","spec":{"identityType":"AGENT_IDENTITY","effectiveIdentity":f"{role}@example.test","deploymentSpec":{"minInstances":0,"maxInstances":1,"agentGatewayConfig":{"clientToAgentConfig":{"agentGateway":"projects/demo/locations/us-central1/agentGateways/day-three-ingress"}}}}})
  if "agentGateways" in url:return Response({"name":"projects/demo/locations/us-central1/agentGateways/day-three-ingress","googleManaged":{"governedAccessPath":"CLIENT_TO_AGENT"},"protocols":["MCP"]})
  return Response({"templates":[{"name":"projects/demo/locations/us-central1/templates/one-advisory-agent-input"},{"name":"projects/demo/locations/us-central1/templates/one-advisory-agent-output"}]})
def test_live_platform_evidence_requires_all_managed_controls():
 result=ManagedPlatformEvidence("demo",session_factory=Session).read()
 assert result["runtime_count"]==4
 assert result["unique_agent_identity_count"]==4
 assert result["all_agent_identities_unique"] is True
 assert result["all_runtimes_gateway_bound"] is True
 assert result["gateway"]["governed_access_path"]=="CLIENT_TO_AGENT"
 assert result["model_armor_template_count"]==2
 assert result["memory"]["raw_transcript_replay"] is False
