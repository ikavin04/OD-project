// Frontend API Configuration
// Automatically detects environment and uses appropriate API URL

const getApiUrl = () => {
  // Production check
  if (window.location.protocol === 'https:' || window.location.hostname !== 'localhost') {
    return `${window.location.protocol}//${window.location.hostname}`;
  }
  
  // Development
  return 'http://localhost:5000';
};

const API_BASE_URL = getApiUrl();

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  
  // Student endpoints
  STUDENT_PROFILE: `${API_BASE_URL}/api/student/profile`,
  STUDENT_OD_REQUESTS: `${API_BASE_URL}/api/student/od-requests`,
  SUBMIT_OD_REQUEST: `${API_BASE_URL}/api/student/od-request`,
  
  // Faculty endpoints
  FACULTY_PROFILE: `${API_BASE_URL}/api/faculty/profile`,
  FACULTY_OD_REQUESTS: `${API_BASE_URL}/api/faculty/od-requests`,
  APPROVE_OD_REQUEST: `${API_BASE_URL}/api/faculty/od-request`,
  
  // File upload
  UPLOAD: `${API_BASE_URL}/api/upload`,
  
  // Health check
  HEALTH: `${API_BASE_URL}/api/health`
};

export default API_BASE_URL;