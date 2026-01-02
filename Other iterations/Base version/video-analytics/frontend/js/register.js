/**
 * Registration Page JavaScript
 */

let webcamStream = null;
let capturedImages = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeMethodSelector();
    initializeUploadForm();
    initializeWebcamForm();
});

/**
 * Initialize method selector (Upload vs Webcam)
 */
function initializeMethodSelector() {
    const methodButtons = document.querySelectorAll('.method-btn');
    const uploadMethod = document.getElementById('uploadMethod');
    const webcamMethod = document.getElementById('webcamMethod');

    methodButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const method = this.dataset.method;

            // Update active button
            methodButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Show/hide methods
            if (method === 'upload') {
                uploadMethod.classList.add('active');
                webcamMethod.classList.remove('active');
                stopWebcam();
            } else {
                uploadMethod.classList.remove('active');
                webcamMethod.classList.add('active');
            }
        });
    });
}

/**
 * Initialize upload form
 */
function initializeUploadForm() {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('imageFiles');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');

    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFileSelection(Array.from(e.target.files));
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--primary-color)';
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--border-color)';
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--border-color)';

        const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
        handleFileSelection(files);
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleUploadRegistration(form);
    });

    // Form reset
    form.addEventListener('reset', function() {
        imagePreview.innerHTML = '';
    });
}

/**
 * Handle file selection
 */
async function handleFileSelection(files) {
    const imagePreview = document.getElementById('imagePreview');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Validate file
        const validation = Utils.validateImageFile(file);
        if (!validation.valid) {
            Utils.showMessage(validation.error, 'error');
            continue;
        }

        // Create preview
        try {
            const previewEl = await Utils.createPreviewElement(file, i);
            imagePreview.appendChild(previewEl);
        } catch (error) {
            console.error('Error creating preview:', error);
        }
    }
}

/**
 * Handle upload registration
 */
async function handleUploadRegistration(form) {
    const submitBtn = document.getElementById('submitBtn');
    const fileInput = document.getElementById('imageFiles');

    try {
        // Validate
        if (!fileInput.files || fileInput.files.length === 0) {
            Utils.showMessage('Please select at least one image', 'error');
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        // Create FormData
        const formData = new FormData(form);

        // Register person
        const result = await api.registerPerson(formData);

        Utils.showMessage(result.message, 'success');

        // Reset form
        form.reset();
        document.getElementById('imagePreview').innerHTML = '';

        // Redirect to persons page after 2 seconds
        setTimeout(() => {
            window.location.href = 'persons.html';
        }, 2000);

    } catch (error) {
        Utils.handleError(error, 'registration');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register Person';
    }
}

/**
 * Initialize webcam form
 */
function initializeWebcamForm() {
    const startBtn = document.getElementById('startWebcam');
    const captureBtn = document.getElementById('captureBtn');
    const form = document.getElementById('webcamForm');

    startBtn.addEventListener('click', startWebcam);
    captureBtn.addEventListener('click', captureImage);

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleWebcamRegistration(form);
    });

    form.addEventListener('reset', function() {
        stopWebcam();
        capturedImages = [];
        document.getElementById('capturedImages').innerHTML = '';
        document.getElementById('captureCount').textContent = '0';
        document.getElementById('submitWebcamBtn').disabled = true;
    });
}

/**
 * Start webcam
 */
async function startWebcam() {
    const video = document.getElementById('webcamVideo');
    const startBtn = document.getElementById('startWebcam');
    const captureBtn = document.getElementById('captureBtn');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 }
        });

        video.srcObject = stream;
        webcamStream = stream;

        startBtn.textContent = 'Stop Camera';
        startBtn.onclick = stopWebcam;
        captureBtn.disabled = false;

        Utils.showMessage('Camera started', 'success');

    } catch (error) {
        Utils.handleError(error, 'starting webcam');
    }
}

/**
 * Stop webcam
 */
function stopWebcam() {
    const video = document.getElementById('webcamVideo');
    const startBtn = document.getElementById('startWebcam');
    const captureBtn = document.getElementById('captureBtn');

    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        webcamStream = null;
    }

    startBtn.textContent = 'Start Camera';
    startBtn.onclick = startWebcam;
    captureBtn.disabled = true;
}

/**
 * Capture image from webcam
 */
function captureImage() {
    if (capturedImages.length >= CONFIG.UI.WEBCAM_SAMPLES) {
        Utils.showMessage('Maximum samples captured', 'info');
        return;
    }

    const video = document.getElementById('webcamVideo');
    const canvas = document.getElementById('webcamCanvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0);

    // Convert to blob
    canvas.toBlob(blob => {
        // Create file from blob
        const file = new File([blob], `capture_${capturedImages.length + 1}.jpg`, { type: 'image/jpeg' });
        capturedImages.push(file);

        // Create preview
        const dataUrl = canvas.toDataURL('image/jpeg');
        const previewContainer = document.getElementById('capturedImages');

        const div = document.createElement('div');
        div.className = 'preview-item';

        const img = document.createElement('img');
        img.src = dataUrl;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'preview-remove';
        removeBtn.innerHTML = '&times;';
        removeBtn.type = 'button';
        removeBtn.onclick = () => {
            const index = capturedImages.indexOf(file);
            if (index > -1) {
                capturedImages.splice(index, 1);
                div.remove();
                updateCaptureCount();
            }
        };

        div.appendChild(img);
        div.appendChild(removeBtn);
        previewContainer.appendChild(div);

        updateCaptureCount();

    }, 'image/jpeg', 0.95);
}

/**
 * Update capture count
 */
function updateCaptureCount() {
    const count = capturedImages.length;
    document.getElementById('captureCount').textContent = count;

    const submitBtn = document.getElementById('submitWebcamBtn');
    submitBtn.disabled = count < 3; // Require at least 3 images
}

/**
 * Handle webcam registration
 */
async function handleWebcamRegistration(form) {
    const submitBtn = document.getElementById('submitWebcamBtn');

    try {
        if (capturedImages.length < 3) {
            Utils.showMessage('Please capture at least 3 images', 'error');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        // Create FormData
        const formData = new FormData();

        // Add form fields
        formData.append('name', form.name.value);
        if (form.email.value) formData.append('email', form.email.value);
        if (form.employee_id.value) formData.append('employee_id', form.employee_id.value);
        if (form.phone.value) formData.append('phone', form.phone.value);
        if (form.department.value) formData.append('department', form.department.value);
        if (form.designation.value) formData.append('designation', form.designation.value);
        if (form.notes.value) formData.append('notes', form.notes.value);

        // Add captured images
        capturedImages.forEach((file, index) => {
            formData.append('images', file, `capture_${index + 1}.jpg`);
        });

        // Register person
        const result = await api.registerPerson(formData);

        Utils.showMessage(result.message, 'success');

        // Stop webcam and reset
        stopWebcam();
        form.reset();
        capturedImages = [];
        document.getElementById('capturedImages').innerHTML = '';
        document.getElementById('captureCount').textContent = '0';

        // Redirect to persons page after 2 seconds
        setTimeout(() => {
            window.location.href = 'persons.html';
        }, 2000);

    } catch (error) {
        Utils.handleError(error, 'registration');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register Person';
    }
}
