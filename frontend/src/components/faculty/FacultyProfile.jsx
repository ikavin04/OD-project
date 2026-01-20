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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Faculty Profile</h1>
          {!editMode && (
            <button
              onClick={() => setEditMode(true)}
              className="btn-primary"
            >
              Edit Profile
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          {/* Basic Information */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2 text-blue-600" />
              Basic Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <div className="input-field bg-gray-50" disabled>
                  {facultyData?.name}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Building className="inline h-4 w-4 mr-1" />
                  Department
                </label>
                <div className="input-field bg-gray-50" disabled>
                  {facultyData?.department}
                </div>
              </div>
            </div>
          </div>

          {/* Class Assignment - Important for Monthly Reports */}
          <div className="mb-8 border-t border-gray-200 pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
              <Users className="h-5 w-5 mr-2 text-blue-600" />
              Class Assignment
            </h2>
            <p className="text-sm text-gray-600 mb-4 bg-blue-50 p-3 rounded-lg border border-blue-200">
              📧 <strong>Monthly Report Notification:</strong> If you are an Advisor or Mentor with an assigned class,
              you will automatically receive monthly OD reports for your students via email.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Faculty Type <span className="text-red-500">*</span>
                </label>
                {editMode ? (
                  <select
                    value={formData.faculty_type}
                    onChange={(e) => setFormData({ ...formData, faculty_type: e.target.value })}
                    className="input-field"
                    required
                  >
                    <option value="">Select Type</option>
                    <option value="Advisor">Advisor</option>
                    <option value="Mentor">Mentor</option>
                    <option value="Class Handling">Class Handling</option>
                  </select>
                ) : (
                  <div className="input-field bg-gray-50" disabled>
                    {facultyData?.faculty_type || 'Not assigned'}
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Advisors & Mentors receive monthly reports
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Assigned Year
                </label>
                {editMode ? (
                  <select
                    value={formData.assigned_year}
                    onChange={(e) => setFormData({ ...formData, assigned_year: e.target.value })}
                    className="input-field"
                  >
                    <option value="">Select Year</option>
                    <option value="2">2nd Year</option>
                    <option value="3">3rd Year</option>
                    <option value="4">4th Year</option>
                  </select>
                ) : (
                  <div className="input-field bg-gray-50" disabled>
                    {facultyData?.assigned_year ? `${facultyData.assigned_year}nd/rd/th Year` : 'Not assigned'}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Assigned Section
                </label>
                {editMode ? (
                  <select
                    value={formData.assigned_section}
                    onChange={(e) => setFormData({ ...formData, assigned_section: e.target.value })}
                    className="input-field"
                  >
                    <option value="">All Sections</option>
                    <option value="A">Section A</option>
                    <option value="B">Section B</option>
                  </select>
                ) : (
                  <div className="input-field bg-gray-50" disabled>
                    {facultyData?.assigned_section ? `Section ${facultyData.assigned_section}` : 'All sections'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Monthly Report Information */}
          {(facultyData?.faculty_type === 'Advisor' || facultyData?.faculty_type === 'Mentor') && 
           facultyData?.assigned_year && (
            <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-green-900 mb-2">
                ✅ Monthly Report Active
              </h3>
              <p className="text-sm text-green-700">
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
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={handleCancel}
                className="btn-secondary flex items-center"
                disabled={saving}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center"
                disabled={saving}
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default FacultyProfile;
