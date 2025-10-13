import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Plus, 
  Calendar, 
  MapPin, 
  Upload,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../utils/api';

// Coimbatore institutions list
const COIMBATORE_INSTITUTIONS = [
  'KPR Institute of Engineering and Technology',
  'PSG College of Technology',
  'PPG Institute of Technology ppgit',
  'Adithya Institute of Technology',
  'Akshaya College of Engineering and Technology',
  'Amrita School of Engineering',
  'Arjun College of Technology',
  'Coimbatore Institute of Technology',
  'Coimbatore Institute of Engineering and Technology',
  'Dr.N.G.P.Institute of technology',
  'Government College of Technology',
  'Hindusthan Institute of Technology',
  'Indus College of Engineering Coimbatore',
  'Info Institute of Engineering',
  'JCT College of Engineering and Technology',
  'Kathir College of Engineering',
  'Kalaignar Karunanidhi Institute of Technology',
  'Kalaivani College of Technology',
  'Karpagam College of Engineering',
  'Karpagam Institute of Technology, Coimbatore',
  'KTVR Knowledge Park for Engineering and Technology',
  'Kumaraguru College of Technology',
  'Maharaja Institute of Technology',
  'Park College of Engineering and Technology',
  'PPG Institute of Technology',
  'PSG Institute of Technology and Applied Research',
  'SNS College of Engineering',
  'SNS College of Technology',
  'Sri Krishna College of Engineering & Technology',
  'Sri Eshwar College of Engineering',
  'Sri Ramakrishna Institute of Technology',
  'Sri Shakthi Institute of Engineering and Technology',
  'Sri Ramakrishna Engineering College',
  'Tamil Nadu College of Engineering',
  'VSB College of Engineering and Technical Campus',
  'PPG College of Arts and Science',
  'ppg college of arts and science',
  'KPR College of Arts, Science and Research',
  'PSG College of Arts and Science',
  'CBM College of Arts and Science',
  'Dr.N.G.P.Arts and science college',
  'Government Arts College',
  'Hindusthan College of Arts and Science',
  'KG College of Arts and Science',
  'Nirmala College for Women',
  'Sankara College of Science and Commerce',
  'Shri Nehru Maha Vidyalaya College of Arts and Science',
  'Sri Krishna Arts and Science College',
  'Sri Ramakrishna College of Arts and Science for Women',
  'Sri Ramakrishna Mission Vidyalaya College of Arts And Science',
  'Sree Narayana Guru College',
  'Rathinam College of Arts and Science'
];

