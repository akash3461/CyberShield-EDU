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
            console.log("User data missing from localStorage, fetching from API...");
            user = await window.api.auth.getMe();
        } catch (error) {
            console.error("Failed to recover user data:", error);
        }
    }

    console.log("Header Update - LoggedIn:", isLoggedIn, "User:", user);

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

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Shared animations
    if (typeof initAnimations === 'function') initAnimations();
    
    // Auth UI Update
    window.updateHeaderAuthUI();
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
    const restrictedTabs = ['url-tab', 'pdf-tab', 'image-tab', 'audio-tab', 'report-tab'];
    
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

// --- Results Rendering (Premium) ---
// --- Results Rendering (Premium) ---
function renderScanResult(result, container) {
    if (!container) return;
    
    const isScam = result.prediction === 'scam';
    const confidence = result.confidence; // decimal 0-1
    const reasoning = result.reasoning || ["Pattern analysis complete.", "Linguistic validation successful."];
    
    // Generate detailed insights with indicators
    const insights = reasoning.map(r => {
        const isAlert = r.includes('ALERT') || r.includes('CRITICAL') || r.includes('Detected');
        const icon = isAlert 
            ? '<svg viewBox="0 0 24 24" fill="currentColor" style="width:1.25rem;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>'
            : '<svg viewBox="0 0 24 24" fill="currentColor" style="width:1.25rem;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
        
        return `
            <div class="insight-item" style="display: flex; gap: 12px; font-size: 0.95rem; color: var(--text-muted); padding: 12px; background: ${isAlert ? 'rgba(239, 68, 68, 0.05)' : 'rgba(34, 197, 94, 0.05)'}; border-radius: 12px; border: 1px solid ${isAlert ? 'rgba(239, 68, 68, 0.1)' : 'var(--glass-border)'}; margin-bottom: 10px; align-items: start;">
                <div style="color: ${isAlert ? 'var(--danger)' : 'var(--success)'}; flex-shrink: 0; margin-top: 2px;">${icon}</div>
                <div style="line-height: 1.4;">${r}</div>
            </div>
        `;
    }).join('');

    // Heuristic Language Detection for UI flair
    let detectedLang = "English";
    const nonLatinPattern = /[^\u0000-\u007F]+/;
    if (nonLatinPattern.test(result.extracted_text_preview || "")) detectedLang = "Multilingual (Detecting...)";

    container.innerHTML = `
        <div class="glass-card animateOnScroll animated" style="padding: 2.5rem; border-color: ${isScam ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)'}; background: var(--bg-card);">
                <div class="result-header" style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;">
                    <div>
                        <div class="status-indicator" style="display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 0.8rem; letter-spacing: 0.1em; color: ${isScam ? 'var(--danger)' : 'var(--success)'}; margin-bottom: 5px;">
                            <div class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: currentColor; box-shadow: 0 0 10px currentColor;"></div>
                            <span>${isScam ? 'SOPHISTICATED THREAT' : 'SECURE SCAN'}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Detected Language: <span style="color: var(--primary);">${detectedLang}</span></div>
                    </div>
                    <div class="confidence-badge" style="background: var(--primary-glow); padding: 4px 12px; border-radius: 2rem; font-size: 0.8rem; font-weight: 700; color: var(--primary);">
                        ${(confidence * 100).toFixed(1)}% Match
                    </div>
                </div>

            <div class="result-body">
                <h3 style="font-size: 1.75rem; color: var(--text-main); margin-bottom: 0.5rem;">
                    ${isScam ? 'Flagged as Fraudulent' : 'Safety Verified'}
                </h3>
                <p style="color: var(--text-muted); margin-bottom: 2rem; line-height: 1.6;">
                    ${result.recommendation || (isScam ? "AI analysis identified critical risk factors." : "Linguistic patterns suggest this content is legitimate.")}
                </p>
                
                <div class="confidence-meter-container" style="margin-bottom: 2.5rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: var(--text-main); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span>AI Detection Score</span>
                        </div>
                        <span>${(confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div style="height: 8px; background: rgba(0,0,0,0.05); border-radius: 10px; overflow: hidden;">
                        <div class="meter-fill" style="height: 100%; width: 0%; background: ${isScam ? 'var(--danger)' : 'var(--success)'}; transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1);"></div>
                    </div>
                </div>

                <div class="indicators-container">
                    <div style="font-size: 0.75rem; font-weight: 800; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 1rem; text-transform: uppercase;">Suspicious Indicators</div>
                    <div class="insights-list">${insights}</div>
                </div>

                ${result.source === 'ocr_scan' ? `
                    <div style="margin-top: 2rem; padding: 1rem; background: rgba(0,0,0,0.02); border-left: 3px solid var(--primary); border-radius: 8px;">
                        <span style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase;">Extracted Text from Image</span>
                        <p style="font-size: 0.85rem; color: var(--text-main); margin-top: 5px; font-style: italic;">"${result.extracted_text_preview}"</p>
                    </div>
                ` : ''}

                ${result.source === 'audio_vishing_scan' ? `
                    <div style="margin-top: 2rem; padding: 1rem; background: rgba(0,0,0,0.02); border-left: 3px solid var(--secondary); border-radius: 8px;">
                        <span style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase;">Voice Transcription</span>
                        <p style="font-size: 0.85rem; color: var(--text-main); margin-top: 5px; font-style: italic;">"${result.transcription}"</p>
                    </div>
                ` : ''}
            </div>

            <div class="result-footer" style="margin-top: 2.5rem; display: flex; gap: 15px;">
                <button class="btn btn-ghost" onclick="location.reload()" style="flex: 1;">
                    New Audit
                </button>
                ${isScam ? `
                    <button class="btn btn-primary" onclick="switchTab('report-tab')" style="flex: 1; background: var(--danger); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); border: none;">
                        Report Phish
                    </button>
                ` : ''}
            </div>
        </div>
    `;

    // Initialize Meter Animation
    setTimeout(() => {
        const fill = container.querySelector('.meter-fill');
        if (fill) fill.style.width = `${confidence * 100}%`;
    }, 100);

    container.style.display = 'block';
    container.classList.add('show');
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Award Gamification Points
    if (window.Gamification) {
        window.Gamification.addXp(10, "Security Audit Completed");
    }
}

