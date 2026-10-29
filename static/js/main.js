/**
 * AgriPulse Agricultural Platform - Client Script
 */

// Voice Text-to-Speech Engine
function speakText(text) {
  if (!('speechSynthesis' in window)) {
    alert("Audio readout is not supported by your browser.");
    return;
  }
  window.speechSynthesis.cancel(); // Stop any ongoing speech

  // Strip Markdown / HTML tags for speech
  const cleanText = text.replace(/<[^>]*>?/gm, '').replace(/[*_#]/g, '');
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 0.95; // Slightly slower for clarity
  utterance.pitch = 1.0;
  
  // Try to pick an English voice or regional voice
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('en-GB') || v.lang.includes('en-US'));
  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  window.speechSynthesis.speak(utterance);
}

function stopSpeech() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

// Voice buttons carry their script in a data attribute: user-typed place names stay data, never code.
document.addEventListener("click", (event) => {
  const voiceBtn = event.target.closest("[data-speech]");
  if (voiceBtn) speakText(voiceBtn.dataset.speech);
});

// Location Switcher
function handleLocationChange(selectElem) {
  const loc = selectElem.value;
  const url = new URL(window.location.href);
  url.searchParams.set("location", loc);
  window.location.href = url.toString();
}

// Sparkline Mini Chart Renderer (SVG)
function renderSparkline(svgId, dataPoints) {
  const svg = document.getElementById(svgId);
  if (!svg || !dataPoints || dataPoints.length < 2) return;

  const width = 120;
  const height = 36;
  const minVal = Math.min(...dataPoints);
  const maxVal = Math.max(...dataPoints);
  const range = maxVal - minVal || 1;

  const points = dataPoints.map((val, idx) => {
    const x = (idx / (dataPoints.length - 1)) * (width - 8) + 4;
    const y = height - 4 - ((val - minVal) / range) * (height - 8);
    return `${x},${y}`;
  }).join(' ');

  const isUp = dataPoints[dataPoints.length - 1] >= dataPoints[0];
  const strokeColor = isUp ? '#16a34a' : '#dc2626';

  svg.innerHTML = `
    <polyline fill="none" stroke="${strokeColor}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" points="${points}" />
  `;
}

// Disease Detection Handler
function initDiseaseDetection() {
  const dropzone = document.getElementById("diseaseDropzone");
  const fileInput = document.getElementById("diseaseFileInput");
  const resultBox = document.getElementById("diseaseResultBox");
  const loadingIndicator = document.getElementById("diseaseLoading");

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      handleDiseaseUpload(fileInput.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleDiseaseUpload(fileInput.files[0]);
    }
  });
}

function handleDiseaseUpload(file, sampleFilename = null) {
  const resultBox = document.getElementById("diseaseResultBox");
  const rejectBox = document.getElementById("diseaseRejectBox");
  const loadingIndicator = document.getElementById("diseaseLoading");
  const cropHint = document.getElementById("cropHintSelect") ? document.getElementById("cropHintSelect").value : "";

  resultBox.classList.remove("active");
  if (rejectBox) rejectBox.classList.remove("active");
  loadingIndicator.style.display = "block";

  const formData = new FormData();
  if (sampleFilename) {
    formData.append("sample_file", sampleFilename);
  } else if (file) {
    formData.append("file", file);
  }
  formData.append("crop_hint", cropHint);

  fetch("/api/disease/detect", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    loadingIndicator.style.display = "none";
    if (data.success) {
      renderDiseaseResult(data);
    } else {
      showDiseaseRejection(data.error || "Unable to read this image.");
    }
  })
  .catch(err => {
    loadingIndicator.style.display = "none";
    showDiseaseRejection("Connection error: " + err.message);
  });
}

// A photo the detector cannot measure gets a reason, not a guess.
function showDiseaseRejection(reason) {
  const rejectBox = document.getElementById("diseaseRejectBox");
  if (!rejectBox) {
    alert("Analysis error: " + reason);
    return;
  }
  document.getElementById("diseaseRejectReason").innerText = reason;
  rejectBox.classList.add("active");
  rejectBox.scrollIntoView({ behavior: "smooth", block: "start" });
}

function selectDiseaseSample(filename, cropHint = "") {
  const select = document.getElementById("cropHintSelect");
  if (select) select.value = cropHint || "";
  handleDiseaseUpload(null, filename);
}

