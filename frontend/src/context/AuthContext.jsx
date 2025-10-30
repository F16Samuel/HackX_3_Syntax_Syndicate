import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../lib/axios';

// Create the context
const AuthContext = createContext(undefined);

// Define the AuthProvider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check auth status on component mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        // Use 'api' instance which has the interceptor
        const response = await api.get('/api/v1/auth/me');
        setUser(response.data);
      } catch (error) {
        console.error("Auth check failed:", error);
        // Clear local storage if token is invalid
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_email');
        setUser(null);
      }
    }
    setLoading(false);
  };

  const login = async (email, password, role) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post(`/api/v1/auth/${role}/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token, role: userRole, email: userEmail } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user_role', userRole);
    localStorage.setItem('user_email', userEmail);

    // Re-check auth to set user state
    await checkAuth();
  };

  const register = async (email, password, role) => {
    // This will just attempt to register. 
    // The user will still need to log in after.
    await api.post(`/api/v1/auth/${role}/register`, { email, password });
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_email');
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

