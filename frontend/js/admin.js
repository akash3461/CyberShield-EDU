// admin.js - Advanced Dashboard Logic

document.addEventListener('DOMContentLoaded', () => {
    initPasswordGate();
    initSidebar();
    initCharts();
    loadDashboardData();
    initAIControl();
});

// --- Authentication / Password Gate ---
function initPasswordGate() {
    const gate = document.getElementById('password-gate');
    const interface = document.getElementById('admin-interface');
    const loginBtn = document.getElementById('btn-admin-login');
    const passwordInput = document.getElementById('adminPasswordInput');
    const errorMsg = document.getElementById('gate-error');

    // Check if already authenticated
    if (localStorage.getItem('admin_authenticated') === 'true') {
        gate.style.display = 'none';
        interface.style.display = 'flex';
    }

    loginBtn?.addEventListener('click', () => {
        if (passwordInput.value === 'admin123') { // Simple mock password
            localStorage.setItem('admin_authenticated', 'true');
            gate.style.display = 'none';
            interface.style.display = 'flex';
        } else {
            errorMsg.style.display = 'block';
            passwordInput.classList.add('shake');
            setTimeout(() => passwordInput.classList.remove('shake'), 400);
        }
    });

    passwordInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginBtn.click();
    });

    document.getElementById('btn-logout')?.addEventListener('click', () => {
        localStorage.removeItem('admin_authenticated');
        location.reload();
    });
}

// --- Sidebar Navigation ---
function initSidebar() {
    const links = document.querySelectorAll('.sidebar-link[data-tab]');
    const sections = document.querySelectorAll('.admin-section');
    const title = document.getElementById('section-title');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = link.dataset.tab;

            // Update Sidebar
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Update Sections
            sections.forEach(s => s.classList.remove('active'));
            const activeSection = document.getElementById(targetTab);
            if (activeSection) activeSection.classList.add('active');

            // Update Header Title
            title.textContent = link.textContent.trim();
        });
    });
}

// --- Charts (Chart.js) ---
let trendsChart, categoryChart;

function initCharts() {
    const ctxTrends = document.getElementById('trendsChart')?.getContext('2d');
    const ctxCategory = document.getElementById('categoryChart')?.getContext('2d');

    if (ctxTrends) {
        trendsChart = new Chart(ctxTrends, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Threats Detected',
                    data: [12, 19, 15, 25, 22, 30, 24],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    if (ctxCategory) {
        categoryChart = new Chart(ctxCategory, {
            type: 'doughnut',
            data: {
                labels: ['Text', 'URL', 'PDF', 'Image'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#6366f1', '#4ade80', '#f59e0b', '#f87171'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } },
                cutout: '70%'
            }
        });
    }
}

// --- Data Loading ---
async function loadDashboardData() {
    try {
        const stats = await window.api.admin.getStats();
        updateStatsUI(stats);
        updateCharts(stats);
    } catch (err) {
        console.error("Failed to load dashboard stats:", err);
    }
    loadScanLogs();
    // loadUserTable(); // Keep mock for now or implement if backend supports
}

function updateStatsUI(stats) {
    document.getElementById('stat-total-scans').textContent = stats.total_scans.toLocaleString();
    document.getElementById('stat-scams-detected').textContent = stats.scams_detected.toLocaleString();
    // Assuming active users is not in stats yet, we could mock or add to backend
}

function updateCharts(stats) {
    if (trendsChart && stats.trends) {
        trendsChart.data.labels = stats.trends.map(t => t.date);
        trendsChart.data.datasets[0].data = stats.trends.map(t => t.count);
        trendsChart.update();
    }
    
    if (categoryChart && stats.distribution) {
        const labels = Object.keys(stats.distribution);
        const data = Object.values(stats.distribution);
        categoryChart.data.labels = labels;
        categoryChart.data.datasets[0].data = data;
        categoryChart.update();
    }
}

function loadScanLogs() {
    const tableBody = document.querySelector('#scan-table tbody');
    if (!tableBody) return;

    const mockLogs = [
        { time: '10:45 AM', type: 'Text', preview: 'Verify your account details...', result: 'Scam', confidence: '98%', status: 'scam' },
        { time: '10:30 AM', type: 'URL', preview: 'http://secure-bank-login.ml', result: 'Scam', confidence: '85%', status: 'scam' },
        { time: '09:12 AM', type: 'PDF', preview: 'invoice_2024.pdf', result: 'Safe', confidence: '99%', status: 'safe' },
        { time: 'Yesterday', type: 'Image', preview: 'qr_code_whatsapp.png', result: 'Scam', confidence: '92%', status: 'scam' },
        { time: 'Yesterday', type: 'Text', preview: 'Hello mom, I lost my phone...', result: 'Scam', confidence: '76%', status: 'scam' },
    ];

    tableBody.innerHTML = mockLogs.map(log => `
        <tr>
            <td>${log.time}</td>
            <td><span class="badge">${log.type}</span></td>
            <td style="font-family: monospace; color: var(--text-muted);">${log.preview}</td>
            <td><span class="status-pill ${log.status}">${log.result}</span></td>
            <td>${log.confidence}</td>
            <td><button class="btn-ghost" style="padding: 4px 8px;">Details</button></td>
        </tr>
    `).join('');
}

function loadUserTable() {
    const tableBody = document.querySelector('#user-list tbody');
    if (!tableBody) return;

    const mockUsers = [
        { name: 'Admin User', email: 'admin@cybershield.edu', role: 'Super Admin', joined: 'Jan 2024', status: 'Online', count: 142 },
        { name: 'Sarah Chen', email: 'sarah.c@edu.pk', role: 'Auditor', joined: 'Feb 2024', status: 'Idle', count: 86 },
        { name: 'John Doe', email: 'j.doe@example.com', role: 'User', joined: 'Mar 2024', status: 'Offline', count: 12 },
    ];

    tableBody.innerHTML = mockUsers.map(user => `
        <tr>
            <td><div style="font-weight:600">${user.name}</div></td>
            <td style="color: var(--text-muted)">${user.email}</td>
            <td><span class="badge">${user.role}</span></td>
            <td>${user.joined}</td>
            <td><span class="status-pill ${user.status === 'Online' ? 'safe' : 'pending'}">${user.status}</span></td>
            <td>${user.count}</td>
        </tr>
    `).join('');
}

// --- AI Control ---
async function initAIControl() {
    const grid = document.getElementById('keywordGrid');
    const form = document.getElementById('addKeywordForm');
    const input = document.getElementById('newKeywordInput');

    if (!grid) return;

    const loadKeywords = async () => {
        try {
            const data = await window.api.admin.getKeywords();
            renderKeywords(data.keywords);
        } catch (err) {
            console.error("Failed to load keywords:", err);
        }
    };

    const renderKeywords = (keywords) => {
        grid.innerHTML = keywords.map(kw => `
            <div class="keyword-chip">
                <span>${kw}</span>
                <span class="remove-keyword" onclick="window.removeKeyword('${kw}')">&times;</span>
            </div>
        `).join('');
    };

    window.removeKeyword = async (kw) => {
        // Backend currently doesn't have a DELETE keyword endpoint in admin.py
        // We might want to add it or just inform the user.
        // For now, let's just alert.
        alert("Removing keywords is not yet implemented on the backend.");
    };

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const val = input.value.trim().toLowerCase();
        if (val) {
            try {
                await window.api.admin.addKeyword(val);
                input.value = '';
                await loadKeywords();
            } catch (err) {
                alert("Failed to add keyword.");
            }
        }
    });

    await loadKeywords();
}
