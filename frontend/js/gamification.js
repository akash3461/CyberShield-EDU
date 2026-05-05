/**
 * CyberShield Gamification Engine
 * Handles user experience points (XP), levels, and badges.
 */

const GAMIF_CONFIG = {
    xpPerScan: 10,
    xpPerScamReport: 50,
    xpPerQuizCorrect: 15,
    levels: [
        { level: 1, minXp: 0, title: "Cyber Initiate" },
        { level: 2, minXp: 100, title: "Shield Bearer" },
        { level: 3, minXp: 300, title: "Data Guardian" },
        { level: 4, minXp: 600, title: "Sentinel Prime" },
        { level: 5, minXp: 1000, title: "Security Legend" }
    ]
};

const Gamification = {
    state: {
        xp: 0,
        level: 1,
        rank: "Cyber Scout",
        badges: [],
        completedModules: [],
        next_level_xp: 100,
        progress_percent: 0
    },

    async init() {
        const isLoggedIn = window.api && window.api.auth && window.api.auth.isLoggedIn();
        if (!isLoggedIn) {
            console.log("Gamification initializing in Guest Mode");
            document.querySelectorAll('[data-gamif]').forEach(el => el.style.display = 'none');
            return;
        }
        await this.syncWithBackend();
        this.updateUI();
        this.setupAcademyClick();
        console.log("Cyber-Academy initialized:", this.state);
    },

    setupAcademyClick() {
        const badgeLogo = document.getElementById('academy-badge-logo');
        if (badgeLogo) {
            badgeLogo.style.cursor = 'pointer';
            badgeLogo.addEventListener('click', () => {
                console.log("Academy Badge Clicked! Celebrating...");
                this.celebrate();
            });
        }
    },

    async syncWithBackend() {
        try {
            const profile = await window.api.gamification.getProfile();
            
            // Persist notification state in localStorage to prevent repeat toasts on page navigation
            const storedLevel = localStorage.getItem('cyberShield_lastLevel');
            const storedBadgeCount = localStorage.getItem('cyberShield_lastBadgeCount');
            
            // Initialization: If first time, don't show toast for current progress
            const lastLevel = storedLevel !== null ? parseInt(storedLevel) : profile.level;
            const lastBadgeCount = storedBadgeCount !== null ? parseInt(storedBadgeCount) : (profile.badges ? profile.badges.length : 0);

            this.state = {
                xp: profile.xp,
                level: profile.level,
                rank: profile.rank,
                badges: profile.badges,
                completedModules: JSON.parse(localStorage.getItem('cyberShield_completedModules') || '[]'),
                next_level_xp: profile.next_level_xp,
                progress_percent: profile.progress_percent
            };

            // Trigger celebrations only for new achievements
            if (this.state.level > lastLevel) {
                this.showToast(`LEVEL UP! You are now a ${this.state.rank}`, "level-up");
                this.celebrate();
            } else if (this.state.badges.length > lastBadgeCount) {
                const newBadge = this.state.badges[this.state.badges.length - 1];
                this.showToast(`NEW BADGE: ${newBadge} Unlocked!`, "badge");
                this.celebrate();
            }

            // Sync localStorage for next view
            localStorage.setItem('cyberShield_lastLevel', this.state.level);
            localStorage.setItem('cyberShield_lastBadgeCount', this.state.badges.length);

            this.updateUI();
        } catch (error) {
            console.error("Academy Sync Failed:", error);
        }
    },

    async addXp(amount, reason = "Activity completed") {
        try {
            // Persist the educational reward to the backend database
            if (window.api && window.api.awareness && window.api.awareness.reward) {
                await window.api.awareness.reward(amount, reason);
            }
        } catch (error) {
            console.error("Academy Persistence Failed:", error);
        }
        
        // Sync the local state with the newly updated backend profile
        await this.syncWithBackend();
        this.showToast(`+${amount} XP: ${reason}`, "xp");
    },

    async completeModule(moduleId) {
        let completed = JSON.parse(localStorage.getItem('cyberShield_completedModules') || '[]');
        if (!completed.includes(moduleId)) {
            completed.push(moduleId);
            localStorage.setItem('cyberShield_completedModules', JSON.stringify(completed));
            this.state.completedModules = completed;
            await this.addXp(30, "Knowledge Module Mastered");
            this.celebrate();
        }
    },

    updateUI() {
        const xpElements = document.querySelectorAll('[data-gamif="xp"]');
        const levelElements = document.querySelectorAll('[data-gamif="level"]');
        const titleElements = document.querySelectorAll('[data-gamif="title"]');
        const progressElements = document.querySelectorAll('[data-gamif="progress"]');
        const badgeGrid = document.getElementById('academy-badges');

        xpElements.forEach(el => el.textContent = this.state.xp);
        levelElements.forEach(el => el.textContent = this.state.level);
        titleElements.forEach(el => el.textContent = this.state.rank);

        if (progressElements.length > 0) {
            progressElements.forEach(el => {
                el.style.width = `${this.state.progress_percent}%`;
            });
        }

        if (badgeGrid) {
            this.renderBadgeGrid(badgeGrid);
        }

        // Dedicated Academy Hub Elements
        const xpToNextEl = document.getElementById('xp-to-next');
        const badgeTotalEl = document.getElementById('badge-total');

        if (xpToNextEl) {
            xpToNextEl.textContent = this.state.next_level_xp - this.state.xp || 0;
        }
        if (badgeTotalEl) {
            badgeTotalEl.textContent = `${this.state.badges.length} Badges Earned`;
        }
    },

    renderBadgeGrid(container) {
        const badgeIcons = {
            "First Response": "🛡️",
            "Phishing Hunter": "🎣",
            "Deep-Fake Detective": "📸",
            "Forensic Analyst": "📄",
            "Shield of Trust": "🛡️✨"
        };

        if (!this.state.badges || this.state.badges.length === 0) {
            container.innerHTML = '<p style="font-size: 0.7rem; color: var(--text-muted); font-style: italic;">No badges earned yet. Start scanning to build your dossier!</p>';
            return;
        }

        container.innerHTML = this.state.badges.map(badge => `
            <div class="academy-badge-item" title="${badge}" style="background: var(--primary-glow); padding: 8px; border-radius: 8px; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; position: relative; border: 1px solid var(--primary); backdrop-filter: blur(4px);">
                ${badgeIcons[badge] || '🏅'}
                <div style="position: absolute; bottom: -4px; right: -4px; background: var(--success); width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--bg-card); box-shadow: 0 0 5px var(--success);"></div>
            </div>
        `).join('');
    },

    showToast(message, type = "default") {
        const container = document.getElementById('toast-container') || this.createToastContainer();
        const toast = document.createElement('div');
        toast.className = `gamif-toast ${type}`;
        
        let icon = '✨';
        if (type === 'level-up') icon = '🏆';
        if (type === 'xp') icon = '⚡';

        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">${message}</div>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
        return container;
    },

    celebrate() {
        const container = document.createElement('div');
        container.className = 'confetti-container';
        document.body.appendChild(container);

        // Get brand colors from CSS variables
        const primary = getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() || '#6366f1';
        const secondary = getComputedStyle(document.documentElement).getPropertyValue('--secondary').trim() || '#a855f7';
        const success = getComputedStyle(document.documentElement).getPropertyValue('--success').trim() || '#10b981';
        const gold = getComputedStyle(document.documentElement).getPropertyValue('--warning').trim() || '#f59e0b';
        const colors = [primary, secondary, success, gold];
        
        for (let i = 0; i < 50; i++) {
            const piece = document.createElement('div');
            piece.className = 'confetti-piece';
            piece.style.left = Math.random() * 100 + 'vw';
            piece.style.animationDelay = Math.random() * 2 + 's';
            piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            container.appendChild(piece);
        }

        setTimeout(() => {
            container.classList.add('fade-out');
            setTimeout(() => container.remove(), 1000);
        }, 5000);
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => Gamification.init());

// Export globally
window.Gamification = Gamification;
