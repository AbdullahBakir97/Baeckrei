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
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    withCredentials: true
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

// Response interceptor
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
            // Retry the request once if CSRF token is invalid
            const originalRequest = error.config;
            if (!originalRequest._retry) {
                originalRequest._retry = true;
                const csrftoken = getCookie('csrftoken');
                if (csrftoken) {
                    originalRequest.headers['X-CSRFToken'] = csrftoken;
                }
                return axiosInstance(originalRequest);
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
