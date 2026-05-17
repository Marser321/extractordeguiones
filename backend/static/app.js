const form = document.querySelector("#process-form");
const submitButton = document.querySelector("#submit-button");
const badgeBrand = document.querySelector("#badge-brand");
const badgeAi = document.querySelector("#badge-ai");
const globalStatusDot = document.querySelector("#global-status-dot");
const globalStatusTitle = document.querySelector("#global-status-title");
const globalStatusSubtitle = document.querySelector("#global-status-subtitle");
const sourceTabs = document.querySelectorAll(".source-tabs .tab");
const mainTabs = document.querySelectorAll(".main-tab");
const views = document.querySelectorAll(".view");
const urlField = document.querySelector("#url-field");
const uploadField = document.querySelector("#upload-field");
const localField = document.querySelector("#local-field");
const urlInput = document.querySelector("#url");
const uploadInput = document.querySelector("#upload-file");
const uploadFileName = document.querySelector("#upload-file-name");
const localInput = document.querySelector("#local-file-path");
const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
// Removed single progress bar, replaced by pipeline tracker
const errorBox = document.querySelector("#error-box");
const resultBox = document.querySelector("#result-box");
const jobBox = document.querySelector("#job-box");
const copySummary = document.querySelector("#copy-summary");
const brandList = document.querySelector("#brand-list");
const videoList = document.querySelector("#video-list");
const videoDetail = document.querySelector("#video-detail");
const refreshVault = document.querySelector("#refresh-vault");
const analysisStatus = document.querySelector("#analysis-status");
const analysisLinks = document.querySelector("#analysis-links");
const analysisPreview = document.querySelector("#analysis-preview");
const analysisOverview = document.querySelector("#analysis-overview");
const creativeStatusPill = document.querySelector("#creative-status-pill");
const creativeSummary = document.querySelector("#creative-summary");
const generateBrandImage = document.querySelector("#generate-brand-image");
const generatedImageContainer = document.querySelector("#generated-image-container");
const generatedImageContent = document.querySelector("#generated-image-content");
const creativeStrategy = document.querySelector("#creative-strategy");
const openaiConfigPill = document.querySelector("#openai-config-pill");
const openaiSummary = document.querySelector("#openai-summary");
const creativePackList = document.querySelector("#creative-pack-list");
const generateCreativePack = document.querySelector("#generate-creative-pack");
const copyCreativePack = document.querySelector("#copy-creative-pack");
const creativeJsonLink = document.querySelector("#creative-json-link");
const creativeMdLink = document.querySelector("#creative-md-link");
const editorTargetBrand = document.querySelector("#editor-target-brand");
const editorAdaptAll = document.querySelector("#editor-adapt-all");
const editorOriginalBrand = document.querySelector("#editor-original-brand");
const editorTargetBrandPill = document.querySelector("#editor-target-brand-pill");
const editorOriginalBlocks = document.querySelector("#editor-original-blocks");
const editorAdaptedBlocks = document.querySelector("#editor-adapted-blocks");
const polishStatusPill = document.querySelector("#polish-status-pill");
const polishSummary = document.querySelector("#polish-summary");
const polishList = document.querySelector("#polish-list");
const runPolish = document.querySelector("#run-polish");
const aiProvider = document.querySelector("#ai-provider");
const aiModel = document.querySelector("#ai-model");
const aiMode = document.querySelector("#ai-mode");
const aiModeStatus = document.querySelector("#ai-mode-status");
const refreshAi = document.querySelector("#refresh-ai");
const aiStatus = document.querySelector("#ai-status");
const ollamaStatus = document.querySelector("#ollama-status");
const configStatus = document.querySelector("#config-status");
const configSummary = document.querySelector("#config-summary");
const aiSummary = document.querySelector("#ai-summary");
const ollamaRunningPill = document.querySelector("#ollama-running-pill");
const geminiConfigPill = document.querySelector("#gemini-config-pill");
const statQwen = document.querySelector("#stat-qwen");
const statQwenNote = document.querySelector("#stat-qwen-note");
const qwenConfigPill = document.querySelector("#qwen-config-pill");
const qwenSummary = document.querySelector("#qwen-summary");
const statMedia = document.querySelector("#stat-media");
const statMediaNote = document.querySelector("#stat-media-note");
const mediaConfigPill = document.querySelector("#media-config-pill");
const mediaSummary = document.querySelector("#media-summary");
const statOpenRouter = document.querySelector("#stat-openrouter");
const statOpenRouterNote = document.querySelector("#stat-openrouter-note");
const openrouterConfigPill = document.querySelector("#openrouter-config-pill");
const openrouterSummary = document.querySelector("#openrouter-summary");
const statGemini = document.querySelector("#stat-gemini");
const statGeminiNote = document.querySelector("#stat-gemini-note");
const statOllama = document.querySelector("#stat-ollama");
const statOllamaNote = document.querySelector("#stat-ollama-note");
const statAudit = document.querySelector("#stat-audit");
const statAuditNote = document.querySelector("#stat-audit-note");
const statVault = document.querySelector("#stat-vault");
const statVaultNote = document.querySelector("#stat-vault-note");
const startOllama = document.querySelector("#start-ollama");
const stopOllama = document.querySelector("#stop-ollama");
const restartOllama = document.querySelector("#restart-ollama");
const aiTestForm = document.querySelector("#ai-test-form");
const aiTestResult = document.querySelector("#ai-test-result");
const brandProfileForm = document.querySelector("#brand-profile-form");
const brandProfileName = document.querySelector("#brand-profile-name");
const brandProfileResult = document.querySelector("#brand-profile-result");
const outputsList = document.querySelector("#outputs-list");
const outputsPreview = document.querySelector("#outputs-preview");
const generatedShortcuts = document.querySelector("#generated-shortcuts");
const contextVideoTitle = document.querySelector("#context-video-title");
const contextVideoSubtitle = document.querySelector("#context-video-subtitle");
const contextAnalysisBadge = document.querySelector("#context-analysis-badge");
const contextAuditBadge = document.querySelector("#context-audit-badge");
const contextCreativeBadge = document.querySelector("#context-creative-badge");
const contextNextAction = document.querySelector("#context-next-action");
const reanalyzeVideo = document.querySelector("#reanalyze-video");
const nextStepBtns = document.querySelectorAll(".next-step");
const prevStepBtns = document.querySelectorAll(".prev-step");
const steps = document.querySelectorAll(".step");
const stepContents = document.querySelectorAll(".step-content");
const refreshAudit = document.querySelector("#refresh-audit");
const auditDetails = document.querySelector("#audit-details");
const auditSummary = document.querySelector("#audit-summary");
const analysisAuditCard = document.querySelector("#analysis-audit-card");
const analysisAuditScore = document.querySelector("#analysis-audit-score");
const analysisAuditWarnings = document.querySelector("#analysis-audit-warnings");
const refineSkillBtn = document.querySelector("#refine-skill-btn");
const brandMaturityPill = document.querySelector("#brand-maturity-pill");
const brandWisdomCard = document.querySelector("#brand-wisdom-card");
const brandWisdomSummary = document.querySelector("#brand-wisdom-summary");
const themeToggle = document.querySelector("#theme-toggle");
const iconLight = document.querySelector(".icon-light");
const iconDark = document.querySelector(".icon-dark");

// Toast Container Initialization
const toastContainer = document.createElement("div");
toastContainer.className = "toast-container";
document.body.appendChild(toastContainer);

function showToast(title, message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  const icons = {
    info: "AD",
    success: "OK",
    warning: "!",
    error: "ER",
    cloud: "AI",
    db: "DB"
  };

  toast.innerHTML = `
    <div class="toast-icon">${icons[type] || "AD"}</div>
    <div class="toast-content">
      <strong>${title}</strong>
      <p>${message}</p>
    </div>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("toast-out");
    toast.addEventListener("animationend", () => toast.remove());
  }, 4500);
}

function initTheme() {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcons(savedTheme);
}

function updateThemeIcons(theme) {
  if (theme === "dark") {
    iconLight?.classList.add("hidden");
    iconDark?.classList.remove("hidden");
  } else {
    iconLight?.classList.remove("hidden");
    iconDark?.classList.add("hidden");
  }
}

// Dev mode removed — all options in Configuración now

themeToggle?.addEventListener("click", () => {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  updateThemeIcons(newTheme);
});

initTheme();

const consolidateWisdomBtn = document.querySelector("#consolidate-wisdom-btn");

let activeSource = "url";
let currentStep = 1;

function setStep(n) {
  currentStep = n;
  steps.forEach(s => s.classList.toggle("active", parseInt(s.dataset.step) <= n));
  stepContents.forEach(c => c.classList.toggle("active", parseInt(c.dataset.step) === n));
}

function humanStatus(value) {
  return {
    completed: "Listo",
    pending: "Pendiente",
    missing: "Falta",
    failed: "Falló",
    queued: "En cola",
    generating_assets: "Generando",
    analyzing_text: "Analizando",
    extracting_audio: "Extrayendo audio",
    transcribing: "Transcribiendo",
  }[value] || value || "Pendiente";
}

function processMessage(job) {
  const status = job?.status || "queued";
  const message = `${job?.message || ""} ${job?.stage || ""}`.toLowerCase();
  if (status === "failed") return "Necesita atención";
  if (status === "completed") return "Listo. Ya puedes revisar los resultados.";
  if (/transcrib/.test(message)) return "Transcribiendo el video...";
  if (/analiz|analysis|analyz/.test(message)) return "Analizando contenido y marca...";
  if (/audio|extract/.test(message)) return "Preparando el video...";
  if (/asset|output|creative/.test(message)) return "Creando outputs...";
  return "Procesando...";
}

function stateBadge(label, ready = false, warning = false) {
  const kind = ready ? "ready" : warning ? "warning" : "neutral";
  return `<span class="state-badge ${kind}">${escapeHtml(label)}</span>`;
}

function updateContextBanner(video = selectedVideo, viewId = document.querySelector(".view.active-view")?.id) {
  const projectBar = document.querySelector("#active-project-bar");
  if (!contextVideoTitle) return;
  if (!video) {
    if (projectBar) projectBar.classList.add("hidden");
    contextAnalysisBadge.textContent = "Análisis pendiente";
    contextAnalysisBadge.className = "state-badge neutral";
    contextAuditBadge.textContent = "Auditoría pendiente";
    contextAuditBadge.className = "state-badge neutral";
    contextCreativeBadge.textContent = "Creativos pendientes";
    contextCreativeBadge.className = "state-badge neutral";
    contextNextAction.textContent = "Procesar o seleccionar pieza";
    return;
  }

  if (projectBar) projectBar.classList.remove("hidden");
  const analysisReady = video.analysis_status === "completed";
  const auditReady = Boolean(video.audit?.overall_score);
  const creativeReady = Boolean(video.creative_pack?.available);
  contextVideoTitle.textContent = `${video.brand_name} / ${video.video_id}`;
  if (contextVideoSubtitle) contextVideoSubtitle.textContent = `${humanStatus(video.status)} · ${video.segments_count || 0} segmentos`;
  contextAnalysisBadge.textContent = analysisReady ? "Análisis listo" : "Falta análisis";
  contextAnalysisBadge.className = `state-badge ${analysisReady ? "ready" : "warning"}`;
  contextAuditBadge.textContent = auditReady ? `Auditoría ${video.audit.overall_score}/10` : "Auditoría pendiente";
  contextAuditBadge.className = `state-badge ${auditReady ? "ready" : "neutral"}`;
  contextCreativeBadge.textContent = creativeReady ? "Pack creativo listo" : "Creativos pendientes";
  contextCreativeBadge.className = `state-badge ${creativeReady ? "ready" : "neutral"}`;
  contextNextAction.textContent = nextActionForVideo(video, viewId);
}

function nextActionForVideo(video, viewId) {
  if (!video) return "Procesar o seleccionar pieza";
  if (video.analysis_status !== "completed") return "Reanalizar para crear outputs";
  if (!video.audit?.overall_score) return "Generar auditoría";
  if (!video.creative_pack?.available) return "Generar pack creativo";
  if (viewId === "polish-view") return "Ejecutar o revisar microtareas";
  if (viewId === "creative-view") return "Copiar piezas por objetivo";
  if (viewId === "outputs-view") return "Abrir assets por uso";
  return "Revisar creativos u outputs";
}

nextStepBtns.forEach(btn => btn.addEventListener("click", () => {
  if (validateCurrentStep()) setStep(currentStep + 1);
}));
prevStepBtns.forEach(btn => btn.addEventListener("click", () => setStep(currentStep - 1)));

function validateCurrentStep() {
  clearError();
  if (currentStep === 1) {
    const brandName = document.querySelector("#brand-name").value.trim();
    const videoId = document.querySelector("#video-id").value.trim();
    if (!brandName || !videoId) {
      showError("Completa marca e ID del video antes de continuar.");
      return false;
    }
  }

  if (currentStep === 2) {
    if (activeSource === "url" && !urlInput.value.trim()) {
      showError("Pega una URL o cambia a Subir reel/video para usar un archivo local.");
      return false;
    }
    if (handleInstagramUrlHint()) return false;
    if (activeSource === "upload" && !uploadInput.files.length) {
      showError("Arrastra un reel/video o elige un archivo del Mac antes de continuar.");
      return false;
    }
    if (activeSource === "local" && !localInput.value.trim()) {
      showError("Indica la ubicación del archivo local antes de continuar.");
      return false;
    }
  }

  return true;
}

async function loadAuditReport() {
  if (!auditDetails || !auditSummary) return;
  auditDetails.textContent = "Solicitando veredicto...";
  try {
    const response = await fetch("/ai/audit-report");
    const data = await response.json();
    if (data.error) {
      auditDetails.textContent = data.error;
      auditSummary.classList.add("hidden");
      return;
    }
    renderAuditReport(data);
    renderAuditStat(data);
  } catch (error) {
    auditDetails.textContent = "Error de conexión con el auditor.";
    if (statAudit) statAudit.textContent = "Error";
    if (statAuditNote) statAuditNote.textContent = "No se pudo cargar";
  }
}

function renderAuditReport(report) {
  const audits = report.audits || [];
  const audit = audits[0];
  if (!audit) {
    auditSummary.classList.add("hidden");
    auditDetails.textContent = "No hay videos auditables todavía.";
    return;
  }

  const scores = audit.scores || {};
  auditSummary.innerHTML = `
    <div class="audit-score-card">
      <span class="label">Promedio</span>
      <span class="value">${report.average_score || audit.overall_score}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Fidelidad</span>
      <span class="value">${scores.fidelidad || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Marca</span>
      <span class="value">${scores.alineacion_marca || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Quiet Luxury</span>
      <span class="value">${scores.quiet_luxury_score || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Estructura</span>
      <span class="value">${scores.estructura_persuasiva || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Engagement</span>
      <span class="value">${scores.engagement_emocional || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Cumplimiento</span>
      <span class="value">${scores.cumplimiento_marca || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Alucinación</span>
      <span class="value">${scores.alucinacion || "-"}/10</span>
    </div>
    <div class="audit-score-card">
      <span class="label">Coherencia Visual</span>
      <span class="value">${scores.coherencia_visual_narrativa || "-"}/10</span>
    </div>
  `;
  auditSummary.classList.remove("hidden");
  auditDetails.innerHTML = `<strong>${audits.length} videos revisados</strong><span>Promedio general: ${report.average_score || audit.overall_score}/10. Usa estos datos para decidir qué piezas conviene publicar o volver a trabajar.</span>`;
}

function renderAuditStat(report) {
  const total = report.total_videos || 0;
  const score = report.average_score;
  if (statAudit) statAudit.textContent = score ? `${score}/10` : "Sin datos";
  if (statAuditNote) statAuditNote.textContent = `${total} videos auditables`;
}

refreshAudit?.addEventListener("click", loadAuditReport);
if (refreshAudit) loadAuditReport();
let latestResult = null;
let latestCreativePack = null;
let pollTimer = null;
let creativePollTimer = null;
let selectedVideo = null;
const INSTAGRAM_UPLOAD_MESSAGE = "Instagram suele bloquear descargas por URL desde Vercel. Descarga el reel/video y usa Arrastra video para procesarlo sin rate-limit ni login.";

function isInstagramUrl(value) {
  try {
    const hostname = new URL(value).hostname.toLowerCase().replace(/^www\./, "");
    return hostname === "instagram.com" || hostname === "instagr.am";
  } catch (_error) {
    return false;
  }
}

function handleInstagramUrlHint() {
  if (activeSource !== "url") return false;
  if (!isInstagramUrl(urlInput.value.trim())) return false;
  showError(INSTAGRAM_UPLOAD_MESSAGE);
  uploadField.classList.remove("hidden");
  uploadField.classList.add("drag-over");
  window.setTimeout(() => uploadField.classList.remove("drag-over"), 1200);
  return true;
}

function setMainView(viewId) {
  // Redirect merged views into Biblioteca sub-tabs
  if (viewId === "polish-view") viewId = "analysis-view";
  if (viewId === "outputs-view") viewId = "creative-view";
  if (viewId === "guide-view") viewId = "process-view";

  // Analysis and Brand now live inside vault-view as sub-tabs
  let bibTarget = null;
  if (viewId === "analysis-view") { bibTarget = "bib-analysis"; viewId = "vault-view"; }
  if (viewId === "brand-view") { bibTarget = "bib-brand"; viewId = "vault-view"; }

  mainTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === viewId));
  views.forEach((view) => view.classList.toggle("active-view", view.id === viewId));
  updateContextBanner(selectedVideo, viewId);

  if (viewId === "vault-view") {
    loadBrands();
    if (bibTarget) switchBibTab(bibTarget);
  }
  if (viewId === "creative-view") { renderCreativeLab(selectedVideo); renderOutputs(selectedVideo); }
  if (viewId === "ai-view") loadAiStatus();
}

function setSource(source) {
  activeSource = source;
  sourceTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.source === source));
  urlField.classList.toggle("hidden", source !== "url");
  uploadField.classList.toggle("hidden", source !== "upload");
  localField.classList.toggle("hidden", source !== "local");
  urlInput.required = source === "url";
  uploadInput.required = source === "upload";
  localInput.required = source === "local";
}

function setDroppedFiles(fileList) {
  if (!fileList || !fileList.length) return;
  const transfer = new DataTransfer();
  transfer.items.add(fileList[0]);
  uploadInput.files = transfer.files;
  uploadFileName.textContent = `${fileList[0].name} listo para procesar.`;
  uploadField.classList.add("has-file");
  setSource("upload");
  clearError();
}

function setStatus(kind, text, progress = null) {
  statusDot.className = `status-dot ${kind}`;
  statusText.textContent = text;
  
  if (progress !== null) {
    const stepTranscribe = document.querySelector("#step-transcribe");
    const stepAnalysis = document.querySelector("#step-analysis");
    const stepCreative = document.querySelector("#step-creative");
    const pb1 = document.querySelector("#progress-bar-1");
    const pb2 = document.querySelector("#progress-bar-2");
    
    if (stepTranscribe && stepAnalysis && stepCreative && pb1 && pb2) {
      // Reset all classes
      [stepTranscribe, stepAnalysis, stepCreative].forEach(el => {
        el.classList.remove("pending", "processing", "completed");
      });
      
      if (progress === 0) {
        stepTranscribe.classList.add("pending");
        stepAnalysis.classList.add("pending");
        stepCreative.classList.add("pending");
        pb1.style.width = "0%";
        pb2.style.width = "0%";
      } else if (progress > 0 && progress < 33) {
        stepTranscribe.classList.add("processing");
        stepAnalysis.classList.add("pending");
        stepCreative.classList.add("pending");
        pb1.style.width = `${(progress / 33) * 100}%`;
        pb2.style.width = "0%";
      } else if (progress >= 33 && progress < 66) {
        stepTranscribe.classList.add("completed");
        stepAnalysis.classList.add("processing");
        stepCreative.classList.add("pending");
        pb1.style.width = "100%";
        pb2.style.width = `${((progress - 33) / 33) * 100}%`;
      } else if (progress >= 66 && progress < 100) {
        stepTranscribe.classList.add("completed");
        stepAnalysis.classList.add("completed");
        stepCreative.classList.add("processing");
        pb1.style.width = "100%";
        pb2.style.width = `${((progress - 66) / 34) * 100}%`;
      } else if (progress >= 100) {
        stepTranscribe.classList.add("completed");
        stepAnalysis.classList.add("completed");
        stepCreative.classList.add("completed");
        pb1.style.width = "100%";
        pb2.style.width = "100%";
      }

      if (kind === "error") {
        document.querySelectorAll(".pipeline-step.processing").forEach(el => {
          el.classList.remove("processing");
          el.classList.add("pending");
        });
      }
    }
  }
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
  setStatus("error", "No se pudo completar el proceso.", 100);
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function setText(id, value) {
  const element = document.querySelector(id);
  if (element) element.textContent = value || "-";
}

function endpointForSource() {
  if (activeSource === "url") return "/jobs/process-url";
  if (activeSource === "upload") return "/jobs/process-upload";
  return "/jobs/process-local-path";
}

async function submitJob(payload) {
  const response = await fetch(endpointForSource(), payload);
  if (response.status === 413) {
    throw new Error("El archivo es demasiado grande (Vercel permite máximo 4.5MB). Pega un link de YouTube en vez de subirlo, o ejecuta la app localmente.");
  }
  
  let data;
  try {
    data = await response.json();
  } catch (err) {
    throw new Error(`Error inesperado del servidor (${response.status}). Es posible que el archivo sea demasiado pesado para la nube.`);
  }

  if (!response.ok) throw new Error(data.detail || "Error desconocido.");
  return data;
}

function buildPayload(formData) {
  const brandName = formData.get("brand_name")?.trim();
  const videoId = formData.get("video_id")?.trim();
  const provider = formData.get("ai_provider") || "qwen";
  const model = formData.get("ai_model") || null;

  if (activeSource === "upload") {
    if (!uploadInput.files.length) throw new Error("Arrastra o elige un archivo local antes de iniciar.");
    const uploadPayload = new FormData();
    uploadPayload.append("brand_name", brandName);
    uploadPayload.append("video_id", videoId);
    uploadPayload.append("ai_provider", provider);
    if (model) uploadPayload.append("ai_model", model);
    uploadPayload.append("file", uploadInput.files[0]);
    return { method: "POST", body: uploadPayload };
  }

  const payload = { brand_name: brandName, video_id: videoId, ai_provider: provider, ai_model: model };
  if (activeSource === "url") {
    const url = formData.get("url")?.trim();
    if (isInstagramUrl(url)) throw new Error(INSTAGRAM_UPLOAD_MESSAGE);
    payload.url = url;
  }
  if (activeSource === "local") payload.local_file_path = formData.get("local_file_path")?.trim();

  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };
}

function renderJob(job) {
  jobBox.classList.remove("hidden");
  jobBox.innerHTML = `<strong>${processMessage(job)}</strong><span>${job.progress || 0}% completado</span>`;

  const kind = job.status === "failed" ? "error" : job.status === "completed" ? "done" : "running";
  setStatus(kind, processMessage(job), job.progress);

  if (job.status === "failed") {
    showError(job.error || "El trabajo falló.");
    stopPolling();
  }

  if (job.status === "completed" && job.result) {
    stopPolling();
    setResult(job.result);
    loadBrands();
  }
}

function startPolling(jobId) {
  stopPolling();
  pollTimer = window.setInterval(async () => {
    try {
      const response = await fetch(`/jobs/${jobId}`);
      const job = await response.json();
      if (!response.ok) throw new Error(job.detail || "No se pudo consultar el job.");
      renderJob(job);
    } catch (error) {
      showError(error.message);
      stopPolling();
    }
  }, 1200);
}

function stopPolling() {
  if (pollTimer) window.clearInterval(pollTimer);
  pollTimer = null;
}

function setResult(data) {
  latestResult = data;
  const preview = document.querySelector("#script-preview");
  if (preview) {
    preview.innerHTML = `<strong>Extracción lista</strong><span>${data.segments_count || 0} segmentos detectados. El guion y los activos iniciales ya quedaron disponibles.</span>`;
  }

  const brand = encodeURIComponent(data.brand_name);
  const video = encodeURIComponent(data.video_id);
  document.querySelector("#script-link").href = `/vault/script/${brand}/${video}`;
  document.querySelector("#metadata-link").href = `/vault/metadata/${brand}/${video}`;
  document.querySelector("#audio-link").href = `/vault/audio/${brand}/${video}`;
  if (generatedShortcuts) {
    generatedShortcuts.innerHTML = `
      <a class="quick-action" href="/vault/script/${brand}/${video}" target="_blank" rel="noreferrer"><strong>Guion</strong><span>Transcripción lista</span></a>
      <button class="quick-action" type="button" onclick="setMainView('analysis-view')"><strong>Análisis creativo</strong><span>Hooks, estructura y auditoría</span></button>
      <button class="quick-action" type="button" onclick="setMainView('creative-view')"><strong>Outputs creativos</strong><span>Prompts y piezas por objetivo</span></button>
      <button class="quick-action" type="button" onclick="setMainView('vault-view')"><strong>Vault</strong><span>Todo guardado por marca</span></button>
    `;
  }

  resultBox.classList.remove("hidden");
  setStatus("done", "Listo. Ya puedes revisar los resultados.", 100);
}

async function loadBrands() {
  const response = await fetch("/vault/brands");
  const data = await response.json();
  if (!response.ok) {
    brandList.textContent = data.detail || "No se pudo cargar el Vault.";
    statVault.textContent = "Error";
    statVaultNote.textContent = "No se pudo cargar";
    return;
  }

  // Filter out ghost/test brands with 0 videos for a clean, professional listing
  const activeBrands = data.brands.filter(b => (b.video_count || 0) > 0);
  const allBrands = data.brands; // Keep all for editor dropdown

  if (!activeBrands.length) {
    brandList.innerHTML = `<div class="empty-state-box"><span class="empty-icon">📂</span><p>Todavía no hay marcas con contenido. Procesa tu primera pieza en "Nueva extracción".</p></div>`;
    statVault.textContent = "0 videos";
    statVaultNote.textContent = "Sin marcas";
    return;
  }

  const totalVideos = activeBrands.reduce((sum, brand) => sum + (brand.video_count || 0), 0);
  statVault.textContent = `${totalVideos} videos`;
  statVaultNote.textContent = `${activeBrands.length} marcas`;
  brandList.innerHTML = activeBrands.map((brand) => `
    <button class="list-item" type="button" data-brand="${escapeAttr(brand.brand_name)}">
      <strong>${escapeHtml(brand.brand_name)}</strong>
      <span>${brand.video_count} videos</span>
    </button>
  `).join("");

  if (editorTargetBrand) {
    editorTargetBrand.innerHTML = `<option value="">Selecciona marca destino…</option>` +
      allBrands.map(brand => `<option value="${escapeAttr(brand.brand_name)}">${escapeHtml(brand.brand_name)}</option>`).join("");
  }
}

async function loadVideos(brandName) {
  videoList.innerHTML = `<div class="empty-state">Cargando videos...</div>`;
  const response = await fetch(`/vault/brands/${encodeURIComponent(brandName)}/videos`);
  const data = await response.json();
  if (!response.ok) {
    videoList.textContent = data.detail || "No se pudieron cargar videos.";
    return;
  }

  if (!data.videos.length) {
    videoList.innerHTML = `<div class="empty-state-box"><span class="empty-icon">VA</span><p>No hay piezas para esta marca.</p></div>`;
    return;
  }

  videoList.innerHTML = data.videos.map((video) => `
    <button class="asset-card" type="button" data-brand="${escapeAttr(video.brand_name)}" data-video="${escapeAttr(video.video_id)}">
      <div class="asset-card-main">
        <strong>${escapeHtml(video.video_id)}</strong>
        <span class="asset-meta">${humanStatus(video.status)} · ${video.segments_count || 0} segmentos</span>
      </div>
      <div class="asset-badges">
        ${stateBadge("Script", Boolean(video.files?.script))}
        ${stateBadge("Análisis", video.analysis_status === "completed")}
        ${stateBadge("Creativos", Boolean(video.creative_pack?.available))}
      </div>
    </button>
  `).join("");
}

async function loadVideoDetail(brandName, videoId) {
  const response = await fetch(`/vault/brands/${encodeURIComponent(brandName)}/videos/${encodeURIComponent(videoId)}`);
  const data = await response.json();
  if (!response.ok) {
    videoDetail.textContent = data.detail || "No se pudo cargar el detalle.";
    return;
  }
  selectedVideo = data;
  updateContextBanner(data);
  renderVideoDetail(data);
  renderAnalysis(data);
  renderCreativeLab(data);
  renderPolish(data);
  renderOutputs(data);
  renderScriptEditor(data);
  loadBrandProfile(data.brand_name);
}

function renderVideoDetail(video) {
  const brand = encodeURIComponent(video.brand_name);
  const videoId = encodeURIComponent(video.video_id);
  videoDetail.innerHTML = `
    <div class="insight-grid single-column">
      <article class="insight-card">
        <span class="label">Video</span>
        <strong>${escapeHtml(video.brand_name)} / ${escapeHtml(video.video_id)}</strong>
        <p>${humanStatus(video.status)} · ${video.segments_count || 0} segmentos detectados.</p>
      </article>
      <article class="insight-card">
        <span class="label">Estado</span>
        <strong>${video.analysis_status === "completed" ? "Análisis listo" : "Falta análisis"}</strong>
        <p>${video.creative_pack?.available ? "Pack creativo listo." : "Creativos pendientes."}</p>
      </article>
    </div>
    <div class="actions">
      ${video.files.script ? `<a class="secondary-button" href="/vault/script/${brand}/${videoId}" target="_blank" rel="noreferrer">Guion</a>` : ""}
      ${video.analysis_status === "completed" ? `<button class="secondary-button" type="button" onclick="setMainView('analysis-view')">Ver análisis</button>` : ""}
      ${video.creative_pack?.available ? `<button class="secondary-button" type="button" onclick="setMainView('creative-view')">Ver creativos</button>` : ""}
    </div>
  `;
}

async function renderCreativeLab(video) {
  latestCreativePack = null;
  stopCreativePolling();
  creativePackList.innerHTML = "";
  creativeStrategy.innerHTML = "";
  creativeJsonLink.classList.add("hidden");
  creativeMdLink.classList.add("hidden");
  copyCreativePack.disabled = true;
  generateCreativePack.disabled = !video;

  if (!video) {
    creativeStatusPill.textContent = "Sin selección";
    creativeSummary.innerHTML = "Selecciona una pieza en Mis proyectos para crear prompts, adsets y formatos listos para herramientas externas.";
    return;
  }

  creativeStatusPill.textContent = video.creative_pack?.available ? "Pack disponible" : "Pendiente";
  creativeSummary.innerHTML = `
    <strong>${escapeHtml(video.brand_name)} / ${escapeHtml(video.video_id)}</strong>
    <span>${video.creative_pack?.available ? "Pack listo para revisar y copiar." : "Genera un pack para extraer prompts, adsets y mensajes listos para copiar."}</span>
  `;

  if (!video.creative_pack?.available) return;
  await loadCreativePack(video.brand_name, video.video_id);
}

async function loadCreativePack(brandName, videoId) {
  try {
    const response = await fetch(`/creative-pack/${encodeURIComponent(brandName)}/${encodeURIComponent(videoId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No se pudo cargar el pack creativo.");
    renderCreativePack(data);
  } catch (error) {
    creativeStatusPill.textContent = "Error";
    creativeSummary.innerHTML = escapeHtml(error.message);
  }
}

async function renderPolish(video) {
  if (!polishSummary || !polishList) return;
  polishList.innerHTML = "";
  runPolish.disabled = !video;

  if (!video) {
    polishStatusPill.textContent = "Sin selección";
    polishSummary.innerHTML = "Selecciona una pieza en Mis proyectos para ejecutar microtareas de pulido.";
    return;
  }

  polishStatusPill.textContent = "Revisando";
  polishSummary.innerHTML = `<strong>${escapeHtml(video.brand_name)} / ${escapeHtml(video.video_id)}</strong><span>Buscando reporte de pulido existente.</span>`;

  try {
    const response = await fetch(`/microtasks/report/${encodeURIComponent(video.brand_name)}/${encodeURIComponent(video.video_id)}`);
    const report = await response.json();
    if (!response.ok) throw new Error(report.detail || "Sin reporte de pulido.");
    renderPolishReport(report);
  } catch (_error) {
    polishStatusPill.textContent = "Sin datos";
    polishSummary.innerHTML = `
      <strong>Microtareas pendientes.</strong>
      <span>Ejecuta el pulido para detectar mejoras pequeñas antes de usar modelos más potentes.</span>
    `;
    polishList.innerHTML = renderPolishEmptyCards();
  }
}

function renderPolishReport(report) {
  const groups = report.groups || [];
  polishStatusPill.textContent = report.status || "Listo";
  polishSummary.innerHTML = `
    <strong>Score de pulido: ${report.overall_score || 0}/10</strong>
    <span>Próxima acción: ${escapeHtml(report.next_action || "Revisar recomendaciones")}.</span>
  `;
  polishList.innerHTML = groups.map(renderPolishCard).join("") || renderPolishEmptyCards();
}

function renderPolishEmptyCards() {
  const defaults = [
    ["Revisar claridad", "Detecta etiquetas confusas y textos largos."],
    ["Pulir creativos", "Normaliza piezas, objetivos y prompts."],
    ["Mejorar análisis", "Prioriza advertencias y especificidad."],
    ["Actualizar memoria", "Sugiere qué puede aprender la marca."],
    ["Auditar resultado", "Revisa si los recursos están listos para usar."],
  ];
  return defaults.map(([title, text]) => `
    <article class="polish-card">
      <span class="state-badge neutral">Sin datos</span>
      <h3>${title}</h3>
      <p>${text}</p>
      <strong>Ejecutar pulido</strong>
    </article>
  `).join("");
}

function renderPolishCard(item) {
  const ready = item.status === "Listo";
  const warning = item.status === "Necesita revisión" || item.status === "Mejorando";
  return `
    <article class="polish-card">
      <span class="state-badge ${ready ? "ready" : warning ? "warning" : "neutral"}">${escapeHtml(item.status || "Sin datos")}</span>
      <h3>${escapeHtml(item.label || "Microtarea")}</h3>
      <strong>${Number(item.score || 0).toFixed(1)}/10</strong>
      <p>${escapeHtml(item.recommendation || "Revisar resultado.")}</p>
      <button class="secondary-button" type="button" data-polish-action="${escapeAttr(item.group || "")}">${escapeHtml(item.primary_action || "Revisar")}</button>
    </article>
  `;
}

function startCreativePolling(jobId, brandName, videoId) {
  stopCreativePolling();
  creativePollTimer = window.setInterval(async () => {
    try {
      const response = await fetch(`/jobs/${jobId}`);
      const job = await response.json();
      if (!response.ok) throw new Error(job.detail || "No se pudo revisar el progreso creativo.");
      creativeStatusPill.textContent = job.status === "failed" ? "Error" : job.status === "completed" ? "Completado" : "Generando";
      creativeSummary.innerHTML = `
        <strong>${processMessage(job)}</strong>
        <span>Progreso: ${job.progress || 0}%</span>
      `;

      if (job.status === "failed") {
        stopCreativePolling();
        creativeSummary.innerHTML = `<strong>No se pudo generar el pack.</strong><span>${escapeHtml(job.error || "Error desconocido.")}</span>`;
        generateCreativePack.disabled = false;
      }

      if (job.status === "completed") {
        stopCreativePolling();
        await loadCreativePack(brandName, videoId);
        await loadVideoDetail(brandName, videoId);
        generateCreativePack.disabled = false;
      }
    } catch (error) {
      stopCreativePolling();
      creativeStatusPill.textContent = "Error";
      creativeSummary.innerHTML = escapeHtml(error.message);
      generateCreativePack.disabled = false;
    }
  }, 1200);
}

function stopCreativePolling() {
  if (creativePollTimer) window.clearInterval(creativePollTimer);
  creativePollTimer = null;
}

function renderCreativePack(data) {
  const pack = data.pack || {};
  latestCreativePack = pack;
  const metadata = pack.pack_metadata || {};
  const strategy = pack.strategy || {};
  const prompts = pack.channel_packs || [];
  const adsets = pack.adsets || [];
  const messages = pack.message_variants || [];
  const exports = pack.external_tool_exports || [];
  const brand = encodeURIComponent(data.brand_name);
  const videoId = encodeURIComponent(data.video_id);

  creativeStatusPill.textContent = badgeLabel(metadata.source_confidence || "requiere_revision");
  creativeSummary.innerHTML = `
    <strong>${escapeHtml(metadata.brand_name || data.brand_name)} / ${escapeHtml(metadata.video_id || data.video_id)}</strong>
    <span>${prompts.length} piezas creativas · ${adsets.length} adsets · ${messages.length} mensajes.</span>
    <span>Esto no genera imágenes; te da instrucciones listas para herramientas externas.</span>
  `;
  creativeJsonLink.href = `/creative-pack/${brand}/${videoId}/creative_pack.json`;
  creativeMdLink.href = `/creative-pack/${brand}/${videoId}/creative_pack.md`;
  creativeJsonLink.classList.remove("hidden");
  creativeMdLink.classList.remove("hidden");
  copyCreativePack.disabled = false;

  creativeStrategy.innerHTML = `
    <article class="strategy-row">
      <div><span class="label">Big idea</span><strong>${escapeHtml(strategy.big_idea || "-")}</strong></div>
      <div><span class="label">Tensión</span><strong>${escapeHtml(strategy.core_tension || "-")}</strong></div>
      <div><span class="label">Ángulo</span><strong>${escapeHtml(strategy.creative_angle || "-")}</strong></div>
    </article>
  `;

  creativePackList.innerHTML = renderCreativeObjectives(prompts, metadata, adsets, messages);
}

function firstOption(value) {
  return String(value || "")
    .split("|")
    .map((item) => item.trim())
    .filter(Boolean)[0] || "";
}

function hasOptionList(value) {
  return String(value || "").includes("|");
}

function humanChannel(value) {
  const key = firstOption(value).toLowerCase();
  return {
    instagram: "Instagram",
    tiktok: "TikTok",
    youtube_shorts: "Shorts",
    youtube_thumbnail: "YouTube",
    linkedin: "LinkedIn",
    meta_ads: "Meta Ads",
    stories: "Stories",
    carousel: "Carrusel",
    dm: "DM",
    email: "Email",
    caption: "Caption",
    comment_reply: "Respuesta",
    story_reply: "Story reply",
  }[key] || firstOption(value) || "Canal";
}

function humanAssetType(value) {
  const key = firstOption(value).toLowerCase();
  if (/adset|ad|pauta/.test(key)) return "Anuncio visual";
  if (/hero/.test(key)) return "Imagen principal";
  if (/thumbnail/.test(key)) return "Miniatura";
  if (/product|service/.test(key)) return "Tarjeta de oferta";
  if (/quote/.test(key)) return "Tarjeta de cita";
  if (/problem|solution/.test(key)) return "Problema / solución";
  if (/comparison/.test(key)) return "Comparativa";
  if (/testimonial/.test(key)) return "Testimonial";
  if (/cover/.test(key)) return "Portada";
  return firstOption(value) || "Pieza visual";
}

function humanObjective(value) {
  const key = firstOption(value);
  return key || "Objetivo creativo";
}

function renderCreativeObjectives(prompts, metadata, adsets = [], messages = []) {
  const groups = [
    ["vender", "Vender", "Adsets, copies, CTA y piezas para pauta."],
    ["educar", "Educar", "Carruseles, posts y explicaciones para guardar."],
    ["retener", "Retener", "Hooks, shorts, reels y story arcs."],
    ["leads", "Generar leads", "DMs, reserva, masterclass y respuestas."],
    ["reutilizar", "Reutilizar", "Thumbnails, cards y prompts para herramientas externas."],
  ];
  return groups.map(([key, title, description]) => {
    const items = prompts.map((item, index) => ({ item, index })).filter(({ item }) => creativeObjectiveFor(item) === key);
    const adsetItems = key === "vender" ? adsets.map((item, index) => ({ item, index })) : [];
    const messageItems = key === "leads" ? messages.map((item, index) => ({ item, index })) : [];
    if (!items.length && !adsetItems.length && !messageItems.length) return "";
    return `
      <section class="objective-section">
        <div class="objective-head">
          <div><span class="label">Objetivo de negocio</span><h3>${title}</h3><p>${description}</p></div>
          <span class="state-badge ready">${items.length + adsetItems.length + messageItems.length} piezas</span>
        </div>
        <div class="objective-grid">
          ${items.map(({ item, index }) => renderCreativeObjectiveCard(item, index, metadata)).join("")}
          ${adsetItems.map(({ item, index }) => renderAdsetCard(item, index)).join("")}
          ${messageItems.map(({ item, index }) => renderMessageCard(item, index)).join("")}
        </div>
      </section>
    `;
  }).join("");
}

function renderAdsetCard(item, index) {
  const visibleSummary = humanObjective(item.objective) || item.audience || "Pieza lista para pauta.";
  return `
    <article class="creative-card">
      <div class="creative-card-head">
        <div><span class="label">Meta Ads</span><h3>${escapeHtml(item.name || "Adset")}</h3></div>
        <span class="pill badge-fuerte">pauta</span>
      </div>
      <div class="creative-card-body">
        <div class="creative-copy-block">
          <span class="label">Copy principal / Headline</span>
          <strong>${escapeHtml(item.primary_text || item.headline || "-")}</strong>
          <div style="margin-top: 8px; font-size: 0.85rem; color: var(--text-muted);">
            ${item.description ? `<span><strong>Descripción:</strong> ${escapeHtml(item.description)}</span><br>` : ""}
            ${item.audience ? `<span><strong>Audiencia:</strong> ${escapeHtml(item.audience)}</span><br>` : ""}
            ${item.objective ? `<span><strong>Objetivo:</strong> ${escapeHtml(humanObjective(item.objective))}</span>` : ""}
          </div>
        </div>
        
        ${item.visual_prompt ? `
        <div class="strategy-box">
          <h4>Prompt Visual</h4>
          <p class="prompt-box" style="margin-top: 8px;">${escapeHtml(item.visual_prompt)}</p>
        </div>` : ""}

        <div class="creative-action-bar">
          <button class="action-btn" type="button" data-creative-type="adset" data-creative-index="${index}" data-action="copy-text">📝 Copiar Texto</button>
          ${item.visual_prompt ? `<button class="action-btn" type="button" data-creative-type="adset" data-creative-index="${index}" data-action="copy-prompt">🪄 Copiar Prompt</button>
          <button class="action-btn generate-img-btn" type="button" data-creative-type="adset" data-creative-index="${index}" data-action="gen-img">🖼️ Generar Imagen</button>` : ""}
          <button class="action-btn" type="button" data-creative-type="adset" data-creative-index="${index}" data-action="copy-full">📋 Copiar Todo</button>
        </div>
      </div>
    </article>
  `;
}

function renderMessageCard(item, index) {
  const visibleSummary = humanChannel(item.use) || item.tone || "Mensaje listo para activar conversación.";
  return `
    <article class="creative-card">
      <div class="creative-card-head">
        <div><span class="label">${escapeHtml(humanChannel(item.use) || "Mensaje")}</span><h3>Mensaje listo para usar</h3></div>
        <span class="pill badge-requiere_revision">lead</span>
      </div>
      <div class="creative-card-body">
        <div class="creative-copy-block">
          <span class="label">Mensaje</span>
          <strong>${escapeHtml(item.message || "-")}</strong>
          <div style="margin-top: 8px; font-size: 0.85rem; color: var(--text-muted);">
            ${item.tone ? `<span><strong>Tono:</strong> ${escapeHtml(item.tone)}</span><br>` : ""}
            ${item.use ? `<span><strong>Uso:</strong> ${escapeHtml(humanChannel(item.use))}</span>` : ""}
          </div>
        </div>

        <div class="creative-action-bar">
          <button class="action-btn" type="button" data-creative-type="message" data-creative-index="${index}" data-action="copy-text">📝 Copiar Texto</button>
          <button class="action-btn" type="button" data-creative-type="message" data-creative-index="${index}" data-action="copy-full">📋 Copiar Todo</button>
        </div>
      </div>
    </article>
  `;
}

function renderCreativeObjectiveCard(item, index, metadata) {
  const channelLabel = humanChannel(item.channel);
  const assetLabel = humanAssetType(item.asset_type);
  const rawOptions = [item.channel, item.asset_type, item.objective].filter(hasOptionList).map((value) => firstOption(value) !== String(value).trim() ? String(value).trim() : "").filter(Boolean);
  
  const hasVisualPrompt = Boolean(item.prompt && (item.asset_type?.toLowerCase().includes("image") || item.asset_type?.toLowerCase().includes("thumbnail") || item.asset_type?.toLowerCase().includes("video")));

  return `
    <article class="creative-card">
      <div class="creative-card-head">
        <div>
          <span class="label">${escapeHtml(channelLabel)}</span>
          <h3>${escapeHtml(assetLabel)}</h3>
        </div>
        <span class="pill badge-${escapeAttr(item.quality_badge || metadata.source_confidence || "requiere_revision")}">${badgeLabel(item.quality_badge || metadata.source_confidence)}</span>
      </div>
      <div class="creative-card-body">
        <div class="creative-copy-block">
          <span class="label">Copy / Texto principal</span>
          <strong>${escapeHtml(item.copy_overlay || item.hook || "-")}</strong>
          <div style="margin-top: 8px; font-size: 0.85rem; color: var(--text-muted);">
            ${item.cta ? `<span><strong>CTA:</strong> ${escapeHtml(item.cta)}</span><br>` : ""}
            ${item.objective ? `<span><strong>Objetivo:</strong> ${escapeHtml(humanObjective(item.objective))}</span>` : ""}
          </div>
        </div>
        
        <div class="strategy-box">
          <h4>Estrategia</h4>
          <p style="margin-bottom: 0;">${escapeHtml(item.why_it_works || "Pieza diseñada para convertir el análisis en una acción creativa concreta.")}</p>
        </div>

        ${item.prompt ? `
        <div class="strategy-box" style="background: var(--surface-2); border-left-color: var(--text-dim);">
          <h4 style="color: var(--text-dim);">Prompt / Instrucción IA</h4>
          <p class="prompt-box" style="margin-top: 8px; max-height: 120px;">${escapeHtml(item.prompt)}</p>
        </div>` : ""}

        <div class="creative-action-bar">
          <button class="action-btn" type="button" data-creative-type="prompt" data-creative-index="${index}" data-action="copy-text">📝 Copiar Texto</button>
          ${item.prompt ? `<button class="action-btn" type="button" data-creative-type="prompt" data-creative-index="${index}" data-action="copy-prompt">🪄 Copiar Prompt</button>` : ""}
          ${hasVisualPrompt ? `<button class="action-btn generate-img-btn" type="button" data-creative-type="prompt" data-creative-index="${index}" data-action="gen-img">🖼️ Generar Imagen</button>` : ""}
          <button class="action-btn" type="button" data-creative-type="prompt" data-creative-index="${index}" data-action="copy-full">📋 Copiar Todo</button>
        </div>
      </div>
    </article>
  `;
}

function creativeObjectiveFor(item) {
  const text = `${item.channel || ""} ${item.objective || ""} ${item.asset_type || ""} ${item.cta || ""}`.toLowerCase();
  if (/meta|ad|sales|venta|pauta|traffic|awareness/.test(text)) return "vender";
  if (/lead|dm|reserva|masterclass|reply|respuesta/.test(text)) return "leads";
  if (/tiktok|short|reel|story|retenci|comentario|suscrip/.test(text)) return "retener";
  if (/carousel|educ|linkedin|post|guardar|compartir/.test(text)) return "educar";
  return "reutilizar";
}

function badgeLabel(value) {
  return {
    fuerte: "fuerte",
    requiere_revision: "requiere revisión",
    basado_en_supuestos: "basado en supuestos",
  }[value] || "requiere revisión";
}

function creativePromptText(item) {
  return [
    `Canal: ${item.channel || "-"}`,
    `Asset: ${item.asset_type || "-"}`,
    `Objetivo: ${item.objective || "-"}`,
    `Aspect ratio: ${item.aspect_ratio || "-"}`,
    `Hook: ${item.hook || "-"}`,
    `Copy overlay: ${item.copy_overlay || "-"}`,
    `CTA: ${item.cta || "-"}`,
    "",
    item.prompt || "",
    "",
    `Negative prompt: ${item.negative_prompt || "-"}`,
    `Notas: ${item.tool_notes || "-"}`,
    `Por qué funciona: ${item.why_it_works || "-"}`,
  ].join("\n");
}

async function copyToClipboard(text, successMessage) {
  await navigator.clipboard.writeText(text);
  creativeSummary.innerHTML = `<strong>${escapeHtml(successMessage)}</strong>`;
}

function renderAnalysis(video) {
  const analysisContext = document.querySelector("#analysis-context");
  if (!video) {
    analysisStatus.textContent = "Sin selección";
    analysisLinks.innerHTML = "";
    analysisOverview.innerHTML = "";
    analysisPreview.textContent = "Selecciona una pieza en Mis proyectos para revisar el análisis creativo.";
    if (analysisContext) analysisContext.textContent = "Selecciona una pieza en Mis proyectos para revisar el análisis creativo.";
    return;
  }

  if (analysisContext) analysisContext.textContent = `${video.brand_name} / ${video.video_id}`;

  const brand = encodeURIComponent(video.brand_name);
  const videoId = encodeURIComponent(video.video_id);
  analysisStatus.textContent = video.analysis_status || "missing";
  analysisStatus.textContent = video.analysis_status === "completed" ? "Análisis listo" : "Falta análisis";
  const files = [
    ["Auditoría", "auditoria_contexto.json", video.files.context_audit],
    ["Resumen", "resumen_ejecutivo.md", video.files.summary],
    ["Hooks", "hooks.json", video.files.hooks],
    ["Momentos virales", "momentos_virales.json", video.files.viral_moments],
    ["Narrativa", "estructura_narrativa.json", video.files.narrative_structure],
    ["Ideas de reels", "ideas_reels.json", video.files.reel_ideas],
    ["Anuncios", "ads.json", video.files.ads],
    ["Brief creativo", "brief_creativo.md", video.files.creative_brief],
    ["Captions", "captions.json", video.files.captions],
    ["Calendario", "calendario_publicacion.json", video.files.calendar],
    ["Dirección visual", "analisis_visual.json", video.files.visual_analysis],
    ["Prompt de marca", "prompt_base_marca.json", video.files.brand_prompt],
    ["Retrospectiva", "retrospectiva.json", video.files.retrospective],
  ].filter((item) => item[2]);

  analysisLinks.innerHTML = files.map(([label, filename]) => (
    `<a class="secondary-button" href="/vault/analysis/${brand}/${videoId}/${encodeURIComponent(filename)}" target="_blank" rel="noreferrer">${label}</a>`
  )).join("");

  if (!files.length) {
    analysisOverview.innerHTML = `<div class="empty-state-box"><span class="empty-icon">AN</span><p>Esta pieza todavía no tiene análisis generado.</p></div>`;
    analysisPreview.textContent = "Este video todavía no tiene análisis generado.";
    return;
  }

  analysisOverview.innerHTML = renderAnalysisOverview(video);
  analysisPreview.innerHTML = `<strong>Recursos listos para revisar</strong><span>Usa los botones superiores para abrir resúmenes, hooks, anuncios y prompts cuando los necesites.</span>`;
  renderFrames(video);
  renderAnalysisAudit(video);
}

function renderAnalysisOverview(video) {
  const auditReady = Boolean(video.audit?.overall_score);
  const score = auditReady ? `${video.audit.overall_score}/10` : "Pendiente";
  const warnings = video.audit?.warnings || [];
  const warningText = warnings.length ? warnings.slice(0, 2).join(" · ") : "Sin advertencias críticas detectadas.";
  return `
    <article class="insight-card">
      <span class="label">Estado</span>
      <strong>${video.analysis_status === "completed" ? "El análisis está listo para revisar" : "Falta completar análisis"}</strong>
      <p>${video.files?.summary ? "Hay resumen, hooks y activos de contenido disponibles." : "Reanaliza el video para generar outputs accionables."}</p>
    </article>
    <article class="insight-card">
      <span class="label">Auditoría</span>
      <strong>${score}</strong>
      <p>${escapeHtml(warningText)}</p>
    </article>
    <article class="insight-card">
      <span class="label">Oportunidad</span>
      <strong>${video.creative_pack?.available ? "Pasar a outputs creativos" : "Generar pack creativo"}</strong>
      <p>${video.creative_pack?.available ? "Ya puedes copiar piezas por objetivo de negocio." : "Convierte el análisis en prompts, copies y adsets listos para herramientas externas."}</p>
    </article>
  `;
}

function renderAnalysisAudit(video) {
  if (!video || !video.audit || !video.audit.overall_score) {
    analysisAuditCard.classList.add("hidden");
    return;
  }

  const audit = video.audit;
  analysisAuditScore.textContent = `${audit.overall_score}/10`;
  analysisAuditScore.className = `pill audit-score-${audit.overall_score >= 7 ? "high" : audit.overall_score >= 5 ? "mid" : "low"}`;
  
  const warnings = audit.warnings || [];
  analysisAuditWarnings.innerHTML = (warnings.length 
    ? warnings.map(w => `<div class="warning-item">⚠️ ${escapeHtml(w)}</div>`).join("")
    : `<div class="success-item">✅ Calidad robusta detectada.</div>`);
    
  refineSkillBtn.disabled = false;
  refineSkillBtn.textContent = audit.overall_score < 7.5 ? "Mejorar análisis" : "Pulir detalles extra";
  analysisAuditCard.classList.remove("hidden");
}

async function refineSkill() {
  if (!selectedVideo) return;
  
  refineSkillBtn.disabled = true;
  refineSkillBtn.textContent = "Refinando...";
  
  try {
    const response = await fetch(`/jobs/refine/${encodeURIComponent(selectedVideo.brand_name)}/${encodeURIComponent(selectedVideo.video_id)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ai_provider: aiProvider.value || "qwen",
        ai_model: aiModel.value || null
      })
    });
    
    const job = await response.json();
    if (!response.ok) throw new Error(job.detail || "Error al iniciar refinamiento.");
    
    setMainView("process-view");
    renderJob(job);
    startPolling(job.job_id);
  } catch (error) {
    alert(error.message);
    refineSkillBtn.disabled = false;
    refineSkillBtn.textContent = "Mejorar análisis";
  }
}

async function previewAnalysisFile(brand, videoId, filename, button) {
  if (button) {
    analysisLinks.querySelectorAll("button").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
  }
  analysisPreview.textContent = "Cargando pensamiento...";
  try {
    const response = await fetch(`/vault/analysis/${brand}/${videoId}/${filename}`);
    const data = filename.endsWith(".json") ? await response.json() : await response.text();
    analysisPreview.textContent = filename.endsWith(".json") ? JSON.stringify(data, null, 2) : data;
  } catch (error) {
    analysisPreview.textContent = "Error cargando archivo.";
  }
}

function renderFrames(video) {
  const container = document.querySelector("#frames-container");
  if (!video || !video.frames || !video.frames.length) {
    container.classList.add("hidden");
    return;
  }

  const brand = encodeURIComponent(video.brand_name);
  const videoId = encodeURIComponent(video.video_id);

  container.innerHTML = video.frames.map((frame) => `
    <div class="frame-card">
      <img src="/vault/frame/${brand}/${videoId}/${frame}" alt="Frame ${frame}" loading="lazy" />
      <span>${frame}</span>
    </div>
  `).join("");
  container.classList.remove("hidden");
}

function renderOutputs(video) {
  if (!video) {
    outputsList.innerHTML = "";
    outputsPreview.textContent = "Selecciona una pieza en Mis proyectos.";
    return;
  }
  const brand = encodeURIComponent(video.brand_name);
  const videoId = encodeURIComponent(video.video_id);
  const outputs = video.outputs || [];
  outputsList.innerHTML = renderOutputGroups(outputs, brand, videoId);
  outputsPreview.innerHTML = outputs.length
    ? `<strong>${outputs.length} recursos disponibles para ${escapeHtml(video.brand_name)} / ${escapeHtml(video.video_id)}</strong><span>Auditoría: ${video.audit?.overall_score ? `${video.audit.overall_score}/10 (${escapeHtml(video.audit.status)})` : "pendiente"}.</span>`
    : "Este video todavía no tiene outputs. Usa Reanalizar.";
}

function renderOutputGroups(outputs, brand, videoId) {
  if (!outputs.length) return "";
  const groups = [
    ["Estrategia", ["summary", "creative_brief", "narrative_structure", "retrospective"]],
    ["Contenido", ["hooks", "viral_moments", "reel_ideas", "ads", "captions", "calendar"]],
    ["Prompts", ["visual_prompts", "brand_prompt", "creative_pack_md"]],
    ["Auditoría", ["context_audit", "analysis_status"]],
  ];
  return groups.map(([title, keys]) => {
    const items = outputs.filter((output) => keys.includes(output.key));
    if (!items.length) return "";
    const links = items.map((output) => (
      `<a class="output-link" href="/vault/analysis/${brand}/${videoId}/${encodeURIComponent(output.filename)}" target="_blank" rel="noreferrer"><strong>${escapeHtml(output.label)}</strong><span>Abrir recurso</span></a>`
    )).join("");
    return `<section class="output-group"><h3>${title}</h3><div class="output-grid">${links}</div></section>`;
  }).join("");
}

async function loadAiStatus() {
  try {
    const [aiResponse, ollamaResponse, configResponse] = await Promise.all([
      fetch("/ai/status"),
      fetch("/ollama/status"),
      fetch("/config/status"),
    ]);
    const aiData = await aiResponse.json();
    const ollamaData = await ollamaResponse.json();
    const configData = await configResponse.json();

    renderOllamaControl(ollamaData);
    renderConfigStatus(configData);
    renderAiSummary(aiData);
    updateAiModels(aiData);
    applyHybridMode(configData);
    updateGlobalStatus(aiData, ollamaData, configData);
  } catch (error) {
    console.error("[AI status]", error);
    aiSummary.textContent = "No se pudo cargar el estado de IA.";
    configSummary.textContent = "No se pudo cargar configuración.";
    if (statQwen) statQwen.textContent = "Error";
    if (statMedia) statMedia.textContent = "Error";
    statOpenRouter.textContent = "Error";
    statGemini.textContent = "Oculto";
    statOllama.textContent = "Error";
  }
}

function applyHybridMode(config) {
  if (config.is_cloud) {
    const localTab = document.querySelector('.tab[data-source="local"]');
    if (localTab) localTab.style.display = 'none';
    if (activeSource === "local") {
      activeSource = "url";
      sourceTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.source === "url"));
      urlField.classList.remove("hidden");
      uploadField.classList.add("hidden");
      localField.classList.add("hidden");
    }

    const ollamaOption = document.querySelector('option[value="ollama"]');
    if (ollamaOption) ollamaOption.disabled = true;
    if (aiProvider?.value === "ollama") aiProvider.value = "qwen";

    const geminiOption = document.querySelector('option[value="gemini"]');
    if (geminiOption && aiProvider?.value !== "gemini") geminiOption.classList.add('hidden');

    const caption = document.querySelector('.product-caption');
    if (caption && !caption.querySelector('.cloud-pill')) {
      const pill = document.createElement('span');
      pill.className = 'cloud-pill';
      pill.textContent = 'CLOUD';
      caption.appendChild(pill);
    }
  }
}

function renderOllamaControl(status) {
  ollamaRunningPill.textContent = status.running ? "Encendido" : "Apagado";
  statOllama.textContent = status.running ? "Encendido" : "Apagado";
  statOllamaNote.textContent = status.installed ? "Disponible en este Mac" : "No disponible";
  ollamaStatus.innerHTML = `<strong>${status.running ? "Motor local encendido." : status.installed ? "Motor local apagado." : "Motor local no disponible."}</strong><span>${status.running ? "Solo úsalo como fallback local o comparación." : status.installed ? "Puedes encenderlo si Qwen/API cloud no está disponible." : "Usa Qwen API como motor principal."}</span>`;
  startOllama.disabled = !status.can_start;
  stopOllama.disabled = !status.can_stop;
  restartOllama.disabled = !status.installed;
}

function renderConfigStatus(status) {
  const qwenReady = Boolean(status.qwen_api_key_configured);
  if (qwenConfigPill) qwenConfigPill.textContent = qwenReady ? "Activo" : "Requerido";
  if (statQwen) statQwen.textContent = qwenReady ? "Listo" : "Pendiente";
  if (statQwenNote) statQwenNote.textContent = qwenReady ? "Core activo" : "Falta key";
  if (qwenSummary) {
    qwenSummary.innerHTML = `
      <strong>${qwenReady ? "Qwen directo está activo." : "Falta la key de Qwen."}</strong>
      <span>${qwenReady ? `Base: ${escapeHtml(status.qwen_base_url || "")}. Modelo rápido: ${escapeHtml(status.qwen_default_model || "")}.` : "Configura DASHSCOPE_API_KEY o QWEN_API_KEY en .env/Vercel."}</span>
    `;
  }

  const falReady = Boolean(status.fal_api_key_configured);
  const hfReady = Boolean(status.huggingface_api_key_configured);
  const mediaReady = falReady || hfReady;
  if (mediaConfigPill) mediaConfigPill.textContent = mediaReady ? "Activo" : "Opcional";
  if (statMedia) statMedia.textContent = mediaReady ? "Listo" : "Opcional";
  if (statMediaNote) statMediaNote.textContent = mediaReady ? `${falReady ? "fal" : ""}${falReady && hfReady ? " + " : ""}${hfReady ? "HF" : ""}` : "Falta FAL_KEY/HF_TOKEN";
  if (mediaSummary) {
    mediaSummary.innerHTML = `
      <strong>${mediaReady ? "Media open-source-first disponible." : "Media visual todavía opcional."}</strong>
      <span>${mediaReady ? "fal/Hugging Face quedan listos para imagen, video o modelos de apoyo." : "Configura FAL_KEY para imagen/video y HF_TOKEN para providers de Hugging Face."}</span>
    `;
  }

  // OpenRouter Status
  const orReady = Boolean(status.openrouter_api_key_configured);
  if (openrouterConfigPill) openrouterConfigPill.textContent = orReady ? "Respaldo activo" : "Sin respaldo";
  if (statOpenRouter) statOpenRouter.textContent = orReady ? "Listo" : "Pendiente";
  if (statOpenRouterNote) statOpenRouterNote.textContent = orReady ? "Fallback cloud" : "No configurado";
  if (openrouterSummary) {
    openrouterSummary.innerHTML = `
      <strong>${orReady ? "OpenRouter está activo." : "OpenRouter no está configurado."}</strong>
      <span>${orReady ? "Queda como respaldo si Qwen directo falla o para comparar modelos." : "Configura OPENROUTER_API_KEY si quieres un seguro cloud."}</span>
    `;
  }

  // OpenAI Status
  const openaiReady = Boolean(status.openai_api_key_configured);
  if (openaiConfigPill) openaiConfigPill.textContent = openaiReady ? "Fallback activo" : "Opcional";
  if (openaiSummary) {
    openaiSummary.innerHTML = `
      <strong>${openaiReady ? "OpenAI está disponible como fallback." : "OpenAI no es requerido para el MVP core."}</strong>
      <span>${openaiReady ? "Puede usarse para GPT Image si se elige manualmente." : "La ruta open-source-first usa fal/Hugging Face para media."}</span>
    `;
  }
  
  if (generateBrandImage) {
    generateBrandImage.classList.remove("hidden");
    generateBrandImage.disabled = !mediaReady && !openaiReady;
    generateBrandImage.textContent = mediaReady ? "Generar Imagen" : openaiReady ? "Generar Imagen" : "Falta FAL_KEY";
  }

  // Gemini Status (Hidden/Secondary)
  const geminiReady = Boolean(status.gemini_api_key_configured && (status.gemini_sdk_installed || status.gemini_legacy_sdk_installed));
  if (geminiConfigPill) geminiConfigPill.textContent = "Oculto";
  if (statGemini) statGemini.textContent = "Oculto";
  if (statGeminiNote) statGeminiNote.textContent = "Secundario";
  if (configSummary) {
    configSummary.innerHTML = `<strong>Gemini queda como secundario para multimodal/transcripción cuando exista key.</strong>`;
  }
}

function updateGlobalStatus(aiData, ollamaData, configData) {
  const isQwenReady = Boolean(configData.qwen_api_key_configured);
  const isOpenRouterReady = Boolean(configData.openrouter_api_key_configured);
  const isGeminiReady = Boolean(configData.gemini_api_key_configured && (configData.gemini_sdk_installed || configData.gemini_legacy_sdk_installed));
  const isOllamaReady = Boolean(ollamaData.running);

  if (isQwenReady) {
    badgeAi?.classList.add("hidden");
    globalStatusDot.className = "status-dot done";
    globalStatusTitle.textContent = "Pipeline Qwen activo";
    globalStatusSubtitle.textContent = "Core listo con Qwen directo";
  } else if (isOpenRouterReady) {
    badgeAi?.classList.add("hidden");
    globalStatusDot.className = "status-dot done";
    globalStatusTitle.textContent = "Respaldo cloud activo";
    globalStatusSubtitle.textContent = "Qwen directo pendiente";
  } else if (isGeminiReady) {
    badgeAi?.classList.add("hidden");
    globalStatusDot.className = "status-dot done";
    globalStatusTitle.textContent = "Gemini activo (Respaldo)";
    globalStatusSubtitle.textContent = "Listo para analizar";
  } else if (isOllamaReady) {
    badgeAi?.classList.add("hidden");
    globalStatusDot.className = "status-dot done";
    globalStatusTitle.textContent = "Motor local activo";
    globalStatusSubtitle.textContent = "Modo desarrollo listo";
  } else {
    badgeAi?.classList.remove("hidden");
    globalStatusDot.className = "status-dot error";
    globalStatusTitle.textContent = "Pipeline pendiente";
    globalStatusSubtitle.textContent = "Falta DASHSCOPE_API_KEY o QWEN_API_KEY";
  }
}


function renderAiSummary(status) {
  const ollama = status.ollama || {};
  const gemini = status.gemini || {};
  const qwen = status.qwen || {};
  const huggingface = status.huggingface || {};
  const fal = status.fal || {};
  const openrouter = status.openrouter || {};
  const registry = status.model_registry || {};
  const fastMode = registry.modes?.fast;
  const fallbackMode = registry.modes?.fallback;
  const recommended = qwen.available ? "Qwen directo" : openrouter.available ? "OpenRouter (respaldo)" : gemini.available ? "Gemini" : ollama.available ? "Ollama local" : "Ninguno";
  const testProvider = document.querySelector("#test-ai-provider");
  if (testProvider) testProvider.value = fastMode?.provider || (recommended === "Gemini" ? "gemini" : recommended.includes("OpenRouter") ? "openrouter" : "ollama");
  const activeModel = qwen.available ? fastMode?.model : openrouter.available ? fallbackMode?.model : gemini.available ? gemini.default_model : ollama.default_model;
  aiSummary.innerHTML = `
    <strong>${recommended === "Ninguno" ? "No hay motor activo." : `${recommended} es la mejor opción ahora.`}</strong>
    <span>${recommended === "Ninguno" ? "Configura DASHSCOPE_API_KEY/QWEN_API_KEY para activar el core." : `Modelo base: ${escapeHtml(activeModel || "")}. Media: ${fal.available ? "fal" : huggingface.available ? "HF" : "pendiente"}.`}</span>
  `;
}

async function runOllamaAction(action) {
  ollamaStatus.innerHTML = `<strong>Aplicando cambio...</strong><span>Esto puede tardar unos segundos.</span>`;
  [startOllama, stopOllama, restartOllama].forEach((button) => {
    button.disabled = true;
  });
  try {
    const response = await fetch(`/ollama/${action}`, { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail));
    ollamaStatus.innerHTML = `<strong>Cambio aplicado.</strong><span>Actualizando estado...</span>`;
  } catch (error) {
    ollamaStatus.innerHTML = `<strong>No se pudo aplicar el cambio.</strong><span>${escapeHtml(error.message)}</span>`;
  } finally {
    await loadAiStatus();
  }
}

function modeIsBlocked(mode, status) {
  if (!mode) return true;
  if (mode.provider === "ollama") {
    if (status.is_cloud) return true;
    const installed = Boolean(mode.installed || (status.ollama?.models || []).includes(mode.model));
    return !installed || !status.ollama?.running;
  }
  if (mode.provider === "qwen") return !status.qwen?.available;
  if (mode.provider === "huggingface") return !status.huggingface?.available;
  if (mode.provider === "fal") return !status.fal?.available;
  if (mode.provider === "openrouter") return !status.openrouter?.available;
  if (mode.provider === "gemini") return !status.gemini?.available;
  if (mode.provider === "groq") return !status.groq?.available;
  return !mode.available;
}

function activeModeFromStatus(status) {
  const registry = status.model_registry || {};
  const modes = registry.modes || {};
  const currentMode = aiMode?.value || registry.default_mode || "fast";
  if (modes[currentMode] && !modeIsBlocked(modes[currentMode], status)) return currentMode;
  const fallbackMode = registry.default_mode || "fast";
  if (modes[fallbackMode] && !modeIsBlocked(modes[fallbackMode], status)) return fallbackMode;
  return Object.keys(modes).find((key) => !modeIsBlocked(modes[key], status)) || currentMode;
}

function updateAiModels(status) {
  const qwen = status.qwen || {};
  const huggingface = status.huggingface || {};
  const fal = status.fal || {};
  const openrouter = status.openrouter || {};
  const gemini = status.gemini || {};
  const ollama = status.ollama || {};
  const registry = status.model_registry || {};
  const modes = registry.modes || {};
  const modeOrder = ["fast", "quality", "deep", "vision", "fallback", "local"].filter((mode) => modes[mode]);
  const selectedMode = activeModeFromStatus(status);
  const selected = modes[selectedMode];

  if (aiMode && modeOrder.length) {
    aiMode.innerHTML = modeOrder.map((modeKey) => {
      const mode = modes[modeKey];
      const blocked = modeIsBlocked(mode, status);
      const suffix = blocked && modeKey === "local" ? " (pendiente)" : "";
      return `<option value="${escapeAttr(modeKey)}" ${modeKey === selectedMode ? "selected" : ""} ${blocked ? "disabled" : ""}>${escapeHtml(mode.label || modeKey)}${suffix}</option>`;
    }).join("");
    aiMode.value = selectedMode;
  }

  let models = [];
  if (selected) {
    aiProvider.value = selected.provider;
    models = [selected.model];
  } else if (aiProvider.value === "qwen") models = qwen.models;
  else if (aiProvider.value === "huggingface") models = huggingface.models;
  else if (aiProvider.value === "fal") models = fal.models;
  else if (aiProvider.value === "openrouter") models = openrouter.models;
  else if (aiProvider.value === "gemini") models = gemini.models;
  else models = ollama.models;

  aiModel.innerHTML = (models || []).map((model) => `<option value="${escapeAttr(model)}">${escapeHtml(model)}</option>`).join("");
  if (!aiModel.innerHTML) {
    aiModel.innerHTML = `<option value=""></option>`;
  }
  if (selected?.model) aiModel.value = selected.model;

  const testProvider = document.querySelector("#test-ai-provider");
  const testModel = document.querySelector("#test-ai-model");
  if (testProvider && selected?.provider) testProvider.value = selected.provider;
  if (testModel && selected?.model) testModel.value = selected.model;

  if (aiModeStatus) {
    if (selected) {
      aiModeStatus.innerHTML = `
        <strong>${escapeHtml(selected.label)}: ${escapeHtml(selected.provider)} / ${escapeHtml(selected.model)}</strong>
        <span>Fallback: ${escapeHtml(selected.fallback_provider || "manual")}. Riesgo/costo: ${escapeHtml(selected.cost_risk || "n/d")}.</span>
      `;
    } else {
      aiModeStatus.innerHTML = `<strong>Sin modo IA activo.</strong><span>Configura Qwen API o usa un respaldo disponible.</span>`;
    }
  }
}

async function loadBrandProfile(brandName) {
  if (!brandName) {
    brandProfileName.textContent = "Sin marca";
    return;
  }
  const response = await fetch(`/vault/brands/${encodeURIComponent(brandName)}/profile`);
  const profile = await response.json();
  if (!response.ok) {
    brandProfileResult.textContent = profile.detail || "No se pudo cargar el perfil.";
    badgeBrand.classList.remove("hidden");
    return;
  }
  
  if (!profile.tone && !profile.audience) {
    badgeBrand.classList.remove("hidden");
  } else {
    badgeBrand.classList.add("hidden");
  }

  brandProfileName.textContent = brandName;
  document.querySelector("#profile-brand-name").value = brandName;
  document.querySelector("#profile-tone").value = profile.tone || "";
  document.querySelector("#profile-audience").value = profile.audience || "";
  document.querySelector("#profile-offer").value = profile.offer || "";
  document.querySelector("#profile-visual-style").value = profile.visual_style || "";
  document.querySelector("#profile-colors").value = (profile.colors || []).join(", ");
  document.querySelector("#profile-forbidden").value = (profile.forbidden_words || []).join(", ");
  document.querySelector("#profile-cta").value = profile.cta || "";
  brandProfileResult.innerHTML = `<strong>${profile.tone || profile.audience ? "Perfil cargado." : "Perfil incompleto."}</strong><span>Completa tono, audiencia, oferta y estilo visual para mejorar los análisis.</span>`;

  // Cargar evolución
  try {
    const evoResponse = await fetch(`/training/evolution/${encodeURIComponent(brandName)}`);
    const evo = await evoResponse.json();
    if (evo && evo.current_level) {
      brandMaturityPill.textContent = `Nivel: ${evo.current_level.toUpperCase()}`;
      brandMaturityPill.className = `pill badge-${evo.current_level === "expert" ? "fuerte" : evo.current_level === "intermediate" ? "requiere_revision" : "basado_en_supuestos"}`;
    }
    
    // Cargar Sabiduría
    const wisdomRes = await fetch(`/training/wisdom/${encodeURIComponent(brandName)}`);
    const wisdom = await wisdomRes.json();
    if (wisdom && (wisdom.reglas_oro || wisdom.barreras_criticas)) {
      brandWisdomCard.classList.remove("hidden");
      let html = "";
      if (wisdom.personalidad_detectada) html += `<em>"${wisdom.personalidad_detectada}"</em><br><br>`;
      if (wisdom.reglas_oro) {
        html += "<strong>Reglas de Oro:</strong><ul>";
        wisdom.reglas_oro.forEach(r => html += `<li>${r}</li>`);
        html += "</ul>";
      }
      if (wisdom.barreras_criticas) {
        html += "<strong>Barreras Críticas:</strong><ul>";
        wisdom.barreras_criticas.forEach(b => html += `<li>${b}</li>`);
        html += "</ul>";
      }
      brandWisdomSummary.innerHTML = html;
    } else {
      brandWisdomCard.classList.add("hidden");
    }
  } catch (e) {
    console.warn("No se pudo cargar la evolución o sabiduría de la marca");
  }
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#039;",
  }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#096;");
}

mainTabs.forEach((tab) => tab.addEventListener("click", () => setMainView(tab.dataset.view)));
sourceTabs.forEach((tab) => tab.addEventListener("click", () => setSource(tab.dataset.source)));

// ═══ Biblioteca sub-tab switching ═══
function switchBibTab(targetId) {
  document.querySelectorAll(".bib-tab").forEach(t => {
    const isActive = t.dataset.bib === targetId;
    t.classList.toggle("active", isActive);
    t.setAttribute("aria-selected", isActive ? "true" : "false");
  });
  document.querySelectorAll(".bib-panel").forEach(p => {
    const isActive = p.id === targetId;
    p.classList.toggle("active-bib", isActive);
    p.hidden = !isActive;
  });
  // Trigger renders when switching to sub-tabs
  if (targetId === "bib-analysis") { renderAnalysis(selectedVideo); renderPolish(selectedVideo); }
  if (targetId === "bib-brand") loadBrandProfile(selectedVideo?.brand_name || document.querySelector("#brand-name")?.value?.trim() || "");
}

document.querySelectorAll(".bib-tab").forEach(tab =>
  tab.addEventListener("click", () => switchBibTab(tab.dataset.bib))
);

// ═══ Config button in sidebar footer ═══
const sidebarConfigBtn = document.querySelector("#sidebar-config-btn");
if (sidebarConfigBtn) {
  sidebarConfigBtn.addEventListener("click", () => setMainView("ai-view"));
}

// ═══ Move analysis-view and brand-view content into Biblioteca sub-panels ═══
document.addEventListener("DOMContentLoaded", () => {
  const analysisView = document.querySelector("#analysis-view");
  const brandView = document.querySelector("#brand-view");
  const bibAnalysis = document.querySelector("#bib-analysis");
  const bibBrand = document.querySelector("#bib-brand");

  if (analysisView && bibAnalysis) {
    // Move all children from analysis-view into bib-analysis
    while (analysisView.firstChild) {
      bibAnalysis.appendChild(analysisView.firstChild);
    }
    analysisView.style.display = "none";
  }

  if (brandView && bibBrand) {
    // Move all children from brand-view into bib-brand
    while (brandView.firstChild) {
      bibBrand.appendChild(brandView.firstChild);
    }
    brandView.style.display = "none";
  }
});
urlInput.addEventListener("input", () => {
  if (!isInstagramUrl(urlInput.value.trim())) return;
  showError(INSTAGRAM_UPLOAD_MESSAGE);
});
urlInput.addEventListener("paste", () => {
  window.setTimeout(handleInstagramUrlHint, 0);
});

consolidateWisdomBtn.addEventListener("click", async () => {
  const brandName = document.querySelector("#profile-brand-name").value.trim() || selectedVideo?.brand_name || "";
  if (!brandName) {
    brandProfileResult.innerHTML = `<strong>Elige una marca primero.</strong><span>Selecciona una pieza del Vault o escribe una marca para actualizar su sabiduría.</span>`;
    return;
  }
  
  consolidateWisdomBtn.disabled = true;
  consolidateWisdomBtn.textContent = "Actualizando...";
  brandProfileResult.innerHTML = `<strong>Actualizando sabiduría...</strong><span>Estoy revisando el historial de auditorías de la marca.</span>`;
  
  try {
    const response = await fetch(`/training/consolidate/${encodeURIComponent(brandName)}?ai_provider=${encodeURIComponent(aiProvider.value || "qwen")}`, { method: "POST" });
    const data = await response.json();
    if (response.ok) {
      brandWisdomCard.classList.remove("hidden");
      brandProfileResult.innerHTML = `<strong>Sabiduría actualizada.</strong><span>La marca ya tiene reglas consolidadas para próximos análisis.</span>`;
      await loadBrandProfile(brandName);
    } else {
      brandProfileResult.innerHTML = `<strong>No se pudo actualizar todavía.</strong><span>${escapeHtml(data.detail || "Hace falta más historial de auditorías para consolidar aprendizaje.")}</span>`;
    }
  } catch (e) {
    brandProfileResult.innerHTML = `<strong>No se pudo conectar.</strong><span>Revisa que la app local siga encendida.</span>`;
  } finally {
    consolidateWisdomBtn.disabled = false;
    consolidateWisdomBtn.textContent = "Actualizar Sabiduría";
  }
});
uploadInput.addEventListener("change", () => {
  if (uploadInput.files.length) {
    uploadFileName.textContent = `${uploadInput.files[0].name} listo para procesar.`;
    uploadField.classList.add("has-file");
  } else {
    uploadFileName.textContent = "Acepta .mp4, .mov, .m4v, .webm, .mp3, .wav y .m4a.";
    uploadField.classList.remove("has-file");
  }
});
["dragenter", "dragover"].forEach((eventName) => {
  uploadField.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    setSource("upload");
    uploadField.classList.add("drag-over");
  });
  document.body.addEventListener(eventName, (event) => {
    if (!event.dataTransfer?.types?.includes("Files")) return;
    event.preventDefault();
    setSource("upload");
    uploadField.classList.add("drag-over");
  });
});
["dragleave", "drop"].forEach((eventName) => {
  uploadField.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    uploadField.classList.remove("drag-over");
  });
});
uploadField.addEventListener("drop", (event) => {
  setDroppedFiles(event.dataTransfer.files);
});
document.body.addEventListener("drop", (event) => {
  if (!event.dataTransfer?.files?.length) return;
  event.preventDefault();
  event.stopPropagation();
  uploadField.classList.remove("drag-over");
  setDroppedFiles(event.dataTransfer.files);
});
refreshVault.addEventListener("click", loadBrands);
refreshAi.addEventListener("click", loadAiStatus);
aiProvider.addEventListener("change", loadAiStatus);
if (aiMode) aiMode.addEventListener("change", loadAiStatus);
startOllama.addEventListener("click", () => runOllamaAction("start"));
stopOllama.addEventListener("click", () => runOllamaAction("stop"));
restartOllama.addEventListener("click", () => runOllamaAction("restart"));

brandList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-brand]");
  if (button) {
    brandList.querySelectorAll(".list-item").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    loadVideos(button.dataset.brand);
  }
});

videoList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-brand][data-video]");
  if (button) {
    videoList.querySelectorAll(".list-item").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    loadVideoDetail(button.dataset.brand, button.dataset.video);
  }
});

videoDetail.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy-path]");
  if (!button) return;
  await navigator.clipboard.writeText(button.dataset.copyPath);
});

aiTestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(aiTestForm);
  aiTestResult.innerHTML = `<strong>Probando conexión...</strong><span>Esto puede tardar unos segundos.</span>`;
  const payload = {
    provider: formData.get("provider"),
    model: formData.get("model") || null,
    prompt: "Responde brevemente si AD MediaSolution Studio está conectado.",
  };
  try {
    const response = await fetch("/ai/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok || data.error) throw new Error(data.detail || data.error || "No se pudo conectar.");
    aiTestResult.innerHTML = `<strong>Conectado.</strong><span>La IA respondió correctamente.</span>`;
  } catch (error) {
    aiTestResult.innerHTML = `<strong>Falló la prueba.</strong><span>${escapeHtml(error.message)}</span>`;
  }
});

generateBrandImage.addEventListener("click", async () => {
  if (!latestCreativePack) return;
  const brandName = selectedVideo?.brand_name;
  const videoId = selectedVideo?.video_id;
  
  // Buscar un prompt visual en el pack
  const visualPrompts = (latestCreativePack.channel_packs || []).filter(p => p.asset_type && String(p.asset_type).toLowerCase().includes("hero"));
  let promptText = "Una imagen premium y cinematográfica para una campaña publicitaria.";
  if (visualPrompts.length > 0 && visualPrompts[0].prompt) {
    promptText = visualPrompts[0].prompt;
  } else if (latestCreativePack.strategy?.visual_direction) {
    promptText = latestCreativePack.strategy.visual_direction;
  }
  
  generateBrandImage.disabled = true;
  generateBrandImage.textContent = "Generando...";
  generatedImageContainer.classList.remove("hidden");
  generatedImageContent.innerHTML = "Llamando al proveedor de imagen... Esto puede tomar unos segundos.";
  
  try {
    const response = await fetch("/api/generate-brand-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brand_name: brandName,
        video_id: videoId,
        prompt: promptText
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No se pudo generar la imagen.");
    
    generatedImageContent.innerHTML = `
      <img src="${data.url}" alt="Brand Image" style="max-width: 100%; height: auto; border-radius: var(--radius); margin-top: var(--space-s); box-shadow: var(--shadow-panel);">
      <div style="margin-top: 8px;">
        <a href="${data.url}" target="_blank" class="secondary-button">Abrir Original</a>
        ${data.local_path ? '<span style="font-size: 0.8rem; color: var(--text-muted); margin-left: 10px;">Guardado en el Vault</span>' : ''}
      </div>
    `;
  } catch (error) {
    generatedImageContent.innerHTML = `<span style="color: var(--danger);">Error: ${escapeHtml(error.message)}</span>`;
  } finally {
    generateBrandImage.disabled = false;
    generateBrandImage.textContent = "Generar Imagen";
  }
});

brandProfileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const brandName = document.querySelector("#profile-brand-name").value.trim();
  if (!brandName) return;
  const payload = {
    tone: document.querySelector("#profile-tone").value,
    audience: document.querySelector("#profile-audience").value,
    offer: document.querySelector("#profile-offer").value,
    visual_style: document.querySelector("#profile-visual-style").value,
    colors: document.querySelector("#profile-colors").value.split(",").map((item) => item.trim()).filter(Boolean),
    forbidden_words: document.querySelector("#profile-forbidden").value.split(",").map((item) => item.trim()).filter(Boolean),
    cta: document.querySelector("#profile-cta").value,
  };
  const response = await fetch(`/vault/brands/${encodeURIComponent(brandName)}/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  brandProfileResult.innerHTML = `<strong>Perfil guardado.</strong><span>La marca ya puede usarse para análisis y creativos más alineados.</span>`;
  badgeBrand.classList.add("hidden");
  showToast("Perfil de Marca", `Configuración de ${brandName} guardada en base de datos.`, "db");
});

reanalyzeVideo.addEventListener("click", async () => {
  if (!selectedVideo) {
    outputsPreview.textContent = "Selecciona una pieza en Mis proyectos antes de reanalizar.";
    return;
  }
  const payload = {
    ai_provider: aiProvider.value || "qwen",
    ai_model: aiModel.value || null,
  };
  const response = await fetch(`/jobs/analyze/${encodeURIComponent(selectedVideo.brand_name)}/${encodeURIComponent(selectedVideo.video_id)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const job = await response.json();
  if (!response.ok) {
    outputsPreview.textContent = job.detail || "No se pudo iniciar análisis.";
    return;
  }
  setMainView("process-view");
  renderJob(job);
  startPolling(job.job_id);
});

refineSkillBtn?.addEventListener("click", refineSkill);

runPolish.addEventListener("click", async () => {
  if (!selectedVideo) {
    polishSummary.innerHTML = "Selecciona una pieza en Mis proyectos antes de ejecutar pulido.";
    return;
  }

  runPolish.disabled = true;
  polishStatusPill.textContent = "Mejorando";
  polishSummary.innerHTML = `<strong>Ejecutando microtareas...</strong><span>Clasificando mejoras pequeñas y acciones recomendadas.</span>`;
  try {
    const response = await fetch(`/microtasks/run/${encodeURIComponent(selectedVideo.brand_name)}/${encodeURIComponent(selectedVideo.video_id)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const report = await response.json();
    if (!response.ok) throw new Error(report.detail || "No se pudo ejecutar pulido.");
    renderPolishReport(report);
  } catch (error) {
    polishStatusPill.textContent = "Necesita revisión";
    polishSummary.innerHTML = `<strong>No se pudo ejecutar pulido.</strong><span>${escapeHtml(error.message)}</span>`;
  } finally {
    runPolish.disabled = false;
  }
});

polishList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-polish-action]");
  if (!button) return;
  const group = button.dataset.polishAction;
  if (group === "creative_cleanup") setMainView("creative-view");
  else if (group === "analysis_refinement") setMainView("analysis-view");
  else if (group === "brand_memory") setMainView("brand-view");
  else if (group === "output_readiness") setMainView("outputs-view");
  else setMainView("polish-view");
});

generateCreativePack.addEventListener("click", async () => {
  if (!selectedVideo) {
    creativeSummary.innerHTML = "Selecciona una pieza en Mis proyectos antes de generar creativos.";
    return;
  }

  generateCreativePack.disabled = true;
  creativeStatusPill.textContent = "Generando";
  creativeSummary.innerHTML = `
    <strong>Creando pack creativo...</strong>
    <span>AD MediaSolution Studio está convirtiendo el análisis en prompts accionables.</span>
  `;

  try {
    const response = await fetch(`/creative-pack/${encodeURIComponent(selectedVideo.brand_name)}/${encodeURIComponent(selectedVideo.video_id)}/job`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ai_provider: aiProvider.value || "qwen",
        ai_model: aiModel.value || null,
        fallback_provider: "openrouter",
      }),
    });
    const job = await response.json();
    if (!response.ok) throw new Error(job.detail || "No se pudo iniciar el laboratorio creativo.");
    creativeSummary.innerHTML = `
      <strong>Laboratorio creativo iniciado.</strong>
      <span>Progreso: ${job.progress || 0}%</span>
    `;
    startCreativePolling(job.job_id, selectedVideo.brand_name, selectedVideo.video_id);
  } catch (error) {
    creativeStatusPill.textContent = "Error";
    creativeSummary.innerHTML = escapeHtml(error.message);
    generateCreativePack.disabled = false;
  } finally {
  }
});

creativePackList.addEventListener("click", async (event) => {
  const btn = event.target.closest(".action-btn");
  if (!latestCreativePack || !btn) return;

  const type = btn.dataset.creativeType;
  const index = parseInt(btn.dataset.creativeIndex, 10);
  const action = btn.dataset.action;

  let item;
  if (type === "adset") item = (latestCreativePack.adsets || [])[index];
  else if (type === "message") item = (latestCreativePack.message_variants || [])[index];
  else if (type === "prompt") item = (latestCreativePack.channel_packs || [])[index];
  
  if (!item) return;

  // Handle Generate Image Action
  if (action === "gen-img") {
    const promptText = item.visual_prompt || item.prompt;
    if (promptText) {
      if (!selectedVideo) return;
      generateBrandImage(selectedVideo, promptText);
    }
    return;
  }

  // Handle Copy Actions
  let textToCopy = "";
  let successMsg = "";

  if (action === "copy-text") {
    textToCopy = item.primary_text || item.headline || item.message || item.copy_overlay || item.hook || "";
    successMsg = "Texto principal copiado.";
  } else if (action === "copy-prompt") {
    textToCopy = item.visual_prompt || item.prompt || "";
    successMsg = "Prompt copiado.";
  } else if (action === "copy-full") {
    if (type === "adset") {
      textToCopy = [
        `Adset: ${item.name || "-"}`,
        `Objetivo: ${item.objective || "-"}`,
        `Audiencia: ${item.audience || "-"}`,
        `Texto: ${item.primary_text || "-"}`,
        `Headline: ${item.headline || "-"}`,
        `Prompt visual: ${item.visual_prompt || "-"}`,
      ].join("\\n");
    } else if (type === "message") {
      textToCopy = [
        `Uso: ${humanChannel(item.use) || "-"}`,
        `Tono: ${item.tone || "-"}`,
        `Mensaje: ${item.message || "-"}`,
      ].join("\\n");
    } else {
      textToCopy = creativePromptText(item);
    }
    successMsg = "Ficha creativa completa copiada.";
  }

  if (textToCopy) {
    await copyToClipboard(textToCopy, successMsg);
  }
});

copyCreativePack.addEventListener("click", async () => {
  if (!latestCreativePack) return;
  const prompts = (latestCreativePack.channel_packs || []).map(creativePromptText).join("\n\n---\n\n");
  const adsets = (latestCreativePack.adsets || []).map((adset) => [
    `Adset: ${adset.name || "-"}`,
    `Objetivo: ${adset.objective || "-"}`,
    `Audiencia: ${adset.audience || "-"}`,
    `Texto: ${adset.primary_text || "-"}`,
    `Headline: ${adset.headline || "-"}`,
    `Prompt visual: ${adset.visual_prompt || "-"}`,
  ].join("\n")).join("\n\n---\n\n");
  await copyToClipboard(`${prompts}\n\n=== ADSETS ===\n\n${adsets}`, "Pack creativo completo copiado.");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  resultBox.classList.add("hidden");
  setStatus("running", "Preparando proceso...", 5);
  submitButton.disabled = true;
  submitButton.textContent = "Creando...";

  try {
    const payload = buildPayload(new FormData(form));
    const job = await submitJob(payload);
    renderJob(job);
    startPolling(job.job_id);
  } catch (error) {
    showError(error.message);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Iniciar extracción";
  }
});

copySummary.addEventListener("click", async () => {
  if (!latestResult) return;

  const text = [
    `Vault: ${latestResult.vault_path}`,
    `Audio: ${latestResult.audio_path}`,
    `Guion: ${latestResult.script_path}`,
    `Metadatos: ${latestResult.metadata_path}`,
  ].join("\n");

  await navigator.clipboard.writeText(text);
  setStatus("done", "Resumen copiado al portapapeles.", 100);
});

setSource(activeSource);
loadBrands();
loadAiStatus();

// ═══════════════════════════════════════════════════
// GUIDE BOT — Contextual floating assistant
// ═══════════════════════════════════════════════════

const guideTips = {
  "process-view": [
    { emoji: "👋", title: "¡Bienvenido a ScriptDNA Studio!", text: "El Studio es tu motor de extracción principal. Aquí la IA procesa videos de YouTube o Reels usando un pipeline visual de 3 fases: Transcripción, Análisis y Creativos.", action: null },
    { emoji: "📝", title: "Paso 1: Identifica tu proyecto", text: "Asigna una Marca y un ID (ej. 'campana-verano'). Estos metadatos organizarán automáticamente los resultados en la nueva Biblioteca centralizada.", action: null },
    { emoji: "🎬", title: "Paso 2: Elige la fuente", text: "Puedes usar un link público de YouTube o arrastrar directamente un archivo MP4/MOV. El sistema manejará la transcripción automáticamente.", action: null },
    { emoji: "🚀", title: "Paso 3: Observa el Pipeline", text: "Haz clic en 'Extraer inteligencia creativa'. Nuestro nuevo tracker visual te mostrará el estado de la IA en tiempo real mientras desgrana el ADN del video.", action: null },
  ],
  "vault-view": [
    { emoji: "📚", title: "Tu Nueva Biblioteca", text: "Hemos consolidado Proyectos, Análisis y Mi Marca en un solo lugar. Usa los sub-tabs superiores para navegar sin fricción mental.", action: null },
    { emoji: "📂", title: "Sub-tab: Proyectos", text: "Aquí se agrupan tus extracciones por marca. Selecciona un video para activar inmediatamente sus datos en las pestañas de Análisis y Editor.", action: null },
    { emoji: "🔬", title: "Sub-tab: Análisis", text: "Aquí verás el breakdown estructural: Hooks, cuerpo, CTAs, arcos narrativos y momentos virales detectados por el motor de IA.", action: null },
    { emoji: "🏷️", title: "Sub-tab: Mi Marca", text: "Define las 'leyes' de tu marca (Tono, Audiencia, Palabras prohibidas). El motor usará esto para el Brand Shifting en el Editor.", action: null },
  ],
  "analysis-view": [
    { emoji: "📊", title: "Tu análisis creativo", text: "Aquí encuentras el resumen ejecutivo, hooks, momentos virales, y estructura narrativa. Usa el botón superior para Sincronizar los cambios con la nube.", action: null },
  ],
  "brand-view": [
    { emoji: "🏷️", title: "Define tu marca", text: "Completa el perfil con tono, audiencia, oferta y estilo visual. Cuanto más detallado, más precisos serán los resultados del AI.", action: null },
  ],
  "editor-view": [
    { emoji: "✍️", title: "Editor de Brand Shifting", text: "Selecciona una pieza extraída y una Marca de destino. La IA reescribirá el guion adaptando la oferta y el tono, pero manteniendo la estructura viral original.", action: null },
    { emoji: "🧩", title: "Bloques Modulares", text: "El guion se presenta en bloques (Hook, Setup, Payoff, CTA). Puedes editar el texto y bloquear segmentos para protegerlos de la reescritura.", action: null },
  ],
  "creative-view": [
    { emoji: "✨", title: "Packs Creativos Automatizados", text: "Genera automáticamente prompts y copys listos para TikTok, Instagram y Meta Ads basándote en la estructura de tu video procesado.", action: null },
    { emoji: "📋", title: "Copy & Paste", text: "Todo está optimizado para flujos de trabajo rápidos. Copia los adsets y lánzalos directamente en tu Ads Manager.", action: null },
  ],
  "ai-view": [
    { emoji: "⚙️", title: "Estado de la IA", text: "En esta configuración controlas el cerebro del sistema: Qwen como core, fal/HF para media, OpenRouter como respaldo y Ollama como última opción local.", action: null },
    { emoji: "🧪", title: "Diagnóstico", text: "Si algo falla, usa el panel de auditoría para probar las conexiones en tiempo real antes de perder tiempo en procesos largos.", action: null },
  ],
};

let guideBotOpen = false;
let guideTipIndex = 0;
let guideCurrentView = "process-view";

const guideBotTrigger = document.querySelector("#guide-bot-trigger");
const guideBotPanel = document.querySelector("#guide-bot-panel");
const guideBotClose = document.querySelector("#guide-bot-close");
const guideBotContent = document.querySelector("#guide-bot-content");
const guideBotPrev = document.querySelector("#guide-bot-prev");
const guideBotNext = document.querySelector("#guide-bot-next");
const guideBotCounter = document.querySelector("#guide-bot-counter");

function guideGetCurrentView() {
  const activeView = document.querySelector(".view.active-view");
  let viewId = activeView ? activeView.id : "process-view";
  
  // Si estamos en la Biblioteca, detectar el sub-tab activo
  if (viewId === "vault-view") {
    const activeBib = document.querySelector(".bib-panel.active-bib");
    if (activeBib) {
      if (activeBib.id === "bib-analysis") return "analysis-view";
      if (activeBib.id === "bib-brand") return "brand-view";
    }
  }
  return viewId;
}

function guideRenderTip() {
  const viewId = guideGetCurrentView();
  if (viewId !== guideCurrentView) {
    guideCurrentView = viewId;
    guideTipIndex = 0;
  }
  const tips = guideTips[viewId] || guideTips["process-view"];
  const tip = tips[guideTipIndex] || tips[0];

  guideBotContent.innerHTML = `
    <div class="guide-tip">
      <span class="guide-tip-emoji">${tip.emoji}</span>
      <h3>${tip.title}</h3>
      <p>${tip.text}</p>
      ${tip.action ? `<button class="guide-action" onclick="${tip.action}">${tip.actionLabel || "Ir"}</button>` : ""}
    </div>
  `;

  guideBotCounter.textContent = `${guideTipIndex + 1}/${tips.length}`;
  guideBotPrev.disabled = guideTipIndex === 0;
  guideBotNext.disabled = guideTipIndex >= tips.length - 1;
}

function guideToggle() {
  guideBotOpen = !guideBotOpen;
  if (guideBotOpen) {
    guideCurrentView = guideGetCurrentView();
    guideTipIndex = 0;
    guideRenderTip();
    guideBotPanel.classList.remove("hidden");
    localStorage.setItem("guideBotSeen", "true");
  } else {
    guideBotPanel.classList.add("hidden");
  }
}

guideBotTrigger?.addEventListener("click", guideToggle);
guideBotClose?.addEventListener("click", () => {
  guideBotOpen = false;
  guideBotPanel.classList.add("hidden");
});

guideBotPrev?.addEventListener("click", () => {
  if (guideTipIndex > 0) { guideTipIndex--; guideRenderTip(); }
});

guideBotNext?.addEventListener("click", () => {
  const tips = guideTips[guideGetCurrentView()] || guideTips["process-view"];
  if (guideTipIndex < tips.length - 1) { guideTipIndex++; guideRenderTip(); }
});

// Auto-open on first visit
if (!localStorage.getItem("guideBotSeen")) {
  setTimeout(() => {
    guideToggle();
  }, 2000);
}

// Update tips when view changes
const originalSetMainView = setMainView;
setMainView = function(viewId) {
  originalSetMainView(viewId);
  if (guideBotOpen) {
    guideCurrentView = "";
    guideRenderTip();
  }
};

// ═══════════════════════════════════════════════════
// EDITOR DE GUIONES (Brand Shifting)
// ═══════════════════════════════════════════════════

async function renderScriptEditor(video) {
  if (!editorOriginalBrand || !editorOriginalBlocks || !editorAdaptedBlocks) return;
  
  editorOriginalBrand.textContent = "Sin selección";
  editorOriginalBlocks.innerHTML = `<div class="human-status">Selecciona una pieza en Mis proyectos.</div>`;
  editorAdaptedBlocks.innerHTML = `<div class="human-status">Elige una marca destino para empezar a adaptar.</div>`;
  if (editorTargetBrand) editorTargetBrand.value = "";
  if (editorAdaptAll) editorAdaptAll.disabled = true;

  if (!video) return;

  editorOriginalBrand.textContent = video.brand_name;
  
  if (!video.files?.script) {
    editorOriginalBlocks.innerHTML = `<div class="human-status">Este video no tiene guion disponible.</div>`;
    return;
  }

  try {
    const response = await fetch(`/vault/script/${encodeURIComponent(video.brand_name)}/${encodeURIComponent(video.video_id)}`);
    if (!response.ok) throw new Error("No se pudo cargar el guion.");
    const scriptText = await response.text();
    
    const blocks = scriptText.split(/\\n\\s*\\n/).filter(b => b.trim());
    
    editorOriginalBlocks.innerHTML = blocks.map((block, i) => `
      <div class="editor-block">
        <div class="editor-block-header">
          <span class="editor-block-title">Bloque ${i + 1}</span>
          <div class="editor-block-actions">
            <button class="secondary-button" type="button" style="padding: 2px 8px; font-size: 0.7rem;" onclick="copyToClipboard(this.parentElement.parentElement.nextElementSibling.value, 'Bloque copiado')">Copiar</button>
          </div>
        </div>
        <textarea class="editor-block-content" readonly>${escapeHtml(block.trim())}</textarea>
      </div>
    `).join("");

  } catch (err) {
    editorOriginalBlocks.innerHTML = `<div class="human-status">Error cargando el guion: ${escapeHtml(err.message)}</div>`;
  }
}

if (editorTargetBrand) {
  editorTargetBrand.addEventListener("change", (e) => {
    const val = e.target.value;
    if (editorTargetBrandPill) {
      editorTargetBrandPill.textContent = val || "Destino";
      editorTargetBrandPill.className = val ? "pill badge-listo" : "pill badge-requiere_revision";
    }
    if (editorAdaptAll) {
      editorAdaptAll.disabled = !val || !selectedVideo;
    }
    
    if (val && selectedVideo) {
      editorAdaptedBlocks.innerHTML = `
        <div class="human-status" style="border: 1px dashed var(--brand-blue); padding: var(--space-l); text-align: center;">
          <span style="font-size: 2rem; display: block; margin-bottom: 8px;">✨</span>
          <strong>Listo para adaptar a ${escapeHtml(val)}</strong>
          <p style="font-size: 0.85rem; margin-top: 8px;">La IA usará el tono, oferta y sabiduría de la nueva marca para reescribir este guion conservando su estructura ganadora.</p>
        </div>
      `;
    } else {
      editorAdaptedBlocks.innerHTML = `<div class="human-status">Elige una marca destino para empezar a adaptar.</div>`;
    }
  });
}

if (editorAdaptAll) {
  editorAdaptAll.addEventListener("click", async () => {
    if (!selectedVideo || !editorTargetBrand.value) return;

    // Recolectar el texto original de los bloques
    const textareas = editorOriginalBlocks.querySelectorAll("textarea");
    const originalScript = Array.from(textareas).map(ta => ta.value).join("\n\n");
    const targetBrand = editorTargetBrand.value;

    editorAdaptAll.disabled = true;
    editorAdaptAll.textContent = "Adaptando...";
    editorAdaptedBlocks.innerHTML = `
      <div class="human-status" style="border: 1px dashed var(--accent); padding: var(--space-l); text-align: center;">
        <div class="spinner" style="margin: 0 auto 16px;"></div>
        <strong>Generando guion adaptado...</strong>
        <p style="font-size: 0.85rem; margin-top: 8px;">Esto puede tomar unos segundos.</p>
      </div>
    `;

    try {
      const response = await fetch("/ai/adapt-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_script: originalScript,
          target_brand: targetBrand
        })
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Error al adaptar el guion");

      const blocks = data.data?.blocks || [];
      
      if (blocks.length === 0) {
        editorAdaptedBlocks.innerHTML = `<div class="human-status">La IA no devolvió bloques válidos. Intenta nuevamente.</div>`;
      } else {
        const typeLabels = {
          hook: "🎣 Hook",
          pain: "😣 Dolor",
          agitate: "🔥 Tensión",
          solution: "💡 Solución",
          proof: "📊 Prueba",
          cta: "🚀 CTA",
          context: "📝 Contexto",
          development: "📖 Desarrollo",
        };
        editorAdaptedBlocks.innerHTML = blocks.map((block, i) => `
          <div class="editor-block" style="border-left: 3px solid var(--accent);">
            <div class="editor-block-header">
              <span class="editor-block-title">${escapeHtml(typeLabels[block.type] || block.type || `Bloque ${i+1}`)}</span>
              <div class="editor-block-actions" style="display: flex; gap: 4px; align-items: center;">
                ${block.psychology ? `<span class="pill" style="font-size: 0.65rem; padding: 2px 6px; background: rgba(var(--accent-rgb, 99,102,241), 0.15); color: var(--accent);">🧠 ${escapeHtml(block.psychology)}</span>` : ""}
                <button class="secondary-button" type="button" style="padding: 2px 8px; font-size: 0.7rem;" onclick="copyToClipboard(this.closest('.editor-block').querySelector('textarea').value, 'Bloque adaptado copiado')">Copiar</button>
              </div>
            </div>
            <textarea class="editor-block-content" style="border-color: var(--accent);">${escapeHtml(block.content || "")}</textarea>
            ${block.rationale ? `<p style="font-size: 0.75rem; color: var(--text-muted); margin: 8px 0 0;">💡 ${escapeHtml(block.rationale)}</p>` : ""}
          </div>
        `).join("");
      }
      
    } catch (err) {
      editorAdaptedBlocks.innerHTML = `<div class="human-status" style="color: var(--error);">Error: ${escapeHtml(err.message)}</div>`;
    } finally {
      editorAdaptAll.disabled = false;
      editorAdaptAll.textContent = "Adaptar todo";
    }
  });
}
