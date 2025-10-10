import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simple initialization - check for token and verify user
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        console.log('Token found in localStorage, verifying with server...');
        
        try {
          // Set the token in axios headers before making request
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Try to get current user info to verify token is still valid
          const response = await api.get('/auth/me');
          if (response.data.user) {
            setUser(response.data.user);
            console.log('✅ Token verified, user set:', response.data.user);
          }
        } catch (error) {
          console.log('❌ Token verification failed, removing token:', error.response?.data || error.message);
          localStorage.removeItem('token');
          delete api.defaults.headers.common['Authorization'];
        }
      } else {
        console.log('No token found in localStorage');
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      console.log('🚀 Starting login process with:', credentials);
      
      const response = await api.post('/auth/login', credentials);
      console.log('✅ Login API response:', response.data);
      
      const { access_token, user: userData } = response.data;

      if (!access_token || !userData) {
        throw new Error('Invalid response from server');
      }

      // Store token and set axios header
      localStorage.setItem('token', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Set user state
      setUser(userData);
      
      console.log('✅ Login successful, user set:', userData);
      return { success: true, user: userData };
      
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Error response:', error.response?.data);
      
      const message = error.response?.data?.message || 'Login failed. Please check your credentials.';
      throw new Error(message);
    }
  };

  const logout = () => {
    console.log('🚪 Logging out user');
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isStudent: user?.role === 'student',
    isFaculty: ['faculty', 'hod', 'admin'].includes(user?.role),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};