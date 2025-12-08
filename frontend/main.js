const apiInput = document.getElementById("api-base");
const apiStatusEl = document.getElementById("api-status");
const degreeListEl = document.getElementById("degree-list");
const degreeCountEl = document.getElementById("degree-count");
const logEl = document.getElementById("log");
const evaluationPreviewEl = document.getElementById("evaluation-preview");
const queryResultsEl = document.getElementById("query-results");
const objectiveListEl = document.getElementById("objective-list");

const state = {
  apiBase: apiInput.value.trim(),
  degrees: [],
  objectives: [],
  recentEvaluations: [],
  sample: {
    degrees: [
      { degree_id: 1, name: "Computer Science", level: "BS" },
      { degree_id: 2, name: "Data Science", level: "MS" },
      { degree_id: 3, name: "Cybersecurity", level: "Cert" }
    ],
    objectives: [
      { objective_id: 1, code: "LO1", title: "Programming Fundamentals" },
      { objective_id: 2, code: "LO2", title: "Data Management" },
      { objective_id: 3, code: "LO3", title: "Security Principles" }
    ],
    evaluations: [
      { degree_id: 1, section_id: 501, objective_id: 301, eval_method: "Project", count_A: 12, count_B: 8, count_C: 3, count_F: 0, improvement_text: "More checkpoints on milestone two." },
      { degree_id: 2, section_id: 640, objective_id: 302, eval_method: "Quiz", count_A: 18, count_B: 6, count_C: 2, count_F: 1, improvement_text: "" }
    ]
  }
};

document.addEventListener("DOMContentLoaded", init);
document.getElementById("test-api").addEventListener("click", testApiConnection);
document.getElementById("refresh-degrees").addEventListener("click", fetchDegrees);
document.getElementById("reload-degrees").addEventListener("click", fetchDegrees);
document.getElementById("reload-objectives").addEventListener("click", fetchObjectives);
document.getElementById("duplicate-eval").addEventListener("click", duplicateEvaluation);

function init() {
  const storedBase = localStorage.getItem("apiBase");
  if (storedBase) {
    apiInput.value = storedBase;
    state.apiBase = storedBase;
  }

  apiInput.addEventListener("change", () => {
    state.apiBase = apiInput.value.trim();
    localStorage.setItem("apiBase", state.apiBase);
    log(`API base set to ${state.apiBase}`);
  });

  bindForms();
  fetchDegrees();
  fetchObjectives();
  renderEvaluationPreview();
}

function bindForms() {
  const forms = document.querySelectorAll("form[data-endpoint]");
  forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const endpoint = form.dataset.endpoint;
      const method = form.dataset.method || "POST";
      const payload = serializeForm(form);

      if (form.id === "instructor-form" && !/^[0-9]{8}$/.test(payload.instructor_id || "")) {
        log("Instructor ID must be exactly 8 digits.");
        return;
      }

      const result = await apiRequest(endpoint, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (result.ok) {
        log(`Saved via ${method} ${endpoint}`);
        form.reset();
        if (endpoint === "/degrees") {
          fetchDegrees();
        }
        if (endpoint === "/objectives") {
          fetchObjectives();
        }
        if (endpoint === "/evaluations") {
          state.recentEvaluations.unshift(payload);
          renderEvaluationPreview();
        }
      } else {
        log(`Failed to reach ${endpoint}: ${result.error || result.status}`);
      }
    });
  });

  document.getElementById("degree-query-form").addEventListener("submit", (event) => {
    event.preventDefault();
    runQuery(event.target);
  });
  document.getElementById("evaluation-query-form").addEventListener("submit", (event) => {
    event.preventDefault();
    runQuery(event.target);
  });
}

async function testApiConnection() {
  const response = await apiRequest("/");
  if (response.ok) {
    setApiStatus("Connected", false);
    log("API is reachable.");
  } else {
    setApiStatus("No response", true);
    log("API did not respond.");
  }
}

async function fetchDegrees() {
  setApiStatus("Loading degrees…", false);
  const response = await apiRequest("/degrees");
  let degrees = [];

  if (response.ok && Array.isArray(response.data)) {
    degrees = response.data.map(normalizeDegree);
  } else if (response.ok && Array.isArray(response.data?.degrees)) {
    degrees = response.data.degrees.map(normalizeDegree);
  } else {
    degrees = state.sample.degrees;
    log("Using sample degrees. Start the API to see live data.");
  }

  state.degrees = degrees;
  renderDegrees(degrees);
  setApiStatus(`Loaded ${degrees.length} item(s)`, false);
}

function normalizeDegree(degree) {
  if (Array.isArray(degree)) {
    const [degree_id, name, level] = degree;
    return { degree_id, name, level };
  }
  return degree;
}

async function fetchObjectives() {
  const response = await apiRequest("/objectives");
  let objectives = [];

  if (response.ok && Array.isArray(response.data)) {
    objectives = response.data;
  } else if (response.ok && Array.isArray(response.data?.objectives)) {
    objectives = response.data.objectives;
  } else {
    objectives = state.sample.objectives;
    log("Using sample objectives. Start the API to see live data.");
  }

  state.objectives = objectives;
  renderObjectives(objectives);
}

