"""Executable One Advisory autonomy acceptance flow."""
from __future__ import annotations
import argparse,json
from urllib.request import Request,urlopen

def call(base,method,path,body=None):
 data=json.dumps(body or {}).encode() if method=="POST" else None
 with urlopen(Request(base.rstrip("/")+path,data=data,method=method,headers={"Content-Type":"application/json"}),timeout=30) as response:return response.status,json.loads(response.read())
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--url",default="http://127.0.0.1:8000");args=parser.parse_args();checks=[]
 def check(name,value):checks.append(bool(value));print(f"{'PASS' if value else 'FAIL'}  {name}")
 _,health=call(args.url,"GET","/health");check("health identifies One Advisory",health["project"]=="one-advisory");check("health exposes governed autonomy",health["autonomy"]=="governed-multi-agent-auto-continuation");check("advisory and allocation authority remain human",health["advisory_authority"]==health["resource_authority"]=="human-only")
 _,incident=call(args.url,"POST","/api/incidents");incident_id=incident["incident_id"];check("authorized feed automatically delivers standing playbooks",incident["status"]=="instructions_delivered" and len(incident["autonomy"]["last_run_actions"])==3);check("out-of-policy closure is rejected",len(incident["policy_rejections"])==1)
 _,wakes=call(args.url,"GET",f"/api/hardening/incidents/{incident_id}/wakes");check("three durable acknowledgement checks are registered",len(wakes["wakes"])==3)
 _,incident=call(args.url,"POST",f"/api/incidents/{incident_id}/facility-updates");check("facility events automatically surface the conflict",incident["status"]=="resource_conflict" and incident["autonomy"]["last_run_actions"]==["resource_conflict_detected"]);check("resource agent does not allocate",incident["resource_conflict"]["selected"] is None)
 _,incident=call(args.url,"POST",f"/api/incidents/{incident_id}/allocate",{"option_id":"slot-to-ltc","approver":"Jordan Lee - synthetic"});check("one allocation automatically resumes escalation",incident["status"]=="response_verified" and len(incident["escalations"])==1);check("allocation is explicitly not AI-made",not incident["resource_conflict"]["selected_by_ai"])
 _,incident=call(args.url,"POST",f"/api/incidents/{incident_id}/recover",{"approver":"Jordan Lee - synthetic"});check("authorized rescission closes three recovery loops",incident["status"]=="closed" and len(incident["recovery"]["checks"])==3)
 _,demo=call(args.url,"POST","/api/demo/full");check("one-request demo completes the governed fleet run",demo["autonomy"]["complete"] and demo["status"]=="closed")
 _,proof=call(args.url,"GET","/api/proof");check("governance proof is green",proof["passed"]==proof["total"])
 print()
 print(f"{sum(checks)}/{len(checks)} checks passed");return 0 if all(checks) else 1
if __name__=="__main__":raise SystemExit(main())