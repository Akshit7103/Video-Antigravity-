// Main app.js - Tab management and initialization

const API_BASE_URL = window.location.origin;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // Update panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Load data for specific tabs
        if (tabName === 'people') {
            loadRegisteredPeople();
        } else if (tabName === 'dashboard') {
            loadDashboard();
        }
    });
});

// Utility functions
function formatDateTime(dateString) {
    // Parse UTC timestamp and convert to local time
    const date = new Date(dateString + 'Z'); // Append Z to ensure UTC parsing
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
}

function formatTime(dateString) {
    // Parse UTC timestamp and convert to local time
    const date = new Date(dateString + 'Z'); // Append Z to ensure UTC parsing
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
}

function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with a toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Video Analytics System initialized');
    initWebSocket();
});
