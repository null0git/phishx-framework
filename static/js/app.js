/**
 * PhishX Framework - Main Application JavaScript
 * Handles global functionality, UI interactions, and utility functions
 */

// Global application state
const PhishX = {
    config: {
        apiBaseUrl: '/api',
        refreshInterval: 30000, // 30 seconds
        notificationDuration: 5000 // 5 seconds
    },
    state: {
        isOnline: true,
        lastUpdate: new Date(),
        activeModals: []
    }
};

// Initialize application on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    startPeriodicUpdates();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('PhishX Framework initialized');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize data tables
    initializeDataTables();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Check online status
    updateOnlineStatus();
    
    // Load user preferences
    loadUserPreferences();
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Online/offline status
    window.addEventListener('online', () => {
        PhishX.state.isOnline = true;
        updateOnlineStatus();
        showNotification('Connection restored', 'success');
    });
    
    window.addEventListener('offline', () => {
        PhishX.state.isOnline = false;
        updateOnlineStatus();
        showNotification('Connection lost', 'warning');
    });
    
    // Form validation
    document.addEventListener('submit', handleFormSubmission);
    
    // Copy to clipboard
    document.addEventListener('click', handleCopyToClipboard);
    
    // Modal management
    document.addEventListener('show.bs.modal', handleModalShow);
    document.addEventListener('hide.bs.modal', handleModalHide);
    
    // Escape key handling
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize DataTables with common settings
 */
function initializeDataTables() {
    if (typeof $.fn.DataTable !== 'undefined') {
        // Default DataTable settings
        $.extend(true, $.fn.dataTable.defaults, {
            responsive: true,
            pageLength: 25,
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            },
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                 '<"row"<"col-sm-12"tr>>' +
                 '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            order: []
        });
    }
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            focusSearch();
        }
        
        // Ctrl/Cmd + N for new campaign
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            openNewCampaignModal();
        }
        
        // Ctrl/Cmd + R for refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshCurrentPage();
        }
    });
}

/**
 * Start periodic updates
 */
function startPeriodicUpdates() {
    setInterval(() => {
        if (PhishX.state.isOnline && !document.hidden) {
            updateDashboardData();
        }
    }, PhishX.config.refreshInterval);
}

/**
 * Update online status indicator
 */
function updateOnlineStatus() {
    const statusIndicators = document.querySelectorAll('.status-indicator');
    statusIndicators.forEach(indicator => {
        indicator.className = `status-indicator ${PhishX.state.isOnline ? 'status-online' : 'status-offline'}`;
        indicator.innerHTML = `<i class="fas fa-circle"></i> ${PhishX.state.isOnline ? 'Online' : 'Offline'}`;
    });
}

/**
 * Handle form submissions with loading states
 */
function handleFormSubmission(e) {
    const form = e.target;
    if (!form.matches('form[data-loading]')) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        submitButton.disabled = true;
        
        // Re-enable after a timeout (fallback)
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 10000);
    }
}

/**
 * Handle copy to clipboard functionality
 */
function handleCopyToClipboard(e) {
    const copyButton = e.target.closest('[data-copy]');
    if (!copyButton) return;
    
    e.preventDefault();
    const textToCopy = copyButton.getAttribute('data-copy') || copyButton.textContent;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        showNotification('Copied to clipboard', 'success');
        
        // Visual feedback
        const originalIcon = copyButton.querySelector('i');
        if (originalIcon) {
            const originalClass = originalIcon.className;
            originalIcon.className = 'fas fa-check';
            setTimeout(() => {
                originalIcon.className = originalClass;
            }, 2000);
        }
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

/**
 * Handle modal show events
 */
function handleModalShow(e) {
    const modal = e.target;
    PhishX.state.activeModals.push(modal.id);
    
    // Auto-focus first input
    const firstInput = modal.querySelector('input:not([type="hidden"]):not([disabled])');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 150);
    }
}

/**
 * Handle modal hide events
 */
