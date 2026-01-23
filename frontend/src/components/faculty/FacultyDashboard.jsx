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

// Authenticated Image Component
const AuthenticatedImage = ({ requestId, fileType, alt, className, onClick }) => {
  const [imageSrc, setImageSrc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let objectUrl = null;
    const loadImage = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await api.get(`/od/view/${requestId}/${fileType}`, {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        // Ensure the Blob has the correct MIME type so browsers can render it inline
        const contentType = response.headers['content-type'] || 'application/octet-stream';
        console.debug('[AuthenticatedImage] Loaded blob', { requestId, fileType, contentType, size: response.data?.size });
        const blob = new Blob([response.data], { type: contentType });
        objectUrl = window.URL.createObjectURL(blob);
        setImageSrc(objectUrl);
        setLoading(false);
      } catch (error) {
        console.error('Failed to load image:', error);
        setError(true);
        setLoading(false);
      }
    };

    loadImage();

    // Cleanup function to revoke the URL
    return () => {
      if (objectUrl) {
        window.URL.revokeObjectURL(objectUrl);
      }
    };
  }, [requestId, fileType]);

  if (loading) {
    return (
      <div className={`${className} flex items-center justify-center bg-secondary-100`}>
        <div className="text-sm text-secondary-500">Loading image...</div>
      </div>
    );
  }

  if (error || !imageSrc) {
    return (
      <div className={`${className} flex flex-col items-center justify-center bg-secondary-50 border-2 border-dashed border-secondary-300 rounded-lg p-4`}>
        <FileText className="h-12 w-12 text-secondary-400 mb-2" />
        <div className="text-sm text-secondary-600 font-medium">Document not available</div>
        <div className="text-xs text-secondary-500 mt-1">File may have been removed or not uploaded</div>
      </div>
    );
  }

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
      onClick={onClick}
      style={onClick ? { cursor: 'pointer' } : {}}
    />
  );
};

// Generic authenticated document preview (PDF iframe fallback)
const AuthenticatedDocument = ({ requestId, fileType, className, onClick }) => {
  const [src, setSrc] = useState(null);
  const [mime, setMime] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const loadDoc = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await api.get(`/od/view/${requestId}/${fileType}`, {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const contentType = response.headers['content-type'] || 'application/octet-stream';
        setMime(contentType);
        const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }));
        setSrc(url);
        setLoading(false);
      } catch (e) {
        console.error('Failed to load document:', e);
        setError(true);
        setLoading(false);
      }
    };
    loadDoc();
    return () => {
      if (src) window.URL.revokeObjectURL(src);
    };
  }, [requestId, fileType]);

  if (loading) {
    return (
      <div className={`${className} flex items-center justify-center bg-secondary-100`}>
        <div className="text-sm text-secondary-500">Loading document...</div>
      </div>
    );
  }
  if (error || !src) {
    return (
      <div className={`${className} flex flex-col items-center justify-center bg-secondary-50 border-2 border-dashed border-secondary-300 rounded-lg p-4`}>
        <FileText className="h-12 w-12 text-secondary-400 mb-2" />
        <div className="text-sm text-secondary-600 font-medium">Document not available</div>
      </div>
    );
  }

  if (mime && mime.startsWith('application/pdf')) {
    return (
      <iframe
        src={src}
        className={className}
        title="Document Preview"
      />
    );
  }

  // Fallback to image rendering
  return (
    <img src={src} className={className} onClick={onClick} alt="Document" />
  );
};

