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
  const loadingIndicator = document.getElementById("diseaseLoading");
  const cropHint = document.getElementById("cropHintSelect") ? document.getElementById("cropHintSelect").value : "";

  resultBox.classList.remove("active");
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
      alert("Analysis error: " + (data.error || "Unable to diagnose"));
    }
  })
  .catch(err => {
    loadingIndicator.style.display = "none";
    alert("Connection error: " + err.message);
  });
}

function selectDiseaseSample(filename) {
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
  document.getElementById("diagArea").innerText = data.affected_area_pct + "% leaf surface";
  document.getElementById("diagSymptoms").innerText = data.symptoms;
  document.getElementById("diagCauses").innerText = data.causes;

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
    const speechScript = `Diagnosis: ${data.name}. Pathogen: ${data.pathogen}. Severity: ${data.severity}. Symptoms: ${data.symptoms}. Recommended organic treatment: ${data.organic_remedies.join('. ')}. Recommended chemical remedy: ${data.chemical_treatments.join('. ')}`;
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
  const loadingIndicator = document.getElementById("qualityLoading");
  const cropName = document.getElementById("qualityCropName") ? document.getElementById("qualityCropName").value : "Produce";

  resultBox.classList.remove("active");
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
      alert("Grading error: " + (data.error || "Unable to grade"));
    }
  })
  .catch(err => {
    loadingIndicator.style.display = "none";
    alert("Connection error: " + err.message);
  });
}

function selectQualitySample(filename) {
  handleQualityUpload(null, filename);
}

function renderQualityResult(data) {
  const resultBox = document.getElementById("qualityResultBox");
  document.getElementById("qualImage").src = data.image_url;
  document.getElementById("qualGradeTitle").innerText = data.grade_title;
  
  const gradeBadge = document.getElementById("qualGradeBadge");
  gradeBadge.innerText = "GRADE " + data.grade;
  gradeBadge.className = "badge " + data.badge;

  document.getElementById("qualScore").innerText = data.overall_score + "/100";
  document.getElementById("qualPriceTag").innerText = data.price_tag;
  document.getElementById("qualDescription").innerText = data.description;
  document.getElementById("qualChannel").innerText = data.recommended_channel;
  document.getElementById("qualShelfLife").innerText = data.shelf_life;

  document.getElementById("qualPurity").innerText = data.metrics.surface_purity_pct + "%";
  document.getElementById("qualVibrancy").innerText = data.metrics.color_vibrancy_pct + "%";
  document.getElementById("qualUniformity").innerText = data.metrics.uniformity_index + "/100";
  document.getElementById("qualDefect").innerText = data.metrics.blemish_defect_pct + "%";

  const tipsList = document.getElementById("qualTips");
  tipsList.innerHTML = "";
  data.handling_tips.forEach(t => {
    const li = document.createElement("li");
    li.innerText = t;
    tipsList.appendChild(li);
  });

  const voiceBtn = document.getElementById("qualVoiceBtn");
  if (voiceBtn) {
    const textToRead = `Quality Assessment: ${data.grade_title}. Score is ${data.overall_score} out of 100. Price tag: ${data.price_tag}. Recommended sales channel: ${data.recommended_channel}. Estimated shelf life: ${data.shelf_life}`;
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