function StudentDashboard() {
  const { user } = useAuth();
  const [odRequests, setOdRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewRequestForm, setShowNewRequestForm] = useState(false);
  const [pendingProofs, setPendingProofs] = useState([]);
  const [newRequest, setNewRequest] = useState({
    event_name: '',
    from_date: '',
    to_date: '',
    venue: '',
    event_description: '',
    od_type: '',
    host_institution: '',
    location_type: ''
  });
  const [permissionImage, setPermissionImage] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchODRequests();
    fetchPendingProofs();
  }, []);

  const fetchODRequests = async () => {
    try {
      const response = await api.get('/od/my-requests');
      setOdRequests(response.data.od_requests || []);
    } catch (error) {
      if (error.response?.status === 401) {
        console.error('Authentication error. User needs to login again.');
        // Clear any invalid tokens
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
        // Redirect to login
        window.location.href = '/login';
      } else {
        console.error('Failed to fetch OD requests:', error);
        toast.error('Failed to load OD requests');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingProofs = async () => {
    try {
      const response = await api.get('/od/my-requests?status=approved');
      const approvedRequests = response.data.od_requests || [];
      
      // Filter for requests that need proof submission
      const needingProofs = approvedRequests.filter(request => {
        const deadlines = request.deadlines || {};
        const now = new Date();
        
        // Check if attendance proof is overdue
        if (!request.attendance_proof && deadlines.attendance_proof_deadline) {
          const deadline = new Date(deadlines.attendance_proof_deadline);
          if (deadline < now) return true;
        }
        
        // Check if certificate is overdue
        if (request.attendance_proof && !request.certificate && deadlines.certificate_deadline) {
          const deadline = new Date(deadlines.certificate_deadline);
          if (deadline < now) return true;
        }
        
        return false;
      });
      
      setPendingProofs(needingProofs);
    } catch (error) {
      console.error('Failed to fetch pending proofs:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewRequest(prev => {
      const updated = {
        ...prev,
        [name]: value
      };
      
      // Auto-fill host institution when intra-college is selected
      if (name === 'od_type' && value === 'intra_college') {
        updated.host_institution = 'KGISL Institute of Technology';
        updated.location_type = ''; // Clear location type for intra-college
      } else if (name === 'od_type' && value === 'inter_college_coimbatore') {
        // Clear host institution and auto-set location type for Coimbatore
        updated.host_institution = '';
        updated.location_type = 'within_state'; // Auto-select within state for Coimbatore
      } else if (name === 'od_type' && value === 'inter_college_others') {
        // Clear host institution when switching to inter-college others
        updated.host_institution = '';
        updated.location_type = ''; // Let user choose for others
      } else if (name === 'od_type' && value !== 'inter_college_coimbatore' && value !== 'inter_college_others') {
        // Clear location type if switching away from inter-college
        updated.location_type = '';
      }
      
      return updated;
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please upload only image files (JPEG, JPG, PNG, GIF)');
        e.target.value = '';
        return;
      }
      
      // Validate file size (max 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        alert('File size must be less than 5MB');
        e.target.value = '';
        return;
      }
      
      setPermissionImage(file);
    }
  };

  const handleSubmitRequest = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      
      // Append all form fields
      Object.keys(newRequest).forEach(key => {
        formData.append(key, newRequest[key]);
      });
      
      // Append permission image as the application file
      if (permissionImage) {
        formData.append('application_file', permissionImage);
      } else {
        throw new Error('Permission document is required');
      }

      await api.post('/od/request', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      toast.success('OD request submitted successfully!');
      setShowNewRequestForm(false);
      setNewRequest({
        event_name: '',
        from_date: '',
        to_date: '',
        venue: '',
        event_description: '',
        od_type: '',
        host_institution: '',
        location_type: ''
      });
      setPermissionImage(null);
      fetchODRequests();
      fetchPendingProofs();
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please refresh the page and try again.');
      } else {
        toast.error(error.response?.data?.message || 'Failed to submit request');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-yellow-600';
      case 'approved': return 'text-green-600';
      case 'rejected': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'approved': return <CheckCircle className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Student Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome, {user?.name}</p>
        </div>
        <button
          onClick={() => setShowNewRequestForm(!showNewRequestForm)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>New OD Request</span>
        </button>
      </div>

      {/* Overdue Proof Notifications */}
      {pendingProofs.length > 0 && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-6 w-6 text-red-600 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-900 mb-2">Urgent: Overdue Proof Submissions</h3>
              <p className="text-sm text-red-800 mb-3">
                You have {pendingProofs.length} OD request{pendingProofs.length > 1 ? 's' : ''} with overdue proof submissions. 
                You cannot apply for new OD requests until these are completed.
              </p>
              <div className="space-y-2">
                {pendingProofs.map((request) => {
                  const deadlines = request.deadlines || {};
                  const now = new Date();
                  let overdueType = '';
                  let daysOverdue = 0;
                  
                  if (!request.attendance_proof && deadlines.attendance_proof_deadline) {
                    const deadline = new Date(deadlines.attendance_proof_deadline);
                    if (deadline < now) {
                      overdueType = 'Attendance Proof';
                      daysOverdue = Math.abs(differenceInDays(now, deadline));
                    }
                  } else if (request.attendance_proof && !request.certificate && deadlines.certificate_deadline) {
                    const deadline = new Date(deadlines.certificate_deadline);
                    if (deadline < now) {
                      overdueType = 'Certificate';
                      daysOverdue = Math.abs(differenceInDays(now, deadline));
                    }
                  }
                  
                  return (
                    <div key={request.id} className="text-sm text-red-700 bg-red-100 rounded p-2">
                      <strong>{request.event_name}</strong> - {overdueType} overdue by {daysOverdue} day{daysOverdue > 1 ? 's' : ''}
                    </div>
                  );
                })}
              </div>
              <Link
                to="/student/proofs"
                className="inline-flex items-center space-x-1 mt-3 text-sm font-medium text-red-700 hover:text-red-900"
              >
                <Upload className="h-4 w-4" />
                <span>Submit Proofs Now</span>
                <ExternalLink className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* New Request Form */}
      {showNewRequestForm && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Submit New OD Request</h2>
          
          <form onSubmit={handleSubmitRequest} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="event_name" className="block text-sm font-medium text-gray-700">
                  Event Name *
                </label>
                <input
                  type="text"
                  id="event_name"
                  name="event_name"
                  required
                  value={newRequest.event_name}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                  placeholder="e.g., Technical Symposium, Conference, etc."
                />
              </div>

              <div>
                <label htmlFor="od_type" className="block text-sm font-medium text-gray-700">
                  OD Type *
                </label>
                <select
                  id="od_type"
                  name="od_type"
                  required
                  value={newRequest.od_type}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                >
                  <option value="">Select OD Type</option>
                  <option value="intra_college">Intra-college</option>
                  <option value="inter_college_coimbatore">Inter-college-Coimbatore</option>
                  <option value="inter_college_others">Inter-college-Others</option>
                </select>
              </div>

              {(newRequest.od_type === 'inter_college_coimbatore' || newRequest.od_type === 'inter_college_others') && (
                <div>
                  <label htmlFor="location_type" className="block text-sm font-medium text-gray-700">
                    Location Type *
                  </label>
                  <select
                    id="location_type"
                    name="location_type"
                    required
                    value={newRequest.location_type}
                    onChange={handleInputChange}
                    disabled={newRequest.od_type === 'inter_college_coimbatore'}
                    className={`input-field mt-1 ${newRequest.od_type === 'inter_college_coimbatore' ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                  >
                    <option value="">Select Location Type</option>
                    <option value="within_state">Within State</option>
                    <option value="out_of_state">Out of State</option>
                  </select>
                  {newRequest.od_type === 'inter_college_coimbatore' && (
                    <p className="mt-1 text-xs text-gray-500">
                      Automatically set to "Within State" for Coimbatore institutions
                    </p>
                  )}
                </div>
              )}

              <div>
                <label htmlFor="host_institution" className="block text-sm font-medium text-gray-700">
                  Host Institution *
                </label>
                {newRequest.od_type === 'inter_college_coimbatore' ? (
                  <select
                    id="host_institution"
                    name="host_institution"
                    required
                    value={newRequest.host_institution}
                    onChange={handleInputChange}
                    className="input-field mt-1"
                  >
                    <option value="">Select Institution</option>
                    {COIMBATORE_INSTITUTIONS.map((institution, index) => (
                      <option key={index} value={institution}>
                        {institution}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="text"
                    id="host_institution"
                    name="host_institution"
                    required
                    value={newRequest.host_institution}
                    onChange={handleInputChange}
                    className="input-field mt-1"
                    placeholder={newRequest.od_type === 'intra_college' ? 'Auto-filled for intra-college' : 'e.g., IIT Madras, Chennai'}
                    readOnly={newRequest.od_type === 'intra_college'}
                  />
                )}
              </div>

              <div>
                <label htmlFor="from_date" className="block text-sm font-medium text-gray-700">
                  Start Date *
                </label>
                <input
                  type="date"
                  id="from_date"
                  name="from_date"
                  required
                  value={newRequest.from_date}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                />
              </div>

              <div>
                <label htmlFor="to_date" className="block text-sm font-medium text-gray-700">
                  End Date *
                </label>
                <input
                  type="date"
                  id="to_date"
                  name="to_date"
                  required
                  value={newRequest.to_date}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                />
              </div>
            </div>

            <div>
              <label htmlFor="event_description" className="block text-sm font-medium text-gray-700">
                Event Description
              </label>
              <textarea
                id="event_description"
                name="event_description"
                rows="3"
                value={newRequest.event_description}
                onChange={handleInputChange}
                className="input-field mt-1"
                placeholder="Additional details about the event..."
              />
            </div>

            <div>
              <label htmlFor="permission_image" className="block text-sm font-medium text-gray-700">
                Permission Document *
              </label>
              <input
                type="file"
                id="permission_image"
                name="permission_image"
                accept="image/jpeg,image/jpg,image/png,image/gif"
                onChange={handleFileChange}
                required
                className="mt-1 block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-medium
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
              />
              <p className="mt-1 text-xs text-gray-500">
                Upload permission document in image format (JPEG, PNG, GIF). Max size: 5MB
              </p>
              {permissionImage && (
                <p className="mt-2 text-sm text-green-600">
                  ✓ Selected: {permissionImage.name}
                </p>
              )}
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={submitting}
                className="btn-primary disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit Request'}
              </button>
              <button
                type="button"
                onClick={() => setShowNewRequestForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* OD Requests List */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Your OD Requests</h2>
        
        {odRequests.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No OD requests found</p>
            <p className="text-sm text-gray-400 mt-1">Submit your first OD request to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {odRequests.map((request) => (
              <div key={request.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`flex items-center space-x-2 ${getStatusColor(request.status)}`}>
                      {getStatusIcon(request.status)}
                      <span className="font-medium capitalize">{request.status}</span>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">#{request.id}</span>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">{request.event_name}</h3>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span className="text-sm">
                      {format(new Date(request.from_date), 'MMM dd, yyyy')} - {format(new Date(request.to_date), 'MMM dd, yyyy')}
                    </span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <MapPin className="h-4 w-4 mr-2" />
                    <span className="text-sm">{request.host_institution || request.venue || 'N/A'}</span>
                    {(request.od_type === 'inter_college_coimbatore' || request.od_type === 'inter_college_others') && request.location_type && (
                      <span className="ml-2 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                        {request.location_type === 'within_state' ? 'Within State' : 'Out of State'}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600">
                    Submitted: {format(new Date(request.created_at), 'MMM dd, yyyy')}
                  </div>
                </div>

                {request.event_description && (
                  <p className="text-gray-600 text-sm mb-4">{request.event_description}</p>
                )}

                {/* Proof Submission Section */}
                {request.status === 'pending' && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Upload className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">Proof Submission</span>
                    </div>
                    <p className="text-xs text-blue-600 mb-3">
                      After approval, you'll need to submit attendance proof within 3 days and certificate within 1 month.
                    </p>
                    <div className="space-y-2">
                      <div className="text-xs text-gray-600">
                        <strong>Step 1:</strong> Attendance Proof (event brochure/live photo) - Due 3 days after approval
                      </div>
                      <div className="text-xs text-gray-600">
                        <strong>Step 2:</strong> Participation Certificate - Due 1 month after attendance proof
                      </div>
                    </div>
                  </div>
                )}

                {request.status === 'approved' && (
                  <div className="mt-4">
                    {(() => {
                      const deadlines = request.deadlines || {};
                      const now = new Date();
                      const hasAttendanceProof = !!request.attendance_proof;
                      const hasCertificate = !!request.certificate;
                      
                      if (hasCertificate) {
                        return (
                          <div className="flex items-center p-3 bg-green-50 border border-green-200 rounded-lg">
                            <CheckCircle className="h-5 w-5 text-green-600 mr-3" />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-green-800">
                                All proofs submitted
                              </p>
                              <p className="text-xs text-green-600 mt-1">
                                Attendance proof and certificate completed
                              </p>
                            </div>
                          </div>
                        );
                      } else if (hasAttendanceProof) {
                        const certificateDeadline = deadlines.certificate_deadline ? new Date(deadlines.certificate_deadline) : null;
                        const daysLeft = certificateDeadline ? differenceInDays(certificateDeadline, now) : null;
                        const isOverdue = certificateDeadline && certificateDeadline < now;
                        
                        return (
                          <div className={`flex items-center p-3 border rounded-lg ${
                            isOverdue ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
                          }`}>
                            <AlertCircle className={`h-5 w-5 mr-3 ${
                              isOverdue ? 'text-red-600' : 'text-yellow-600'
                            }`} />
                            <div className="flex-1">
                              <p className={`text-sm font-medium ${
                                isOverdue ? 'text-red-800' : 'text-yellow-800'
                              }`}>
                                {isOverdue ? 'Certificate submission overdue' : 'Certificate submission pending'}
                              </p>
                              <p className={`text-xs mt-1 ${
                                isOverdue ? 'text-red-600' : 'text-yellow-600'
                              }`}>
                                {isOverdue 
                                  ? `Overdue by ${Math.abs(daysLeft)} day${Math.abs(daysLeft) > 1 ? 's' : ''}`
                                  : daysLeft !== null 
                                    ? `${daysLeft} day${daysLeft !== 1 ? 's' : ''} remaining`
                                    : 'Deadline not set'
                                }
                              </p>
                            </div>
                            <Link
                              to="/student/proofs"
                              className="text-xs font-medium text-blue-600 hover:text-blue-800"
                            >
                              Submit Now
                            </Link>
                          </div>
                        );
                      } else {
                        const attendanceDeadline = deadlines.attendance_proof_deadline ? new Date(deadlines.attendance_proof_deadline) : null;
                        const daysLeft = attendanceDeadline ? differenceInDays(attendanceDeadline, now) : null;
                        const isOverdue = attendanceDeadline && attendanceDeadline < now;
                        
                        return (
                          <div className={`flex items-center p-3 border rounded-lg ${
                            isOverdue ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
                          }`}>
                            <AlertCircle className={`h-5 w-5 mr-3 ${
                              isOverdue ? 'text-red-600' : 'text-yellow-600'
                            }`} />
                            <div className="flex-1">
                              <p className={`text-sm font-medium ${
                                isOverdue ? 'text-red-800' : 'text-yellow-800'
                              }`}>
                                {isOverdue ? 'Attendance proof overdue' : 'Attendance proof required'}
                              </p>
                              <p className={`text-xs mt-1 ${
                                isOverdue ? 'text-red-600' : 'text-yellow-600'
                              }`}>
                                {isOverdue 
                                  ? `Overdue by ${Math.abs(daysLeft)} day${Math.abs(daysLeft) > 1 ? 's' : ''}`
                                  : daysLeft !== null 
                                    ? `${daysLeft} day${daysLeft !== 1 ? 's' : ''} remaining`
                                    : 'Submit within 3 days of approval'
                                }
                              </p>
                            </div>
                            <Link
                              to="/student/proofs"
                              className="text-xs font-medium text-blue-600 hover:text-blue-800"
                            >
                              Submit Now
                            </Link>
                          </div>
                        );
                      }
                    })()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentDashboard;