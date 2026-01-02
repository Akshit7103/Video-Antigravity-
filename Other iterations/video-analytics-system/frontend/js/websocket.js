// WebSocket connection for real-time updates

let ws = null;
let reconnectInterval = null;

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    console.log('Connecting to WebSocket:', wsUrl);

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            updateConnectionStatus(true);

            // Clear reconnect interval if exists
            if (reconnectInterval) {
                clearInterval(reconnectInterval);
                reconnectInterval = null;
            }
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            updateConnectionStatus(false);

            // Attempt to reconnect
            if (!reconnectInterval) {
                reconnectInterval = setInterval(() => {
                    console.log('Attempting to reconnect...');
                    initWebSocket();
                }, 5000);
            }
        };
    } catch (error) {
        console.error('Error creating WebSocket:', error);
        updateConnectionStatus(false);
    }
}

function handleWebSocketMessage(message) {
    console.log('WebSocket message received:', message);

    switch (message.type) {
        case 'person_detection':
            handlePersonDetection(message.data);
            break;
        case 'phone_detection':
            handlePhoneDetection(message.data);
            break;
        default:
            console.log('Unknown message type:', message.type);
    }
}

function handlePersonDetection(data) {
    // Add to dashboard if on dashboard tab
    const dashboardTab = document.getElementById('dashboard');
    if (dashboardTab.classList.contains('active')) {
        addPersonLogRow(data);
    }

    // Show notification
    const status = data.is_authorized ? 'Authorized' : 'Unauthorized';
    const notificationType = data.is_authorized ? 'success' : 'warning';
    showNotification(`${status} person detected: ${data.person_name}`, notificationType);
}

function handlePhoneDetection(data) {
    // Add to dashboard if on dashboard tab
    const dashboardTab = document.getElementById('dashboard');
    if (dashboardTab.classList.contains('active')) {
        addPhoneLogRow(data);
    }

    // Show notification
    showNotification('Phone detected in frame', 'info');
}

function updateConnectionStatus(connected) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Close WebSocket on page unload
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
});
