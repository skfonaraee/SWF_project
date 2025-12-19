const API_BASE = 'http://localhost:8000/api';

// Проверка статуса авторизации
function checkAuthStatus() {
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');
    
    const authButtons = document.getElementById('auth-buttons');
    const userProfile = document.getElementById('user-profile');
    const usernameSpan = document.getElementById('username');
    const userAvatar = document.getElementById('user-avatar');
    
    if (user && token) {
        // Пользователь авторизован
        if (authButtons) authButtons.style.display = 'none';
        if (userProfile) userProfile.classList.remove('hidden');
        if (usernameSpan) usernameSpan.textContent = user.username || 'Пользователь';
        if (userAvatar) {
            userAvatar.src = user.avatar || `https://ui-avatars.com/api/?name=${user.username || 'User'}&background=0F4C81&color=fff`;
        }
        return { user, token };
    } else {
        // Пользователь не авторизован
        if (authButtons) authButtons.style.display = 'flex';
        if (userProfile) userProfile.classList.add('hidden');
        return null;
    }
}

// Проверка роли и редирект на нужный дашборд
function checkAndRedirect() {
    const auth = checkAuthStatus();
    if (auth) {
        const { user } = auth;
        if (window.location.pathname.includes('login.html') || 
            window.location.pathname.includes('register.html')) {
            // Если пользователь уже авторизован и находится на странице входа/регистрации
            redirectToDashboard(user.role);
        }
    } else {
        // Если пользователь не авторизован и пытается зайти на дашборд
        if (window.location.pathname.includes('dashboard/')) {
            window.location.href = '../login.html';
        }
    }
}

// Редирект на соответствующий дашборд
function redirectToDashboard(role) {
    switch(role) {
        case 'admin':
            window.location.href = 'dashboard/admin.html';
            break;
        case 'moderator':
            window.location.href = 'dashboard/moderator.html';
            break;
        case 'student':
        default:
            window.location.href = 'dashboard/student.html';
            break;
    }
}

// Вход
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('token', data.access || data.token);
            localStorage.setItem('refresh_token', data.refresh || '');
            
            showSuccess('Успешный вход!');
            
            // Редирект в зависимости от роли
            setTimeout(() => {
                redirectToDashboard(data.user.role);
            }, 1000);
            
            return true;
        } else {
            showError(data.detail || data.message || 'Ошибка входа');
            return false;
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Ошибка соединения с сервером');
        return false;
    }
}

// Регистрация
async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('token', data.access || data.token);
            localStorage.setItem('refresh_token', data.refresh || '');
            
            showSuccess('Регистрация успешна!');
            
            // Все новые пользователи - студенты
            setTimeout(() => {
                window.location.href = 'dashboard/student.html';
            }, 1000);
            
            return true;
        } else {
            const errorMessage = data.detail || 
                               (data.errors ? Object.values(data.errors).flat().join(', ') : '') ||
                               'Ошибка регистрации';
            showError(errorMessage);
            return false;
        }
    } catch (error) {
        console.error('Register error:', error);
        showError('Ошибка соединения с сервером');
        return false;
    }
}

// Выход
function logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    window.location.href = '../index.html';
}

// Показать ошибку
function showError(message) {
    // Создать уведомление
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-transform transform translate-x-full';
    errorDiv.textContent = message;
    errorDiv.id = 'error-notification';
    
    document.body.appendChild(errorDiv);
    
    // Анимация появления
    setTimeout(() => {
        errorDiv.classList.remove('translate-x-full');
    }, 10);
    
    // Удалить через 5 секунд
    setTimeout(() => {
        errorDiv.classList.add('translate-x-full');
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 300);
    }, 5000);
}

// Показать успех
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-transform transform translate-x-full';
    successDiv.textContent = message;
    successDiv.id = 'success-notification';
    
    document.body.appendChild(successDiv);
    
    // Анимация появления
    setTimeout(() => {
        successDiv.classList.remove('translate-x-full');
    }, 10);
    
    setTimeout(() => {
        successDiv.classList.add('translate-x-full');
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 300);
    }, 4000);
}

// Обновить токен
async function refreshToken() {
    try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            return false;
        }
        
        const response = await fetch(`${API_BASE}/auth/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access);
            return true;
        }
        return false;
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

// Проверка на странице входа
document.addEventListener('DOMContentLoaded', function() {
    // Проверка авторизации и редирект если нужно
    checkAndRedirect();
    
    // Обработка кнопки выхода
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    // Обработка мобильной кнопки выхода
    const logoutBtnMobile = document.getElementById('logout-btn-mobile');
    if (logoutBtnMobile) {
        logoutBtnMobile.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
});