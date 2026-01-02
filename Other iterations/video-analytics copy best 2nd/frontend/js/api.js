/**
 * API Client for Video Analytics Backend
 */

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        const defaultOptions = {
            headers: {
                // Add default headers if needed
            }
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const error = new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
                error.status = response.status;
                error.statusText = response.statusText;
                error.data = errorData;
                throw error;
            }

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;

        return this.request(url, {
            method: 'GET'
        });
    }

    /**
     * POST request with JSON body
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    }

    /**
     * POST request with FormData (for file uploads)
     */
    async postFormData(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            body: formData
            // Don't set Content-Type header - browser will set it with boundary
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // ========== Person APIs ==========

    /**
     * Get all persons
     */
    async getPersons(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.PERSONS, params);
    }

    /**
     * Get person by ID
     */
    async getPerson(id) {
        return this.get(CONFIG.API_ENDPOINTS.PERSON_BY_ID(id));
    }

    /**
     * Register new person
     */
    async registerPerson(formData) {
        return this.postFormData(CONFIG.API_ENDPOINTS.PERSONS_REGISTER, formData);
    }

    /**
     * Delete person
     */
    async deletePerson(id) {
        return this.delete(CONFIG.API_ENDPOINTS.PERSON_DELETE(id));
    }

    // ========== Detection APIs ==========

    /**
     * Detect faces in image
     */
    async detectFaces(formData) {
        return this.postFormData(CONFIG.API_ENDPOINTS.DETECT, formData);
    }

    /**
     * Get detections with filters
     */
    async getDetections(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.DETECTIONS, params);
    }

    // ========== Analytics APIs ==========

    /**
     * Get analytics summary
     */
    async getAnalyticsSummary(days = 7) {
        return this.get(CONFIG.API_ENDPOINTS.ANALYTICS_SUMMARY, { days });
    }

    // ========== Camera APIs ==========

    /**
     * Get all cameras
     */
    async getCameras() {
        return this.get(CONFIG.API_ENDPOINTS.CAMERAS);
    }

    /**
     * Start camera stream
     */
    async startCamera(cameraId) {
        return this.post(CONFIG.API_ENDPOINTS.CAMERA_START(cameraId));
    }

    /**
     * Stop camera stream
     */
    async stopCamera(cameraId) {
        return this.post(CONFIG.API_ENDPOINTS.CAMERA_STOP(cameraId));
    }

    // ========== Health Check ==========

    /**
     * Check API health
     */
    async healthCheck() {
        return this.get(CONFIG.API_ENDPOINTS.HEALTH);
    }
}

// Create global API client instance
const api = new APIClient(CONFIG.API_BASE_URL);
window.api = api;
