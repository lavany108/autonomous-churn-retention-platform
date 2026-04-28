const IS_FILE_PROTOCOL = window.location.protocol === "file:";
const API_BASE_CANDIDATES = [
  "http://127.0.0.1:5001",
  "http://localhost:5001",
  "http://127.0.0.1:5002",
  "http://localhost:5002",
  "http://127.0.0.1:5000",
  "http://localhost:5000",
];
const USE_STATIC_PAGE_URLS = IS_FILE_PROTOCOL || window.location.pathname.endsWith(".html");
let RESOLVED_BASE_URL = null;
let LAST_BACKEND_ERROR = "";

function getCredentialsMode() {
  return "include";
}

function withTimeout(ms) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  return { controller, timer };
}

async function probeBaseUrl(baseUrl) {
  const { controller, timer } = withTimeout(1200);
  try {
    const response = await fetch(`${baseUrl}/health`, {
      method: "GET",
      signal: controller.signal,
    });
    return response.ok;
  } catch (error) {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

function getCandidateBaseUrls() {
  const manualBase = localStorage.getItem("apiBaseUrl");
  return manualBase ? [manualBase, ...API_BASE_CANDIDATES] : API_BASE_CANDIDATES;
}

function dedupeUrls(urls) {
  return [...new Set(urls)];
}

async function getBaseUrl() {
  if (RESOLVED_BASE_URL) {
    return RESOLVED_BASE_URL;
  }

  if (!USE_STATIC_PAGE_URLS) {
    RESOLVED_BASE_URL = window.location.origin;
    return RESOLVED_BASE_URL;
  }

  const candidates = dedupeUrls(getCandidateBaseUrls());

  for (const candidate of candidates) {
    // Use the first healthy backend to avoid hardcoded port mismatches.
    if (await probeBaseUrl(candidate)) {
      RESOLVED_BASE_URL = candidate;
      localStorage.setItem("apiBaseUrl", candidate);
      return RESOLVED_BASE_URL;
    }
  }

  RESOLVED_BASE_URL = candidates[0];
  return RESOLVED_BASE_URL;
}

async function apiFetch(path, options = {}) {
  const baseUrl = await getBaseUrl();

  try {
    return await fetch(`${baseUrl}${path}`, options);
  } catch (error) {
    LAST_BACKEND_ERROR = `Primary backend failed: ${baseUrl}`;

    if (!USE_STATIC_PAGE_URLS) {
      throw error;
    }

    // Retry using the next healthy local candidate if static mode is being used.
    const retryCandidates = dedupeUrls(getCandidateBaseUrls()).filter((candidate) => candidate !== baseUrl);
    for (const candidate of retryCandidates) {
      if (!(await probeBaseUrl(candidate))) {
        continue;
      }

      RESOLVED_BASE_URL = candidate;
      localStorage.setItem("apiBaseUrl", candidate);
      return fetch(`${candidate}${path}`, options);
    }

    throw error;
  }
}

function getPageUrl(pageName) {
  return USE_STATIC_PAGE_URLS ? `${pageName}.html` : `/${pageName}`;
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return { msg: text || "Unexpected server response" };
}

const DEFAULT_FEATURES = {
  SeniorCitizen: 0,
  Partner: "Yes",
  Dependents: "No",
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "DSL",
  OnlineSecurity: "No",
  OnlineBackup: "Yes",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "Yes",
  StreamingMovies: "No",
  PaperlessBilling: "Yes",
  PaymentMethod: "Credit card (automatic)",
};

function setMessage(id, message, isError = false) {
  const el = document.getElementById(id);
  if (!el) {
    return;
  }
  el.textContent = message;
  el.style.color = isError ? "#cc1f1a" : "#0c6f4f";
}

async function updateBackendStatus() {
  const statusEl = document.getElementById("backendStatus");
  if (!statusEl) {
    return;
  }

  const url = await getBaseUrl();
  const healthy = await probeBaseUrl(url);
  const note = LAST_BACKEND_ERROR ? ` | ${LAST_BACKEND_ERROR}` : "";
  statusEl.textContent = healthy
    ? `Backend connected: ${url}`
    : `Backend unavailable: ${url}${note}`;
  statusEl.style.color = healthy ? "#0c6f4f" : "#cc1f1a";
}

function getToken() {
  return localStorage.getItem("token");
}

function requireAuth() {
  if (!getToken() && USE_STATIC_PAGE_URLS) {
    window.location.href = getPageUrl("login");
    return false;
  }
  return true;
}

async function handleSignup(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value,
  };

  try {
    const response = await apiFetch("/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: getCredentialsMode(),
      body: JSON.stringify(payload),
    });

    const data = await parseResponse(response);
    if (!response.ok) {
      setMessage("authMessage", data.msg || "Signup failed", true);
      return;
    }

    setMessage("authMessage", "Signup successful. Redirecting to login...");
    setTimeout(() => {
      window.location.href = getPageUrl("login");
    }, 800);
  } catch (error) {
    setMessage("authMessage", "Cannot reach backend. Start Flask and check /health.", true);
    updateBackendStatus();
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const payload = {
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value,
  };

  try {
    const response = await apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: getCredentialsMode(),
      body: JSON.stringify(payload),
    });

    const data = await parseResponse(response);
    if (!response.ok || !data.token) {
      setMessage("authMessage", data.msg || "Login failed", true);
      return;
    }

    localStorage.setItem("token", data.token);
    window.location.href = getPageUrl("dashboard");
  } catch (error) {
    setMessage("authMessage", "Cannot reach backend. Start Flask and check /health.", true);
    updateBackendStatus();
  }
}

