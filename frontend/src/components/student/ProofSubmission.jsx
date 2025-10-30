import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  Upload, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Calendar,
  FileText,
  MapPin
} from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../utils/api';

function ProofSubmission() {
  const { user } = useAuth();
  const [odRequests, setOdRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submittingProof, setSubmittingProof] = useState({});
  const [selectedFiles, setSelectedFiles] = useState({});

  useEffect(() => {
    fetchApprovedODRequests();
  }, []);

  const fetchApprovedODRequests = async () => {
    try {
      const response = await api.get('/od-requests');
      // Filter for approved requests only
      const approvedRequests = (response.data.od_requests || []).filter(
        req => req.status === 'approved'
      );
      setOdRequests(approvedRequests);
    } catch (error) {
      console.error('Failed to fetch approved OD requests:', error);
      toast.error('Failed to load OD requests');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (odId, proofType, file) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
    
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload only image files (JPEG, PNG, GIF) or PDF documents');
      return;
    }
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      toast.error('File size must be less than 10MB');
      return;
    }
    
    setSelectedFiles(prev => ({
      ...prev,
      [`${odId}-${proofType}`]: file
    }));
  };

  const submitProof = async (odId, proofType) => {
    const fileKey = `${odId}-${proofType}`;
    const file = selectedFiles[fileKey];
    
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setSubmittingProof(prev => ({ ...prev, [fileKey]: true }));

    try {
      const formData = new FormData();
      formData.append(proofType === 'attendance' ? 'attendance_proof' : 'certificate', file);

      const endpoint = proofType === 'attendance' 
        ? `/od-requests/${odId}/submit-attendance-proof` 
        : `/od-requests/${odId}/submit-certificate`;

      await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success(`${proofType === 'attendance' ? 'Attendance proof' : 'Certificate'} submitted successfully!`);
      
      // Clear selected file
      setSelectedFiles(prev => {
        const updated = { ...prev };
        delete updated[fileKey];
        return updated;
      });
      
      // Refresh data
      fetchApprovedODRequests();
    } catch (error) {
      toast.error(error.response?.data?.message || `Failed to submit ${proofType} proof`);
    } finally {
      setSubmittingProof(prev => ({ ...prev, [fileKey]: false }));
    }
  };

  const getProofStatusInfo = (odRequest) => {
    const now = new Date();
    const deadlines = odRequest.deadlines || {};
    
    let attendanceStatus = 'pending';
    let certificateStatus = 'not_available';
    let attendanceDaysLeft = null;
    let certificateDaysLeft = null;

    // Check attendance proof status
    if (odRequest.attendance_proof) {
      attendanceStatus = 'completed';
    } else if (deadlines.attendance_proof_deadline) {
      const deadline = new Date(deadlines.attendance_proof_deadline);
      attendanceDaysLeft = differenceInDays(deadline, now);
      
      if (attendanceDaysLeft < 0) {
        attendanceStatus = 'overdue';
      } else {
        attendanceStatus = 'pending';
      }
    }

    // Check certificate status
    if (odRequest.certificate) {
      certificateStatus = 'completed';
    } else if (odRequest.attendance_proof && deadlines.certificate_deadline) {
      const deadline = new Date(deadlines.certificate_deadline);
      certificateDaysLeft = differenceInDays(deadline, now);
      
      if (certificateDaysLeft < 0) {
        certificateStatus = 'overdue';
      } else {
        certificateStatus = 'pending';
      }
    } else if (odRequest.attendance_proof) {
      certificateStatus = 'pending';
    }

    return {
      attendanceStatus,
      certificateStatus,
      attendanceDaysLeft,
      certificateDaysLeft,
      deadlines
    };
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50 border-green-200';
      case 'pending': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'overdue': return 'text-red-600 bg-red-50 border-red-200';
      case 'not_available': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5" />;
      case 'pending': return <Clock className="h-5 w-5" />;
      case 'overdue': return <AlertCircle className="h-5 w-5" />;
      default: return <FileText className="h-5 w-5" />;
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Proof Submission</h1>
        <p className="text-gray-600 mt-1">Submit attendance proof and certificates for your approved OD requests</p>
      </div>

      {/* Important Instructions */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-6 w-6 text-blue-600 mt-1" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Important Instructions</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Step 1:</strong> Submit attendance proof (event brochure/live photo) within 3 days after OD approval</li>
              <li>• <strong>Step 2:</strong> Submit participation certificate within 1 month after attendance proof submission</li>
              <li>• <strong>Note:</strong> You cannot apply for new OD requests until all proofs are submitted</li>
            </ul>
          </div>
        </div>
      </div>

      {/* OD Requests List */}
      <div className="space-y-6">
        {odRequests.length === 0 ? (
          <div className="card text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No approved OD requests found</p>
            <p className="text-sm text-gray-400 mt-1">Complete OD requests will appear here for proof submission</p>
          </div>
        ) : (
          odRequests.map((odRequest) => {
            const statusInfo = getProofStatusInfo(odRequest);
            
            return (
              <div key={odRequest.id} className="card">
                {/* OD Details Header */}
                <div className="border-b border-gray-200 pb-4 mb-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">{odRequest.event_name}</h3>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {format(new Date(odRequest.from_date), 'MMM dd')} - {format(new Date(odRequest.to_date), 'MMM dd, yyyy')}
                        </div>
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {odRequest.host_institution}
                        </div>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
                      Approved
                    </span>
                  </div>
                </div>

                {/* Proof Submission Sections */}
                <div className="space-y-6">
                  {/* Attendance Proof Section */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full border ${getStatusColor(statusInfo.attendanceStatus)}`}>
                          {getStatusIcon(statusInfo.attendanceStatus)}
                          <span className="font-medium">
                            {statusInfo.attendanceStatus === 'completed' ? 'Completed' :
                             statusInfo.attendanceStatus === 'overdue' ? 'Overdue' :
                             statusInfo.attendanceStatus === 'pending' ? 'Pending' : 'Not Available'}
                          </span>
                        </div>
                        {statusInfo.attendanceDaysLeft !== null && statusInfo.attendanceStatus === 'pending' && (
                          <span className="text-sm text-gray-600">
                            {statusInfo.attendanceDaysLeft} day{statusInfo.attendanceDaysLeft !== 1 ? 's' : ''} left
                          </span>
                        )}
                      </div>
                      {statusInfo.deadlines.attendance_proof_deadline && (
                        <span className="text-sm text-gray-500">
                          Due: {format(new Date(statusInfo.deadlines.attendance_proof_deadline), 'MMM dd, yyyy')}
                        </span>
                      )}
                    </div>

                    <h4 className="font-medium text-gray-900 mb-2">Attendance Proof</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      Upload event brochure, live photo, or any document that proves your attendance at the event.
                    </p>

                    {odRequest.attendance_proof ? (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="h-5 w-5" />
                        <span className="text-sm font-medium">
                          Submitted: {odRequest.attendance_proof.filename}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({format(new Date(odRequest.attendance_proof.uploaded_at), 'MMM dd, yyyy')})
                        </span>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <input
                          type="file"
                          accept="image/*,application/pdf"
                          onChange={(e) => handleFileSelect(odRequest.id, 'attendance', e.target.files[0])}
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        {selectedFiles[`${odRequest.id}-attendance`] && (
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-green-600">
                              ✓ Selected: {selectedFiles[`${odRequest.id}-attendance`].name}
                            </span>
                            <button
                              onClick={() => submitProof(odRequest.id, 'attendance')}
                              disabled={submittingProof[`${odRequest.id}-attendance`]}
                              className="btn-primary text-sm disabled:opacity-50"
                            >
                              {submittingProof[`${odRequest.id}-attendance`] ? 'Submitting...' : 'Submit Attendance Proof'}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Certificate Section */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full border ${getStatusColor(statusInfo.certificateStatus)}`}>
                          {getStatusIcon(statusInfo.certificateStatus)}
                          <span className="font-medium">
                            {statusInfo.certificateStatus === 'completed' ? 'Completed' :
                             statusInfo.certificateStatus === 'overdue' ? 'Overdue' :
                             statusInfo.certificateStatus === 'pending' ? 'Pending' : 'Not Available'}
                          </span>
                        </div>
                        {statusInfo.certificateDaysLeft !== null && statusInfo.certificateStatus === 'pending' && (
                          <span className="text-sm text-gray-600">
                            {statusInfo.certificateDaysLeft} day{statusInfo.certificateDaysLeft !== 1 ? 's' : ''} left
                          </span>
                        )}
                      </div>
                      {statusInfo.deadlines.certificate_deadline && (
                        <span className="text-sm text-gray-500">
                          Due: {format(new Date(statusInfo.deadlines.certificate_deadline), 'MMM dd, yyyy')}
                        </span>
                      )}
                    </div>

                    <h4 className="font-medium text-gray-900 mb-2">Participation Certificate</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      Upload your participation certificate received from the event organizers.
                    </p>

                    {odRequest.certificate ? (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="h-5 w-5" />
                        <span className="text-sm font-medium">
                          Submitted: {odRequest.certificate.filename}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({format(new Date(odRequest.certificate.uploaded_at), 'MMM dd, yyyy')})
                        </span>
                      </div>
                    ) : !odRequest.attendance_proof ? (
                      <div className="flex items-center space-x-2 text-gray-500">
                        <AlertCircle className="h-5 w-5" />
                        <span className="text-sm">
                          Submit attendance proof first before uploading certificate
                        </span>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <input
                          type="file"
                          accept="image/*,application/pdf"
                          onChange={(e) => handleFileSelect(odRequest.id, 'certificate', e.target.files[0])}
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        {selectedFiles[`${odRequest.id}-certificate`] && (
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-green-600">
                              ✓ Selected: {selectedFiles[`${odRequest.id}-certificate`].name}
                            </span>
                            <button
                              onClick={() => submitProof(odRequest.id, 'certificate')}
                              disabled={submittingProof[`${odRequest.id}-certificate`]}
                              className="btn-primary text-sm disabled:opacity-50"
                            >
                              {submittingProof[`${odRequest.id}-certificate`] ? 'Submitting...' : 'Submit Certificate'}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default ProofSubmission;