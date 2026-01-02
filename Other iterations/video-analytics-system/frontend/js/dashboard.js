// Dashboard functionality

async function loadDashboard() {
    await Promise.all([
        loadPersonStats(),
        loadPersonLogs(),
        loadPhoneLogs()
    ]);
}

// Load statistics
async function loadPersonStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/logs/person/stats`);
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalDetections').textContent = stats.total_detections;
            document.getElementById('authorizedCount').textContent = stats.authorized_detections;
            document.getElementById('unauthorizedCount').textContent = stats.unauthorized_detections;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load person detection logs
async function loadPersonLogs(limit = 50) {
    const tbody = document.getElementById('personLogsBody');

    try {
        const response = await fetch(`${API_BASE_URL}/api/logs/person?limit=${limit}`);
        if (response.ok) {
            const logs = await response.json();

            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="loading">No detection logs yet</td></tr>';
                return;
            }

            tbody.innerHTML = logs.map(log => {
                const statusBadge = log.is_authorized
                    ? '<span class="badge badge-success">Authorized</span>'
                    : '<span class="badge badge-danger">Unauthorized</span>';

                const confidence = log.confidence
                    ? (log.confidence * 100).toFixed(1) + '%'
                    : 'N/A';

                return `
                    <tr>
                        <td>${formatTime(log.detected_at)}</td>
                        <td><strong>${log.person_name}</strong></td>
                        <td>${statusBadge}</td>
                        <td>${confidence}</td>
                        <td>#${log.track_id || 'N/A'}</td>
                    </tr>
                `;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">Failed to load logs</td></tr>';
        }
    } catch (error) {
        console.error('Error loading person logs:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Error loading logs</td></tr>';
    }
}

// Load phone detection logs
async function loadPhoneLogs(limit = 50) {
    const tbody = document.getElementById('phoneLogsBody');

    try {
        const response = await fetch(`${API_BASE_URL}/api/logs/phone?limit=${limit}`);
        if (response.ok) {
            const logs = await response.json();

            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td class="loading">No phone detections yet</td></tr>';
                return;
            }

            tbody.innerHTML = logs.map(log => `
                <tr>
                    <td>${formatTime(log.detected_at)}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td class="loading">Failed to load logs</td></tr>';
        }
    } catch (error) {
        console.error('Error loading phone logs:', error);
        tbody.innerHTML = '<tr><td class="loading">Error loading logs</td></tr>';
    }
}

// Add new person log (called by WebSocket)
function addPersonLogRow(log) {
    const tbody = document.getElementById('personLogsBody');

    // Remove "no logs" message if present
    if (tbody.querySelector('.loading')) {
        tbody.innerHTML = '';
    }

    const statusBadge = log.is_authorized
        ? '<span class="badge badge-success">Authorized</span>'
        : '<span class="badge badge-danger">Unauthorized</span>';

    const confidence = log.confidence
        ? (log.confidence * 100).toFixed(1) + '%'
        : 'N/A';

    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${formatTime(log.detected_at)}</td>
        <td><strong>${log.person_name}</strong></td>
        <td>${statusBadge}</td>
        <td>${confidence}</td>
        <td>#${log.track_id || 'N/A'}</td>
    `;

    // Add to top
    tbody.insertBefore(row, tbody.firstChild);

    // Highlight animation
    row.style.backgroundColor = '#fef3c7';
    setTimeout(() => {
        row.style.transition = 'background-color 1s';
        row.style.backgroundColor = '';
    }, 100);

    // Keep only last 50 rows
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }

    // Update stats
    loadPersonStats();
}

// Add new phone log (called by WebSocket)
function addPhoneLogRow(log) {
    const tbody = document.getElementById('phoneLogsBody');

    // Remove "no logs" message if present
    if (tbody.querySelector('.loading')) {
        tbody.innerHTML = '';
    }

    const row = document.createElement('tr');
    row.innerHTML = `<td>${formatTime(log.detected_at)}</td>`;

    // Add to top
    tbody.insertBefore(row, tbody.firstChild);

    // Highlight animation
    row.style.backgroundColor = '#fef3c7';
    setTimeout(() => {
        row.style.transition = 'background-color 1s';
        row.style.backgroundColor = '';
    }, 100);

    // Keep only last 50 rows
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Refresh buttons
document.getElementById('refreshPersonLogs')?.addEventListener('click', loadPersonLogs);
document.getElementById('refreshPhoneLogs')?.addEventListener('click', loadPhoneLogs);
