import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, User, Mail, GraduationCap, Users } from 'lucide-react';
import toast from 'react-hot-toast';

const LoginForm = () => {
  const [userType, setUserType] = useState('student');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    rollNumber: '',
    password: '',
  });

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleUserTypeChange = (type) => {
    setUserType(type);
    setFormData({
      email: '',
      rollNumber: '',
      password: '',
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🎯 Form submitted');
    
    if (isLoading) {
      console.log('⏳ Already loading, ignoring submit');
      return;
    }

    setIsLoading(true);

    try {
      // Build login data
      let loginData = {
        password: formData.password,
        user_type: userType
      };

      // Validate and add identifier
      if (userType === 'student') {
        if (!formData.email && !formData.rollNumber) {
          toast.error('Please enter either email or roll number');
          setIsLoading(false);
          return;
        }
        if (formData.email) {
          loginData.email = formData.email;
        }
        if (formData.rollNumber) {
          loginData.roll_number = formData.rollNumber;
        }
      } else {
        if (!formData.email) {
          toast.error('Please enter your email');
          setIsLoading(false);
          return;
        }
        loginData.email = formData.email;
      }

      console.log('📤 Sending login request:', loginData);
      
      // Call login function
      const result = await login(loginData);
      
      console.log('✅ Login function returned:', result);
      
      if (result.success && result.user) {
        toast.success('Login successful!');
        
        // Navigate based on role
        console.log('🧭 Navigating based on role:', result.user.role);
        
        if (result.user.role === 'student') {
          console.log('➡️ Navigating to /student');
          navigate('/student', { replace: true });
        } else if (['faculty', 'hod', 'admin'].includes(result.user.role)) {
          console.log('➡️ Navigating to /faculty');
          navigate('/faculty', { replace: true });
        } else {
          console.log('❓ Unknown role, navigating to /login');
          navigate('/login', { replace: true });
        }
      } else {
        throw new Error('Login failed - invalid response');
      }
      
    } catch (error) {
      console.error('❌ Login failed:', error);
      toast.error(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-600 text-white">
            <GraduationCap className="h-6 w-6" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            OD Management System
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        {/* User Type Selector */}
        <div className="flex space-x-4 bg-gray-100 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => handleUserTypeChange('student')}
            className={`flex-1 flex items-center justify-center py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              userType === 'student'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <User className="h-4 w-4 mr-2" />
            Student
          </button>
          <button
            type="button"
            onClick={() => handleUserTypeChange('faculty')}
            className={`flex-1 flex items-center justify-center py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              userType === 'faculty'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="h-4 w-4 mr-2" />
            Faculty
          </button>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
                {userType === 'student' && (
                  <span className="text-gray-500 font-normal"> (or use roll number below)</span>
                )}
              </label>
              <div className="mt-1 relative">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="input-field pl-10"
                  placeholder={userType === 'student' ? 'student@college.edu' : 'faculty@college.edu'}
                />
                <Mail className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              </div>
            </div>

            {/* Roll Number Field (Students Only) */}
            {userType === 'student' && (
              <div>
                <label htmlFor="rollNumber" className="block text-sm font-medium text-gray-700">
                  Roll Number
                  <span className="text-gray-500 font-normal"> (or use email above)</span>
                </label>
                <div className="mt-1 relative">
                  <input
                    id="rollNumber"
                    name="rollNumber"
                    type="text"
                    autoComplete="username"
                    value={formData.rollNumber}
                    onChange={handleInputChange}
                    className="input-field pl-10"
                    placeholder="CS2021001"
                  />
                  <User className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>
              </div>
            )}

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="input-field pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Signing in...
                </div>
              ) : (
                'Sign in'
              )}
            </button>
          </div>

          {/* Default Credentials Info */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Test Login Credentials:</h4>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Student:</strong> 24ucs158manisha@kgkite.ac.in / Kgkite@1234</div>
              <div><strong>Roll Number:</strong> 24UCS158</div>
              <div><strong>Faculty:</strong> dr.rajesh@kgkite.ac.in / Faculty@123</div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;