import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Search, 
  Filter,
  Eye,
  Check,
  X,
  Calendar,
  MapPin,
  User,
  Download
} from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../utils/api';

const FacultyDashboard = () => {
  const { user } = useAuth();
  const [odRequests, setOdRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    fetchODRequests();
  }, []);

  const fetchODRequests = async () => {
    try {
      console.log('Fetching OD requests for faculty...');
      const response = await api.get('/faculty/od-requests');
      console.log('Faculty OD requests response:', response.data);
      setOdRequests(response.data.od_requests || []);
    } catch (error) {
      console.error('API Error:', error);
      console.error('Response data:', error.response?.data);
      
      if (error.response?.status === 401) {
        // Handle authentication errors gracefully
        console.log('Authentication error - user may need to re-login');
        toast.error('Session expired. Please refresh the page to continue.');
        setOdRequests([]); // Show empty state instead of crashing
      } else {
        toast.error('Failed to fetch OD requests. Please try again later.');
        setOdRequests([]); // Show empty state for other errors too
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApproveReject = async (requestId, action, reason = '') => {
    setActionLoading(requestId);
    try {
      await api.post(`/faculty/od-request/${requestId}/${action}`, 
        action === 'reject' ? { reason } : {}
      );
      toast.success(`Request ${action}ed successfully!`);
      fetchODRequests();
      setShowModal(false);
      setSelectedRequest(null);
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please refresh the page and try again.');
      } else {
        toast.error(error.response?.data?.message || `Failed to ${action} request`);
      }
    } finally {
      setActionLoading(null);
    }
  };

  const filteredRequests = odRequests.filter(request => {
    const matchesSearch = request.student_info?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.student_info?.roll_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.event_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || request.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'status-badge status-pending';
      case 'approved':
        return 'status-badge status-approved';
      case 'rejected':
        return 'status-badge status-rejected';
      default:
        return 'status-badge bg-gray-100 text-gray-800';
    }
  };

  const RequestDetailsModal = () => {
    const [rejectionReason, setRejectionReason] = useState('');

    if (!selectedRequest) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">OD Request Details</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Student Information */}
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Student Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Name</label>
                    <p className="text-gray-900">{selectedRequest.student_info?.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Roll Number</label>
                    <p className="text-gray-900">{selectedRequest.student_info?.roll_number}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Email</label>
                    <p className="text-gray-900">{selectedRequest.student_info?.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Department</label>
                    <p className="text-gray-900">{selectedRequest.student_info?.department}</p>
                  </div>
                </div>
              </div>

              {/* Request Information */}
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Request Details</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Event Name</label>
                    <p className="text-gray-900">{selectedRequest.event_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Host Institution</label>
                    <p className="text-gray-900">{selectedRequest.host_institution || selectedRequest.venue || 'N/A'}</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Start Date</label>
                      <p className="text-gray-900">{format(new Date(selectedRequest.from_date), 'MMM dd, yyyy')}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">End Date</label>
                      <p className="text-gray-900">{format(new Date(selectedRequest.to_date), 'MMM dd, yyyy')}</p>
                    </div>
                  </div>
                  {selectedRequest.event_description && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Description</label>
                      <p className="text-gray-900">{selectedRequest.event_description}</p>
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium text-gray-600">Status</label>
                    <span className={getStatusBadgeClass(selectedRequest.status)}>
                      {selectedRequest.status.charAt(0).toUpperCase() + selectedRequest.status.slice(1)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              {selectedRequest.status === 'pending' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Actions</h3>
                  
                  <div className="space-y-3">
                    <button
                      onClick={() => handleApproveReject(selectedRequest.id, 'approve')}
                      disabled={actionLoading === selectedRequest.id}
                      className="btn-primary w-full flex items-center justify-center"
                    >
                      <Check className="h-5 w-5 mr-2" />
                      {actionLoading === selectedRequest.id ? 'Approving...' : 'Approve Request'}
                    </button>

                    <div className="space-y-2">
                      <textarea
                        value={rejectionReason}
                        onChange={(e) => setRejectionReason(e.target.value)}
                        placeholder="Enter reason for rejection (optional)"
                        className="input-field w-full"
                        rows="3"
                      />
                      <button
                        onClick={() => handleApproveReject(selectedRequest.id, 'reject', rejectionReason)}
                        disabled={actionLoading === selectedRequest.id}
                        className="btn-danger w-full flex items-center justify-center"
                      >
                        <X className="h-5 w-5 mr-2" />
                        {actionLoading === selectedRequest.id ? 'Rejecting...' : 'Reject Request'}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedRequest.rejection_reason && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm font-medium text-red-800">Rejection Reason:</p>
                  <p className="text-sm text-red-700">{selectedRequest.rejection_reason}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Faculty Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.name || user?.email}! Review and manage OD requests.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Requests</p>
              <p className="text-2xl font-bold text-gray-900">{odRequests.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">
                {odRequests.filter(req => req.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-gray-900">
                {odRequests.filter(req => req.status === 'approved').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">
                {odRequests.filter(req => req.status === 'rejected').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by student name, roll number, or reason..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Filter className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input-field pl-10 pr-8"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* OD Requests List */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">OD Requests</h2>
        
        {filteredRequests.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No OD requests found</p>
            <p className="text-sm text-gray-400 mt-1">Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredRequests.map((request) => (
              <div key={request.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(request.status)}
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{request.event_name}</h3>
                      <p className="text-sm text-gray-600">
                        {request.student_info?.name} ({request.student_info?.roll_number})
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={getStatusBadgeClass(request.status)}>
                      {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedRequest(request);
                        setShowModal(true);
                      }}
                      className="p-2 text-gray-400 hover:text-gray-600"
                    >
                      <Eye className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span className="text-sm">
                      {format(new Date(request.from_date), 'MMM dd')} - {format(new Date(request.to_date), 'MMM dd, yyyy')}
                    </span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <MapPin className="h-4 w-4 mr-2" />
                    <span className="text-sm">{request.host_institution || request.venue || 'N/A'}</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Submitted: {format(new Date(request.created_at), 'MMM dd, yyyy')}
                  </div>
                </div>

                {request.status === 'pending' && (
                  <div className="flex space-x-3 mt-4">
                    <button
                      onClick={() => handleApproveReject(request.id, 'approve')}
                      disabled={actionLoading === request.id}
                      className="btn-primary text-sm flex items-center"
                    >
                      <Check className="h-4 w-4 mr-1" />
                      Approve
                    </button>
                    <button
                      onClick={() => {
                        setSelectedRequest(request);
                        setShowModal(true);
                      }}
                      className="btn-danger text-sm flex items-center"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && <RequestDetailsModal />}
    </div>
  );
};

export default FacultyDashboard;