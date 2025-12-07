const DEGREE_ENDPOINT = "http://localhost:5000/degrees";

const statusEl = document.getElementById("status");
const listContainer = document.getElementById("list-container");
const refreshButton = document.getElementById("refresh");

refreshButton.addEventListener("click", fetchDegrees);
document.addEventListener("DOMContentLoaded", fetchDegrees);

async function fetchDegrees() {
  setStatus("Loading degrees…");
  renderEmpty("Fetching data…");

  try {
    const response = await fetch(DEGREE_ENDPOINT);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    if (!Array.isArray(data)) {
      throw new Error("Expected an array response from /degrees");
    }

    renderDegrees(data);
    setStatus(`Loaded ${data.length} degree${data.length === 1 ? "" : "s"}.`);
  } catch (error) {
    setStatus(`Error: ${error.message}`);
    renderEmpty("Unable to load degrees. Make sure the API is running on port 5000.");
  }
}

function setStatus(message) {
  statusEl.textContent = message;
}

function renderEmpty(message) {
  listContainer.innerHTML = "";
  const emptyState = document.createElement("div");
  emptyState.className = "empty";
  emptyState.textContent = message;
  listContainer.appendChild(emptyState);
}

function renderDegrees(degrees) {
  if (!degrees.length) {
    renderEmpty("No degrees returned by the API.");
    return;
  }

  const list = document.createElement("ul");
  degrees.forEach((degree, index) => {
    const listItem = document.createElement("li");

    const title = document.createElement("div");
    title.textContent = getDegreeTitle(degree, index);

    listItem.appendChild(title);

    const detailText = getDegreeDetail(degree);
    if (detailText) {
      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = detailText;
      listItem.appendChild(pill);
    }

    list.appendChild(listItem);
  });

  listContainer.innerHTML = "";
  listContainer.appendChild(list);
}

function getDegreeTitle(degree, index) {
  if (degree && typeof degree === "object") {
    const title =
      degree.name ||
      degree.title ||
      degree.degree ||
      degree.program ||
      degree.major ||
      degree.id;
    if (title !== undefined && title !== null) {
      return String(title);
    }
    return `Degree ${index + 1}`;
  }

  return String(degree);
}

function getDegreeDetail(degree) {
  if (degree && typeof degree === "object") {
    const entries = Object.entries(degree)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => `${key}: ${value}`);
    return entries.join(" • ");
  }

  return "";
}
