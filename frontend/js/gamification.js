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
        badges: [],
        completedModules: []
    },

    init() {
        const isLoggedIn = window.api && window.api.auth && window.api.auth.isLoggedIn();
        if (!isLoggedIn) {
            console.log("Gamification initializing in Guest Mode");
            // Only hide the standalone legacy badge if it exists
            document.querySelectorAll('.user-stats-badge').forEach(el => el.style.display = 'none');
            return;
        }
        this.loadState();
        this.updateUI();
        console.log("Gamification initialized:", this.state);
    },

    loadState() {
        const saved = localStorage.getItem('cs_gamification');
        if (saved) {
            this.state = JSON.parse(saved);
        }
    },

    saveState() {
        localStorage.setItem('cs_gamification', JSON.stringify(this.state));
        this.updateUI();
    },

    addXp(amount, reason = "Activity completed") {
        this.state.xp += amount;
        this.checkLevelUp();
        this.saveState();
        this.showToast(`+${amount} XP: ${reason}`, "xp");
    },

    checkLevelUp() {
        const currentLevel = this.state.level;
        const newLevel = GAMIF_CONFIG.levels.reduce((prev, curr) => {
            return this.state.xp >= curr.minXp ? curr : prev;
        }, GAMIF_CONFIG.levels[0]);

        if (newLevel.level > currentLevel) {
            this.state.level = newLevel.level;
            this.showToast(`LEVEL UP! You are now a ${newLevel.title}`, "level-up");
        }
    },

    getCurrentLevelInfo() {
        return GAMIF_CONFIG.levels.find(l => l.level === this.state.level);
    },

    getNextLevelInfo() {
        return GAMIF_CONFIG.levels.find(l => l.level === this.state.level + 1) || null;
    },

    completeModule(moduleId) {
        if (!this.state.completedModules.includes(moduleId)) {
            this.state.completedModules.push(moduleId);
            this.addXp(30, "Education Module Mastery");
            this.saveState();
            this.checkLearningPathCompletion();
        }
    },

    checkLearningPathCompletion() {
        const paths = {
            'phishing-101': [1, 2, 3],
            'financial-fraud': [4, 5]
        };

        for (const [pathId, moduleIds] of Object.entries(paths)) {
            const isDone = moduleIds.every(id => this.state.completedModules.includes(id));
            if (isDone && !this.state.badges.includes(pathId)) {
                this.addBadge(pathId, `Certified in ${pathId}`);
                this.addXp(100, `Path Mastery: ${pathId}`);
            }
        }
    },

    updateUI() {
        // Update all elements with [data-gamif]
        const xpElements = document.querySelectorAll('[data-gamif="xp"]');
        const levelElements = document.querySelectorAll('[data-gamif="level"]');
        const titleElements = document.querySelectorAll('[data-gamif="title"]');
        const progressElements = document.querySelectorAll('[data-gamif="progress"]');

        const levelInfo = this.getCurrentLevelInfo();
        const nextLevel = this.getNextLevelInfo();

        xpElements.forEach(el => {
            el.textContent = this.state.xp;
            el.style.display = ''; 
        });
        levelElements.forEach(el => {
            el.textContent = this.state.level;
            el.style.display = '';
        });
        titleElements.forEach(el => {
            el.textContent = levelInfo.title;
            el.style.display = '';
        });

        if (progressElements.length > 0 && nextLevel) {
            const currentLevelXp = levelInfo.minXp;
            const neededXp = nextLevel.minXp - currentLevelXp;
            const progressXp = this.state.xp - currentLevelXp;
            const percent = Math.min(100, (progressXp / neededXp) * 100);
            
            progressElements.forEach(el => {
                el.style.width = `${percent}%`;
                el.style.display = '';
            });
        }
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

        // Animation
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
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => Gamification.init());

// Export globally
window.Gamification = Gamification;
