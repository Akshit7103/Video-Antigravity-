/**
 * Utility Functions for Video Analytics Frontend
 */

const Utils = {
    /**
     * Format date/time (converts UTC to local timezone)
     */
    formatDateTime(dateString, format = 'long') {
        // Parse as UTC if no timezone info
        const date = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'));

        if (format === 'short') {
            return date.toLocaleDateString();
        } else if (format === 'time') {
            return date.toLocaleTimeString();
        } else {
            // Format: DD/MM/YYYY, HH:MM:SS AM/PM
            return date.toLocaleString('en-GB', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
        }
    },

    /**
     * Format relative time (e.g., "2 hours ago")
     */
    formatRelativeTime(dateString) {
        // Parse as UTC if no timezone info
        const date = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'));
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffSec < 60) {
            return 'Just now';
        } else if (diffMin < 60) {
            return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
        } else if (diffHour < 24) {
            return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
        } else if (diffDay < 7) {
            return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
        } else {
            return this.formatDateTime(dateString, 'short');
        }
    },

    /**
     * Format confidence as percentage
     */
    formatConfidence(confidence) {
        return `${(confidence * 100).toFixed(1)}%`;
    },

    /**
     * Show status message
     */
    showMessage(message, type = 'info', duration = CONFIG.UI.STATUS_MESSAGE_DURATION) {
        const messageEl = document.getElementById('statusMessage') || this.createMessageElement();

        messageEl.textContent = message;
        messageEl.className = `status-message ${type}`;
        messageEl.hidden = false;

        // Auto-hide after duration
        setTimeout(() => {
            messageEl.hidden = true;
        }, duration);
    },

    /**
     * Create status message element if it doesn't exist
     */
    createMessageElement() {
        const el = document.createElement('div');
        el.id = 'statusMessage';
        el.className = 'status-message';
        el.hidden = true;
        document.body.appendChild(el);
        return el;
    },

    /**
     * Show loading state
     */
    showLoading(element, message = 'Loading...') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }

        if (element) {
            element.innerHTML = `<div class="loading-spinner">${message}</div>`;
        }
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    },

    /**
     * Validate image file
     */
    validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!validTypes.includes(file.type)) {
            return { valid: false, error: 'Invalid file type. Please upload JPEG, PNG, or GIF.' };
        }

        if (file.size > maxSize) {
            return { valid: false, error: 'File too large. Maximum size is 10MB.' };
        }

        return { valid: true };
    },

    /**
     * Create image preview from file
     */
    createImagePreview(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                resolve(e.target.result);
            };

            reader.onerror = () => {
                reject(new Error('Failed to read file'));
            };

            reader.readAsDataURL(file);
        });
    },

    /**
     * Create preview element for image
     */
    async createPreviewElement(file, index) {
        const previewUrl = await this.createImagePreview(file);

        const div = document.createElement('div');
        div.className = 'preview-item';
        div.dataset.index = index;

        const img = document.createElement('img');
        img.src = previewUrl;
        img.alt = file.name;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'preview-remove';
        removeBtn.innerHTML = '&times;';
        removeBtn.type = 'button';
        removeBtn.onclick = () => div.remove();

        div.appendChild(img);
        div.appendChild(removeBtn);

        return div;
    },

    /**
     * Handle errors with user-friendly messages
     */
    handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);

        let message = 'An error occurred. Please try again.';

        if (error.message) {
            message = error.message;
        }

        this.showMessage(message, 'error');
    },

    /**
     * Confirm action
     */
    confirm(message) {
        return window.confirm(message);
    },

    /**
     * Get URL parameter
     */
    getUrlParameter(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    },

    /**
     * Set URL parameter without reload
     */
    setUrlParameter(name, value) {
        const url = new URL(window.location);
        url.searchParams.set(name, value);
        window.history.pushState({}, '', url);
    },

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showMessage('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showMessage('Failed to copy', 'error');
        }
    },

    /**
     * Download data as JSON file
     */
    downloadJSON(data, filename) {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
    },

    /**
     * Create pagination controls
     */
    createPagination(currentPage, totalPages, onPageChange) {
        const container = document.createElement('div');
        container.className = 'pagination';

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = 'Previous';
        prevBtn.className = 'btn btn-secondary';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => onPageChange(currentPage - 1);
        container.appendChild(prevBtn);

        // Page info
        const pageInfo = document.createElement('span');
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        pageInfo.style.margin = '0 1rem';
        container.appendChild(pageInfo);

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.className = 'btn btn-secondary';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => onPageChange(currentPage + 1);
        container.appendChild(nextBtn);

        return container;
    }
};

// Export for use in other scripts
window.Utils = Utils;
