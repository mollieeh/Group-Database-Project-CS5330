const apiInput = document.getElementById("api-base");
const apiStatusEl = document.getElementById("api-status");
const degreeListEl = document.getElementById("degree-list");
const degreeCountEl = document.getElementById("degree-count");
const degreeMessageEl = document.getElementById("degree-message");
const courseMessageEl = document.getElementById("course-message");
const instructorMessageEl = document.getElementById("instructor-message");
const objectiveMessageEl = document.getElementById("objective-message");
const logEl = document.getElementById("log");
const evaluationPreviewEl = document.getElementById("evaluation-preview");
const queryResultsEl = document.getElementById("query-results");
const objectiveListEl = document.getElementById("objective-list");
const degreeCourseListEl = document.getElementById("degree-course-list");
const sectionInstructorSelect = document.getElementById("section-instructor-select");
const sectionCourseSelect = document.getElementById("section-course-select");
const assocDegreeSelect = document.getElementById("assoc-degree-select");
const assocCourseSelect = document.getElementById("assoc-course-select");
const assocObjectiveSelect = document.getElementById("assoc-objective-select");

const state = {
  apiBase: apiInput.value.trim(),
  degrees: [],
  objectives: [],
  degreeCourses: [],
  instructors: [],
  courses: [],
  recentEvaluations: [],
  sample: {
    degrees: [
      { degree_id: 1, name: "Computer Science", level: "BS" },
      { degree_id: 2, name: "Data Science", level: "MS" },
      { degree_id: 3, name: "Cybersecurity", level: "Cert" }
    ],
    courses: [
      { course_id: 101, course_number: "CSCI101", name: "Intro to CS" },
      { course_id: 201, course_number: "CSCI201", name: "Data Structures" }
    ],
    instructors: [
      { instructor_id: "90012345", name: "Ada Lovelace" },
      { instructor_id: "90054321", name: "Alan Turing" }
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
  fetchCourses();
  fetchInstructors();
  fetchObjectives();
  populateAssocDropdowns();
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

      if (form.id === "association-form") {
        payload.is_core = form.querySelector('input[name="is_core"]').checked ? 1 : 0;
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
          setDegreeMessage(`Saved "${payload.name}" (${payload.level})`, "success");
          fetchDegrees();
        }
        if (endpoint === "/courses") {
          setCourseMessage(`Saved course "${payload.name}" (${payload.course_number})`, "success");
          fetchCourses();
        }
        if (endpoint === "/instructors") {
          setInstructorMessage(`Saved instructor "${payload.name}" (${payload.instructor_id})`, "success");
        }
        if (endpoint === "/objectives") {
          setObjectiveMessage(`Saved objective "${payload.title}" (${payload.code})`, "success");
          fetchObjectives();
          populateAssocObjectives();
        }
        if (endpoint === "/evaluations") {
          state.recentEvaluations.unshift(payload);
          renderEvaluationPreview();
        }
        if (endpoint === "/course-objectives" && payload.degree_id) {
          fetchDegreeCourses(payload.degree_id);
        }
      } else {
        if (endpoint === "/degrees" && result.status === 409) {
          setDegreeMessage("Degree already exists for that name and level.", "error");
          log("Degree already exists.");
        } else if (endpoint === "/degrees") {
          setDegreeMessage("Could not save degree. Please try again.", "error");
        }
        if (endpoint === "/courses" && result.status === 409) {
          setCourseMessage("Course already exists (number or name).", "error");
          log("Course already exists.");
        } else if (endpoint === "/courses") {
          setCourseMessage("Could not save course. Please try again.", "error");
        }
        if (endpoint === "/instructors" && result.status === 409) {
          setInstructorMessage("Instructor already exists.", "error");
          log("Instructor already exists.");
        } else if (endpoint === "/instructors") {
          setInstructorMessage("Could not save instructor. Please try again.", "error");
        }
        if (endpoint === "/objectives" && result.status === 409) {
          setObjectiveMessage(result.error || "Objective code/title must be unique.", "error");
          log("Objective already exists.");
        } else if (endpoint === "/objectives") {
          setObjectiveMessage("Could not save objective. Please try again.", "error");
        }
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
  populateAssocDegrees();
}

async function fetchCourses() {
  const response = await apiRequest("/courses");
  let courses = [];

  if (response.ok && Array.isArray(response.data)) {
    courses = response.data;
  } else if (response.ok && Array.isArray(response.data?.courses)) {
    courses = response.data.courses;
  } else {
    courses = state.sample.courses;
    log("Using sample courses. Start the API to see live data.");
  }

  state.courses = courses;
  renderSectionCourseOptions(courses);
  populateAssocCourses();
}

async function fetchInstructors() {
  const response = await apiRequest("/instructors");
  let instructors = [];

  if (response.ok && Array.isArray(response.data)) {
    instructors = response.data;
  } else if (response.ok && Array.isArray(response.data?.instructors)) {
    instructors = response.data.instructors;
  } else {
    instructors = state.sample.instructors;
    log("Using sample instructors. Start the API to see live data.");
  }

  state.instructors = instructors;
  renderSectionInstructorOptions(instructors);
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
  populateAssocObjectives();
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

async function fetchDegreeCourses(degreeId, degreeName = "") {
  const response = await apiRequest(`/degrees/${degreeId}/courses`);
  let rows = [];
  if (response.ok && Array.isArray(response.data)) {
    rows = response.data;
  } else {
    log(`Could not load courses for degree ${degreeId}; showing empty state.`);
  }
  state.degreeCourses = rows;
  renderDegreeCourses(rows, degreeId, degreeName);
}

function renderDegreeCourses(rows, degreeId, degreeName) {
  if (!degreeCourseListEl) return;
  if (!rows.length) {
    degreeCourseListEl.innerHTML = `<div class="empty">No courses found for degree ${degreeName || degreeId || ""}.</div>`;
    return;
  }

  const fragment = document.createDocumentFragment();
  rows.forEach((row) => {
    const card = document.createElement("div");
    card.className = "card";
    const title = document.createElement("div");
    title.className = "card__title";
    title.textContent = row.name || row.course_number || "Course";
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "card__meta";
    meta.textContent = `Number: ${row.course_number || "—"} • ID: ${row.course_id ?? "?"}`;
    card.appendChild(meta);

    const core = document.createElement("div");
    core.className = "card__meta";
    core.textContent = row.is_core ? "Core course" : "Elective";
    card.appendChild(core);

    fragment.appendChild(card);
  });

  degreeCourseListEl.innerHTML = "";
  degreeCourseListEl.appendChild(fragment);
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
    const degreeId = degree.degree_id ?? degree.id;
    card.dataset.degreeId = degreeId;

    const title = document.createElement("div");
    title.className = "card__title";
    title.textContent = degree.name || degree.title || "Degree";
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "card__meta";
    meta.textContent = `Level: ${degree.level || "—"} • ID: ${degreeId ?? "?"}`;
    card.appendChild(meta);

    card.addEventListener("click", () => {
      if (degreeId != null) {
        fetchDegreeCourses(degreeId, degree.name || `Degree ${degreeId}`);
      }
    });

    fragment.appendChild(card);
  });

  degreeListEl.innerHTML = "";
  degreeListEl.appendChild(fragment);
}

function setApiStatus(text, isError = false) {
  apiStatusEl.textContent = text;
  apiStatusEl.className = `badge ${isError ? "" : "badge--muted"}`;
}

function setDegreeMessage(text, tone = "muted") {
  if (!degreeMessageEl) return;
  const toneClass =
    tone === "success" ? "badge--success" : tone === "error" ? "badge--error" : "badge--muted";
  degreeMessageEl.textContent = text;
  degreeMessageEl.className = `badge ${toneClass}`;
}

function setCourseMessage(text, tone = "muted") {
  if (!courseMessageEl) return;
  const toneClass =
    tone === "success" ? "badge--success" : tone === "error" ? "badge--error" : "badge--muted";
  courseMessageEl.textContent = text;
  courseMessageEl.className = `badge ${toneClass}`;
}

function setInstructorMessage(text, tone = "muted") {
  if (!instructorMessageEl) return;
  const toneClass =
    tone === "success" ? "badge--success" : tone === "error" ? "badge--error" : "badge--muted";
  instructorMessageEl.textContent = text;
  instructorMessageEl.className = `badge ${toneClass}`;
}

function setObjectiveMessage(text, tone = "muted") {
  if (!objectiveMessageEl) return;
  const toneClass =
    tone === "success" ? "badge--success" : tone === "error" ? "badge--error" : "badge--muted";
  objectiveMessageEl.textContent = text;
  objectiveMessageEl.className = `badge ${toneClass}`;
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

function renderSectionCourseOptions(courses = []) {
  if (!sectionCourseSelect) return;
  sectionCourseSelect.innerHTML = "";

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a course";
  placeholder.disabled = true;
  placeholder.selected = true;
  sectionCourseSelect.appendChild(placeholder);

  courses.forEach((course) => {
    const option = document.createElement("option");
    option.value = course.course_id;
    option.textContent = `${course.course_number || ""} — ${course.name || "Course"}`.trim();
    sectionCourseSelect.appendChild(option);
  });
}

function renderSectionInstructorOptions(instructors = []) {
  if (!sectionInstructorSelect) return;
  sectionInstructorSelect.innerHTML = "";

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select an instructor";
  placeholder.disabled = true;
  placeholder.selected = true;
  sectionInstructorSelect.appendChild(placeholder);

  instructors.forEach((inst) => {
    const option = document.createElement("option");
    option.value = inst.instructor_id;
    option.textContent = `${inst.instructor_id || ""} — ${inst.name || "Instructor"}`.trim();
    sectionInstructorSelect.appendChild(option);
  });
}

function populateAssocDropdowns() {
  populateAssocDegrees();
  populateAssocCourses();
  populateAssocObjectives();
}

function populateAssocDegrees() {
  if (!assocDegreeSelect) return;
  assocDegreeSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a degree";
  placeholder.disabled = true;
  placeholder.selected = true;
  assocDegreeSelect.appendChild(placeholder);

  state.degrees.forEach((deg) => {
    const option = document.createElement("option");
    option.value = deg.degree_id ?? deg.id;
    option.textContent = `${deg.degree_id ?? deg.id}: ${deg.name || "Degree"} (${deg.level || ""})`.trim();
    assocDegreeSelect.appendChild(option);
  });
}

function populateAssocCourses() {
  if (!assocCourseSelect) return;
  assocCourseSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a course";
  placeholder.disabled = true;
  placeholder.selected = true;
  assocCourseSelect.appendChild(placeholder);

  state.courses.forEach((course) => {
    const option = document.createElement("option");
    option.value = course.course_id ?? course.id;
    option.textContent = `${course.course_number || ""} — ${course.name || "Course"}`.trim();
    assocCourseSelect.appendChild(option);
  });
}

function populateAssocObjectives() {
  if (!assocObjectiveSelect) return;
  assocObjectiveSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select an objective";
  placeholder.disabled = true;
  placeholder.selected = true;
  assocObjectiveSelect.appendChild(placeholder);

  state.objectives.forEach((obj) => {
    const option = document.createElement("option");
    option.value = obj.objective_id ?? obj.id;
    option.textContent = `${obj.code || ""} — ${obj.title || "Objective"}`.trim();
    assocObjectiveSelect.appendChild(option);
  });
}

function log(message) {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement("div");
  entry.textContent = `[${time}] ${message}`;
  logEl.prepend(entry);
}
