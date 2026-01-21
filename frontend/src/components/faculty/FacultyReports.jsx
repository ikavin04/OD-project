import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  FileText,
  Filter,
  Download,
  Calendar,
  User,
  MapPin,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  FileSpreadsheet
} from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../utils/api';
import * as XLSX from 'xlsx';

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

        const contentType = response.headers['content-type'] || 'application/octet-stream';
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

    return () => {
      if (objectUrl) {
        window.URL.revokeObjectURL(objectUrl);
      }
    };
  }, [requestId, fileType]);

  if (loading) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-100`}>
        <div className="text-sm text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error || !imageSrc) {
    return (
      <div className={`${className} flex flex-col items-center justify-center bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-4`}>
        <FileText className="h-12 w-12 text-gray-400 mb-2" />
        <div className="text-sm text-gray-600 font-medium">Not available</div>
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

const FacultyReports = () => {
  const { user } = useAuth();
  const [odRequests, setOdRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Filter states
  const [filters, setFilters] = useState({
    year: '',
    section: '',
    status: '',
    dateFrom: '',
    dateTo: '',
    studentName: '',
    eventName: '',
    proofStatus: ''
  });

  useEffect(() => {
    fetchODRequests();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filters, odRequests]);

  const fetchODRequests = async () => {
    try {
      setLoading(true);
      const response = await api.get('/faculty/od-requests');
      setOdRequests(response.data.od_requests || []);
    } catch (error) {
      console.error('Error fetching OD requests:', error);
      toast.error('Failed to fetch OD requests');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...odRequests];

    // Year filter
    if (filters.year) {
      filtered = filtered.filter(req => req.student?.year === parseInt(filters.year));
    }

    // Section filter
    if (filters.section) {
      filtered = filtered.filter(req => req.student?.section === filters.section);
    }

    // Status filter
    if (filters.status) {
      filtered = filtered.filter(req => req.status === filters.status);
    }

    // Date range filter
    if (filters.dateFrom) {
      filtered = filtered.filter(req => new Date(req.from_date) >= new Date(filters.dateFrom));
    }
    if (filters.dateTo) {
      filtered = filtered.filter(req => new Date(req.to_date) <= new Date(filters.dateTo));
    }

    // Student name filter
    if (filters.studentName) {
      filtered = filtered.filter(req => 
        req.student?.name?.toLowerCase().includes(filters.studentName.toLowerCase())
      );
    }

    // Event name filter
    if (filters.eventName) {
      filtered = filtered.filter(req => 
        req.event_name?.toLowerCase().includes(filters.eventName.toLowerCase())
      );
    }

    // Proof status filter
    if (filters.proofStatus) {
      filtered = filtered.filter(req => req.proof_submission_status === filters.proofStatus);
    }

    // Sort by created date (newest first)
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    setFilteredRequests(filtered);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const resetFilters = () => {
    setFilters({
      year: '',
      section: '',
      status: '',
      dateFrom: '',
      dateTo: '',
      studentName: '',
      eventName: '',
      proofStatus: ''
    });
  };

  const handleViewDetails = (request) => {
    setSelectedRequest(request);
    setShowModal(true);
  };

  const handleDownloadDocument = async (requestId, fileType) => {
    try {
      const response = await api.get(`/od/${requestId}/download-${fileType}`, {
        responseType: 'blob'
      });

      const contentDisposition = response.headers['content-disposition'];
      let filename = `${fileType}-${requestId}.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Document downloaded successfully');
    } catch (error) {
      console.error('Error downloading document:', error);
      toast.error('Failed to download document');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800', icon: XCircle }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getProofStatusBadge = (proofStatus) => {
    const statusConfig = {
      'NOT_SUBMITTED': { color: 'bg-gray-100 text-gray-800', text: 'Not Submitted' },
      'attendance_pending': { color: 'bg-yellow-100 text-yellow-800', text: 'Attendance Pending' },
      'ATTENDANCE_SUBMITTED': { color: 'bg-blue-100 text-blue-800', text: 'Attendance Submitted' },
      'certificate_pending': { color: 'bg-orange-100 text-orange-800', text: 'Certificate Pending' },
      'certificate_submitted': { color: 'bg-purple-100 text-purple-800', text: 'Certificate Submitted' },
      'COMPLETED': { color: 'bg-green-100 text-green-800', text: 'Completed' }
    };

    const config = statusConfig[proofStatus] || statusConfig['NOT_SUBMITTED'];

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    );
  };

  const getProofStatusText = (proofStatus) => {
    const statusText = {
      'NOT_SUBMITTED': 'Not Submitted',
      'attendance_pending': 'Attendance Pending',
      'ATTENDANCE_SUBMITTED': 'Attendance Submitted',
      'certificate_pending': 'Certificate Pending',
      'certificate_submitted': 'Certificate Submitted',
      'COMPLETED': 'Completed'
    };
    return statusText[proofStatus] || 'Not Submitted';
  };

  const exportToExcel = () => {
    try {
      // Prepare data for Excel
      const excelData = filteredRequests.map((request, index) => ({
        'Roll Number': request.student?.roll_number || 'N/A',
        'Department': request.student?.department || 'N/A',
        'Year': request.student?.year || 'N/A',
        'Attendance Proof Submitted': request.attendance_proof_file_data || request.attendance_proof?.filename ? 'Yes' : 'No',
        'Certificate Uploaded Status': request.certificate_file_data || request.certificate?.filename ? 'Yes' : 'No'
      }));

      // Create worksheet
      const worksheet = XLSX.utils.json_to_sheet(excelData);

      // Set column widths
      const columnWidths = [
        { wch: 15 }, // Roll Number
        { wch: 25 }, // Department
        { wch: 8 },  // Year
        { wch: 25 }, // Attendance Proof Submitted
        { wch: 25 }  // Certificate Uploaded Status
      ];
      worksheet['!cols'] = columnWidths;

      // Create workbook
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'OD Reports');

      // Generate filename with current date
      const filename = `OD_Reports_${format(new Date(), 'dd-MM-yyyy_HHmm')}.xlsx`;

      // Download file
      XLSX.writeFile(workbook, filename);

      toast.success(`Exported ${filteredRequests.length} records to Excel`);
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      toast.error('Failed to export to Excel');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <FileText className="mr-3 h-8 w-8 text-blue-600" />
                OD Reports
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                View and filter OD documents, attendance proofs, and certificates
              </p>
            </div>
            <button
              onClick={exportToExcel}
              disabled={filteredRequests.length === 0}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                filteredRequests.length === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700 shadow-md hover:shadow-lg'
              }`}
            >
              <FileSpreadsheet className="h-5 w-5" />
              <span>Export to Excel</span>
            </button>
          </div>
        </div>

        {/* Filters Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Filter className="mr-2 h-5 w-5 text-blue-600" />
              Filters
            </h2>
            <button
              onClick={resetFilters}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Reset All
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Year Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
              <select
                value={filters.year}
                onChange={(e) => handleFilterChange('year', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Years</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
              </select>
            </div>

            {/* Section Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Section</label>
              <select
                value={filters.section}
                onChange={(e) => handleFilterChange('section', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Sections</option>
                <option value="A">Section A</option>
                <option value="B">Section B</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">OD Status</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Proof Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Proof Status</label>
              <select
                value={filters.proofStatus}
                onChange={(e) => handleFilterChange('proofStatus', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Proof Statuses</option>
                <option value="NOT_SUBMITTED">Not Submitted</option>
                <option value="attendance_pending">Attendance Pending</option>
                <option value="ATTENDANCE_SUBMITTED">Attendance Submitted</option>
                <option value="certificate_pending">Certificate Pending</option>
                <option value="certificate_submitted">Certificate Submitted</option>
                <option value="COMPLETED">Completed</option>
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Student Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Student Name</label>
              <input
                type="text"
                value={filters.studentName}
                onChange={(e) => handleFilterChange('studentName', e.target.value)}
                placeholder="Search by name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Event Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
              <input
                type="text"
                value={filters.eventName}
                onChange={(e) => handleFilterChange('eventName', e.target.value)}
                placeholder="Search by event..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            Showing {filteredRequests.length} of {odRequests.length} records
          </div>
        </div>

        {/* Results Section */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {filteredRequests.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No records found</h3>
              <p className="mt-1 text-sm text-gray-500">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Event
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proof Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredRequests.map((request) => (
                    <tr key={request.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {request.student?.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {request.student?.roll_number} | Year {request.student?.year} - {request.student?.section}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{request.event_name}</div>
                        <div className="text-sm text-gray-500">{request.host_institution || request.college_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {format(new Date(request.from_date), 'dd MMM yyyy')}
                        </div>
                        <div className="text-sm text-gray-500">
                          to {format(new Date(request.to_date), 'dd MMM yyyy')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(request.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getProofStatusBadge(request.proof_submission_status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => handleViewDetails(request)}
                          className="text-blue-600 hover:text-blue-900 flex items-center"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal for viewing details */}
      {showModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">OD Request Details</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              {/* Student Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-600" />
                  Student Information
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Name</p>
                    <p className="font-medium">{selectedRequest.student?.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Roll Number</p>
                    <p className="font-medium">{selectedRequest.student?.roll_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Year & Section</p>
                    <p className="font-medium">Year {selectedRequest.student?.year} - Section {selectedRequest.student?.section}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Department</p>
                    <p className="font-medium">{selectedRequest.student?.department}</p>
                  </div>
                </div>
              </div>

              {/* Event Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-blue-600" />
                  Event Information
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Event Name</p>
                    <p className="font-medium">{selectedRequest.event_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Institution</p>
                    <p className="font-medium">{selectedRequest.host_institution || selectedRequest.college_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">From Date</p>
                    <p className="font-medium">{format(new Date(selectedRequest.from_date), 'dd MMM yyyy')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">To Date</p>
                    <p className="font-medium">{format(new Date(selectedRequest.to_date), 'dd MMM yyyy')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Venue</p>
                    <p className="font-medium">{selectedRequest.venue || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">OD Type</p>
                    <p className="font-medium">{selectedRequest.od_type?.replace(/_/g, ' ')}</p>
                  </div>
                </div>
                {selectedRequest.event_description && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-600">Description</p>
                    <p className="font-medium">{selectedRequest.event_description}</p>
                  </div>
                )}
              </div>

              {/* Status Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Status Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">OD Status</p>
                    <div className="mt-1">{getStatusBadge(selectedRequest.status)}</div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Proof Status</p>
                    <div className="mt-1">{getProofStatusBadge(selectedRequest.proof_submission_status)}</div>
                  </div>
                  {selectedRequest.approval_comments && (
                    <div className="col-span-2">
                      <p className="text-sm text-gray-600">Comments</p>
                      <p className="font-medium">{selectedRequest.approval_comments}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Documents Section */}
              <div className="space-y-6">
                {/* OD Application Document */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center justify-between">
                    <span className="flex items-center">
                      <FileText className="h-5 w-5 mr-2 text-blue-600" />
                      OD Application Document
                    </span>
                    <button
                      onClick={() => handleDownloadDocument(selectedRequest.id, 'application')}
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </button>
                  </h3>
                  <div className="border rounded-lg p-4 bg-white">
                    <AuthenticatedImage
                      requestId={selectedRequest.id}
                      fileType="application"
                      alt="OD Application"
                      className="w-full max-h-96 object-contain"
                    />
                  </div>
                </div>

                {/* Attendance Proof */}
                {selectedRequest.attendance_proof_file_data || selectedRequest.attendance_proof?.filename ? (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center justify-between">
                      <span className="flex items-center">
                        <FileText className="h-5 w-5 mr-2 text-green-600" />
                        Attendance Proof
                      </span>
                      <button
                        onClick={() => handleDownloadDocument(selectedRequest.id, 'attendance-proof')}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </button>
                    </h3>
                    <div className="border rounded-lg p-4 bg-white">
                      <AuthenticatedImage
                        requestId={selectedRequest.id}
                        fileType="attendance-proof"
                        alt="Attendance Proof"
                        className="w-full max-h-96 object-contain"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600">Attendance proof not submitted yet</p>
                  </div>
                )}

                {/* Certificate */}
                {selectedRequest.certificate_file_data || selectedRequest.certificate?.filename ? (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center justify-between">
                      <span className="flex items-center">
                        <FileText className="h-5 w-5 mr-2 text-purple-600" />
                        Certificate
                      </span>
                      <button
                        onClick={() => handleDownloadDocument(selectedRequest.id, 'certificate')}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </button>
                    </h3>
                    <div className="border rounded-lg p-4 bg-white">
                      <AuthenticatedImage
                        requestId={selectedRequest.id}
                        fileType="certificate"
                        alt="Certificate"
                        className="w-full max-h-96 object-contain"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600">Certificate not submitted yet</p>
                  </div>
                )}
              </div>
            </div>

            <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200">
              <button
                onClick={() => setShowModal(false)}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FacultyReports;