function renderObjectives(objectives) {
  if (!objectiveListEl) return;
  if (!objectives.length) {
    objectiveListEl.innerHTML = `<div class="empty">No objectives returned yet.</div>`;
    return;
  }

  const fragment = document.createDocumentFragment();
  objectives.forEach((obj, idx) => {
    const card = document.createElement("div");
    card.className = "card";
    const title = document.createElement("div");
    title.className = "card__title";
    title.textContent = obj.title || `Objective ${idx + 1}`;
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "card__meta";
    meta.textContent = `Code: ${obj.code || "—"} • ID: ${obj.objective_id ?? "?"}`;
    card.appendChild(meta);

    if (obj.description) {
      const desc = document.createElement("div");
      desc.className = "card__meta";
      desc.textContent = obj.description;
      card.appendChild(desc);
    }

    fragment.appendChild(card);
  });

  objectiveListEl.innerHTML = "";
  objectiveListEl.appendChild(fragment);
}

function serializeForm(form) {
  const formData = new FormData(form);
  const payload = {};
  for (const [key, value] of formData.entries()) {
    if (value === "") continue;
    const numericAllowed = key !== "eval_method" && key !== "title" && key !== "description" && key !== "name" && key !== "code" && key !== "term" && key !== "instructor_id";
    if (!Number.isNaN(Number(value)) && numericAllowed) {
      payload[key] = Number(value);
    } else {
      payload[key] = value;
    }
  }
  if (form.querySelector('input[name="is_core"]')) {
    payload.is_core = form.querySelector('input[name="is_core"]').checked ? 1 : 0;
  }
  return payload;
}

async function apiRequest(path, options = {}) {
  const url = path.startsWith("http") ? path : `${state.apiBase}${path}`;
  try {
    const response = await fetch(url, options);
    const data = await safeJson(response);
    return { ok: response.ok, status: response.status, data };
  } catch (error) {
    return { ok: false, status: "network-error", error: error.message };
  }
}

async function safeJson(response) {
  try {
    return await response.json();
  } catch (_) {
    return null;
  }
}

function renderDegrees(degrees) {
  if (!degrees.length) {
    degreeListEl.innerHTML = `<div class="empty">No degrees returned yet.</div>`;
    degreeCountEl.textContent = "0";
    return;
  }

  degreeCountEl.textContent = degrees.length;
  const fragment = document.createDocumentFragment();
  degrees.forEach((degree) => {
    const card = document.createElement("div");
    card.className = "card";
    const title = document.createElement("div");
    title.className = "card__title";
    title.textContent = degree.name || degree.title || "Degree";
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "card__meta";
    meta.textContent = `Level: ${degree.level || "—"} • ID: ${degree.degree_id ?? degree.id ?? "?"}`;
    card.appendChild(meta);
    fragment.appendChild(card);
  });

  degreeListEl.innerHTML = "";
  degreeListEl.appendChild(fragment);
}

function setApiStatus(text, isError = false) {
  apiStatusEl.textContent = text;
  apiStatusEl.className = `badge ${isError ? "" : "badge--muted"}`;
}

function duplicateEvaluation() {
  const form = document.getElementById("evaluation-form");
  const degreeId = form.elements.degree_id.value;
  if (degreeId) {
    form.elements.duplicate_degree_id.value = degreeId;
    log(`Prepared duplicate entry for degree ${degreeId}.`);
  }
}

function renderEvaluationPreview() {
  const rows = state.recentEvaluations.length ? state.recentEvaluations : state.sample.evaluations;
  if (!rows.length) {
    evaluationPreviewEl.innerHTML = `<div class="empty">Submit an evaluation to preview it here.</div>`;
    return;
  }

  const table = document.createElement("table");
  table.innerHTML = `
    <thead>
      <tr>
        <th>Degree</th><th>Section</th><th>Objective</th><th>Method</th><th>A/B/C/F</th>
      </tr>
    </thead>
    <tbody></tbody>
  `;
  const body = table.querySelector("tbody");
  rows.slice(0, 6).forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.degree_id}</td>
      <td>${row.section_id}</td>
      <td>${row.objective_id}</td>
      <td>${row.eval_method}</td>
      <td>${row.count_A}/${row.count_B}/${row.count_C}/${row.count_F}</td>
    `;
    body.appendChild(tr);
  });

  evaluationPreviewEl.innerHTML = "";
  evaluationPreviewEl.appendChild(table);
}

async function runQuery(form) {
  const endpoint = form.dataset.endpoint || "/";
  const payload = serializeForm(form);
  const params = new URLSearchParams();
  Object.entries(payload).forEach(([key, value]) => {
    params.append(key, value);
  });
  const path = params.toString() ? `${endpoint}?${params.toString()}` : endpoint;
  const response = await apiRequest(path, { method: "GET" });

  if (response.ok && response.data) {
    renderQueryResults(response.data);
    log(`Query success: ${path}`);
  } else {
    log(`Query fallback for ${path}`);
    renderQueryResults(state.sample.evaluations);
  }
}

function renderQueryResults(results) {
  if (!results || (Array.isArray(results) && results.length === 0)) {
    queryResultsEl.innerHTML = `<div class="empty">No results yet.</div>`;
    return;
  }

  const normalized = Array.isArray(results) ? results : [results];
  const fragment = document.createDocumentFragment();
  normalized.slice(0, 12).forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "card";
    const title = document.createElement("div");
    title.className = "card__title";
    title.textContent = item.name || item.title || `Result ${idx + 1}`;
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "card__meta";
    meta.textContent = Object.entries(item)
      .map(([k, v]) => `${k}: ${v}`)
      .join(" • ");
    card.appendChild(meta);
    fragment.appendChild(card);
  });
  queryResultsEl.innerHTML = "";
  queryResultsEl.appendChild(fragment);
}

function log(message) {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement("div");
  entry.textContent = `[${time}] ${message}`;
  logEl.prepend(entry);
}
