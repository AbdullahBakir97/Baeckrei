import axios from 'axios';

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000/',
    timeout: 15000, // Increased timeout
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    withCredentials: true,
    // Add retry configuration
    retry: 3,
    retryDelay: 1000
});

// Add retry interceptor
axiosInstance.interceptors.response.use(null, async (error) => {
    const { config } = error;
    if (!config || !config.retry) {
        return Promise.reject(error);
    }

    config.retryCount = config.retryCount || 0;

    if (config.retryCount >= config.retry) {
        return Promise.reject(error);
    }

    config.retryCount += 1;
    const delayRetry = new Promise(resolve => setTimeout(resolve, config.retryDelay));
    await delayRetry;
    
    return axiosInstance(config);
});

// Request interceptor
axiosInstance.interceptors.request.use(
    (config) => {
        // Add CSRF token to headers
        const csrftoken = getCookie('csrftoken');
        if (csrftoken) {
            config.headers['X-CSRFToken'] = csrftoken;
        }

        // Add Authorization header if token exists
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default axiosInstance;