async function loadDashboardHeader() {
  try {
    const token = getToken();
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    const response = await apiFetch("/api/dashboard", {
      headers,
      credentials: getCredentialsMode(),
    });

    const data = await parseResponse(response);

    if (!response.ok) {
      if (response.status === 403) {
        setMessage("dashboardMessage", data.msg || "Dashboard is available to business users only.", true);
        setTimeout(() => {
          window.location.href = getPageUrl("index");
        }, 1200);
        return false;
      }

      localStorage.removeItem("token");
      window.location.href = getPageUrl("login");
      return false;
    }

    setMessage("dashboardMessage", `Welcome, ${data.user.name}!`);
    return true;
  } catch (error) {
    setMessage("dashboardMessage", "Cannot reach backend. Start Flask and check /health.", true);
    updateBackendStatus();
    return false;
  }
}

async function loadSegmentsSummary() {
  try {
    const token = getToken();
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    const response = await apiFetch("/api/segments/summary", {
      headers,
      credentials: getCredentialsMode(),
    });

    const data = await parseResponse(response);

    if (!response.ok) {
      if (response.status === 403) {
        setMessage("segmentsMessage", data.msg || "Dashboard is available to business users only.", true);
        setTimeout(() => {
          window.location.href = getPageUrl("index");
        }, 1200);
        return false;
      }

      setMessage("segmentsMessage", data.msg || "Unable to load segment summary", true);
      return false;
    }

    renderSegments(data);
    return true;
  } catch (error) {
    setMessage("segmentsMessage", "Cannot reach backend. Start Flask and check /health.", true);
    updateBackendStatus();
    return false;
  }
}

function renderSegments(summary) {
  const host = document.getElementById("segmentsGrid");
  if (!host) {
    return;
  }

  host.innerHTML = "";

  setMessage(
    "segmentsMessage",
    `Model: ${summary.model} | Segments: ${summary.segment_count} | Customers: ${summary.total_customers}`
  );

  summary.segments.forEach((segment) => {
    const card = document.createElement("article");
    card.className = "segment-card";

    card.innerHTML = `
      <h3>${segment.segment_name}</h3>
      <p class="muted">${segment.segment_description}</p>
      <p><strong>Cluster ID:</strong> ${segment.segment_id}</p>
      <p><strong>Population:</strong> ${segment.size}</p>
      <p><strong>Avg Tenure:</strong> ${segment.avg_tenure ?? "-"}</p>
      <p><strong>Avg Monthly Charges:</strong> ${segment.avg_monthly_charges ?? "-"}</p>
      <p><strong>Dominant Contract:</strong> ${segment.dominant_contract ?? "-"}</p>
    `;

    host.appendChild(card);
  });
}

async function performLogout() {
  try {
    await apiFetch("/auth/logout", {
      method: "POST",
      credentials: getCredentialsMode(),
    });
  } catch (error) {
    // Frontend logout should still proceed even if backend logout call fails.
  }

  localStorage.removeItem("token");
  window.location.href = getPageUrl("login");
}

