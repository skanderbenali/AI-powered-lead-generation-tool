import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Image from 'next/image';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../../components/Layout';
import ProtectedRoute from '../../components/ProtectedRoute';
import { UserCircleIcon, PencilSquareIcon, CheckIcon, XMarkIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import styles from '../../styles/profile.module.css';

// Define the types for our profile form
interface ProfileFormData {
  username: string;
  full_name: string;
  email: string;
  avatar_url: string;
  bio: string;
  company: string;
  job_title: string;
  location: string;
}

const ProfilePage = () => {
  const { user, token } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [profileData, setProfileData] = useState<ProfileFormData>({
    username: user?.username || '',
    full_name: user?.full_name || '',
    email: user?.email || '',
    avatar_url: user?.avatar_url || '',
    bio: '',
    company: '',
    job_title: '',
    location: ''
  });

  // Fetch extended profile data if needed
  useEffect(() => {
    if (user) {
      setProfileData(prev => ({
        ...prev,
        username: user.username || prev.username,
        full_name: user.full_name || prev.full_name,
        email: user.email || prev.email,
        avatar_url: user.avatar_url || prev.avatar_url
      }));
    }
  }, [user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/users/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update profile');
      }

      // Success
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditing(false);
      // Update the user context with the new data
      // This would require adding an updateUser function to the AuthContext
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage({ type: 'error', text: error instanceof Error ? error.message : 'An error occurred' });
    } finally {
      setIsSaving(false);
    }
  };

  const cancelEditing = () => {
    // Reset form data to original values
    if (user) {
      setProfileData({
        username: user.username || '',
        full_name: user.full_name || '',
        email: user.email || '',
        avatar_url: user.avatar_url || '',
        bio: '',
        company: '',
        job_title: '',
        location: ''
      });
    }
    setIsEditing(false);
    setMessage({ type: '', text: '' });
  };

  return (
    <ProtectedRoute>
      <Layout>
        <Head>
          <title>My Profile | LeadGen AI</title>
          <link rel="icon" href="/logo-icon.svg" />
        </Head>
        <div className="px-4 py-5 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto">
            {/* Header */}
            <div className="md:flex md:items-center md:justify-between mb-8">
              <div className="flex-1 min-w-0">
                <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                  My Profile
                </h1>
              </div>
              <div className="mt-4 flex md:mt-0 md:ml-4">
                {!isEditing ? (
                  <button
                    type="button"
                    onClick={() => setIsEditing(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <PencilSquareIcon className="h-4 w-4 mr-2" />
                    Edit Profile
                  </button>
                ) : (
                  <div className="space-x-2">
                    <button
                      type="button"
                      onClick={cancelEditing}
                      className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <XMarkIcon className="h-4 w-4 mr-2" />
                      Cancel
                    </button>
                    <button
                      type="submit"
                      form="profile-form"
                      disabled={isSaving}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {isSaving ? (
                        <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <CheckIcon className="h-4 w-4 mr-2" />
                      )}
                      Save Changes
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Notification */}
            {message.text && (
              <div className={`rounded-md p-4 mb-6 ${message.type === 'success' ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className="flex">
                  <div className="flex-shrink-0">
                    {message.type === 'success' ? (
                      <CheckIcon className="h-5 w-5 text-green-400" aria-hidden="true" />
                    ) : (
                      <XMarkIcon className="h-5 w-5 text-red-400" aria-hidden="true" />
                    )}
                  </div>
                  <div className="ml-3">
                    <p className={`text-sm font-medium ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
                      {message.text}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Profile Content */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="border-b border-gray-200 px-4 py-5 sm:px-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-24 w-24 relative">
                    <div className={styles.profileImageContainer}>
                      {profileData.avatar_url ? (
                        <Image 
                          src={profileData.avatar_url} 
                          alt="Profile" 
                          width={96} 
                          height={96} 
                          className={styles.profileImage} 
                          unoptimized={true}
                          onError={(e) => {
                            // Set src to empty to trigger the CSS fallback
                            const imgElement = e.currentTarget as HTMLImageElement;
                            imgElement.src = "";
                          }}
                        />
                      ) : (
                        <UserCircleIcon className="h-24 w-24 text-gray-300" />
                      )}
                    </div>
                  </div>
                  <div className="ml-6">
                    <h2 className="text-xl font-bold text-gray-900">
                      {user?.full_name || user?.username}
                    </h2>
                    <p className="text-sm text-gray-500">
                      Joined {user?.id ? new Date().toLocaleDateString() : ''}
                    </p>
                  </div>
                </div>
              </div>

              {/* Profile Form */}
              <form id="profile-form" onSubmit={handleSubmit}>
                <div className="px-4 py-5 sm:p-6">
                  <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                    {/* Username */}
                    <div className="sm:col-span-3">
                      <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                        Username
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          name="username"
                          id="username"
                          value={profileData.username}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>

                    {/* Full Name */}
                    <div className="sm:col-span-3">
                      <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                        Full Name
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          name="full_name"
                          id="full_name"
                          value={profileData.full_name}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>

                    {/* Email Address */}
                    <div className="sm:col-span-3">
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Email Address
                      </label>
                      <div className="mt-1">
                        <input
                          type="email"
                          name="email"
                          id="email"
                          value={profileData.email}
                          onChange={handleInputChange}
                          disabled={true} // Always disabled to prevent email changes
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                        />
                      </div>
                      <p className="mt-1 text-xs text-gray-500">Email address cannot be changed</p>
                    </div>

                    {/* Avatar URL */}
                    <div className="sm:col-span-3">
                      <label htmlFor="avatar_url" className="block text-sm font-medium text-gray-700">
                        Profile Picture URL
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          name="avatar_url"
                          id="avatar_url"
                          value={profileData.avatar_url}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          placeholder="https://example.com/avatar.jpg"
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>

                    {/* Bio */}
                    <div className="sm:col-span-6">
                      <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                        Bio
                      </label>
                      <div className="mt-1">
                        <textarea
                          name="bio"
                          id="bio"
                          rows={3}
                          value={profileData.bio}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          placeholder="Tell us about yourself..."
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>

                    {/* Company */}
                    <div className="sm:col-span-3">
                      <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                        Company
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          name="company"
                          id="company"
                          value={profileData.company}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>

                    {/* Job Title */}
                    <div className="sm:col-span-3">
                      <label htmlFor="job_title" className="block text-sm font-medium text-gray-700">
                        Job Title
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          name="job_title"
                          id="job_title"
                          value={profileData.job_title}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>

                    {/* Location */}
                    <div className="sm:col-span-3">
                      <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                        Location
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          name="location"
                          id="location"
                          value={profileData.location}
                          onChange={handleInputChange}
                          disabled={!isEditing || isSaving}
                          placeholder="City, Country"
                          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md disabled:bg-gray-100 disabled:cursor-not-allowed"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </form>

              {/* Account Details Section */}
              <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Account Details</h3>
                <div className="mt-5 border-t border-gray-200">
                  <dl className="divide-y divide-gray-200">
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt className="text-sm font-medium text-gray-500">Authentication Provider</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 capitalize">{user?.auth_provider || 'Local'}</dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt className="text-sm font-medium text-gray-500">Account ID</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{user?.id || 'N/A'}</dd>
                    </div>
                  </dl>
                </div>
              </div>

              {/* Security Settings Section */}
              <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Security Settings</h3>
                <div className="mt-3">
                  <button
                    type="button"
                    onClick={() => router.push('/profile/change-password')}
                    disabled={user?.auth_provider !== 'local'}
                    className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                      user?.auth_provider !== 'local' ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    Change Password
                  </button>
                  {user?.auth_provider !== 'local' && (
                    <p className="mt-2 text-sm text-gray-500">Password change is only available for local accounts.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default ProfilePage;
