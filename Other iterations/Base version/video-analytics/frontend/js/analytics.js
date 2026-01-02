/**
 * Analytics Page JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    const periodSelect = document.getElementById('periodSelect');
    const refreshBtn = document.getElementById('refreshBtn');

    // Load initial data
    await loadAnalytics(7);

    // Period change
    periodSelect.addEventListener('change', function() {
        const days = parseInt(this.value);
        loadAnalytics(days);
    });

    // Refresh button
    refreshBtn.addEventListener('click', function() {
        const days = parseInt(periodSelect.value);
        loadAnalytics(days);
    });

    // Auto-refresh every 30 seconds
    setInterval(() => {
        const days = parseInt(periodSelect.value);
        loadAnalytics(days);
    }, CONFIG.UI.REFRESH_INTERVAL);
});

/**
 * Load analytics data
 */
async function loadAnalytics(days) {
    try {
        console.log('Loading analytics for', days, 'days');

        // Load analytics summary
        const analytics = await api.getAnalyticsSummary(days);

        console.log('Analytics data received:', analytics);

        // Update stats
        document.getElementById('totalDetections').textContent = analytics.total_detections || 0;
        document.getElementById('uniquePersons').textContent = analytics.unique_persons || 0;
        document.getElementById('activeCameras').textContent = analytics.active_cameras || 0;

        // Calculate average detections per day
        const avgDetections = days > 0 ? (analytics.total_detections / days).toFixed(1) : 0;
        document.getElementById('avgDetections').textContent = avgDetections;

        // Display top visitors
        displayTopVisitors(analytics.top_persons || [], analytics.total_detections);

        // Load recent activity
        await loadRecentActivity(days);

    } catch (error) {
        console.error('Analytics error:', error);
        Utils.handleError(error, 'loading analytics');

        // Set default values on error
        document.getElementById('totalDetections').textContent = '0';
        document.getElementById('uniquePersons').textContent = '0';
        document.getElementById('activeCameras').textContent = '0';
        document.getElementById('avgDetections').textContent = '0';
    }
}

/**
 * Display top visitors
 */
function displayTopVisitors(topPersons, totalDetections) {
    const tbody = document.getElementById('topVisitors');

    if (!topPersons || topPersons.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="loading">No data available</td></tr>';
        return;
    }

    tbody.innerHTML = topPersons.map((person, index) => {
        const percentage = totalDetections > 0 ? ((person.count / totalDetections) * 100).toFixed(1) : 0;

        return `
            <tr>
                <td>${index + 1}</td>
                <td>${person.name}</td>
                <td>${person.count}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="background: var(--primary-color); height: 20px; width: ${percentage}%; border-radius: 4px;"></div>
                        <span>${percentage}%</span>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Load recent activity
 */
async function loadRecentActivity(days) {
    try {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const detections = await api.getDetections({
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            limit: 50
        });

        const tbody = document.getElementById('recentActivity');

        if (!detections || detections.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading">No activity found</td></tr>';
            return;
        }

        tbody.innerHTML = detections.map(detection => `
            <tr>
                <td>${Utils.formatDateTime(detection.timestamp)}</td>
                <td>${detection.person_name}</td>
                <td>${detection.camera_id}</td>
                <td>${Utils.formatConfidence(detection.confidence)}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading recent activity:', error);
        document.getElementById('recentActivity').innerHTML =
            '<tr><td colspan="4" class="loading">Error loading activity</td></tr>';
    }
}