async function handlePredict(event) {
  event.preventDefault();

  const formData = new FormData(event.target);
  const features = {
    ...DEFAULT_FEATURES,
    gender: formData.get("gender"),
    tenure: Number(formData.get("tenure")),
    Contract: formData.get("Contract"),
    MonthlyCharges: Number(formData.get("MonthlyCharges")),
    TotalCharges: Number(formData.get("TotalCharges")),
  };

  let result;
  let segmentResult;

  try {
    const response = await apiFetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      },
      credentials: getCredentialsMode(),
      body: JSON.stringify({ features }),
    });

    result = await parseResponse(response);
    if (!response.ok) {
      if (response.status === 403) {
        setMessage("dashboardMessage", result.msg || "Dashboard is available to business users only.", true);
        return;
      }

      setMessage("dashboardMessage", result.msg || "Prediction failed", true);
      return;
    }
  } catch (error) {
    setMessage("dashboardMessage", "Cannot reach backend. Start Flask and check /health.", true);
    updateBackendStatus();
    return;
  }

  try {
    const segmentResponse = await apiFetch("/api/segment", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      },
      credentials: getCredentialsMode(),
      body: JSON.stringify({ features }),
    });

    segmentResult = await parseResponse(segmentResponse);
    if (!segmentResponse.ok) {
      if (segmentResponse.status === 403) {
        setMessage("dashboardMessage", segmentResult.msg || "Dashboard is available to business users only.", true);
        return;
      }

      setMessage("dashboardMessage", segmentResult.msg || "Segmentation failed", true);
      return;
    }
  } catch (error) {
    setMessage("dashboardMessage", "Cannot reach backend. Start Flask and check /health.", true);
    updateBackendStatus();
    return;
  }

  const riskBadge = document.getElementById("riskTierBadge");
  const probabilityBar = document.getElementById("probabilityBar");
  const probabilityText = document.getElementById("probabilityText");

  const riskTier = result.risk_tier;
  const probability = result.churn_probability * 100;

  riskBadge.textContent = riskTier;
  riskBadge.className = "badge";
  riskBadge.classList.add(riskTier.toLowerCase().replace(/\s+/g, "-"));

  if (riskTier === "Very Low" || riskTier === "Low") {
    probabilityBar.style.background = "#0ea47a";
  } else if (riskTier === "Medium") {
    probabilityBar.style.background = "#f59e0b";
  } else if (riskTier === "High") {
    probabilityBar.style.background = "#f97316";
  } else {
    probabilityBar.style.background = "#dc2626";
  }

  probabilityBar.style.width = `${probability}%`;
  probabilityText.textContent = `${probability.toFixed(2)}%`;
  document.getElementById("actionBox").textContent = result.recommended_action;
  document.getElementById("segmentName").textContent = segmentResult.segment_name;
  document.getElementById("segmentDescription").textContent = segmentResult.segment_description;
  document.getElementById("result").classList.remove("hidden");
}

async function setupPage() {
  const page = document.body.dataset.page;

  if (page === "signup") {
    document.getElementById("signupForm").addEventListener("submit", handleSignup);
  }

  if (page === "login") {
    document.getElementById("loginForm").addEventListener("submit", handleLogin);
  }

  if (page === "dashboard") {
    if (!requireAuth()) {
      return;
    }

    document.getElementById("dashboardMain").classList.remove("hidden");
    await updateBackendStatus();

    const reconnectBtn = document.getElementById("reconnectBtn");
    if (reconnectBtn) {
      reconnectBtn.addEventListener("click", async () => {
        RESOLVED_BASE_URL = null;
        LAST_BACKEND_ERROR = "";
        await updateBackendStatus();
      });
    }

    const isAuthorized = await loadDashboardHeader();
    if (!isAuthorized) {
      return;
    }

    document.getElementById("churnForm").addEventListener("submit", handlePredict);
    document.getElementById("logoutLink").addEventListener("click", async (event) => {
      event.preventDefault();
      await performLogout();
    });
  }

  if (page === "segments") {
    if (!requireAuth()) {
      return;
    }

    document.getElementById("segmentsMain").classList.remove("hidden");
    const isLoaded = await loadSegmentsSummary();
    if (!isLoaded) {
      return;
    }

    document.getElementById("logoutLink").addEventListener("click", async (event) => {
      event.preventDefault();
      await performLogout();
    });
  }
}

setupPage();