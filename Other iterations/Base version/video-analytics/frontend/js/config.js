/**
 * Configuration for Video Analytics Frontend
 */

const CONFIG = {
    // API Base URL - change this to your backend URL
    API_BASE_URL: 'http://localhost:8000',

    // API Endpoints
    API_ENDPOINTS: {
        // Persons
        PERSONS: '/api/persons',
        PERSONS_REGISTER: '/api/persons/register',
        PERSON_BY_ID: (id) => `/api/persons/${id}`,
        PERSON_DELETE: (id) => `/api/persons/${id}`,

        // Detection
        DETECT: '/api/detect',
        DETECTIONS: '/api/detections',

        // Analytics
        ANALYTICS_SUMMARY: '/api/analytics/summary',

        // Cameras
        CAMERAS: '/api/cameras',
        CAMERA_START: (id) => `/api/cameras/${id}/start`,
        CAMERA_STOP: (id) => `/api/cameras/${id}/stop`,

        // Health
        HEALTH: '/api/health'
    },

    // UI Settings
    UI: {
        // Number of samples to capture from webcam
        WEBCAM_SAMPLES: 5,

        // Delay between webcam captures (ms)
        WEBCAM_CAPTURE_DELAY: 1000,

        // Status message display duration (ms)
        STATUS_MESSAGE_DURATION: 5000,

        // Refresh interval for dashboards (ms)
        REFRESH_INTERVAL: 30000
    },

    // Date/Time formatting
    DATE_FORMAT: {
        SHORT: 'MM/DD/YYYY',
        LONG: 'MMM DD, YYYY hh:mm A',
        TIME: 'hh:mm:ss A'
    }
};

// Export for use in other scripts
window.CONFIG = CONFIG;
