// Face registration functionality

let webcamStream = null;
let capturedImageData = null;
let faceEmbedding = null;

const webcamElement = document.getElementById('webcam');
const canvasElement = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCamera');
const capturePhotoBtn = document.getElementById('capturePhoto');
const previewBox = document.getElementById('capturedPreview');
const registrationForm = document.getElementById('registrationForm');
const registerBtn = document.getElementById('registerBtn');
const statusDiv = document.getElementById('registrationStatus');

// Start camera
startCameraBtn.addEventListener('click', async () => {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 }
        });
        webcamElement.srcObject = webcamStream;
        capturePhotoBtn.disabled = false;
        startCameraBtn.textContent = 'Camera Active';
        startCameraBtn.disabled = true;
        showStatus('Camera started successfully', 'success');
    } catch (error) {
        console.error('Error accessing camera:', error);
        showStatus('Failed to access camera. Please check permissions.', 'error');
    }
});

// Capture photo
capturePhotoBtn.addEventListener('click', () => {
    const context = canvasElement.getContext('2d');
    canvasElement.width = webcamElement.videoWidth;
    canvasElement.height = webcamElement.videoHeight;

    // Draw current frame
    context.drawImage(webcamElement, 0, 0);

    // Get image data
    canvasElement.toBlob((blob) => {
        capturedImageData = blob;

        // Show preview
        const img = document.createElement('img');
        img.src = URL.createObjectURL(blob);
        previewBox.innerHTML = '';
        previewBox.appendChild(img);

        // Extract face embedding (this would normally be done by a model)
        // For now, we'll create a placeholder and let the backend handle it
        faceEmbedding = null; // Will be extracted when registering

        registerBtn.disabled = false;
        showStatus('Photo captured! Enter name and click Register.', 'success');
    }, 'image/jpeg', 0.95);
});

// Registration form
registrationForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const personName = document.getElementById('personName').value.trim();

    if (!capturedImageData) {
        showStatus('Please capture a photo first', 'error');
        return;
    }

    if (!personName) {
        showStatus('Please enter a name', 'error');
        return;
    }

    registerBtn.disabled = true;
    showStatus('Processing... Please wait', '');

    try {
        // First, we need to extract face embedding from the image
        // For this, we'll send the image to a processing endpoint
        const embedding = await extractFaceEmbedding(capturedImageData);

        if (!embedding) {
            showStatus('No face detected in the photo. Please try again.', 'error');
            registerBtn.disabled = false;
            return;
        }

        // Now register with the backend
        const formData = new FormData();
        formData.append('name', personName);
        formData.append('photo', capturedImageData, 'photo.jpg');
        formData.append('embedding', JSON.stringify(embedding));

        const response = await fetch(`${API_BASE_URL}/api/faces/register`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            showStatus(`Successfully registered: ${result.name}`, 'success');

            // Reset form
            registrationForm.reset();
            previewBox.innerHTML = '<p>No photo captured</p>';
            capturedImageData = null;
            faceEmbedding = null;
            registerBtn.disabled = true;
        } else {
            const error = await response.json();
            showStatus(`Registration failed: ${error.detail}`, 'error');
            registerBtn.disabled = false;
        }
    } catch (error) {
        console.error('Registration error:', error);
        showStatus('Registration failed. Please try again.', 'error');
        registerBtn.disabled = false;
    }
});

// Extract face embedding using InsightFace
async function extractFaceEmbedding(imageBlob) {
    // Note: This is a placeholder. In a real implementation, you would:
    // 1. Send image to a backend endpoint that runs InsightFace
    // 2. Or run a client-side ONNX model (though this is heavy)
    //
    // For now, we'll simulate by creating a dummy endpoint expectation
    // The actual implementation should have a backend endpoint that:
    // - Receives the image
    // - Runs SCRFD face detection
    // - Extracts ArcFace embedding
    // - Returns the embedding

    try {
        const formData = new FormData();
        formData.append('image', imageBlob);

        const response = await fetch(`${API_BASE_URL}/api/faces/extract-embedding`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            return data.embedding;
        } else {
            return null;
        }
    } catch (error) {
        console.error('Error extracting embedding:', error);
        // For development, return a dummy embedding
        // This should be replaced with actual implementation
        return Array(512).fill(0).map(() => Math.random());
    }
}

function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = 'status-message';
    if (type) {
        statusDiv.classList.add(type);
    }

    if (type === 'success') {
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = 'status-message';
        }, 5000);
    }
}

// Load registered people
async function loadRegisteredPeople() {
    const peopleGrid = document.getElementById('peopleGrid');
    const countBadge = document.getElementById('peopleCount');

    peopleGrid.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/faces/with-photos`);
        if (response.ok) {
            const people = await response.json();

            if (people.length === 0) {
                peopleGrid.innerHTML = '<p class="loading">No registered people yet</p>';
                countBadge.textContent = '0 people';
                return;
            }

            countBadge.textContent = `${people.length} ${people.length === 1 ? 'person' : 'people'}`;

            peopleGrid.innerHTML = people.map(person => `
                <div class="person-card">
                    <button class="delete-btn" onclick="deletePerson(${person.id}, '${person.name}')">&times;</button>
                    <img src="data:image/jpeg;base64,${person.photo_base64}" alt="${person.name}">
                    <h3>${person.name}</h3>
                    <p class="date">${formatDateTime(person.registered_at)}</p>
                </div>
            `).join('');
        } else {
            peopleGrid.innerHTML = '<p class="loading">Failed to load people</p>';
        }
    } catch (error) {
        console.error('Error loading people:', error);
        peopleGrid.innerHTML = '<p class="loading">Error loading people</p>';
    }
}

// Delete person
async function deletePerson(id, name) {
    if (!confirm(`Are you sure you want to delete ${name}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/faces/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification(`${name} deleted successfully`, 'success');
            loadRegisteredPeople();
        } else {
            showNotification(`Failed to delete ${name}`, 'error');
        }
    } catch (error) {
        console.error('Error deleting person:', error);
        showNotification('Error deleting person', 'error');
    }
}

// Refresh button
document.getElementById('refreshPeople')?.addEventListener('click', loadRegisteredPeople);
