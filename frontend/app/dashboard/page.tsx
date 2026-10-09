"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { api } from '@/app/lib/api';
import axios from 'axios';

interface UserProfile {
  full_name: string;
  registration_number: string | null;
  email: string;
  phone: string;
  role: string;
}

interface Complaint {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  
  const [user, setUser] = useState<UserProfile | null>(null);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  
  // A trigger to force a re-fetch without defining functions outside useEffect
  const [refreshKey, setRefreshKey] = useState(0);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newPriority, setNewPriority] = useState('MEDIUM');
  const [submitError, setSubmitError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userRes, complaintsRes] = await Promise.all([
          api.get('/api/v1/auth/me'),
          api.get('/api/v1/complaints/')
        ]);
        setUser(userRes.data);
        setComplaints(complaintsRes.data);
      } catch (error) {
        console.error("Data fetch failed:", error);
        Cookies.remove('token');
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, refreshKey]); // Re-runs whenever router or refreshKey changes

  const handleLogout = () => {
    Cookies.remove('token');
    router.push('/login');
  };

  const handleCreateComplaint = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError('');

    try {
      await api.post('/api/v1/complaints/', {
        title: newTitle,
        description: newDescription,
        category_id: 1, 
        priority: newPriority
      });
      
      setIsModalOpen(false);
      setNewTitle('');
      setNewDescription('');
      setNewPriority('MEDIUM'); 
      
      setRefreshKey(oldKey => oldKey + 1);
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        setSubmitError(error.response?.data?.detail || 'Failed to submit complaint');
      } else {
        setSubmitError('An unexpected error occurred.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
    const handleDeleteComplaint = async (id: number) => {
        try {
        await api.delete(`/api/v1/complaints/${id}`);
        setRefreshKey(oldKey => oldKey + 1);
        } catch (error) {
        console.error("Failed to delete complaint:", error);
        alert("Could not delete the complaint. Please try again.");
        }
    };
  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800';
      case 'RESOLVED': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && refreshKey === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <p className="text-xl text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8 relative">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
        
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Student Dashboard</h1>
          <button 
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none"
          >
            Logout
          </button>
        </div>
        
        <div className="bg-blue-50 border border-blue-100 p-5 rounded-lg mb-8 text-black">
          <h2 className="text-xl font-semibold mb-3 text-blue-900">
            Welcome, {user?.full_name}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <p><strong>Reg No:</strong> {user?.registration_number || 'N/A'}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Phone:</strong> {user?.phone}</p>
            <p><strong>Role:</strong> {user?.role}</p>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">My Complaints</h2>
            <button 
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              + New Complaint
            </button>
          </div>
          
          {complaints.length === 0 ? (
            <div className="p-8 text-center text-gray-500 border-2 border-dashed rounded-lg">
              No complaints found.
            </div>
          ) : (
            <div className="space-y-4">
              {complaints.map((complaint) => (
                <div key={complaint.id} className="border p-4 rounded-lg flex justify-between items-stretch text-black bg-white hover:shadow-sm transition-shadow">
                  
                  {/* Left Column: Details */}
                  <div className="flex flex-col justify-between pr-4">
                    <div>
                      <h3 className="font-semibold text-lg">{complaint.title}</h3>
                      <p className="text-gray-600 mt-1">{complaint.description}</p>
                    </div>
                    <p className="text-sm text-gray-400 mt-4">
                      Filed on: {new Date(complaint.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  {/* Right Column: Badges & Action */}
                  <div className="flex flex-col items-end justify-between min-w-[100px]">
                    <div className="flex flex-col items-end space-y-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(complaint.status)}`}>
                        {complaint.status}
                      </span>
                      <span className="text-xs font-medium bg-red-100 text-red-800 px-3 py-1 rounded-full border border-red-200">
                        {complaint.priority}
                      </span>
                    </div>
                    
                    {/* Dustbin Icon Button */}
                    <button 
                      onClick={() => handleDeleteComplaint(complaint.id)}
                      className="text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all mt-4 p-1.5 rounded-md flex items-center justify-center"
                      title="Delete Complaint"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>

                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">File a New Complaint</h2>
            
            {submitError && (
              <div className="p-3 mb-4 text-sm text-red-700 bg-red-100 rounded">
                {submitError}
              </div>
            )}

            <form onSubmit={handleCreateComplaint} className="space-y-4 text-black">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Issue Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="E.g., Broken Window"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  required
                  rows={4}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Provide details about the issue..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority Level</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-400"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}