// --- Interactive Features (Tips, Ticker, Modals) ---
const QUICK_TIPS = [
    "Always check the sender's email address for slight misspellings.",
    "Be wary of 'urgent' requests for money or personal information.",
    "Real companies won't ask for your password via email or SMS.",
    "If an internship offer sounds too good to be true, it probably is.",
    "Check for HTTPS and lock icons, but remember scammers use them too.",
    "Don't click links in suspicious messages; go to the official site instead."
];

function initQuickTips() {
    const tipEl = document.getElementById('quickTipText');
    if (!tipEl) return;
    
    let currentTip = 0;
    setInterval(() => {
        tipEl.style.opacity = 0;
        setTimeout(() => {
            currentTip = (currentTip + 1) % QUICK_TIPS.length;
            tipEl.textContent = QUICK_TIPS[currentTip];
            tipEl.style.opacity = 1;
        }, 500);
    }, 8000);
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
    initAnimations();
    initQuickTips();
    initScamTicker();
    initModals();
    
    // --- Guest UI Initialization ---
    function initGuestUI() {
        if (!window.api || !window.api.auth) return;
        
        const isLoggedIn = window.api.auth.isLoggedIn();
        const indicator = document.getElementById('guest-indicator');
        const locks = document.querySelectorAll('.lock-icon');
        
        if (!isLoggedIn) {
            if (indicator) {
                const count = parseInt(localStorage.getItem('cs_guest_scans') || '0');
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
    
    initGuestUI();

    // --- Audio Page Guard ---
    if (window.location.pathname.includes('audio-scan.html')) {
        const isLoggedIn = window.api && window.api.auth && window.api.auth.isLoggedIn();
        if (!isLoggedIn) {
            showAuthPrompt("Audio vishing detection is a premium security feature. Please log in to continue.");
        }
    }
    
    // --- Guest Mode Logic ---
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
                    incrementGuestScanCount();
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
    const pdfInput = document.getElementById('pdfInput');
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
    const imgInput = document.getElementById('imageInput');
    if (imgBtn && imgInput) {
        imgBtn.addEventListener('click', async () => {
            if (!window.api.auth.isLoggedIn()) {
                showAuthPrompt("OCR image analysis is reserved for registered users. Log in to analyze screenshots.");
                return;
            }

            const file = imgInput.files[0];
            if (!file) return alert("Please select an image.");

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

    // --- Audio (Vishing) Scan ---
    const audioBtn = document.getElementById('btn-audio-scan');
    const audioInput = document.getElementById('audioInput');
    if (audioBtn && audioInput) {
        audioBtn.addEventListener('click', async () => {
            if (!window.api.auth.isLoggedIn()) {
                showAuthPrompt("Audio vishing detection is a premium security feature. Log in to analyze voice notes.");
                return;
            }

            const file = audioInput.files[0];
            if (!file) return alert("Please select an audio file.");

            setLoadingState(audioBtn, true, "Analyzing Audio...");
            const formData = new FormData();
            formData.append('file', file);

            try {
                const result = await window.api.detection.analyzeAudio(formData);
                renderScanResult(result, resultContainer);
            } catch (err) {
                alert("Audio Analysis failed.");
            } finally {
                setLoadingState(audioBtn, false);
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
                // Using a relative path which will work if the JS is served from the same origin as API
                // or window.api.base_url if defined in api.js
                const baseUrl = window.api && window.api.base_url ? window.api.base_url : 'http://localhost:8000/api/v1';
                const response = await fetch(`${baseUrl}/report/reports`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    reportForm.style.display = 'none';
                    successEl.style.display = 'block';
                    // Scroll to success message
                    successEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    alert("Submission failed: " + (data.detail || "Unknown error"));
                }
            } catch (err) {
                console.error("Report submission failed:", err);
                alert("Failed to connect to the reporting server.");
            } finally {
                setLoadingState(submitBtn, false);
            }
        });
    }
});
