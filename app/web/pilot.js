let incidentSummaries = [];

async function refreshIncidents(preferredId = incident?.incident_id) {
  const data = await api("/api/pilot/incidents");
  incidentSummaries = data.incidents;
  const select = $("#incident-select");
  select.innerHTML = incidentSummaries.length
    ? incidentSummaries.map((row) => `<option value="${escapeHtml(row.incident_id)}">${escapeHtml(row.title)} · ${escapeHtml(row.zone)} · ${escapeHtml(stateName(row.status))}</option>`).join("")
    : '<option value="">No incidents yet</option>';
  if (preferredId && incidentSummaries.some((row) => row.incident_id === preferredId)) select.value = preferredId;
}

async function loadIncident(incidentId) {
  if (!incidentId) return;
  render(await api(`/api/incidents/${incidentId}`));
  $("#incident-origin").textContent = incident.origin === "pilot_input" ? "Custom synthetic exercise" : "Sample fixture";
}

reset = async function loadSample() {
  const created = await api("/api/incidents", { method: "POST" });
  render(created);
  await refreshIncidents(created.incident_id);
  $("#incident-origin").textContent = "Sample fixture";
  toast("New synthetic sample loaded");
};

const coreAdvance = advance;
advance = async function advanceAndRefresh() {
  await coreAdvance();
  if (incident) await refreshIncidents(incident.incident_id);
};

const coreRenderConflict = renderConflict;
renderConflict = function renderNamedConflict(conflict) {
  coreRenderConflict(conflict);
  if (!conflict) return;
  const cards = $$("#conflict-panel .request-pair div b");
  conflict.requests.forEach((request, index) => {
    const facility = incident.facilities.find((row) => row.facility_id === request.facility_id);
    if (cards[index] && facility) cards[index].textContent = facility.name;
  });
};

function openPilotDialog() { $("#incident-dialog").showModal(); }
function closePilotDialog() { $("#incident-dialog").close(); }

async function submitPilotIncident(event) {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget));
  const payload = {
    synthetic_acknowledgement: true,
    data_class: "synthetic",
    advisory: {
      title: values.title,
      authority: values.authority,
      issued_at: values.issued_at,
      zone_name: values.zone_name,
      source_title: values.source_title,
      source_url: values.source_url,
    },
    facilities: [
      { type: "dialysis", name: values.dialysis_name, contact: values.dialysis_contact, capacity_note: values.dialysis_note },
      { type: "school_childcare", name: values.school_name, contact: values.school_contact, capacity_note: values.school_note },
      { type: "long_term_care", name: values.care_name, contact: values.care_contact, capacity_note: values.care_note },
    ],
  };
  try {
    const created = await api("/api/pilot/incidents", { method: "POST", body: JSON.stringify(payload) });
    closePilotDialog();
    render(created);
    await refreshIncidents(created.incident_id);
    $("#incident-origin").textContent = "Custom synthetic exercise";
    toast("Custom synthetic incident created");
  } catch (error) { toast(error.message); }
}

document.addEventListener("DOMContentLoaded", async () => {
  $("#new-incident").onclick = openPilotDialog;
  $("#incident-close").onclick = closePilotDialog;
  $("#incident-cancel").onclick = closePilotDialog;
  $("#incident-form").onsubmit = submitPilotIncident;
  $("#incident-select").onchange = (event) => loadIncident(event.target.value);
  try {
    await refreshIncidents();
    if (incidentSummaries.length) await loadIncident(incidentSummaries[0].incident_id);
    else await reset();
  } catch (error) { toast(error.message); }
});
