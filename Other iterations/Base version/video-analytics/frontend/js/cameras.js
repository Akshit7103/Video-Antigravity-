/**
 * Cameras Page JavaScript with Live Face Detection
 */

let webcamStream = null;
let detectionInterval = null;
let currentCameraId = null;

document.addEventListener('DOMContentLoaded', async function() {
    displayCameras();
});

/**
 * Display cameras grid
 */
function displayCameras() {
    const grid = document.getElementById('camerasGrid');

    // Single laptop webcam camera
    grid.innerHTML = `
        <div class="camera-card">
            <div class="camera-header">
                <div class="camera-name">Laptop Webcam</div>
            </div>

            <div class="camera-info">
                <strong>Camera ID:</strong> webcam_01
            </div>

            <div class="camera-info">
                <strong>Location:</strong> Local Device
            </div>

            <div class="camera-actions">
                <button class="btn btn-success btn-sm" onclick="startLiveCamera('webcam_01', 'Laptop Webcam')">
                    Start Live View
                </button>
            </div>
        </div>
    `;
}

/**
 * Start live camera with face detection
 */
async function startLiveCamera(cameraId, cameraName) {
    try {
        currentCameraId = cameraId;

        // Show live view section
        document.getElementById('liveView').style.display = 'block';
        document.getElementById('liveCameraName').textContent = `${cameraName} - Live View`;

        // Get video element
        const video = document.getElementById('liveVideo');

        // Request webcam access
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        video.srcObject = stream;
        webcamStream = stream;

        // Wait for video to load
        await new Promise(resolve => {
            video.onloadedmetadata = () => {
                video.play();
                resolve();
            };
        });

        // Setup canvas
        const canvas = document.getElementById('liveCanvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        Utils.showMessage('Camera started successfully', 'success');

        // Start face detection loop
        startDetectionLoop();

    } catch (error) {
        console.error('Error starting camera:', error);
        Utils.handleError(error, 'starting camera');
    }
}

/**
 * Start continuous face detection
 */
function startDetectionLoop() {
    // Clear any existing interval
    if (detectionInterval) {
        clearInterval(detectionInterval);
    }

    // Run detection every 500ms (2 times per second)
    detectionInterval = setInterval(async () => {
        await detectFaces();
    }, 500);
}

/**
 * Detect faces in current video frame
 */
async function detectFaces() {
    try {
        const video = document.getElementById('liveVideo');
        const canvas = document.getElementById('liveCanvas');
        const ctx = canvas.getContext('2d');

        // Check if video is ready
        if (video.videoWidth === 0 || video.videoHeight === 0) {
            console.log('Video not ready yet');
            return;
        }

        // Create temporary canvas to capture frame
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');

        // Draw current video frame
        tempCtx.drawImage(video, 0, 0);

        // Convert to blob
        const blob = await new Promise(resolve => {
            tempCanvas.toBlob(resolve, 'image/jpeg', 0.95);
        });

        // Create form data
        const formData = new FormData();
        formData.append('image', blob, 'frame.jpg');
        formData.append('camera_id', currentCameraId);
        formData.append('save_detection', 'true');

        console.log('Sending frame for detection...');

        // Send to backend for detection
        const detections = await api.detectFaces(formData);

        console.log('Detection response:', detections);

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw detection results
        if (detections && detections.length > 0) {
            console.log('Faces detected:', detections.length);
            drawDetections(ctx, detections, canvas.width, canvas.height);
            updateDetectionInfo(detections);
        } else {
            console.log('No faces detected');
            updateDetectionInfo([]);
        }

    } catch (error) {
        console.error('Detection error:', error);
        updateDetectionInfo([]);
        // Show error in detection info
        const listEl = document.getElementById('detectionList');
        listEl.innerHTML = `<p style="color: var(--danger-color); margin-top: 0.5rem;">Error: ${error.message}</p>`;
    }
}

/**
 * Draw detection bounding boxes and labels
 */
function drawDetections(ctx, detections, canvasWidth, canvasHeight) {
    detections.forEach((detection, index) => {
        const text = detection.is_unknown ? 'Unknown' : detection.person_name;
        const confidence = (detection.confidence * 100).toFixed(1);

        // Color: green for known, red for unknown
        const boxColor = detection.is_unknown ? '#ff6b6b' : '#51cf66';
        const textColor = '#ffffff';

        if (detection.bbox && detection.bbox.length === 4) {
            // Draw bounding box using coordinates from backend
            const [x, y, width, height] = detection.bbox;

            // Draw rectangle
            ctx.strokeStyle = boxColor;
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, width, height);

            // Prepare label
            const label = `${text} (${confidence}%)`;

            // Draw label background
            ctx.font = 'bold 16px Arial';
            const textMetrics = ctx.measureText(label);
            const textWidth = textMetrics.width;
            const textHeight = 20;
            const padding = 4;

            // Position label above box, or below if at top of screen
            let labelX = x;
            let labelY = y - textHeight - padding;

            if (labelY < 0) {
                labelY = y + height + textHeight + padding;
            }

            // Draw label background
            ctx.fillStyle = boxColor;
            ctx.fillRect(labelX, labelY - textHeight, textWidth + padding * 2, textHeight + padding);

            // Draw label text
            ctx.fillStyle = textColor;
            ctx.fillText(label, labelX + padding, labelY - padding);

        } else {
            // Fallback: draw text at top if no bbox coordinates
            ctx.font = 'bold 24px Arial';
            ctx.fillStyle = boxColor;
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 3;

            const label = `${text} (${confidence}%)`;
            const x = 20;
            const y = 40 + (index * 35);

            ctx.strokeText(label, x, y);
            ctx.fillText(label, x, y);
        }
    });
}

/**
 * Update detection information display
 */
function updateDetectionInfo(detections) {
    const countEl = document.getElementById('detectionCount');
    const listEl = document.getElementById('detectionList');

    countEl.textContent = detections.length;

    if (detections.length === 0) {
        listEl.innerHTML = '<p style="color: var(--text-secondary); margin-top: 0.5rem;">No faces detected</p>';
    } else {
        listEl.innerHTML = detections.map(d => `
            <div style="margin-top: 0.5rem; padding: 0.5rem; background: var(--bg-primary); border-radius: 4px;">
                <strong style="color: ${d.is_unknown ? 'var(--danger-color)' : 'var(--success-color)'};">
                    ${d.is_unknown ? 'Unknown Person' : d.person_name}
                </strong>
                <br>
                <small>Confidence: ${(d.confidence * 100).toFixed(1)}%</small>
                ${d.timestamp ? `<br><small>Time: ${new Date(d.timestamp).toLocaleTimeString()}</small>` : ''}
            </div>
        `).join('');
    }
}

/**
 * Stop live view
 */
function stopLiveView() {
    // Stop detection loop
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }

    // Stop webcam
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }

    // Clear video
    const video = document.getElementById('liveVideo');
    video.srcObject = null;

    // Clear canvas
    const canvas = document.getElementById('liveCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Hide live view
    document.getElementById('liveView').style.display = 'none';

    currentCameraId = null;

    Utils.showMessage('Live view stopped', 'info');
}

// Make functions global for onclick handlers
window.startLiveCamera = startLiveCamera;
window.stopLiveView = stopLiveView;