function renderDiseaseResult(data) {
  const resultBox = document.getElementById("diseaseResultBox");

  // Set preview image
  document.getElementById("diagImage").src = data.image_url;
  document.getElementById("diagName").innerText = data.name;
  document.getElementById("diagPathogen").innerText = data.pathogen;

  const badge = document.getElementById("diagSeverity");
  badge.innerText = "Severity: " + data.severity;
  badge.className = "badge badge-" + data.badge_color;

  document.getElementById("diagConfidence").innerText = data.confidence + "%";
  const accNote = document.getElementById("diagConfidenceNote");
  if (accNote) {
    accNote.innerText = data.tested_photos
      ? `right on ${data.tested_correct} of ${data.tested_photos} test photos of this`
      : "no measured accuracy for this result";
  }
  document.getElementById("diagArea").innerText = data.affected_area_pct + "% of leaf";
  document.getElementById("diagSymptoms").innerText = data.symptoms;
  document.getElementById("diagCauses").innerText = data.causes;

  const quality = data.image_quality || {};
  const warnings = quality.warnings || [];
  document.getElementById("diagQuality").innerText = warnings.length
    ? "Photo problems: " + warnings.join("; ")
    : `Photo usable: sharpness ${quality.sharpness}, brightness ${quality.brightness}.`;

  // Differential: what else the same measurements are consistent with
  const diffList = document.getElementById("diagDifferential");
  diffList.innerHTML = "";
  (data.candidates || []).forEach(c => {
    const li = document.createElement("li");
    li.innerText = `${c.name} — ${c.share}% of the measured evidence`;
    diffList.appendChild(li);
  });
  if (!diffList.children.length) {
    const li = document.createElement("li");
    li.innerText = "Nothing in the disease database matched the colours measured in this photo.";
    diffList.appendChild(li);
  } else if (diffList.children.length === 1) {
    const li = document.createElement("li");
    li.innerText = "No second candidate: nothing else in the database matched these measurements.";
    diffList.appendChild(li);
  }
  document.getElementById("diagAccuracyNote").innerText = data.accuracy_note || "";

  // The numbers the diagnosis was actually built from
  const evidenceList = document.getElementById("diagEvidence");
  evidenceList.innerHTML = "";
  (data.evidence || []).forEach(note => {
    const li = document.createElement("li");
    li.innerText = note;
    evidenceList.appendChild(li);
  });

  // Render organic remedies
  const orgList = document.getElementById("diagOrganic");
  orgList.innerHTML = "";
  data.organic_remedies.forEach(rem => {
    const li = document.createElement("li");
    li.innerText = rem;
    orgList.appendChild(li);
  });

  // Render chemical treatments
  const chemList = document.getElementById("diagChemical");
  chemList.innerHTML = "";
  data.chemical_treatments.forEach(tr => {
    const li = document.createElement("li");
    li.innerText = tr;
    chemList.appendChild(li);
  });

  // Render preventive measures
  const prevList = document.getElementById("diagPreventive");
  prevList.innerHTML = "";
  data.preventive_measures.forEach(p => {
    const li = document.createElement("li");
    li.innerText = p;
    prevList.appendChild(li);
  });

  // Setup Voice Readout Button
  const voiceBtn = document.getElementById("diagVoiceBtn");
  if (voiceBtn) {
    const speechScript = `Diagnosis: ${data.name}. Pathogen: ${data.pathogen}. Severity: ${data.severity}. Symptoms: ${data.symptoms}. Recommended organic treatment: ${data.organic_remedies.join('. ')}. Recommended chemical remedy: ${data.chemical_treatments.join('. ')}. ${data.accuracy_note || ''}`;
    voiceBtn.onclick = () => speakText(speechScript);
  }

  resultBox.classList.add("active");
  resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Crop Quality Assessment Handler
function initQualityAssessment() {
  const dropzone = document.getElementById("qualityDropzone");
  const fileInput = document.getElementById("qualityFileInput");
  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      handleQualityUpload(fileInput.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleQualityUpload(fileInput.files[0]);
    }
  });
}

