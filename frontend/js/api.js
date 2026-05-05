// api.js - Vanilla JS wrapper for FastAPI backend

const API_BASE_URL = 'http://localhost:8000/api/v1';
const ROOT_API_URL = 'http://localhost:8000';

/**
 * Helper to get the auth token from localStorage.
 */
const getAuthToken = () => localStorage.getItem('access_token');

/**
 * Helper to create headers with Auth token if available.
 */
const getHeaders = (contentType = 'application/json') => {
    const headers = {};
    if (contentType) headers['Content-Type'] = contentType;
    const token = getAuthToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
};

const authApi = {
    async login(username, password) {
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    async register(username, email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }
            return await response.json();
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },

    isLoggedIn() {
        return !!getAuthToken();
    },

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    async getMe() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch user profile');
            const user = await response.json();
            localStorage.setItem('user', JSON.stringify(user));
            return user;
        } catch (error) {
            console.error('getMe error:', error);
            throw error;
        }
    }
};

const detectionApi = {
    async analyzeText(text) {
        try {
            const response = await fetch(`${API_BASE_URL}/detect/text`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ text }),
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Text analysis failed:', error);
            throw error;
        }
    },

    async analyzeUrl(url) {
        try {
            const response = await fetch(`${API_BASE_URL}/detect/url`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ url }),
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('URL analysis failed:', error);
            throw error;
        }
    },

    async analyzePdf(formData) {
        try {
            const response = await fetch(`${API_BASE_URL}/detect/pdf`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${getAuthToken()}` },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('PDF analysis failed:', error);
            throw error;
        }
    },

    async analyzeImage(formData) {
        try {
            const response = await fetch(`${API_BASE_URL}/detect/image`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${getAuthToken()}` },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Image analysis failed:', error);
            throw error;
        }
    },


    async getHistory() {
        try {
            const response = await fetch(`${API_BASE_URL}/detect/history`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch scan history:', error);
            throw error;
        }
    }
};

const tasksApi = {
    async getStatus(taskId) {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/status/${taskId}`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Task status fetch failed:', error);
            throw error;
        }
    },

    /**
     * Poll until a task is finished.
     */
    async pollUntilFinished(taskId, interval = 2000) {
        return new Promise((resolve, reject) => {
            const poll = async () => {
                try {
                    const status = await this.getStatus(taskId);
                    if (status.status === 'SUCCESS') {
                        resolve(status.result);
                    } else if (status.status === 'FAILURE') {
                        reject(new Error(status.error || 'Task failed'));
                    } else {
                        setTimeout(poll, interval);
                    }
                } catch (error) {
                    reject(error);
                }
            };
            poll();
        });
    }
};

const awarenessApi = {
    async getContent() {
        try {
            const response = await fetch(`${ROOT_API_URL}/awareness`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch education content:', error);
            throw error;
        }
    },

    async reward(xp_amount, reason) {
        try {
            const response = await fetch(`${API_BASE_URL}/awareness/reward`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ xp_amount, reason })
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to persist educational reward:', error);
            throw error;
        }
    }
};

const adminApi = {
    async getStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/system/stats`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch stats');
            return await response.json();
        } catch (error) {
            console.error('getStats error:', error);
            throw error;
        }
    },
    async getThresholds() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/config/thresholds`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch thresholds');
            return await response.json();
        } catch (error) {
            console.error('getThresholds error:', error);
            throw error;
        }
    },
    async updateThresholds(low, high) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/config/thresholds`, {
                method: 'PUT',
                headers: getHeaders(),
                body: JSON.stringify({ low, high })
            });
            if (!response.ok) throw new Error('Failed to update thresholds');
            return await response.json();
        } catch (error) {
            console.error('updateThresholds error:', error);
            throw error;
        }
    },
    async getLogs() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/logs`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch logs');
            return await response.json();
        } catch (error) {
            console.error('getLogs error:', error);
            throw error;
        }
    },
    async getUsers() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/users`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch users');
            return await response.json();
        } catch (error) {
            console.error('getUsers error:', error);
            throw error;
        }
    },
    async getKeywords() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/keywords`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch admin keywords:', error);
            throw error;
        }
    },
    async addKeyword(keyword) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/keywords`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ keyword }),
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to add admin keyword:', error);
            throw error;
        }
    }
};

const quizApi = {
    async getQuestions(limit = 5) {
        try {
            const response = await fetch(`${API_BASE_URL}/awareness/questions?limit=${limit}`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch quiz questions:', error);
            throw error;
        }
    },

    async submit() {
        try {
            const response = await fetch(`${API_BASE_URL}/awareness/submit`, {
                method: 'POST',
                headers: getHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to submit quiz:', error);
            throw error;
        }
    }
};

const gamificationApi = {
    async getProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/gamification/profile`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch gamification profile:', error);
            throw error;
        }
    }
};

// Export to global scope
window.api = {
    auth: authApi,
    detection: detectionApi,
    tasks: tasksApi,
    awareness: awarenessApi,
    quiz: quizApi,
    admin: adminApi,
    gamification: gamificationApi
};
