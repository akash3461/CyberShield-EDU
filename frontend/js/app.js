// --- Modern App Logic & Redesign Support ---

(function() {
    // Theme Loading
    const mode = localStorage.getItem('themeMode') || 'light';
    document.body.className = `mode-${mode}`;
})();

// --- Authentication & Header UI ---
window.updateHeaderAuthUI = async function() {
    const authButtons = document.getElementById('auth-buttons');
    const userProfile = document.getElementById('user-profile');
    const usernameDisplay = document.getElementById('header-username');
    
    // Safety check for API initialization
    if (!window.api || !window.api.auth) return;

    const isLoggedIn = window.api.auth.isLoggedIn();
    let user = window.api.auth.getCurrentUser();

    // If logged in but no user object in localStorage, try to fetch it
    if (isLoggedIn && !user) {
        try {
            // console.log("User data missing from localStorage, fetching from API...");
            user = await window.api.auth.getMe();
        } catch (error) {
            console.error("Failed to recover user data:", error);
        }
    }

    // console.log("Header Update - LoggedIn:", isLoggedIn, "User:", user);

    if (isLoggedIn && user) {
        if (authButtons) authButtons.style.display = 'none';
        if (userProfile) {
            userProfile.style.display = 'flex';
            // Ensure gamification indicators are not hidden
            userProfile.querySelectorAll('[data-gamif]').forEach(el => el.style.display = '');
        }
        
        if (usernameDisplay) {
            usernameDisplay.textContent = user.username || user.name || 'User';
            // Add clickability to username
            usernameDisplay.style.cursor = 'pointer';
            usernameDisplay.title = 'Go to Account Settings';
            usernameDisplay.onclick = () => window.location.href = 'settings.html';
        }
        
        // Hide Admin panel for students
        const adminNav = document.getElementById('admin-nav');
        if (adminNav) {
            if (user.role === 'student' || !user.role) {
                adminNav.parentElement.style.display = 'none';
            } else if (user.role === 'admin') {
                adminNav.parentElement.style.display = '';
            }
        }

        // Ensure gamification is initialized
        if (window.Gamification && typeof window.Gamification.init === 'function') {
            window.Gamification.init();
        }
    } else {
        if (authButtons) authButtons.style.display = 'flex';
        if (userProfile) userProfile.style.display = 'none';
        
        // Show Admin panel for guests (it has its own password gate)
        const adminNav = document.getElementById('admin-nav');
        if (adminNav) adminNav.parentElement.style.display = '';
    }
};

window.logout = async function() {
    if (window.api && window.api.auth) {
        await window.api.auth.logout();
        window.location.href = 'index.html';
    }
};

// --- Global Helper Functions ---
function initGuestUI() {
    if (!window.api || !window.api.auth) return;
    
    const isLoggedIn = window.api.auth.isLoggedIn();
    const indicator = document.getElementById('guest-indicator');
    const locks = document.querySelectorAll('.lock-icon');
    
    if (!isLoggedIn) {
        if (indicator) {
            const count = getGuestScanCount();
            const remaining = Math.max(0, 3 - count);
            indicator.textContent = `Guest Mode: ${remaining} Scans Left`;
            indicator.style.display = 'block';
        }
        locks.forEach(lock => lock.style.display = 'inline-block');
    } else {
        if (indicator) indicator.style.display = 'none';
        locks.forEach(lock => lock.style.display = 'none');
        // Hide Login/Signup buttons in header
        document.querySelectorAll('header .nav-actions .btn').forEach(btn => {
            if (btn.textContent.includes('Login') || btn.textContent.includes('Sign Up')) {
                btn.style.display = 'none';
            }
        });
    }
}

function getGuestScanCount() {
    return parseInt(localStorage.getItem('cs_guest_scans') || '0');
}

function incrementGuestScanCount() {
    const count = getGuestScanCount() + 1;
    localStorage.setItem('cs_guest_scans', count.toString());
    return count;
}

function showAuthPrompt(message = "Join CyberShield to unlock full protection and track your security history.") {
    const modal = document.getElementById('authPromptModal');
    const messageEl = document.getElementById('authPromptMessage');
    if (modal && messageEl) {
        messageEl.textContent = message;
        modal.classList.add('show');
    } else {
        if (confirm(message + "\n\nWould you like to log in now?")) {
            window.location.href = 'login.html';
        }
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Shared animations
    if (typeof initAnimations === 'function') initAnimations();
    
    // Auth UI Update
    if (window.updateHeaderAuthUI) window.updateHeaderAuthUI();

    initScamTicker();
    initModals();

    // Initialize Guest UI
    initGuestUI();
});


