const API_BASE = ""; // v2.1 cache buster

const UI = {
    // Basic Info
    restaurantName: document.getElementById('restaurant-name'),
    restaurantDesc: document.getElementById('restaurant-desc'),
    venueId: document.getElementById('venue-id'),
    statusBadge: document.getElementById('status-badge'),
    
    // Intelligence View
    hygieneScore: document.getElementById('hygiene-score'),
    riskLevel: document.getElementById('risk-level'),
    trustBar: document.getElementById('trust-bar'),
    trustValue: document.getElementById('trust-value'),
    auditAge: document.getElementById('audit-age'),
    sentiment: document.getElementById('sentiment'),
    explanation: document.getElementById('explanation-text'),
    
    // Supply Chain View
    supplierStatus: document.getElementById('supplier-status'),
    storageStatus: document.getElementById('storage-status'),
    deliveryRiskBar: document.getElementById('delivery-risk-bar'),
    deliveryRiskText: document.getElementById('delivery-risk-text'),
    
    // Compliance View
    complianceStatus: document.getElementById('compliance-status'),
    complianceReason: document.getElementById('compliance-reason'),
    licenseStatus: document.getElementById('license-status'),
    violationCount: document.getElementById('violation-count'),
    auditRecency: document.getElementById('audit-recency'),
    
    // Tables & Controls
    historyBody: document.getElementById('history-body'),
    taskSelect: document.getElementById('task-select'),
    btnReset: document.getElementById('btn-reset'),
    
    // Tabs
    tabIntelligence: document.getElementById('tab-intelligence'),
    tabSupplyChain: document.getElementById('tab-supply-chain'),
    tabCompliance: document.getElementById('tab-compliance'),
    viewIntelligence: document.getElementById('intelligence-view'),
    viewSupplyChain: document.getElementById('supply-chain-view'),
    viewCompliance: document.getElementById('compliance-view'),
    
    // Actions
    btnInspect: document.getElementById('btn-inspect'),
    btnApprove: document.getElementById('btn-approve'),
    btnHide: document.getElementById('btn-hide'),
    btnFlag: document.getElementById('btn-flag'),
};

let stepCount = 0;
let lastState = null;

function switchTab(tab) {
    // Update active class on tabs
    [UI.tabIntelligence, UI.tabSupplyChain, UI.tabCompliance].forEach(t => t.classList.remove('active'));
    UI[`tab${tab}`].classList.add('active');

    // Update visibility of views
    [UI.viewIntelligence, UI.viewSupplyChain, UI.viewCompliance].forEach(v => v.classList.add('hidden'));
    UI[`view${tab}`].classList.remove('hidden');
}

