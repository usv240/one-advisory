"""Idempotently register One Advisory capabilities in Google Cloud Agent Registry."""
from __future__ import annotations
import os,time
import google.auth
from google.auth.transport.requests import AuthorizedSession

PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT","agentic-fleet-2026");LOCATION=os.getenv("REGION","us-central1")
SERVICE_URL=os.getenv("ONE_ADVISORY_URL","https://one-advisory-109051079423.us-central1.run.app")
API_ROOT="https://agentregistry.googleapis.com/v1"
CAPABILITIES={
 "one-advisory-facility-fleet":("One Advisory Facility Fleet","Discovers differentiated, source-bearing work for synthetic critical facilities.","/api/registry"),
 "one-advisory-policy-gateway":("One Advisory Policy Gateway","Rejects actions outside registered scope and named-human authority.","/api/proof"),
 "one-advisory-resource-coordinator":("One Advisory Resource Coordinator","Surfaces resource conflicts and options without allocating.","/api/conformance"),
 "one-advisory-recovery-verifier":("One Advisory Recovery Verifier","Verifies failure-safe recovery, idempotent wakes, and authority gates.","/api/hardening/proof"),
}

def wait_for_operation(session,response):
 operation=response.json();name=str(operation.get("name",""))
 if "/operations/" not in name or operation.get("done"):return
 for _ in range(60):
  status=session.get(f"{API_ROOT}/{name}",timeout=15);status.raise_for_status();operation=status.json()
  if operation.get("done"):
   if operation.get("error"):raise RuntimeError(operation["error"])
   return
  time.sleep(1)
 raise TimeoutError(name)

def main():
 credentials,_=google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"]);session=AuthorizedSession(credentials);parent=f"projects/{PROJECT}/locations/{LOCATION}"
 for service_id,(display_name,description,path) in CAPABILITIES.items():
  body={"displayName":display_name,"description":description,"interfaces":[{"url":SERVICE_URL+path,"protocolBinding":"HTTP_JSON"}],"agentSpec":{"type":"NO_SPEC"}}
  resource=f"{API_ROOT}/{parent}/services/{service_id}";current=session.get(resource,timeout=15)
  if current.status_code==404:response=session.post(f"{API_ROOT}/{parent}/services",params={"serviceId":service_id},json=body,timeout=30);action="created"
  else:current.raise_for_status();response=session.patch(resource,params={"updateMask":"displayName,description,interfaces,agentSpec"},json={"name":resource.removeprefix(API_ROOT+"/"),**body},timeout=30);action="updated"
  response.raise_for_status();wait_for_operation(session,response);print(f"{action}: {service_id}")

if __name__=="__main__":main()
