import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Building, Calendar, Users, Save, X } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../utils/api';

const FacultyProfile = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [facultyData, setFacultyData] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    faculty_type: '',
    assigned_year: '',
    assigned_section: ''
  });

  useEffect(() => {
    fetchFacultyProfile();
  }, []);

  const fetchFacultyProfile = async () => {
    try {
      const response = await api.get('/faculty/profile');
      setFacultyData(response.data.faculty);
      setFormData({
        faculty_type: response.data.faculty.faculty_type || '',
        assigned_year: response.data.faculty.assigned_year || '',
        assigned_section: response.data.faculty.assigned_section || ''
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      toast.error('Failed to load profile');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await api.put('/faculty/profile', formData);
      setFacultyData(response.data.faculty);
      toast.success('Profile updated successfully!');
      setEditMode(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error(error.response?.data?.error || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      faculty_type: facultyData?.faculty_type || '',
      assigned_year: facultyData?.assigned_year || '',
      assigned_section: facultyData?.assigned_section || ''
    });
    setEditMode(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 lg:p-8">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 sm:gap-4 mb-4 sm:mb-6">
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Faculty Profile</h1>
            {!editMode && (
              <button
                onClick={() => setEditMode(true)}
                className="btn-primary w-full sm:w-auto"
              >
                Edit Profile
              </button>
            )}
          </div>

        <form onSubmit={handleSubmit}>
          {/* Basic Information */}
          <div className="mb-4 sm:mb-6">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <User className="h-4 w-4 sm:h-5 sm:w-5 mr-2 flex-shrink-0 text-blue-600" />
              Basic Information
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">Name</label>
                <div className="input-field bg-gray-50 text-sm sm:text-base">
                  {facultyData?.name}
                </div>
              </div>
              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">
                  <Building className="inline h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                  Department
                </label>
                <div className="input-field bg-gray-50 text-sm sm:text-base">
                  {facultyData?.department}
                </div>
              </div>
            </div>
          </div>

          {/* Class Assignment - Important for Monthly Reports */}
          <div className="mb-4 sm:mb-6 border-t border-gray-200 pt-4 sm:pt-6">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 mb-2 flex items-center">
              <Users className="h-4 w-4 sm:h-5 sm:w-5 mr-2 flex-shrink-0 text-blue-600" />
              Class Assignment
            </h2>
            <div className="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4 bg-blue-50 p-3 sm:p-3.5 rounded-lg border border-blue-200">
              <p className="flex items-start gap-2">
                <span className="text-base sm:text-lg flex-shrink-0">📧</span>
                <span><strong>Monthly Report Notification:</strong> If you are an Advisor or Mentor with an assigned class, you will automatically receive monthly OD reports for your students via email.</span>
              </p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">
                  Faculty Type <span className="text-red-500">*</span>
                </label>
                {editMode ? (
                  <select
                    value={formData.faculty_type}
                    onChange={(e) => {
                      const newType = e.target.value;
                      setFormData({ 
                        ...formData, 
                        faculty_type: newType,
                        // Clear year and section if Class Handling is selected
                        assigned_year: newType === 'Class Handling' ? '' : formData.assigned_year,
                        assigned_section: newType === 'Class Handling' ? '' : formData.assigned_section
                      });
                    }}
                    className="input-field text-sm sm:text-base"
                    required
                  >
                    <option value="">Select Type</option>
                    <option value="Advisor">Advisor</option>
                    <option value="Mentor">Mentor</option>
                    <option value="Class Handling">Class Handling</option>
                  </select>
                ) : (
                  <div className="input-field bg-gray-50 text-sm sm:text-base">
                    {facultyData?.faculty_type || 'Not assigned'}
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Advisors & Mentors receive monthly reports
                </p>
              </div>

              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">
                  <Calendar className="inline h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                  Assigned Year
                </label>
                {editMode ? (
                  <select
                    value={formData.assigned_year}
                    onChange={(e) => setFormData({ ...formData, assigned_year: e.target.value })}
                    className="input-field text-sm sm:text-base"
                    disabled={formData.faculty_type === 'Class Handling'}
                  >
                    <option value="">Select Year</option>
                    <option value="2">2nd Year</option>
                    <option value="3">3rd Year</option>
                    <option value="4">4th Year</option>
                  </select>
                ) : (
                  <div className="input-field bg-gray-50 text-sm sm:text-base">
                    {facultyData?.assigned_year ? `${facultyData.assigned_year}nd/rd/th Year` : 'Not assigned'}
                  </div>
                )}
                {formData.faculty_type === 'Class Handling' && editMode && (
                  <p className="text-xs text-gray-500 mt-1 italic">
                    Not required for Class Handling faculty
                  </p>
                )}
              </div>

              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">
                  Assigned Section
                </label>
                {editMode ? (
                  <select
                    value={formData.assigned_section}
                    onChange={(e) => setFormData({ ...formData, assigned_section: e.target.value })}
                    className="input-field text-sm sm:text-base"
                    disabled={formData.faculty_type === 'Class Handling'}
                  >
                    <option value="">All Sections</option>
                    <option value="A">Section A</option>
                    <option value="B">Section B</option>
                  </select>
                ) : (
                  <div className="input-field bg-gray-50 text-sm sm:text-base">
                    {facultyData?.assigned_section ? `Section ${facultyData.assigned_section}` : 'All sections'}
                  </div>
                )}
                {formData.faculty_type === 'Class Handling' && editMode && (
                  <p className="text-xs text-gray-500 mt-1 italic">
                    Not required for Class Handling faculty
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Monthly Report Information */}
          {(facultyData?.faculty_type === 'Advisor' || facultyData?.faculty_type === 'Mentor') && 
           facultyData?.assigned_year && (
            <div className="mb-4 sm:mb-6 bg-green-50 border border-green-200 rounded-lg p-3 sm:p-4">
              <h3 className="text-xs sm:text-sm font-semibold text-green-900 mb-1.5 sm:mb-2 flex items-center gap-2">
                <span className="text-base sm:text-lg">✅</span>
                <span>Monthly Report Active</span>
              </h3>
              <p className="text-xs sm:text-sm text-green-700 leading-relaxed">
                You will receive automated monthly OD reports for{' '}
                <strong>
                  Year {facultyData.assigned_year}
                  {facultyData.assigned_section ? ` - Section ${facultyData.assigned_section}` : ' (All Sections)'}
                </strong>{' '}
                students in your department.
              </p>
            </div>
          )}

          {/* Action Buttons */}
          {editMode && (
            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 sm:gap-3 pt-4 sm:pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={handleCancel}
                className="btn-secondary flex items-center justify-center gap-2 w-full sm:w-auto text-sm sm:text-base py-2 sm:py-2.5"
                disabled={saving}
              >
                <X className="h-4 w-4" />
                <span>Cancel</span>
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center justify-center gap-2 w-full sm:w-auto text-sm sm:text-base py-2 sm:py-2.5"
                disabled={saving}
              >
                <Save className="h-4 w-4" />
                <span>{saving ? 'Saving...' : 'Save Changes'}</span>
              </button>
            </div>
          )}
        </form>
        </div>
      </div>
    </div>
  );
};

export default FacultyProfile;