async function updateState(data) {
    const obs = data.observation || data.state;
    const reward = data.reward || 0.0;
    const info = data.info || null;
    
    // Strict nesting extraction
    const r = obs ? obs.restaurant : null;
    
    if (!r) {
        UI.restaurantName.innerText = "Error loading data...";
        return;
    }
    
    lastState = r;
    
    // Update basic text
    UI.restaurantName.innerText = r.restaurant_name || "Loading restaurant data...";
    UI.venueId.innerText = `EST ID: ${r.restaurant_id || '---'}`;
    if (UI.restaurantDesc) UI.restaurantDesc.innerText = r.description || "No description available";
    
    // --- INTEGRIGENCE VIEW ---
    UI.hygieneScore.innerText = Math.round(r.hygiene_score);
    const gauge = document.querySelector('.gauge');
    if (gauge) gauge.style.background = `conic-gradient(var(--accent) ${r.hygiene_score}%, var(--border) 0%)`;
    
    if (r.hygiene_score > 90 && r.complaints_count === 0 && !r.is_hidden_risk) {
        UI.riskLevel.innerText = "ULTRA-LOW RISK";
        UI.riskLevel.style.color = "var(--success)";
    } else if (r.hygiene_score > 75 && !r.is_hidden_risk) {
        UI.riskLevel.innerText = "MODERATE RISK";
        UI.riskLevel.style.color = "var(--warning)";
    } else {
        UI.riskLevel.innerText = "HIGH HAZARD";
        UI.riskLevel.style.color = "var(--danger)";
    }

    if (r.badge_visible) {
        UI.statusBadge.innerText = "AI VERIFIED SAFE";
        UI.statusBadge.className = "badge";
    } else if (r.flagged) {
        UI.statusBadge.innerText = "WARNING: FLAGGED";
        UI.statusBadge.className = "badge danger";
        UI.statusBadge.style.color = "var(--danger)";
        UI.statusBadge.style.borderColor = "var(--danger)";
    } else {
        UI.statusBadge.innerText = "PENDING ANALYSIS";
        UI.statusBadge.className = "badge inactive";
        UI.statusBadge.style.color = "var(--text-secondary)";
        UI.statusBadge.style.borderColor = "var(--border)";
    }

    UI.trustValue.innerText = `${Math.round(r.user_trust)}%`;
    UI.trustBar.style.width = `${r.user_trust}%`;
    UI.auditAge.innerText = `${r.inspection_age_days} Days Ago`;
    
    if (r.complaints_count === 0) {
        UI.sentiment.innerText = "Positive";
        UI.sentiment.className = "positive";
    } else if (r.complaints_count < 5) {
        UI.sentiment.innerText = "Neutral";
        UI.sentiment.className = "neutral";
    } else {
        UI.sentiment.innerText = "CRITICAL";
        UI.sentiment.className = "danger";
    }

    if (info && info.info) {
        UI.explanation.innerText = info.info.reason;
        UI.explanation.parentElement.style.borderLeftColor = reward > 0.6 ? "var(--success)" : (reward < 0.4 ? "var(--danger)" : "var(--warning)");
    }

    // --- SUPPLY CHAIN VIEW ---
    if (r.hygiene_score > 85) {
        UI.supplierStatus.innerText = "Optimal";
        UI.supplierStatus.style.color = "var(--success)";
    } else if (r.hygiene_score > 65) {
        UI.supplierStatus.innerText = "Stable";
        UI.supplierStatus.style.color = "var(--warning)";
    } else {
        UI.supplierStatus.innerText = "At Risk";
        UI.supplierStatus.style.color = "var(--danger)";
    }

    if (r.hygiene_score > 70) {
        UI.storageStatus.innerText = "Compliant";
        UI.storageStatus.style.color = "var(--success)";
    } else {
        UI.storageStatus.innerText = "Warning";
        UI.storageStatus.style.color = "var(--danger)";
    }

    const deliveryRisk = Math.min(100, r.complaints_count * 10);
    UI.deliveryRiskBar.style.width = `${deliveryRisk}%`;
    UI.deliveryRiskBar.style.background = deliveryRisk > 50 ? "var(--danger)" : (deliveryRisk > 20 ? "var(--warning)" : "var(--success)");
    UI.deliveryRiskText.innerText = deliveryRisk > 50 ? "High Logistics Risk" : "Stable Logistics";

    // --- COMPLIANCE VIEW ---
    if (r.hygiene_score > 85) {
        UI.complianceStatus.innerText = "PASS";
        UI.complianceStatus.style.color = "var(--success)";
        UI.complianceStatus.nextElementSibling.innerText = "Standard safety thresholds maintained";
    } else if (r.hygiene_score > 60) {
        UI.complianceStatus.innerText = "WARNING";
        UI.complianceStatus.style.color = "var(--warning)";
        UI.complianceStatus.nextElementSibling.innerText = "Minor discrepancies detected";
    } else {
        UI.complianceStatus.innerText = "FAIL";
        UI.complianceStatus.style.color = "var(--danger)";
        UI.complianceStatus.nextElementSibling.innerText = "Critical safety violations found";
    }

    UI.licenseStatus.innerText = r.hygiene_score > 50 ? "VALID" : "UNDER REVIEW";
    UI.licenseStatus.style.color = r.hygiene_score > 50 ? "var(--success)" : "var(--danger)";
    UI.violationCount.innerText = r.complaints_count;
    UI.auditRecency.innerText = `${r.inspection_age_days} Days`;
}

async function performAction(actionName) {
    try {
        const resp = await fetch(`${API_BASE}/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: actionName })
        });
        const data = await resp.json();
        
        stepCount++;
        addHistoryRow(stepCount, actionName, data.reward, data.info.info.reason);
        updateState(data);
    } catch (err) {
        console.error("Action failed", err);
    }
}

function addHistoryRow(step, action, reward, reason) {
    const row = document.createElement('tr');
    const now = new Date().toLocaleTimeString();
    row.innerHTML = `
        <td>#${step}</td>
        <td style="color: var(--accent)">${action.toUpperCase()}</td>
        <td style="font-size: 0.75rem">${reason}</td>
        <td style="color: ${reward > 0.6 ? 'var(--success)' : 'var(--danger)'}">${reward.toFixed(6)}</td>
        <td style="color: var(--text-secondary); font-size: 0.7rem">${now}</td>
    `;
    UI.historyBody.prepend(row);
}

async function resetTask() {
    const taskId = UI.taskSelect.value;
    const resp = await fetch(`${API_BASE}/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId })
    });
    const data = await resp.json();
    stepCount = 0;
    UI.historyBody.innerHTML = "";
    UI.explanation.innerText = "Select an action to begin analysis.";
    updateState(data);
}

// Event Listeners
UI.btnInspect.onclick = () => performAction('request_inspection');
UI.btnApprove.onclick = () => performAction('show_safety_badge');
UI.btnHide.onclick = () => performAction('hide_info');
UI.btnFlag.onclick = () => performAction('flag_restaurant');
UI.btnReset.onclick = resetTask;

UI.tabIntelligence.onclick = () => switchTab('Intelligence');
UI.tabSupplyChain.onclick = () => switchTab('SupplyChain');
UI.tabCompliance.onclick = () => switchTab('Compliance');

// Initialize
window.onload = async () => {
    const resp = await fetch(`${API_BASE}/state`);
    const data = await resp.json();
    updateState(data);
};
