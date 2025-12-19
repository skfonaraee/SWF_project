const API_BASE = 'http://localhost:8000/api';


// Получить заголовки с токеном
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

// Обертка для fetch с обработкой ошибок авторизации
async function fetchWithAuth(url, options = {}) {
    const headers = getAuthHeaders();
    
    const response = await fetch(url, {
        ...options,
        headers: {
            ...headers,
            ...options.headers,
        },
    });
    
    // Если токен истек, пробуем обновить
    if (response.status === 401) {
        // Попробовать обновить токен
        const refreshed = await refreshToken();
        if (refreshed) {
            // Повторить запрос с новым токеном
            const newHeaders = getAuthHeaders();
            return fetch(url, {
                ...options,
                headers: {
                    ...newHeaders,
                    ...options.headers,
                },
            });
        } else {
            // Если не удалось обновить токен - разлогинить
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            window.location.href = '../login.html';
            throw new Error('Session expired');
        }
    }
    
    return response;
}

// Получить список программ
async function fetchPrograms(filters = {}) {
    try {
        const params = new URLSearchParams(filters).toString();
        const response = await fetchWithAuth(`${API_BASE}/programs/?${params}`);
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error fetching programs:', response.status);
            return [];
        }
    } catch (error) {
        console.error('Fetch programs error:', error);
        return [];
    }
}

// ... остальные функции остаются такими же, но используем fetchWithAuth вместо fetch ...

// API для дашбордов
const dashboardAPI = {
    // Статистика для админа
    getAdminStats: async () => {
        try {
            const response = await fetchWithAuth(`${API_BASE}/admin/stats/`);
            return response.ok ? await response.json() : null;
        } catch (error) {
            console.error('Error fetching admin stats:', error);
            return null;
        }
    },
    
    // Пользователи для админа
    getUsers: async () => {
        const response = await fetch(`${API_BASE}/admin/users/`, {
            headers: getAuthHeaders(),
        });
        return response.ok ? await response.json() : [];
    },
    
    // Избранные программы
    getFavorites: async () => {
        const response = await fetch(`${API_BASE}/favorites/`, {
            headers: getAuthHeaders(),
        });
        return response.ok ? await response.json() : [];
    },
    
    // Заявки студента
    getApplications: async () => {
        const response = await fetch(`${API_BASE}/applications/`, {
            headers: getAuthHeaders(),
        });
        return response.ok ? await response.json() : [];
    },
    
    // История AI
    getAIHistory: async () => {
        const response = await fetch(`${API_BASE}/ai/history/`, {
            headers: getAuthHeaders(),
        });
        return response.ok ? await response.json() : [];
    },
    
    // Обновить профиль
    updateProfile: async (profileData) => {
        const response = await fetch(`${API_BASE}/users/profile/`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(profileData),
        });
        return response.ok ? await response.json() : null;
    },
};


// Получить список программ
async function fetchPrograms(filters = {}) {
    try {
        const params = new URLSearchParams(filters).toString();
        const response = await fetch(`${API_BASE}/programs/?${params}`, {
            headers: getAuthHeaders(),
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error fetching programs:', response.status);
            return [];
        }
    } catch (error) {
        console.error('Fetch programs error:', error);
        return [];
    }
}

// Получить список университетов
async function fetchUniversities(filters = {}) {
    try {
        const params = new URLSearchParams(filters).toString();
        const response = await fetch(`${API_BASE}/universities/?${params}`, {
            headers: getAuthHeaders(),
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error fetching universities:', response.status);
            return [];
        }
    } catch (error) {
        console.error('Fetch universities error:', error);
        return [];
    }
}

// Получить детали программы
async function fetchProgramById(id) {
    try {
        const response = await fetch(`${API_BASE}/programs/${id}/`, {
            headers: getAuthHeaders(),
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error fetching program:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Fetch program error:', error);
        return null;
    }
}

// Получить детали университета
async function fetchUniversityById(id) {
    try {
        const response = await fetch(`${API_BASE}/universities/${id}/`, {
            headers: getAuthHeaders(),
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error fetching university:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Fetch university error:', error);
        return null;
    }
}

export { fetchPrograms, fetchUniversities, fetchProgramById, fetchUniversityById, dashboardAPI, fetchWithAuth };

// Экспортируем для использования в HTML
window.fetchWithAuth = fetchWithAuth;
window.dashboardAPI = dashboardAPI;

// API для дашбордов
// const dashboardAPI = {
//     // Статистика для админа
//     getAdminStats: async () => {
//         const response = await fetch(`${API_BASE}/admin/stats/`, {
//             headers: getAuthHeaders(),
//         });
//         return response.ok ? await response.json() : null;
//     },
    
//     // Пользователи для админа
//     getUsers: async () => {
//         const response = await fetch(`${API_BASE}/admin/users/`, {
//             headers: getAuthHeaders(),
//         });
//         return response.ok ? await response.json() : [];
//     },
    
//     // Избранные программы
//     getFavorites: async () => {
//         const response = await fetch(`${API_BASE}/favorites/`, {
//             headers: getAuthHeaders(),
//         });
//         return response.ok ? await response.json() : [];
//     },
    
//     // Заявки студента
//     getApplications: async () => {
//         const response = await fetch(`${API_BASE}/applications/`, {
//             headers: getAuthHeaders(),
//         });
//         return response.ok ? await response.json() : [];
//     },
    
//     // История AI
//     getAIHistory: async () => {
//         const response = await fetch(`${API_BASE}/ai/history/`, {
//             headers: getAuthHeaders(),
//         });
//         return response.ok ? await response.json() : [];
//     },
    
//     // Обновить профиль
//     updateProfile: async (profileData) => {
//         const response = await fetch(`${API_BASE}/users/profile/`, {
//             method: 'PUT',
//             headers: getAuthHeaders(),
//             body: JSON.stringify(profileData),
//         });
//         return response.ok ? await response.json() : null;
//     },
// };

// export { fetchPrograms, fetchUniversities, fetchProgramById, fetchUniversityById, dashboardAPI };