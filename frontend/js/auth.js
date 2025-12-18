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
    } else {
        // Пользователь не авторизован
        if (authButtons) authButtons.style.display = 'flex';
        if (userProfile) userProfile.classList.add('hidden');
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
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('token', data.access || data.token);
            
            // Редирект в зависимости от роли
            if (data.user.role === 'admin') {
                window.location.href = '/dashboard/admin.html';
            } else if (data.user.role === 'moderator') {
                window.location.href = '/dashboard/moderator.html';
            } else {
                window.location.href = '/dashboard/student.html';
            }
            
            return true;
        } else {
            const error = await response.json();
            showError(error.detail || 'Ошибка входа');
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
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('token', data.access || data.token);
            
            // Все новые пользователи - студенты
            window.location.href = '/dashboard/student.html';
            return true;
        } else {
            const error = await response.json();
            showError(error.detail || Object.values(error).join(', ') || 'Ошибка регистрации');
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
    window.location.href = '/index.html';
}

// Показать ошибку
function showError(message) {
    // Создать уведомление
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    // Удалить через 5 секунд
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Показать успех
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    successDiv.textContent = message;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

// Проверка на странице входа
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    checkAuthStatus();
});

export { login, register, logout, checkAuthStatus }; 