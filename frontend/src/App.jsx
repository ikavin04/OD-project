import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';

// Components
import LoadingSpinner from './components/common/LoadingSpinner';
import ProtectedRoute from './components/common/ProtectedRoute';
import Header from './components/common/Header';
import LoginForm from './components/auth/LoginForm';
import StudentDashboard from './components/student/StudentDashboard';
import FacultyDashboard from './components/faculty/FacultyDashboard';
import DebugPage from './components/debug/DebugPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppRoutes() {
  const { loading, isAuthenticated, user } = useAuth();

  console.log('🔄 AppRoutes render - loading:', loading, 'isAuthenticated:', isAuthenticated, 'user:', user);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <Header />
      <Routes>
        {/* Login Route */}
        <Route 
          path="/login" 
          element={
            isAuthenticated ? (
              <Navigate to={user?.role === 'student' ? '/student' : '/faculty'} replace />
            ) : (
              <LoginForm />
            )
          } 
        />

        {/* Root Route */}
        <Route 
          path="/" 
          element={
            <Navigate to={isAuthenticated ? (user?.role === 'student' ? '/student' : '/faculty') : '/login'} replace />
          } 
        />

        {/* Student Dashboard */}
        <Route 
          path="/student" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          } 
        />

        {/* Faculty Dashboard */}
        <Route 
          path="/faculty" 
          element={
            <ProtectedRoute allowedRoles={['faculty', 'hod', 'admin']}>
              <FacultyDashboard />
            </ProtectedRoute>
          } 
        />

        {/* Debug Page */}
        <Route 
          path="/debug" 
          element={<DebugPage />} 
        />

        {/* 404 Route */}
        <Route 
          path="*" 
          element={
            <Navigate to={isAuthenticated ? (user?.role === 'student' ? '/student' : '/faculty') : '/login'} replace />
          } 
        />
      </Routes>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <div className="min-h-screen bg-gray-50">
            <AppRoutes />
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  style: {
                    background: '#10b981',
                  },
                },
                error: {
                  style: {
                    background: '#ef4444',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;