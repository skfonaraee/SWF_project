// dashboard.js - общие функции для всех дашбордов

// Инициализация дашборда
function initDashboard() {
    // Проверка авторизации
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');
    
    if (!user || !token) {
        window.location.href = '../login.html';
        return null;
    }
    
    // Обновление UI с информацией о пользователе
    updateUserInfo(user);
    
    // Настройка обработчиков событий
    setupEventListeners();
    
    return user;
}

// Обновление информации о пользователе в UI
function updateUserInfo(user) {
    const elements = {
        'username': user.username || user.email,
        'user-email': user.email,
        'user-initial': user.username ? user.username.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase(),
        'welcome-username': user.username || user.email
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
    
    // Обновление аватара
    const avatar = document.getElementById('avatar-preview');
    if (avatar && user.avatar) {
        avatar.src = user.avatar;
    }
}

// Настройка общих обработчиков событий
function setupEventListeners() {
    // Выход
    const logoutButtons = document.querySelectorAll('[id*="logout"]');
    logoutButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    });
    
    // Переключение языка
    const langSwitch = document.getElementById('lang-switch');
    if (langSwitch) {
        langSwitch.addEventListener('click', toggleLanguage);
    }
    
    // Мобильное меню
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', openMobileMenu);
    }
    if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', closeMobileMenu);
    }
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeMobileMenu);
    }
}

// Функции мобильного меню
function openMobileMenu() {
    const mobileNav = document.getElementById('mobile-nav');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (mobileNav) mobileNav.classList.add('active');
    if (mobileOverlay) mobileOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMobileMenu() {
    const mobileNav = document.getElementById('mobile-nav');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (mobileNav) mobileNav.classList.remove('active');
    if (mobileOverlay) mobileOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

// Переключение языка
function toggleLanguage() {
    const langText = document.getElementById('lang-text');
    if (langText) {
        const currentLang = langText.textContent;
        const newLang = currentLang === 'РУС' ? 'ENG' : 'РУС';
        langText.textContent = newLang;
        showToast('Язык изменен', `Язык интерфейса изменен на ${newLang === 'РУС' ? 'русский' : 'английский'}`);
    }
}

// Toast уведомления
function showToast(title, description) {
    if (window.sonner) {
        window.sonner.toast(title, {
            description: description,
            duration: 4000,
        });
    } else {
        alert(`${title}: ${description}`);
    }
}

// Выход (дублируем из auth.js для удобства)
function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        window.location.href = '../index.html';
    }
}

export { initDashboard, updateUserInfo, showToast, logout };