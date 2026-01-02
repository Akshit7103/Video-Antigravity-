/**
 * Home Page JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    await loadDashboardData();

    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, CONFIG.UI.REFRESH_INTERVAL);
});

/**
 * Load dashboard data
 */
async function loadDashboardData() {
    try {
        // Load analytics summary
        const analytics = await api.getAnalyticsSummary(7);

        // Update stats
        document.getElementById('totalPersons').textContent = analytics.total_registered || 0;
        document.getElementById('activeCameras').textContent = analytics.active_cameras || 0;
        document.getElementById('totalDetections').textContent = analytics.total_detections || 0;
        document.getElementById('uniquePersons').textContent = analytics.unique_persons || 0;

        // Load recent detections
        await loadRecentDetections();

    } catch (error) {
        Utils.handleError(error, 'loading dashboard data');
    }
}

/**
 * Load recent detections
 */
async function loadRecentDetections() {
    try {
        const detections = await api.getDetections({ limit: 10 });

        const tbody = document.getElementById('recentDetections');

        if (!detections || detections.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading">No recent detections</td></tr>';
            return;
        }

        tbody.innerHTML = detections.map(detection => `
            <tr>
                <td>${Utils.formatRelativeTime(detection.timestamp)}</td>
                <td>${detection.person_name}</td>
                <td>${detection.camera_id}</td>
                <td>${Utils.formatConfidence(detection.confidence)}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading recent detections:', error);
        document.getElementById('recentDetections').innerHTML =
            '<tr><td colspan="4" class="loading">Error loading detections</td></tr>';
    }
}
