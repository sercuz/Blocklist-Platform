import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with authentication token handling
const axiosInstance = axios.create({
  baseURL: API_URL
});

// Add a request interceptor to include the token in requests
axiosInstance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      // Use Bearer format for JWT tokens
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Check if we're using an API key instead
    const apiKey = localStorage.getItem('apiKey');
    if (apiKey && !token) {
      // Use ApiKey format for API keys
      config.headers.Authorization = `ApiKey ${apiKey}`;
    }
    
    return config;
  },
  error => Promise.reject(error)
);

// Helper function to handle API errors
const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    console.error('API Error Response:', error.response.data);
    if (error.response.status === 401 && !error.config._retry) {
      // Unauthorized - token expired or invalid
      // Don't remove tokens here - let the interceptor in AuthContext handle refresh
      console.log('401 error detected in API service');
    }
  } else if (error.request) {
    // The request was made but no response was received
    console.error('API Error Request:', error.request);
  } else {
    // Something happened in setting up the request that triggered an Error
    console.error('API Error:', error.message);
  }
};

// Authentication
export const login = async (username, password) => {
  try {
    console.log('Attempting login with:', { username, password: '***' });
    // Use our new direct login endpoint
    const response = await axios.post(`${API_URL}/login/`, { username, password });
    console.log('Login response:', response.data);
    localStorage.setItem('token', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);
    return response.data;
  } catch (error) {
    console.error('Login error details:', error);
    handleApiError(error);
    throw error;
  }
};

export const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    console.log('Refreshing token...');
    const response = await axios.post(`${API_URL}/token/refresh/`, { refresh: refreshToken });
    console.log('Token refresh response:', response.data);
    localStorage.setItem('token', response.data.access);
    return response.data;
  } catch (error) {
    console.error('Token refresh error:', error);
    handleApiError(error);
    throw error;
  }
};

// Blocklist operations
export const getBlocklist = async (type = null) => {
  try {
    const params = type ? { indicator_type: type } : {};
    const response = await axiosInstance.get('/blocklist/', { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getLogs = async () => {
  try {
    const response = await axiosInstance.get('/logs/');
    console.log('Raw logs response type:', typeof response.data);
    
    // Handle different response formats
    if (response.data && typeof response.data === 'object') {
      // If it's a nested object with entries field
      if (response.data.entries && Array.isArray(response.data.entries)) {
        return response.data.entries;
      }
      
      // If it's already an array
      if (Array.isArray(response.data)) {
        return response.data;
      }
      
      // If it's a string that might be JSON
      if (typeof response.data === 'string') {
        try {
          const parsed = JSON.parse(response.data);
          if (Array.isArray(parsed)) {
            return parsed;
          }
        } catch (e) {
          console.error('Failed to parse logs string:', e);
        }
      }
    }
    
    // Default to empty array if we couldn't process the data
    console.error('Could not process logs data:', response.data);
    return [];
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const blockIndicators = async (indicatorType, indicators, reason) => {
  try {
    const response = await axiosInstance.post('/block/', {
      indicator_type: indicatorType,
      indicators,
      reason
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const unblockIndicators = async (indicatorType, indicators, reason) => {
  try {
    const response = await axiosInstance.post('/unblock/', {
      indicator_type: indicatorType,
      indicators,
      reason
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Direct access to blocklist files
export const getIpBlocklist = async () => {
  try {
    const response = await axiosInstance.get('/ip-blocklist/');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getDomainBlocklist = async () => {
  try {
    const response = await axiosInstance.get('/domain-blocklist/');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getUrlBlocklist = async () => {
  try {
    const response = await axiosInstance.get('/url-blocklist/');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// API Key Management
export const getApiKeys = async () => {
  try {
    const response = await axiosInstance.get('/api-keys/');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const createApiKey = async (name, readOnly = true) => {
  try {
    const response = await axiosInstance.post('/api-keys/', {
      name,
      read_only: readOnly
    });
    // Store the API key for immediate use if needed
    if (response.data && response.data.key) {
      localStorage.setItem('apiKey', response.data.key);
    }
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const deleteApiKey = async (id) => {
  try {
    await axiosInstance.delete(`/api-keys/${id}/`);
    // If we're deleting the current API key, remove it from storage
    const currentKey = localStorage.getItem('apiKey');
    if (currentKey) {
      localStorage.removeItem('apiKey');
    }
    return true;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const regenerateApiKey = async (id) => {
  try {
    const response = await axiosInstance.post(`/api-keys/${id}/regenerate/`);
    // Update the stored API key if it's the one we're using
    if (response.data && response.data.key) {
      localStorage.setItem('apiKey', response.data.key);
    }
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// API Logs
export const getApiLogs = async () => {
  try {
    const response = await axiosInstance.get('/api-logs/');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};