function handleQualityUpload(file, sampleFilename = null) {
  const resultBox = document.getElementById("qualityResultBox");
  const rejectBox = document.getElementById("qualityRejectBox");
  const loadingIndicator = document.getElementById("qualityLoading");
  const cropName = document.getElementById("qualityCropName") ? document.getElementById("qualityCropName").value : "Produce";

  resultBox.classList.remove("active");
  if (rejectBox) rejectBox.classList.remove("active");
  loadingIndicator.style.display = "block";

  const formData = new FormData();
  if (sampleFilename) {
    formData.append("sample_file", sampleFilename);
  } else if (file) {
    formData.append("file", file);
  }
  formData.append("crop_name", cropName);

  fetch("/api/quality/assess", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    loadingIndicator.style.display = "none";
    if (data.success) {
      renderQualityResult(data);
    } else {
      showQualityRejection(data.error || "Unable to grade this photo.");
    }
  })
  .catch(err => {
    loadingIndicator.style.display = "none";
    showQualityRejection("Connection error: " + err.message);
  });
}

// A photo with nothing measurable in it gets a reason, not a grade.
function showQualityRejection(reason) {
  const rejectBox = document.getElementById("qualityRejectBox");
  if (!rejectBox) {
    alert("Grading error: " + reason);
    return;
  }
  document.getElementById("qualityRejectReason").innerText = reason;
  rejectBox.classList.add("active");
  rejectBox.scrollIntoView({ behavior: "smooth", block: "start" });
}

function selectQualitySample(filename) {
  handleQualityUpload(null, filename);
}

const QUALITY_SUB_LABELS = [
  ["clean", "Skin free of dark, pale, cut or off-colour patches"],
  ["ripeness", "Ripeness and colour strength of the lot"],
  ["evenness", "How even the colour is across the pieces"]
];

function renderQualityResult(data) {
  const resultBox = document.getElementById("qualityResultBox");
  const m = data.metrics || {};
  const sub = data.sub_scores || {};
  const weights = data.sub_weights || {};

  document.getElementById("qualImage").src = data.image_url;
  document.getElementById("qualGradeTitle").innerText = data.grade_title;

  const gradeBadge = document.getElementById("qualGradeBadge");
  gradeBadge.innerText = "GRADE " + data.grade;
  gradeBadge.className = "badge " + data.badge;

  document.getElementById("qualScore").innerText = data.overall_score + "/100";
  document.getElementById("qualPriceTag").innerText = data.price_tag;
  document.getElementById("qualCropLabel").innerText =
    "Labelled as: " + (data.crop_name || "Produce") + " - a label you typed, not a detection";
  document.getElementById("qualDescription").innerText = data.description;
  document.getElementById("qualChannel").innerText = data.recommended_channel;
  document.getElementById("qualShelfLife").innerText = data.shelf_life;

  document.getElementById("qualPurity").innerText = m.surface_purity_pct + "%";
  document.getElementById("qualDefect").innerText = m.blemish_area_pct + "%";
  document.getElementById("qualEvenness").innerText = m.colour_evenness_pct + "%";
  document.getElementById("qualSaturation").innerText = m.dominant_saturation_pct + "%";

  const quality = data.image_quality || {};
  const warnings = quality.warnings || [];
  document.getElementById("qualQualityLine").innerText = warnings.length
    ? "Photo problems: " + warnings.join("; ")
    : `Photo usable: sharpness ${quality.sharpness}, brightness ${quality.brightness}.`;

  // The three parts the score is actually made of, with their weights.
  const subBox = document.getElementById("qualSubScores");
  subBox.innerHTML = "";
  QUALITY_SUB_LABELS.forEach(pair => {
    const key = pair[0];
    const v = sub[key];
    if (v === null || v === undefined) return;
    const row = document.createElement("div");
    row.style.cssText = "background:#f8fafc; border:1px solid #e2e8f0; border-radius:var(--radius-sm); padding:10px 12px;";
    const pct = Math.round((weights[key] || 0) * 100);
    row.innerHTML =
      `<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-muted);">` +
      `<span>${pair[1]} <em>(weight ${pct}%)</em></span><strong>${v}</strong></div>` +
      `<div style="height:6px; background:#e2e8f0; border-radius:3px; margin-top:6px;">` +
      `<div style="height:6px; width:${v}%; background:var(--primary-500, #16a34a); border-radius:3px;"></div></div>`;
    subBox.appendChild(row);
  });

  const evidenceList = document.getElementById("qualEvidence");
  evidenceList.innerHTML = "";
  (data.evidence || []).forEach(note => {
    const li = document.createElement("li");
    li.innerText = note;
    evidenceList.appendChild(li);
  });

  const limitsList = document.getElementById("qualUnmeasurable");
  limitsList.innerHTML = "";
  (data.unmeasurable || []).forEach(note => {
    const li = document.createElement("li");
    li.innerText = note;
    limitsList.appendChild(li);
  });

  document.getElementById("qualAccuracyNote").innerText = data.accuracy_note || "";

  const tipsList = document.getElementById("qualTips");
  tipsList.innerHTML = "";
  data.handling_tips.forEach(t => {
    const li = document.createElement("li");
    li.innerText = t;
    tipsList.appendChild(li);
  });

  const voiceBtn = document.getElementById("qualVoiceBtn");
  if (voiceBtn) {
    const textToRead = `Quality assessment. ${data.grade_title}. The measured surface scored ${data.overall_score} out of 100. ${data.accuracy_note || ''} Price assumption: ${data.price_tag}. Recommended sales channel: ${data.recommended_channel}. Estimated shelf life: ${data.shelf_life}`;
    voiceBtn.onclick = () => speakText(textToRead);
  }

  resultBox.classList.add("active");
  resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Harvesting Readiness Checklist Calculator
function calculateReadiness() {
  const cropSelect = document.getElementById("readinessCropSelect");
  if (!cropSelect) return;
  const cropId = cropSelect.value;

  const checkboxes = document.querySelectorAll(".readiness-chk:checked");
  const checkedIds = Array.from(checkboxes).map(cb => cb.value);

  fetch("/api/harvesting/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ crop_id: cropId, checked_ids: checkedIds })
  })
  .then(res => res.json())
  .then(data => {
    const resultBox = document.getElementById("readinessResultBox");
    if (!resultBox) return;

    document.getElementById("readinessScore").innerText = data.score_pct + "%";
    document.getElementById("readinessVerdict").innerText = data.verdict;
    
    const badge = document.getElementById("readinessBadge");
    badge.innerText = data.urgency;
    badge.className = "badge " + data.badge;

    document.getElementById("readinessAdvice").innerText = data.recommendation;
    resultBox.style.display = "block";
  })
  .catch(err => console.error(err));
}