// --- Theme Management ---
window.toggleTheme = function() {
    const isLight = document.body.classList.contains('mode-light');
    const newMode = isLight ? 'dark' : 'light';
    
    document.body.className = `mode-${newMode}`;
    localStorage.setItem('themeMode', newMode);
    
    // Update switch UI if needed
    updateThemeUI(newMode);
};

function updateThemeUI(mode) {
    const slider = document.querySelector('.theme-switch .slider');
    if (!slider) return;
    
    // The icon switching logic can go here if we were using separate icons
    // For now, the CSS transform handles the physical slider movement
}

// --- Scroll & Entrance Animations ---
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animateOnScroll').forEach(el => observer.observe(el));
}

// --- Unified Tab System ---
window.switchTab = function(tabId) {
    const isLoggedIn = window.api && window.api.auth && window.api.auth.isLoggedIn();
    const restrictedTabs = ['url-tab', 'pdf-tab', 'image-tab', 'report-tab'];
    
    if (!isLoggedIn && restrictedTabs.includes(tabId)) {
        showAuthPrompt(`The ${tabId.replace('-tab', '').toUpperCase()} tools are premium security features. Please log in to unlock full protection.`);
        return;
    }

    // Content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    // Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    const activeTab = document.getElementById(tabId);
    if (activeTab) activeTab.classList.add('active');
    
    // Clear and hide results when switching tabs
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
        resultContainer.innerHTML = '';
        resultContainer.classList.remove('show');
    }

    // Find the button that was clicked and activate it
    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
    if (activeBtn) activeBtn.classList.add('active');
};

