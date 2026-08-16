import json
from infra.runtime_agent import CAPABILITIES,OneAdvisoryRuntimeAgent

class Armor:
 def screen_request(self,payload):return {"screened":True}
 def screen_response(self,payload):return {"screened":True}
class Response:
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self):return json.dumps({"ok":True}).encode()

def test_each_runtime_role_has_one_get_only_capability():
 assert len(CAPABILITIES)==4
 assert all(row.method=="GET" and row.path.startswith("/api/") for row in CAPABILITIES.values())

def test_runtime_screens_before_and_after_bounded_invocation():
 seen=[]
 def opener(request,timeout):seen.append((request.full_url,request.method,timeout));return Response()
 agent=OneAdvisoryRuntimeAgent("policy-gateway","https://example.test",Armor(),opener)
 result=agent.query({"incident_id":"synthetic"})
 assert seen==[("https://example.test/api/proof","GET",30)]
 assert result["guardrails"]["request"]["screened"] is True
 assert result["guardrails"]["response"]["screened"] is True
