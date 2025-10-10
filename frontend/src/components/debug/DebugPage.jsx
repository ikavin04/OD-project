import React from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

const DebugPage = () => {
  const { user, isAuthenticated, loading, login, logout } = useAuth();

  const handleTestLogin = async () => {
    try {
      const result = await login({
        email: 'student@college.edu',
        password: 'Student@2025!Pass',
        user_type: 'student'
      });
      console.log('Test login result:', result);
    } catch (error) {
      console.error('Test login error:', error);
    }
  };

  const handleTestAPI = async () => {
    try {
      const response = await api.get('/auth/me');
      console.log('API test result:', response.data);
    } catch (error) {
      console.error('API test error:', error);
    }
  };

  const handleClearStorage = () => {
    localStorage.clear();
    window.location.reload();
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      
      <div className="space-y-4">
        <div>
          <h2 className="font-semibold">Auth State:</h2>
          <p>Loading: {loading ? 'true' : 'false'}</p>
          <p>Authenticated: {isAuthenticated ? 'true' : 'false'}</p>
          <p>User: {JSON.stringify(user, null, 2)}</p>
        </div>
        
        <div className="space-x-2">
          <button 
            onClick={handleTestLogin}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Test Login
          </button>
          <button 
            onClick={handleTestAPI}
            className="bg-green-500 text-white px-4 py-2 rounded"
          >
            Test API
          </button>
          <button 
            onClick={logout}
            className="bg-red-500 text-white px-4 py-2 rounded"
          >
            Logout
          </button>
          <button 
            onClick={handleClearStorage}
            className="bg-gray-500 text-white px-4 py-2 rounded"
          >
            Clear Storage
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebugPage;