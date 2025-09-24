import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If specific roles are required, check if user has permission
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    // Instead of redirecting, show unauthorized message or redirect to login
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;