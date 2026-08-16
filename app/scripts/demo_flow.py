"""Executable One Advisory acceptance flow."""
from __future__ import annotations
import argparse,json
from urllib.error import HTTPError
from urllib.request import Request,urlopen

def call(base,method,path,body=None):
    data=json.dumps(body or {}).encode() if method=="POST" else None
    with urlopen(Request(base.rstrip("/")+path,data=data,method=method,headers={"Content-Type":"application/json"}),timeout=20) as response:return response.status,json.loads(response.read())
def main():
    p=argparse.ArgumentParser();p.add_argument("--url",default="http://127.0.0.1:8000");a=p.parse_args();checks=[]
    def check(name,value):checks.append(bool(value));print(f"{'PASS' if value else 'FAIL'}  {name}")
    _,health=call(a.url,"GET","/health");check("health identifies One Advisory",health["project"]=="one-advisory");check("authority remains human",health["advisory_authority"]==health["resource_authority"]=="human-only")
    _,inc=call(a.url,"POST","/api/incidents");iid=inc["incident_id"];check("starts with authorized advisory",not inc["advisory"]["decision_by_system"])
    try:call(a.url,"POST",f"/api/incidents/{iid}/approve",{"approver":"Jordan Lee"});blocked=False
    except HTTPError as e:blocked=e.code==409
    check("early approval blocked",blocked)
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/activate");check("nine tasks are source-backed",sum(len(f["tasks"]) for f in inc["facilities"])==9)
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/policy-test");check("unregistered closure rejected",len(inc["policy_rejections"])==1)
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/approve",{"approver":"Jordan Lee - synthetic"});check("instructions require named approval",len(inc["approvals"])==1)
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/facility-updates");check("non-response remains visible",any(f["response_state"]=="no_response" for f in inc["facilities"]))
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/detect-conflict");check("resource agent does not allocate",inc["resource_conflict"]["selected"] is None)
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/allocate",{"option_id":"slot-to-ltc","approver":"Jordan Lee - synthetic"});check("human allocation recorded",not inc["resource_conflict"]["selected_by_ai"])
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/escalate");check("non-response escalated",len(inc["escalations"])==1)
    _,inc=call(a.url,"POST",f"/api/incidents/{iid}/recover",{"approver":"Jordan Lee - synthetic"});check("three recovery loops close",inc["status"]=="closed" and len(inc["recovery"]["checks"])==3)
    _,proof=call(a.url,"GET","/api/proof");check("governance proof green",proof["passed"]==proof["total"])
    print(f"\n{sum(checks)}/{len(checks)} checks passed");return 0 if all(checks) else 1
if __name__=="__main__":raise SystemExit(main())