// Sell vs Hold Market Profit Simulator
function runMarketSimulator() {
  const cropElem = document.getElementById("simCropSelect");
  const qtyElem = document.getElementById("simQuantityInput");
  const costElem = document.getElementById("simStorageCostInput");

  if (!cropElem || !qtyElem) return;

  const cropId = cropElem.value;
  const quantity = parseFloat(qtyElem.value) || 50;
  const storageCost = parseFloat(costElem.value) || 30;

  fetch("/api/market/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ crop_id: cropId, quantity: quantity, storage_cost: storageCost })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("simCurrentRevenue").innerText = "₹" + data.current_revenue.toLocaleString('en-IN');
    document.getElementById("simFutureRevenue").innerText = "₹" + data.gross_future_revenue.toLocaleString('en-IN');
    document.getElementById("simStorageCost").innerText = "-₹" + data.storage_cost.toLocaleString('en-IN');
    
    const netElem = document.getElementById("simNetGain");
    const isGain = data.net_gain_loss >= 0;
    netElem.innerText = (isGain ? "+₹" : "-₹") + Math.abs(data.net_gain_loss).toLocaleString('en-IN');
    netElem.style.color = isGain ? "#16a34a" : "#dc2626";

    document.getElementById("simVerdictText").innerText = data.verdict;
    const badge = document.getElementById("simUrgencyBadge");
    badge.innerText = data.urgency;
    badge.className = "badge " + data.badge;

    // Render Mandi Table Comparison
    const mandiTbody = document.getElementById("simMandiTbody");
    if (mandiTbody && data.mandi_options) {
      mandiTbody.innerHTML = "";
      data.mandi_options.forEach(opt => {
        const tr = document.createElement("tr");
        const diffText = (opt.profit_difference >= 0 ? "+₹" : "-₹") + Math.abs(opt.profit_difference).toLocaleString('en-IN');
        const diffColor = opt.profit_difference >= 0 ? "trend-up" : "trend-down";
        tr.innerHTML = `
          <td><strong>${opt.name}</strong></td>
          <td>${opt.distance_km} km</td>
          <td>₹${opt.price_per_qtl}</td>
          <td>₹${opt.transport_cost_total.toLocaleString('en-IN')}</td>
          <td><strong>₹${opt.net_revenue.toLocaleString('en-IN')}</strong></td>
          <td class="${diffColor}">${diffText}</td>
        `;
        mandiTbody.appendChild(tr);
      });
    }
  })
  .catch(err => console.error(err));
}

// Auto-run on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initDiseaseDetection();
  initQualityAssessment();
});
