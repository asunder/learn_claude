// Main JavaScript for Hypervisor Agent website

document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeTooltips();
    initializeCopyButtons();
});

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#search') && !e.target.closest('#searchResults')) {
            hideSearchResults();
        }
    });
}

function performSearch(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(results => {
            displaySearchResults(results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(results) {
    let searchResultsDiv = document.getElementById('searchResults');
    
    if (!searchResultsDiv) {
        searchResultsDiv = document.createElement('div');
        searchResultsDiv.id = 'searchResults';
        searchResultsDiv.className = 'search-results';
        document.getElementById('search').parentNode.appendChild(searchResultsDiv);
    }
    
    if (results.length === 0) {
        searchResultsDiv.innerHTML = '<div class="search-result-item">No results found</div>';
    } else {
        searchResultsDiv.innerHTML = results.map(result => `
            <div class="search-result-item" onclick="navigateToResult('${result.url || '#'}')">
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-description">${result.description}</div>
            </div>
        `).join('');
    }
    
    searchResultsDiv.style.display = 'block';
}

function hideSearchResults() {
    const searchResultsDiv = document.getElementById('searchResults');
    if (searchResultsDiv) {
        searchResultsDiv.style.display = 'none';
    }
}

function navigateToResult(url) {
    if (url && url !== '#') {
        window.location.href = url;
    }
    hideSearchResults();
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Copy buttons functionality
function initializeCopyButtons() {
    document.querySelectorAll('[data-copy]').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.copy;
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                copyToClipboard(targetElement.textContent);
                showCopyFeedback(this);
            }
        });
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
        return Promise.resolve();
    }
}

function showCopyFeedback(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i> Copied!';
    button.classList.add('btn-success');
    button.classList.remove('btn-outline-primary');
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-primary');
    }, 2000);
}

// Utility functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function showError(message, containerId = 'errorDiv') {
    const errorDiv = document.getElementById(containerId);
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorDiv && errorMessage) {
        errorMessage.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function hideError(containerId = 'errorDiv') {
    const errorDiv = document.getElementById(containerId);
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Dynamic content loading
function loadContent(url, containerId) {
    showLoading('loadingDiv');
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            document.getElementById(containerId).innerHTML = html;
            hideLoading('loadingDiv');
        })
        .catch(error => {
            hideLoading('loadingDiv');
            showError('Failed to load content: ' + error.message);
        });
}

// Syntax highlighting helper
function highlightCode() {
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
}

// Smooth scrolling
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Local storage helpers
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('Failed to save to localStorage:', e);
    }
}

function loadFromStorage(key) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : null;
    } catch (e) {
        console.warn('Failed to load from localStorage:', e);
        return null;
    }
}

// Theme handling (if needed in future)
function toggleTheme() {
    const currentTheme = document.body.dataset.theme || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.body.dataset.theme = newTheme;
    saveToStorage('theme', newTheme);
}

function initializeTheme() {
    const savedTheme = loadFromStorage('theme');
    if (savedTheme) {
        document.body.dataset.theme = savedTheme;
    }
}

// Export functions for global use
window.HypervisorAgent = {
    copyToClipboard,
    showLoading,
    hideLoading,
    showError,
    hideError,
    validateForm,
    loadContent,
    highlightCode,
    smoothScrollTo,
    saveToStorage,
    loadFromStorage
};