const FacultyDashboard = () => {
  const { user } = useAuth();
  const [odRequests, setOdRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [yearFilter, setYearFilter] = useState('all');
  const [sectionFilter, setSectionFilter] = useState('all');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const startY = React.useRef(0);
  const pullDistance = React.useRef(0);

  useEffect(() => {
    fetchODRequests();
    
    // Pull-to-refresh for mobile
    const handleTouchStart = (e) => {
      if (window.scrollY === 0) {
        startY.current = e.touches[0].pageY;
      }
    };

    const handleTouchMove = (e) => {
      if (window.scrollY === 0 && !refreshing) {
        const currentY = e.touches[0].pageY;
        pullDistance.current = currentY - startY.current;
        
        if (pullDistance.current > 80) {
          handleRefresh();
        }
      }
    };

    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchmove', handleTouchMove);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
    };
  }, [yearFilter, sectionFilter, refreshing]);

  const fetchODRequests = async () => {
    try {
      console.log('[INFO] Fetching OD requests for faculty...');
      console.log('[AUTH] Current auth token:', localStorage.getItem('token') ? 'Present' : 'Missing');
      
      // Build query parameters
      const params = {};
      if (yearFilter && yearFilter !== 'all') {
        params.year = yearFilter;
      }
      if (sectionFilter && sectionFilter !== 'all') {
        params.section = sectionFilter;
      }
      
      console.log('[FILTERS] Applying filters:', params);
      
      const response = await api.get('/faculty/od-requests', { params });
      console.log('[OK] Faculty OD requests response status:', response.status);
      console.log('[DATA] Faculty OD requests response data:', response.data);
      console.log('[STATS] Number of requests received:', response.data.od_requests?.length || 0);
      
      setOdRequests(response.data.od_requests || []);
      
      if (response.data.od_requests?.length > 0) {
        console.log('[ACTION] First request details:', response.data.od_requests[0]);
        // Use a fixed toast id to avoid duplicate toasts (React StrictMode may call effects twice)
        toast.success(`Loaded ${response.data.od_requests.length} OD requests successfully!`, { id: 'od-requests-loaded' });
      } else {
        console.log('[INFO] No OD requests found');
        // toast.info is not available in react-hot-toast, using console log instead
      }
      
    } catch (error) {
      console.error('[ERROR] API Error:', error);
      console.error('[ERROR] Error response status:', error.response?.status);
      console.error('[ERROR] Error response data:', error.response?.data);
      console.error('[ERROR] Error message:', error.message);
      
      if (error.response?.status === 401) {
        console.log('[AUTH] Authentication error - user may need to re-login');
        toast.error('Session expired. Please refresh and login again.');
        setOdRequests([]);
      } else if (error.response?.status === 403) {
        console.log('[ACCESS] Access denied - insufficient permissions');
        toast.error('Access denied. You may not have faculty permissions.');
        setOdRequests([]);
      } else {
        console.log('[ERROR] Other error occurred');
        toast.error(`Failed to fetch OD requests: ${error.response?.data?.message || error.message}`);
        setOdRequests([]);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchODRequests();
    toast.success('Refreshed!');
  };

  const handleApproveReject = async (requestId, action, reason = '') => {
    setActionLoading(requestId);
    try {
      console.log(`[ACTION] ${action}ing request ID: ${requestId}`);
      
      const endpoint = `/faculty/od-requests/${requestId}/${action}`;
      const payload = action === 'reject' ? { comments: reason } : {};
      
      console.log('[REQUEST] Sending to endpoint:', endpoint);
      console.log('[REQUEST] Payload:', payload);
      
      await api.post(endpoint, payload);
      toast.success(`Request ${action}d successfully!`);
      fetchODRequests();
      setShowModal(false);
      setSelectedRequest(null);
    } catch (error) {
      console.error(`[ERROR] Failed to ${action} request:`, error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please refresh the page and try again.');
      } else {
        toast.error(error.response?.data?.message || `Failed to ${action} request`);
      }
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownloadFile = async (requestId, fileType, originalFilename = null) => {
    try {
      console.log('Downloading file:', { requestId, fileType, originalFilename });
      const token = localStorage.getItem('token');
      console.log('Token exists:', !!token);
      
      const response = await api.get(`/od/download/${requestId}/${fileType}`, {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from multiple sources
      let filename = 'document';
      
      // First try to get from response headers
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        // Try different patterns for content-disposition
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      // Fallback to originalFilename parameter if header parsing failed
      if (filename === 'document' && originalFilename) {
        filename = originalFilename;
      }
      
      // Final fallback based on file type
      if (filename === 'document') {
        const extension = fileType === 'application' ? 'jpg' : 'pdf';
        filename = `${fileType}_${requestId}.${extension}`;
      }
      
      console.log('Final filename:', filename);
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`File "${filename}" downloaded successfully!`);
    } catch (error) {
      console.error('Failed to download file:', error);
      if (error.response?.status === 401) {
        toast.error('Authentication required. Please login again.');
      } else {
        toast.error('Failed to download file');
      }
    }
  };

  const handleViewFile = async (requestId, fileType) => {
    try {
      console.log('Viewing file:', { requestId, fileType });
      const token = localStorage.getItem('token');
      console.log('Token exists:', !!token);
      
      const response = await api.get(`/od/view/${requestId}/${fileType}`, {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Get the content type from response headers
      const contentType = response.headers['content-type'] || 'application/octet-stream';
      console.log('Content type:', contentType);
      
      // Create blob with proper MIME type
      const blob = new Blob([response.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      
      // Open in new tab/window
      const newWindow = window.open(url, '_blank');
      
      if (!newWindow) {
        // If popup was blocked, try a different approach
        const link = document.createElement('a');
        link.href = url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
      
      // Clean up the URL after a delay to allow the browser to load it
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 5000);
      
      toast.success('Opening student OD form image...');
    } catch (error) {
      console.error('Failed to view file:', error);
      if (error.response?.status === 401) {
        toast.error('Authentication required. Please login again.');
      } else {
        toast.error('Failed to view student OD form image');
      }
    }
  };

  const filteredRequests = odRequests.filter(request => {
    const matchesSearch = request.student?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.student?.roll_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.event_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || request.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-secondary-500" />;
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-primary-500" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-secondary-600" />;
      default:
        return <Clock className="h-5 w-5 text-secondary-500" />;
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
        return 'status-badge bg-secondary-100 text-secondary-800';
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
              <h2 className="text-xl font-semibold text-secondary-900">OD Request Details</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Student Information */}
              <div className="border-b border-secondary-200 pb-4">
                <h3 className="text-lg font-medium text-secondary-900 mb-3">Student Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Name</label>
                    <p className="text-secondary-900">{selectedRequest.student?.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Roll Number</label>
                    <p className="text-secondary-900">{selectedRequest.student?.roll_number}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Email</label>
                    <p className="text-secondary-900">{selectedRequest.student?.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Department</label>
                    <p className="text-secondary-900">{selectedRequest.student?.department}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Year</label>
                    <p className="text-secondary-900">{selectedRequest.student?.year ? `${selectedRequest.student.year}${selectedRequest.student.year === 1 ? 'st' : selectedRequest.student.year === 2 ? 'nd' : selectedRequest.student.year === 3 ? 'rd' : 'th'} Year` : 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Section</label>
                    <p className="text-secondary-900">{selectedRequest.student?.section || 'N/A'}</p>
                  </div>
                </div>
              </div>

              {/* Request Information */}
              <div className="border-b border-secondary-200 pb-4">
                <h3 className="text-lg font-medium text-secondary-900 mb-3">Request Details</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-secondary-600">Event Name</label>
                    <p className="text-secondary-900">{selectedRequest.event_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-secondary-600">OD Type</label>
                    <p className="text-secondary-900">
                      {selectedRequest.od_type === 'intra_college' ? 'Intra-college' :
                       selectedRequest.od_type === 'inter_college_coimbatore' ? 'Inter-college (Coimbatore)' :
                       selectedRequest.od_type === 'inter_college_others' ? 'Inter-college (Others)' :
                       selectedRequest.od_type}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Host Institution</label>
                    <p className="text-gray-900">{selectedRequest.host_institution || selectedRequest.college_name || selectedRequest.venue || 'N/A'}</p>
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
                  {selectedRequest.location_type && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Location Type</label>
                      <p className="text-gray-900">
                        {selectedRequest.location_type === 'within_state' ? 'Within State' : 
                         selectedRequest.location_type === 'out_of_state' ? 'Out of State' : 
                         selectedRequest.location_type}
                      </p>
                    </div>
                  )}
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
                  <div>
                    <label className="text-sm font-medium text-gray-600">Submitted On</label>
                    <p className="text-gray-900">{format(new Date(selectedRequest.created_at), 'MMM dd, yyyy hh:mm a')}</p>
                  </div>
                </div>
              </div>

              {/* Permission Document - CRITICAL FOR APPROVAL */}
              <div className="border-2 border-blue-200 bg-blue-50 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-3">
                  <FileText className="h-6 w-6 text-blue-600 mr-2" />
                  <h3 className="text-xl font-bold text-blue-900">Student Permission Document</h3>
                  <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full">REQUIRED FOR APPROVAL</span>
                </div>
                
                {selectedRequest.application_file ? (
                  <div className="space-y-4">
                    {/* File Information */}
                    <div className="bg-white rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center space-x-3">
                        <label className="text-sm font-semibold text-gray-700">File Name:</label>
                        <span className="text-sm font-medium text-gray-900">{selectedRequest.application_file.filename}</span>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {(selectedRequest.application_file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-3">
                      <button
                        onClick={() => handleDownloadFile(selectedRequest.id, 'application', selectedRequest.application_file.filename)}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-blue-300 shadow-sm text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download Original
                      </button>
                      <button
                        onClick={() => handleViewFile(selectedRequest.id, 'application')}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-green-300 shadow-sm text-sm font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View Document
                      </button>
                    </div>
                    
                    {/* Large Image Preview - MOST IMPORTANT */}
                    {selectedRequest.application_file.mime_type?.startsWith('image/') && (
                      <div className="bg-white rounded-lg border-2 border-gray-300 p-4">
                        <div className="text-center mb-3">
                          <h4 className="text-lg font-semibold text-gray-900">Student's Permission Document Preview</h4>
                          <p className="text-sm text-gray-600">Review this document carefully before making approval decision</p>
                        </div>
                        <div className="flex justify-center">
                          <AuthenticatedImage
                            requestId={selectedRequest.id}
                            fileType="application"
                            alt="Student Permission Document - Required for Approval"
                            className="max-w-full h-auto max-h-[600px] border-2 border-gray-400 rounded-lg shadow-lg cursor-pointer hover:shadow-xl transition-shadow"
                            onClick={() => handleViewFile(selectedRequest.id, 'application')}
                          />
                        </div>
                        <div className="mt-3 text-center">
                          <p className="text-xs text-gray-500">Click image to view in full resolution</p>
                        </div>
                      </div>
                    )}
                    
                    {/* Alert if not an image */}
                    {!selectedRequest.application_file.mime_type?.startsWith('image/') && (
                      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
                        <div className="flex items-center">
                          <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.96-.833-2.73 0L4.084 15.5c-.77.833.192 2.5 1.732 2.5z" />
                          </svg>
                          <div>
                            <h4 className="text-sm font-medium text-yellow-800">Document is not an image</h4>
                            <p className="text-sm text-yellow-700">Click "View Document" or "Download Original" to review the PDF document</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <svg className="h-6 w-6 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <h4 className="text-lg font-semibold text-red-800">No Permission Document Found</h4>
                        <p className="text-sm text-red-700">Student has not uploaded their permission document. This request cannot be approved without it.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Proof Submissions Section */}
              {selectedRequest.status === 'approved' && (
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Proof Submissions</h3>
                  <div className="text-sm text-gray-600 mb-4">
                    Status: <span className="font-semibold text-blue-600">
                      {selectedRequest.proof_submission_status === 'not_submitted' ? 'Not[Submitted]' :
                       selectedRequest.proof_submission_status === 'attendance_pending' ? 'Awaiting Attendance Proof' :
                       selectedRequest.proof_submission_status === 'certificate_pending' ? 'Awaiting Certificate' :
                       selectedRequest.proof_submission_status === 'completed' ? 'All Proofs[Submitted]' :
                       selectedRequest.proof_submission_status}
                    </span>
                  </div>

                  {/* Attendance Proof */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-800 mb-2 flex items-center">
                      <FileText className="h-5 w-5 mr-2 text-blue-600" />
                      Attendance Proof
                    </h4>
                    {selectedRequest.attendance_proof ? (
                      <div className="space-y-3">
                        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-green-800">[Submitted]</p>
                              <p className="text-xs text-green-600">
                                {selectedRequest.attendance_proof.uploaded_at && 
                                  `Uploaded: ${format(new Date(selectedRequest.attendance_proof.uploaded_at), 'MMM dd, yyyy hh:mm a')}`}
                              </p>
                              <p className="text-xs text-gray-600 mt-1">
                                File: {selectedRequest.attendance_proof.filename}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleViewFile(selectedRequest.id, 'attendance_proof')}
                                className="btn-secondary flex items-center text-sm"
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </button>
                              <button
                                onClick={() => handleDownloadFile(selectedRequest.id, 'attendance_proof', selectedRequest.attendance_proof.filename)}
                                className="btn-primary flex items-center text-sm"
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </button>
                            </div>
                          </div>
                        </div>
                        
                        {/* Attendance Proof Preview */}
                        {selectedRequest.attendance_proof.mime_type?.startsWith('image/') && (
                          <div className="bg-white rounded-lg border-2 border-green-300 p-4">
                            <div className="text-center mb-2">
                              <h5 className="text-sm font-semibold text-gray-900">Attendance Proof Preview</h5>
                            </div>
                            <div className="flex justify-center">
                              <AuthenticatedImage
                                requestId={selectedRequest.id}
                                fileType="attendance_proof"
                                alt="Attendance Proof"
                                className="max-w-full h-auto max-h-[400px] border-2 border-gray-300 rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-shadow"
                                onClick={() => handleViewFile(selectedRequest.id, 'attendance_proof')}
                              />
                            </div>
                            <div className="mt-2 text-center">
                              <p className="text-xs text-gray-500">Click to view in full size</p>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-3">
                        <div className="flex items-center">
                          <Clock className="h-5 w-5 text-yellow-500 mr-2" />
                          <div>
                            <p className="text-sm font-medium text-yellow-800">Pending</p>
                            <p className="text-xs text-yellow-700">
                              {selectedRequest.deadlines?.attendance_proof_deadline
                                ? `Deadline: ${format(new Date(selectedRequest.deadlines.attendance_proof_deadline), 'MMM dd, yyyy')}`
                                : 'Student has not[Submitted] attendance proof yet'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Certificate */}
                  <div>
                    <h4 className="text-md font-semibold text-gray-800 mb-2 flex items-center">
                      <FileText className="h-5 w-5 mr-2 text-purple-600" />
                      Participation Certificate
                    </h4>
                    {selectedRequest.certificate ? (
                      <div className="space-y-3">
                        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-green-800">[Submitted]</p>
                              <p className="text-xs text-green-600">
                                {selectedRequest.certificate.uploaded_at && 
                                  `Uploaded: ${format(new Date(selectedRequest.certificate.uploaded_at), 'MMM dd, yyyy hh:mm a')}`}
                              </p>
                              <p className="text-xs text-gray-600 mt-1">
                                File: {selectedRequest.certificate.filename}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleViewFile(selectedRequest.id, 'certificate')}
                                className="btn-secondary flex items-center text-sm"
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </button>
                              <button
                                onClick={() => handleDownloadFile(selectedRequest.id, 'certificate', selectedRequest.certificate.filename)}
                                className="btn-primary flex items-center text-sm"
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </button>
                            </div>
                          </div>
                        </div>
                        
                        {/* Certificate Preview */}
                        {selectedRequest.certificate && (
                          <div className="bg-white rounded-lg border-2 border-purple-300 p-4">
                            <div className="text-center mb-2">
                              <h5 className="text-sm font-semibold text-gray-900">Certificate Preview</h5>
                            </div>
                            <div className="flex justify-center">
                              {selectedRequest.certificate.mime_type?.startsWith('image/') ? (
                                <AuthenticatedImage
                                  requestId={selectedRequest.id}
                                  fileType="certificate"
                                  alt="Participation Certificate"
                                  className="w-full h-[400px] object-contain border-2 border-gray-300 rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-shadow"
                                  onClick={() => handleViewFile(selectedRequest.id, 'certificate')}
                                />
                              ) : selectedRequest.certificate.mime_type === 'application/pdf' ? (
                                <AuthenticatedDocument
                                  requestId={selectedRequest.id}
                                  fileType="certificate"
                                  className="w-full h-[500px] border-2 border-gray-300 rounded-lg shadow-md"
                                />
                              ) : (
                                <div className="text-sm text-gray-600">Preview not available for this file type. Use the View button.</div>
                              )}
                            </div>
                            <div className="mt-2 text-center">
                              <p className="text-xs text-gray-500">Click to view in full size</p>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3">
                        <div className="flex items-center">
                          <Clock className="h-5 w-5 text-gray-500 mr-2" />
                          <div>
                            <p className="text-sm font-medium text-gray-700">Not Yet[Submitted]</p>
                            <p className="text-xs text-gray-600">
                              {selectedRequest.attendance_proof 
                                ? selectedRequest.deadlines?.certificate_deadline
                                  ? `Deadline: ${format(new Date(selectedRequest.deadlines.certificate_deadline), 'MMM dd, yyyy')}`
                                  : 'Awaiting certificate submission'
                                : 'Certificate can be[Submitted] after attendance proof'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

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
    <div className="min-h-screen bg-transparent">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6">
        {/* Header */}
        <div className="mb-4 sm:mb-6">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900">Faculty Dashboard</h1>
          <p className="mt-1 sm:mt-2 text-xs sm:text-sm md:text-base text-gray-600">
            Welcome back, {user?.name || user?.email}! Review and manage OD requests.
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-3 sm:p-4 md:p-6 mb-4 sm:mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Search */}
            <div className="col-span-1 sm:col-span-2">
              <div className="relative">
                <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Search by student name, roll number, or event..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input-field pl-9 pr-3 w-full text-sm"
                />
              </div>
            </div>
            
            {/* Year Filter */}
            <div className="relative">
              <Filter className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
              <select
                value={yearFilter}
                onChange={(e) => setYearFilter(e.target.value)}
                className="input-field pl-9 pr-8 w-full text-sm appearance-none"
              >
                <option value="all">All Years</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
              </select>
            </div>
            
            {/* Section Filter */}
            <div className="relative">
              <Filter className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
              <select
                value={sectionFilter}
                onChange={(e) => setSectionFilter(e.target.value)}
                className="input-field pl-9 pr-8 w-full text-sm appearance-none"
              >
                <option value="all">All Sections</option>
                <option value="A">Section A</option>
                <option value="B">Section B</option>
              </select>
            </div>
            
            {/* Status Filter */}
            <div className="relative col-span-1 sm:col-span-2 lg:col-span-1">
              <Filter className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
              <select
                value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
                className="input-field pl-9 pr-8 w-full text-sm appearance-none"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            
            {/* Active Filters Display */}
            {(yearFilter !== 'all' || sectionFilter !== 'all' || statusFilter !== 'all') && (
              <div className="col-span-1 sm:col-span-2 lg:col-span-4 flex flex-wrap items-center gap-2 pt-2 border-t border-gray-100">
                <span className="text-gray-600 text-xs font-medium">Active filters:</span>
                {yearFilter !== 'all' && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                    Year: {yearFilter}
                  </span>
                )}
                {sectionFilter !== 'all' && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    Section: {sectionFilter}
                  </span>
                )}
                {statusFilter !== 'all' && (
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                    Status: {statusFilter}
                  </span>
                )}
                <button
                  onClick={() => {
                    setYearFilter('all');
                    setSectionFilter('all');
                    setStatusFilter('all');
                  }}
                  className="text-gray-500 hover:text-gray-700 underline text-xs font-medium ml-1"
                >
                  Clear all
                </button>
              </div>
            )}
          </div>
        </div>

        {/* OD Requests List */}
        <div className="bg-white rounded-lg shadow-sm p-3 sm:p-4 md:p-6">
          <h2 className="text-base sm:text-lg md:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">OD Requests</h2>
        {filteredRequests.length === 0 ? (
          <div className="text-center py-8 sm:py-10">
            <FileText className="h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-sm sm:text-base">No OD requests found</p>
            <p className="text-xs sm:text-sm text-gray-400 mt-1">Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredRequests.map((request) => (
              <div key={request.id} className="border border-gray-200 rounded-lg p-3 sm:p-4 hover:shadow-md transition-shadow">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 sm:gap-3 mb-3">
                  <div className="flex items-start gap-2">
                    {getStatusIcon(request.status)}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm sm:text-base font-medium text-gray-900 break-words leading-snug">{request.event_name}</h3>
                      <p className="text-xs text-gray-600 mt-1 leading-relaxed">
                        {request.student?.name} ({request.student?.roll_number}) - Year {request.student?.year}, Section {request.student?.section || 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 self-end sm:self-start flex-shrink-0">
                    <span className={`${getStatusBadgeClass(request.status)} text-xs`}>
                      {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedRequest(request);
                        setShowModal(true);
                      }}
                      className="p-1.5 text-gray-400 hover:text-gray-600"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3 text-xs">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-3 w-3 mr-1.5 flex-shrink-0" />
                    <span className="truncate">
                      {format(new Date(request.from_date), 'MMM dd')} - {format(new Date(request.to_date), 'MMM dd, yyyy')}
                    </span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <MapPin className="h-3 w-3 mr-1.5 flex-shrink-0" />
                    <span className="truncate">{request.host_institution || request.venue || 'N/A'}</span>
                  </div>
                  <div className="text-gray-600 truncate col-span-1 sm:col-span-2">
                   Submitted: {format(new Date(request.created_at), 'MMM dd, yyyy')}
                  </div>
                </div>

                {request.status === 'pending' && (
                  <div className="flex flex-col sm:flex-row gap-2 mt-3 pt-3 border-t border-gray-100">
                    <button
                      onClick={() => handleApproveReject(request.id, 'approve')}
                      disabled={actionLoading === request.id}
                      className="btn-primary text-xs sm:text-sm py-2 flex items-center justify-center w-full sm:flex-1"
                    >
                      <Check className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                      <span>Approve</span>
                    </button>
                    <button
                      onClick={() => {
                        setSelectedRequest(request);
                        setShowModal(true);
                      }}
                      className="btn-danger text-xs sm:text-sm py-2 flex items-center justify-center w-full sm:flex-1"
                    >
                      <X className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                      <span>Reject</span>
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
    </div>
  );
};

export default FacultyDashboard;