function handleModalHide(e) {
    const modal = e.target;
    const index = PhishX.state.activeModals.indexOf(modal.id);
    if (index > -1) {
        PhishX.state.activeModals.splice(index, 1);
    }
    
    // Clear form data
    const form = modal.querySelector('form');
    if (form) {
        form.reset();
    }
}

/**
 * Close all open modals
 */
function closeAllModals() {
    PhishX.state.activeModals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info', duration = null) {
    const toastContainer = getOrCreateToastContainer();
    const toastId = 'toast-' + Date.now();
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${getIconForType(type)} text-${type} me-2"></i>
            <strong class="me-auto">PhishX</strong>
            <small>now</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration || PhishX.config.notificationDuration
    });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Get icon for notification type
 */
function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * Focus search input
 */
function focusSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="search" i]');
    if (searchInputs.length > 0) {
        searchInputs[0].focus();
    }
}

/**
 * Open new campaign modal
 */
function openNewCampaignModal() {
    const modal = document.getElementById('createCampaignModal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

/**
 * Refresh current page data
 */
function refreshCurrentPage() {
    // Add loading indicator
    const refreshButton = document.querySelector('[data-refresh]');
    if (refreshButton) {
        const originalContent = refreshButton.innerHTML;
        refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        setTimeout(() => {
            refreshButton.innerHTML = originalContent;
            location.reload();
        }, 1000);
    } else {
        location.reload();
    }
}

/**
 * Update dashboard data via AJAX
 */
function updateDashboardData() {
    if (!window.location.pathname.includes('dashboard')) return;
    
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            updateStatCards(data);
            PhishX.state.lastUpdate = new Date();
        })
        .catch(error => {
            console.warn('Failed to update dashboard data:', error);
        });
}

/**
 * Update statistic cards
 */
function updateStatCards(data) {
    const statElements = {
        'total-campaigns': data.total_campaigns,
        'active-campaigns': data.active_campaigns,
        'total-credentials': data.total_credentials,
        'total-sessions': data.total_sessions
    };
    
    Object.entries(statElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateValue(element, parseInt(element.textContent) || 0, value);
        }
    });
}

/**
 * Animate number values
 */
function animateValue(element, start, end, duration = 1000) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = Math.floor(current);
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = end;
            clearInterval(timer);
        }
    }, 16);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    const preferences = localStorage.getItem('phishx-preferences');
    if (preferences) {
        try {
            const prefs = JSON.parse(preferences);
            applyUserPreferences(prefs);
        } catch (error) {
            console.warn('Failed to load user preferences:', error);
        }
    }
}

/**
 * Save user preferences to localStorage
 */
function saveUserPreferences(preferences) {
    try {
        localStorage.setItem('phishx-preferences', JSON.stringify(preferences));
    } catch (error) {
        console.warn('Failed to save user preferences:', error);
    }
}

/**
 * Apply user preferences
 */
function applyUserPreferences(preferences) {
    // Apply theme, language, etc.
    if (preferences.theme) {
        document.documentElement.setAttribute('data-bs-theme', preferences.theme);
    }
    
    if (preferences.autoRefresh !== undefined) {
        PhishX.config.refreshInterval = preferences.autoRefresh ? 30000 : 0;
    }
}

/**
 * Utility function to format numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Utility function to format dates
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to throttle function calls
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Smooth scroll to element
 */
function scrollToElement(element, offset = 0) {
    const elementPosition = element.offsetTop - offset;
    window.scrollTo({
        top: elementPosition,
        behavior: 'smooth'
    });
}

/**
 * Export functions for global use
 */
window.PhishX = PhishX;
window.showNotification = showNotification;
window.copyToClipboard = handleCopyToClipboard;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.debounce = debounce;
window.throttle = throttle;
window.isInViewport = isInViewport;
window.scrollToElement = scrollToElement;

// Console welcome message
console.log('%cPhishX Framework', 'color: #0d6efd; font-size: 24px; font-weight: bold;');
console.log('%cAdvanced Phishing Simulation Platform', 'color: #6c757d; font-size: 14px;');
console.log('%cFor authorized security testing only', 'color: #dc3545; font-size: 12px; font-weight: bold;');
