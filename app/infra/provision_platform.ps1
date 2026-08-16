param(
    [string]$ProjectId = "agentic-fleet-2026",
    [string]$Location = "us-central1",
    [string]$RuntimePython = ".\.venv-agent\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
$GatewayId = "day-three-ingress"

gcloud config set api_endpoint_overrides/modelarmor "https://modelarmor.$Location.rep.googleapis.com/"
gcloud services enable modelarmor.googleapis.com networkservices.googleapis.com networksecurity.googleapis.com iap.googleapis.com --project $ProjectId --quiet

foreach ($Template in @("one-advisory-agent-input", "one-advisory-agent-output")) {
    if (-not (gcloud model-armor templates describe $Template --project $ProjectId --location $Location 2>$null)) {
        gcloud model-armor templates create $Template --project=$ProjectId --location=$Location --pi-and-jailbreak-filter-settings-enforcement=enabled --pi-and-jailbreak-filter-settings-confidence-level=medium-and-above --malicious-uri-filter-settings-enforcement=enabled --basic-config-filter-enforcement=enabled --template-metadata-log-sanitize-operations --quiet
    }
}

$Token = gcloud auth print-access-token
$Headers = @{ Authorization = "Bearer $Token" }
$GatewayUrl = "https://networkservices.googleapis.com/v1/projects/$ProjectId/locations/$Location/agentGateways/$GatewayId"
Invoke-RestMethod -Method Get -Uri $GatewayUrl -Headers $Headers | Out-Null

& $RuntimePython infra\deploy_runtimes.py
if ($LASTEXITCODE -ne 0) {
    throw "Agent Runtime deployment failed."
}

$Platform = Invoke-RestMethod "https://one-advisory-109051079423.us-central1.run.app/api/platform"
foreach ($Runtime in $Platform.runtimes) {
    $Member = "principal://$($Runtime.effective_identity)"
    foreach ($Role in @("roles/aiplatform.expressUser", "roles/serviceusage.serviceUsageConsumer")) {
        gcloud projects add-iam-policy-binding $ProjectId --member=$Member --role=$Role --condition=None --quiet | Out-Null
    }
}

& $RuntimePython infra\verify_runtimes.py
if ($LASTEXITCODE -ne 0) {
    throw "Managed Agent Runtime verification failed."
}