// --- API Helper & Loading State ---
function setLoadingState(button, isLoading, text = "Processing...") {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 11-6.219-8.56" />
                </svg>
                ${text}
            </div>
        `;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || "Run Analysis";
    }
}

// --- Pillar 1: LLM-Driven Scam Explainer (Cyber-Tutor) - [PAUSED] ---
/*
async function fetchExplanation(scanType, result) {
    try {
        const response = await fetch(`${API_BASE_URL}/help/explain`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scan_type: scanType, result: result })
        });
        const data = await response.json();
        return data.explanation;
    } catch (error) {
        console.error("Explanation failed:", error);
        return "Could not load detailed explanation at this time.";
    }
}
*/


// --- Results Rendering (Premium) ---
// --- Results Rendering (Premium) ---
function renderScanResult(result, container) {
    if (!container) return;
    
    const prediction = result.prediction.toLowerCase();
    const confidence = result.confidence; 
    const reasoning = result.reasoning || ["Pattern analysis complete."];
    
    // Tiered color-coding: 0-30% Safe, 30-70% Suspicious, 70-100% Scam
    let statusColor, statusLabel, statusText, statusDot, bgColor, borderAlpha;
    
    if (prediction === 'scam' || confidence >= 0.7) {
        statusColor = 'var(--danger)';
        statusLabel = 'THREAT DETECTED';
        statusText = 'Fraudulent Content Flagged';
        statusDot = '#ef4444';
        bgColor = 'rgba(239, 68, 68, 0.1)';
        borderAlpha = '0.3';
    } else if (prediction === 'suspicious' || (confidence >= 0.3 && confidence < 0.7)) {
        statusColor = 'var(--warning)';
        statusLabel = 'CAUTION REQUIRED';
        statusText = 'Suspicious Patterns Found';
        statusDot = '#f59e0b';
        bgColor = 'rgba(245, 158, 11, 0.1)';
        borderAlpha = '0.25';
    } else {
        statusColor = 'var(--success)';
        statusLabel = 'SYSTEMS CLEAR';
        statusText = 'Identity & Safety Verified';
        statusDot = '#22c55e';
        bgColor = 'rgba(34, 197, 94, 0.05)';
        borderAlpha = '0.2';
    }

    const isAlert = prediction === 'scam' || prediction === 'suspicious';
    
    // 1. Generate standard insights
    const insightsHtml = reasoning.map(r => {
        const isWarning = r.includes('ALERT') || r.includes('CRITICAL') || r.includes('Detected') || isAlert;
        return `
            <div class="insight-item" style="display: flex; gap: 12px; font-size: 0.9rem; color: var(--text-muted); padding: 10px; background: ${isWarning ? 'rgba(255, 150, 0, 0.05)' : 'rgba(34, 197, 94, 0.05)'}; border-radius: 10px; border: 1px solid var(--glass-border); margin-bottom: 8px;">
                <div style="color: ${isWarning ? 'var(--warning)' : 'var(--success)'}; font-weight: bold;">${isWarning ? '!' : '✓'}</div>
                <div>${r}</div>
            </div>
        `;
    }).join('');

    // 2. Generate Technical Forensic Panel
    let forensicsHtml = '';
    const forens = result.forensics || result.metadata?.forensics || {};
    const insights = result.insights || {};

    if (result.forensics || result.insights || result.metadata?.forensics) {
        
        forensicsHtml = `
            <div class="insight-panel">
                <div class="insight-header">
                    <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    <h3>Technical Forensics</h3>
                </div>
                
                <div class="insight-grid">
                    ${forens.geo_location ? `
                        <div class="forensic-group">
                            <span class="forensic-label">Server Origin</span>
                            <div class="geo-tag">
                                <span>${forens.geo_location.flag}</span>
                                <span>${forens.geo_location.city}, ${forens.geo_location.country}</span>
                            </div>
                            <div style="font-size: 0.7rem; color: var(--text-muted); font-family: monospace; margin-top: 4px;">IP: ${forens.geo_location.ip}</div>
                        </div>
                    ` : ''}
                    
                    ${result.metadata?.entropy ? `
                        <div class="forensic-group">
                            <span class="forensic-label">Domain Entropy</span>
                            <div class="forensic-value">${result.metadata.entropy}</div>
                            <div style="font-size: 0.7rem; color: ${result.metadata.entropy > 3.5 ? 'var(--danger)' : 'var(--text-muted)'};">
                                ${result.metadata.entropy > 3.5 ? '⚠️ Highly Suspicious randomness' : '✓ Normal character distribution'}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${forens.asn_info ? `
                        <div class="forensic-group">
                            <span class="forensic-label">Network (ASN)</span>
                            <div class="forensic-value">${forens.asn_info.isp}</div>
                            <div style="font-size: 0.7rem; color: var(--primary);">${forens.asn_info.asn}</div>
                        </div>
                    ` : ''}

                    ${insights.complexity ? `
                        <div class="forensic-group">
                            <span class="forensic-label">Linguistic Profile</span>
                            <div class="forensic-value">${insights.complexity}</div>
                        </div>
                    ` : ''}

                    ${forens.ocr_confidence ? `
                        <div class="forensic-group">
                            <span class="forensic-label">OCR Reliability</span>
                            <div class="forensic-badge">${(forens.ocr_confidence * 100).toFixed(0)}% Certainty</div>
                        </div>
                    ` : ''}

                    ${forens.author ? `
                        <div class="forensic-group">
                            <span class="forensic-label">Document Metadata</span>
                            <div class="forensic-value" style="font-size: 0.8rem;">Author: ${forens.author}</div>
                            <div class="forensic-value" style="font-size: 0.75rem; opacity: 0.7;">Tool: ${forens.creator_tool}</div>
                        </div>
                    ` : ''}
                </div>

                ${forens.risk_breakdown ? `
                    <div class="risk-breakdown">
                        <span class="forensic-label">Risk Vector Distribution</span>
                        <div class="risk-bar-container">
                            <div class="risk-segment heuristics" style="width: ${forens.risk_breakdown.heuristics * 100}%"></div>
                            <div class="risk-segment content" style="width: ${forens.risk_breakdown.content_ai * 100}%"></div>
                            <div class="risk-segment external" style="width: ${forens.risk_breakdown.external_intel * 100}%"></div>
                        </div>
                        <div class="risk-legend">
                            <div class="legend-item"><div class="legend-dot heuristics"></div> Heuristics (${Math.round(forens.risk_breakdown.heuristics * 100)}%)</div>
                            <div class="legend-item"><div class="legend-dot content"></div> Content AI (${Math.round(forens.risk_breakdown.content_ai * 100)}%)</div>
                            <div class="legend-item"><div class="legend-dot external"></div> Threat Intel (${Math.round(forens.risk_breakdown.external_intel * 100)}%)</div>
                        </div>
                    </div>
                ` : ''}

                <div class="forensics-footer">
                    Forensic data extracted via Multi-Vector Analysis Engine v2.1.0
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        <div class="glass-card animateOnScroll animated" style="padding: 2rem; border-color: ${statusColor.replace('var(--', 'rgba(var(--').replace(')', ', ' + borderAlpha + ')')}; background: var(--bg-card); box-shadow: 0 10px 30px ${bgColor};">
            <div class="result-header" style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;">
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div class="status-indicator" style="display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 0.8rem; color: ${statusColor};">
                        <div class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: ${statusDot}; box-shadow: 0 0 10px ${statusDot};"></div>
                        <span>${statusLabel}</span>
                    </div>
                    
                    ${(result.forensics?.trust_info || result.metadata?.forensics?.trust_info) ? `
                        <div class="trust-badge">
                            <span class="trust-badge-icon">🛡️</span>
                            <span class="trust-badge-text">Verified Institution</span>
                        </div>
                    ` : ''}
                </div>
                <div class="confidence-badge" style="background: var(--primary-glow); padding: 4px 12px; border-radius: 2rem; font-size: 0.8rem; font-weight: 700; color: var(--primary);">
                    ${(confidence * 100).toFixed(1)}% Certainty
                </div>
            </div>

            <div class="result-body">
                <h3 style="font-size: 1.5rem; color: var(--text-main); margin-bottom: 0.5rem;">
                    ${statusText}
                </h3>
                <p style="color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.95rem;">
                    ${result.recommendation || (isAlert ? "Vigilance and thorough verification recommended." : "No malicious patterns identified.")}
                </p>

                ${insights.impersonated_brand ? `
                    <div class="impersonation-alert" style="display: flex; align-items: center; gap: 15px; background: rgba(239, 68, 68, 0.15); border: 2px solid var(--danger); padding: 15px; border-radius: 12px; margin-bottom: 2rem; animation: pulse 2s infinite;">
                        <span style="font-size: 2rem;">👤⚠️</span>
                        <div>
                            <h4 style="margin: 0; color: #f87171; font-weight: 800;">IMPERSONATION DETECTED</h4>
                            <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: var(--text-muted);">This message claims to be from <b>${insights.impersonated_brand}</b>, but the link points to an unrelated destination.</p>
                        </div>
                    </div>
                ` : ''}

                <div class="scoring-breakdown" style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
                    <h4 style="margin: 0 0 1rem 0; font-size: 0.9rem; color: var(--primary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Why this score? (Vector Analysis)</h4>
                    <div class="analysis-grid" style="display: flex; flex-direction: column; gap: 12px;">
                        ${result.score_explanation ? Object.entries(result.score_explanation).map(([factor, weight]) => `
                            <div class="analysis-row" style="display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 6px; height: 6px; border-radius: 50%; background: var(--primary);"></div>
                                    <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: capitalize;">${factor.replace('_', ' ')}</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px; flex: 1; margin: 0 20px;">
                                    <div style="flex: 1; height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden;">
                                        <div style="width: ${Math.min(100, weight)}%; height: 100%; background: var(--primary); box-shadow: 0 0 8px var(--primary);"></div>
                                    </div>
                                </div>
                                <span style="font-size: 0.75rem; color: var(--text-main); font-weight: bold; width: 35px; text-align: right;">${weight}%</span>
                            </div>
                        `).join('') : '<div style="font-size: 0.8rem; color: var(--text-muted); font-style: italic;">Heuristic pattern weight distribution active (Dynamic).</div>'}
                    </div>
                </div>

                <div class="insights-list">${insightsHtml}</div>

                <!--
                <div id="tutor-panel" class="tutor-panel" style="margin-top: 2rem; border-top: 1px solid var(--glass-border); padding-top: 2rem;">
                    <div style="display: flex; gap: 15px; align-items: start;">
                        <div class="tutor-avatar" style="font-size: 2rem; background: var(--primary-glow); padding: 10px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 122, 255, 0.2);">🛡️</div>
                        <div class="tutor-content">
                            <h4 style="margin: 0; font-size: 1.1rem; color: var(--primary); font-weight: 700;">CyberShield Tutor Perspective</h4>
                            <p id="tutor-text" style="color: var(--text-muted); font-size: 0.92rem; line-height: 1.7; margin-top: 8px; font-style: italic;">
                                Analyzing forensic vectors for deeper insights...
                            </p>
                        </div>
                    </div>
                </div>
                -->
                
                ${result.forensic_report ? `
                    <div class="forensic-lab-container" style="margin-top: 2rem; background: rgba(15, 23, 42, 0.4); border: 1px solid var(--primary); border-radius: 12px; padding: 1.5rem; position: relative; overflow: hidden;">
                        <div style="position: absolute; top: 0; right: 0; padding: 4px 8px; font-size: 0.65rem; font-family: monospace; background: var(--primary); color: white; border-bottom-left-radius: 8px; text-transform: uppercase;">Forensic Mode v5.0</div>
                        
                        <div class="lab-header" style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                            <h4 style="margin: 0; font-family: 'Outfit'; font-weight: 700; color: white;">${result.metadata?.forensics ? 'Document Forensic Audit' : 'Image Integrity Report'}</h4>
                        </div>

                        <div class="integrity-gauge" style="margin-bottom: 1.5rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 6px;">
                                <span>Signal Integrity Score</span>
                                <span style="color: ${result.forensic_report.integrity_score > 70 ? 'var(--success)' : 'var(--danger)'}; font-weight: bold;">${result.forensic_report.integrity_score}%</span>
                            </div>
                            <div style="height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden;">
                                <div style="width: ${result.forensic_report.integrity_score}%; height: 100%; background: linear-gradient(90deg, var(--danger), var(--primary), var(--success)); transition: width 1s ease-out;"></div>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 1.5rem;">
                            <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;">
                                <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 4px;">${result.metadata?.forensics ? 'Linguistic Intent' : 'Texture Analysis'}</div>
                                <div style="font-size: 0.9rem; color: ${result.prediction === 'safe' ? 'var(--success)' : 'var(--danger)'}; font-weight: 600;">
                                    ${result.metadata?.forensics ? (result.ai_analysis?.prediction?.toUpperCase() || 'UNAIDED') : result.forensic_report.texture_analysis}
                                </div>
                            </div>
                            <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;">
                                <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 4px;">Metadata Trust</div>
                                <div style="font-size: 0.9rem; color: ${result.metadata?.forensics?.author === 'Unknown' ? 'var(--primary)' : 'var(--success)'}; font-weight: 600; text-transform: capitalize;">
                                    ${result.metadata?.forensics?.author || result.forensic_report?.metadata_trust || 'Standard'}
                                </div>
                            </div>
                        </div>

                        ${result.forensic_report.is_synthetic ? `
                            <div style="display: flex; align-items: center; gap: 10px; background: rgba(239, 68, 68, 0.15); border: 1px solid var(--danger); padding: 12px; border-radius: 8px; margin-top: 10px;">
                                <span style="font-size: 1.2rem;">⚠️</span>
                                <div style="font-size: 0.85rem; color: #f87171; font-weight: 600;">AI/Synthetic Signatures Detected</div>
                            </div>
                        ` : ''}

                        ${result.correlation_report && result.correlation_report.reasons.length > 0 ? `
                            <div class="correlation-logic" style="margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                                <div style="font-size: 0.7rem; color: var(--primary); font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Correlation Intelligence</div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    ${result.correlation_report.reasons.map(reason => `
                                        <div style="font-size: 0.8rem; color: var(--text-main); background: rgba(56, 189, 248, 0.05); padding: 8px; border-radius: 6px; border-left: 2px solid var(--primary);">
                                            ${reason}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <details style="margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                            <summary style="font-size: 0.75rem; color: var(--primary); cursor: pointer; list-style: none;">🔍 View Raw Metadata Inspector</summary>
                            <div style="margin-top: 10px; font-family: monospace; font-size: 0.7rem; color: var(--text-muted); max-height: 200px; overflow-y: auto;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    ${result.metadata.forensics.exif.tags ? Object.entries(result.metadata.forensics.exif.tags).map(([k, v]) => `
                                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                            <td style="padding: 4px; color: var(--text-main); font-weight: bold;">${k}</td>
                                            <td style="padding: 4px; color: #38bdf8;">${v}</td>
                                        </tr>
                                    `).join('') : '<tr><td>No tags found</td></tr>'}
                                </table>
                            </div>
                        </details>
                    </div>
                ` : forensicsHtml}

                ${result.url_analysis && result.url_analysis.length > 0 ? `
                    <div class="recursive-link-hub" style="margin-top: 2rem; background: rgba(30, 41, 59, 0.5); border: 1px solid var(--primary); border-radius: 12px; padding: 1.5rem; position: relative; overflow: hidden;">
                        <div style="position: absolute; top: 0; right: 0; padding: 4px 8px; font-size: 0.65rem; font-family: monospace; background: var(--primary); color: white; border-bottom-left-radius: 8px; text-transform: uppercase;">Pillar 8 // Recursive Audit</div>
                        
                        <div class="lab-header" style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" /></svg>
                            <h4 style="margin: 0; font-family: 'Outfit'; font-weight: 700; color: white;">Recursive Link Audit</h4>
                        </div>

                        <div class="link-grid" style="display: flex; flex-direction: column; gap: 12px;">
                            ${result.url_analysis.map(link => `
                                <div class="link-audit-item-wrapper" style="background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid ${link.prediction === 'scam' ? 'var(--danger)' : 'var(--success)'}; overflow: hidden; margin-bottom: 8px;">
                                    <div class="link-audit-item" style="display: flex; align-items: center; justify-content: space-between; padding: 12px 15px;">
                                        <div style="flex: 1; min-width: 0; margin-right: 15px;">
                                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                                ${link.type === 'ghost' ? '<span title="Ghost-Link: Hidden in PDF structure" style="font-size: 1.1rem; opacity: 0.8;">🕵️</span>' : '<span style="font-size: 0.9rem; opacity: 0.6;">🔗</span>'}
                                                <div style="font-size: 0.85rem; color: var(--text-main); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: monospace;">
                                                    ${link.url}
                                                </div>
                                            </div>
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <span style="font-size: 0.65rem; background: ${link.type === 'ghost' ? 'var(--primary-glow)' : 'rgba(255,255,255,0.1)'}; color: ${link.type === 'ghost' ? 'var(--primary)' : 'var(--text-muted)'}; padding: 1px 6px; border-radius: 4px; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px;">${link.type || 'Visible'}</span>
                                                ${link.forensics?.geo_location ? `
                                                    <span title="${link.forensics.geo_location.country}" style="font-size: 0.8rem;">${link.forensics.geo_location.flag || '🌐'}</span>
                                                    <span style="font-size: 0.65rem; color: var(--text-muted);">${link.forensics.geo_location.city || 'Origin Hidden'}</span>
                                                ` : '<span style="font-size: 0.65rem; color: var(--text-muted);">🌐 Global Origin</span>'}
                                            </div>
                                        </div>
                                        <div class="audit-status" style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                                            <span style="font-size: 0.7rem; font-weight: 800; color: ${link.prediction === 'scam' ? 'var(--danger)' : 'var(--success)'}; text-transform: uppercase; letter-spacing: 0.5px;">
                                                ${link.prediction === 'scam' ? 'SCAM' : 'SAFE'}
                                            </span>
                                            <div style="height: 4px; width: 40px; background: rgba(255,255,255,0.1); border-radius: 2px;">
                                                <div style="height: 100%; width: ${Math.round(link.score * 100)}%; background: ${link.prediction === 'scam' ? 'var(--danger)' : 'var(--success)'}; border-radius: 2px;"></div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    ${link.redirect_chain && link.redirect_chain.length > 1 ? `
                                        <div class="redirect-chain-ui" style="background: rgba(0,0,0,0.2); padding: 8px 15px; border-top: 1px solid rgba(255,255,255,0.05);">
                                            <div style="font-size: 0.65rem; color: var(--primary); font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 5px;">
                                                <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg>
                                                REDIRECT CHAIN DETECTED (${link.redirect_chain.length} HOPS)
                                            </div>
                                            <div style="display: flex; flex-direction: column; gap: 4px; border-left: 1px dashed var(--primary); margin-left: 4px; padding-left: 10px;">
                                                ${link.redirect_chain.map((hop, idx) => `
                                                    <div style="font-size: 0.6rem; font-family: monospace; color: ${idx === link.redirect_chain.length - 1 ? 'white' : 'var(--text-muted)'}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                                        ${idx === 0 ? 'START' : '➔'} ${hop}
                                                    </div>
                                                `).join('')}
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>

                        ${result.url_analysis.length >= 10 ? `
                            <div style="margin-top: 10px; text-align: center; font-size: 0.65rem; color: var(--text-muted); font-style: italic;">
                                Forensics limited to top 10 suspicious artifacts to maintain system pulse.
                            </div>
                        ` : ''}
                    </div>
                ` : ''}

            </div>

            <div class="result-footer" style="margin-top: 2rem; display: flex; gap: 12px;">
                <button class="btn btn-ghost" onclick="location.reload()" style="flex: 1;">New Audit</button>
                ${isAlert ? `<button class="btn btn-primary" onclick="window.location.href='phish-sim.html'" style="flex: 1; background: ${prediction === 'scam' ? 'var(--danger)' : 'var(--warning)'}; border: none;">Take Quiz</button>` : ''}
            </div>
        </div>
    `;

    // Award Gamification Points
    if (window.Gamification) window.Gamification.addXp(15, "Deep Audit Completed");
    
    container.style.display = 'block';
    container.classList.add('show');
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // 4. Trigger explanation fetch (Pillar 1) - [PAUSED]
    /*
    let type = 'text';
    if (window.location.pathname.includes('url')) type = 'url';
    if (window.location.pathname.includes('pdf')) type = 'pdf';
    if (window.location.pathname.includes('image')) type = 'image';

    fetchExplanation(type, result).then(explanation => {
        const text = document.getElementById('tutor-text');
        if (text) text.innerHTML = explanation;
    });
    */
}



async function initScamTicker() {
    const tickerEl = document.getElementById('scamTicker');
    if (!tickerEl) return;

    try {
        const baseUrl = window.api && window.api.base_url ? window.api.base_url : 'http://localhost:8000/api/v1';
        const response = await fetch(`${baseUrl}/report/recent`);
        const reports = await response.json();
        
        if (reports && reports.length > 0) {
            tickerEl.innerHTML = `<span>${reports.map(r => `🚨 ${r.company_name}: ${r.description.substring(0, 100)}...`).join(' • ')}</span>`;
        } else {
            tickerEl.innerHTML = `<span>No recent reports. Stay vigilant! • Report any suspicious activity to help the community.</span>`;
        }
    } catch (err) {
        tickerEl.innerHTML = `<span>Stay vigilant! • Report any suspicious activity to help the community.</span>`;
    }
}

window.showConfidenceInfo = function() {
    const modal = document.getElementById('confidenceModal');
    if (modal) modal.classList.add('show');
};

function initModals() {
    const modal = document.getElementById('confidenceModal');
    const closeBtn = document.querySelector('.close-modal');
    
    if (closeBtn && modal) {
        closeBtn.onclick = () => modal.classList.remove('show');
        window.onclick = (event) => {
            if (event.target == modal) modal.classList.remove('show');
        };
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Guest UI Refresh
    initGuestUI();

    // Global result container
    const resultContainer = document.getElementById('result-container');

    // --- Text Scan ---
    const textBtn = document.getElementById('btn-text-scan');
    if (textBtn) {
        textBtn.addEventListener('click', async () => {
            const isLoggedIn = window.api && window.api.auth && window.api.auth.isLoggedIn();
            
            if (!isLoggedIn) {
                const count = getGuestScanCount();
                if (count >= 3) {
                    showAuthPrompt("You've reached your limit of 3 guest scans. Create a free account to continue scanning.");
                    return;
                }
            }

            const text = document.getElementById('textScanInput').value.trim();
            if (!text) return alert("Please enter text to analyze.");

            setLoadingState(textBtn, true, "Analyzing message...");
            try {
                const result = await window.api.detection.analyzeText(text);
                renderScanResult(result, resultContainer);
                
                if (!isLoggedIn) {
                    const newCount = incrementGuestScanCount();
                    initGuestUI(); // Update indicator
                }
            } catch (err) {
                alert("Analysis failed. Backend might be offline.");
            } finally {
                setLoadingState(textBtn, false);
            }
        });
    }

    // --- URL Scan ---
    const urlBtn = document.getElementById('btn-url-scan');
    if (urlBtn) {
        urlBtn.addEventListener('click', async () => {
            if (!window.api.auth.isLoggedIn()) {
                showAuthPrompt("URL scanning is a premium security feature. Please log in to continue.");
                return;
            }

            const url = document.getElementById('urlScanInput').value.trim();
            if (!url) return alert("Please enter a URL.");

            setLoadingState(urlBtn, true, "Analyzing URL...");
            try {
                const result = await window.api.detection.analyzeUrl(url);
                renderScanResult(result, resultContainer);
            } catch (err) {
                alert("Scan failed.");
            } finally {
                setLoadingState(urlBtn, false);
            }
        });
    }

    // --- PDF Scan ---
    const pdfBtn = document.getElementById('btn-pdf-scan');
    const pdfInput = document.getElementById('pdfInput') || document.getElementById('pdfFileInput');
    const pdfFileNameDisplay = document.getElementById('pdfFileName');
    const pdfFileSizeDisplay = document.getElementById('pdfFileSize');
    const pdfPreviewWrapper = document.getElementById('pdfPreviewWrapper');
    const pdfDropPrompt = document.getElementById('pdfDropPrompt');
    const btnClearPdf = document.getElementById('btn-clear-pdf');

    if (pdfInput) {
        pdfInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                // Update file info
                if (pdfFileNameDisplay) pdfFileNameDisplay.textContent = file.name;
                if (pdfFileSizeDisplay) {
                    const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
                    pdfFileSizeDisplay.textContent = `${sizeMb} MB // EVIDENCE STAGED`;
                }

                // Toggle Preview
                if (pdfPreviewWrapper && pdfDropPrompt) {
                    pdfPreviewWrapper.classList.remove('hidden');
                    pdfPreviewWrapper.style.display = 'block';
                    pdfDropPrompt.style.display = 'none';
                }
            }
        });
    }

    if (btnClearPdf) {
        btnClearPdf.addEventListener('click', (e) => {
            e.stopPropagation(); // Avoid triggering file input
            if (pdfInput) pdfInput.value = '';
            if (pdfPreviewWrapper && pdfDropPrompt) {
                pdfPreviewWrapper.classList.add('hidden');
                pdfPreviewWrapper.style.display = 'none';
                pdfDropPrompt.style.display = 'block';
            }
        });
    }

    if (pdfBtn && pdfInput) {
        pdfBtn.addEventListener('click', async () => {
            if (!window.api.auth.isLoggedIn()) {
                showAuthPrompt("PDF deep analysis requires a secure account. Log in to start scanning documents.");
                return;
            }

            const file = pdfInput.files[0];
            if (!file) return alert("Please select a PDF file.");

            setLoadingState(pdfBtn, true, "Analyzing PDF...");
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await window.api.detection.analyzePdf(formData);
                if (response.task_id) {
                    const result = await window.api.tasks.pollUntilFinished(response.task_id);
                    renderScanResult(result, resultContainer);
                } else {
                    // Fallback for non-task responses
                    renderScanResult(response, resultContainer);
                }
            } catch (err) {
                alert("PDF Scan failed.");
            } finally {
                setLoadingState(pdfBtn, false);
            }
        });
    }

    // --- Image Scan ---
    const imgBtn = document.getElementById('btn-image-scan');
    const imgInput = document.getElementById('imageFileInput');
    const fileNameDisplay = document.getElementById('imageFileNameDisplay');
    const previewWrapper = document.getElementById('imagePreviewWrapper');
    const previewImg = document.getElementById('imagePreview');
    const dropZonePrompt = document.getElementById('dropZonePrompt');
    const btnClearImage = document.getElementById('btn-clear-image');

    if (imgInput) {
        imgInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                // Update filename display
                if (fileNameDisplay) {
                    fileNameDisplay.querySelector('span').textContent = file.name;
                    fileNameDisplay.style.display = 'block';
                }

                // Render Preview
                const reader = new FileReader();
                reader.onload = (event) => {
                    if (previewImg && previewWrapper && dropZonePrompt) {
                        previewImg.src = event.target.result;
                        previewWrapper.style.display = 'block';
                        dropZonePrompt.style.display = 'none';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (btnClearImage) {
        btnClearImage.addEventListener('click', (e) => {
            e.stopPropagation(); // Don't trigger the file input click
            if (imgInput) imgInput.value = '';
            if (previewImg) previewImg.src = '';
            if (previewWrapper) previewWrapper.style.display = 'none';
            if (dropZonePrompt) dropZonePrompt.style.display = 'block';
            if (fileNameDisplay) fileNameDisplay.style.display = 'none';
        });
    }

    if (imgBtn && imgInput) {
        imgBtn.addEventListener('click', async () => {
            if (!window.api.auth.isLoggedIn()) {
                showAuthPrompt("OCR image analysis is reserved for registered users. Log in to analyze screenshots.");
                return;
            }

            const file = imgInput.files[0];
            if (!file) return alert("Please select an image first.");

            setLoadingState(imgBtn, true, "Analyzing Image...");
            const formData = new FormData();
            formData.append('file', file);

            try {
                const result = await window.api.detection.analyzeImage(formData);
                renderScanResult(result, resultContainer);
            } catch (err) {
                alert("Image Scan failed.");
            } finally {
                setLoadingState(imgBtn, false);
            }
        });
    }

    // --- Scam Report ---
    const reportForm = document.getElementById('scamReportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('btn-submit-report');
            const successEl = document.getElementById('report-success');
            
            const formData = new FormData(reportForm);
            setLoadingState(submitBtn, true, "Submitting Report...");
            
            try {
                const baseUrl = window.api && window.api.base_url ? window.api.base_url : 'http://localhost:8000/api/v1';
                const response = await fetch(`${baseUrl}/report/reports`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (response.ok) {
                    reportForm.style.display = 'none';
                    successEl.style.display = 'block';
                    successEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    alert("Submission failed: " + (data.detail || "Unknown error"));
                }
            } catch (err) {
                alert("Failed to connect to the reporting server.");
            } finally {
                setLoadingState(submitBtn, false);
            }
        });
    }
});
