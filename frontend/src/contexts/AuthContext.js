import React, { createContext, useState, useContext, useEffect } from 'react';
import jwt_decode from 'jwt-decode';
import axios from 'axios';
import { login as apiLogin, refreshToken as apiRefreshToken } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Set up axios interceptor for token refresh
  useEffect(() => {
    // Add a response interceptor to handle token expiration
    const interceptor = axios.interceptors.response.use(
      response => response,
      async error => {
        const originalRequest = error.config;
        
        // If the error is due to an expired token and we haven't tried to refresh yet
        if (error.response && 
            error.response.status === 401 && 
            error.response.data.code === 'token_not_valid' && 
            !originalRequest._retry) {
          
          originalRequest._retry = true;
          
          try {
            // Try to refresh the token
            console.log('Token expired, attempting refresh...');
            const success = await refreshToken();
            
            if (success) {
              // If refresh was successful, update the Authorization header
              const token = localStorage.getItem('token');
              originalRequest.headers['Authorization'] = `Bearer ${token}`;
              console.log('Token refreshed successfully, retrying request');
              return axios(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            // If refresh fails, log the user out
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Clean up interceptor on unmount
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Decode token to check expiration
          const decoded = jwt_decode(token);
          console.log('Decoded token:', decoded); // Debug output
          const currentTime = Date.now() / 1000;
          
          if (decoded.exp > currentTime) {
            // Set axios default headers
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            setUser({
              username: decoded.username || decoded.user_id,
              is_staff: decoded.is_staff === true
            });
            setIsAuthenticated(true);
          } else {
            // Token expired, try to refresh
            const refreshed = await refreshToken();
            if (!refreshed) {
              logout();
            }
          }
        } catch (error) {
          console.error('Error checking authentication:', error);
          logout();
        }
      }
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      console.log('AuthContext: Attempting login with:', username);
      const userData = await apiLogin(username, password);
      console.log('AuthContext: Login response:', userData);
      
      // Set user directly from API response
      setUser({
        username: userData.username || userData.user_id,
        is_staff: userData.is_staff === true
      });
      
      // Set axios default headers
      const token = localStorage.getItem('token');
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
      
      setIsAuthenticated(true);
      
      return true;
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      return false;
    }
  };

  const refreshToken = async () => {
    try {
      const data = await apiRefreshToken();
      
      // Set axios default headers
      const token = localStorage.getItem('token');
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
      
      // Decode and set user
      const decoded = jwt_decode(data.access);
      console.log('Refresh decoded token:', decoded); // Debug output
      
      setUser({
        username: decoded.username || decoded.user_id,
        is_staff: decoded.is_staff === true
      });
      setIsAuthenticated(true);
      
      return true;
    } catch (error) {
      console.error('Refresh token error:', error);
      return false;
    }
  };

  const logout = () => {
    // Remove tokens
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    
    // Clear auth state
    setUser(null);
    setIsAuthenticated(false);
    
    // Clear axios headers
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      login,
      logout,
      refreshToken,
      loading
    }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
