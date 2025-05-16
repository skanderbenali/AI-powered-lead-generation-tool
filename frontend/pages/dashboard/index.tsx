import { useState } from 'react';
import { useQuery } from 'react-query';
import Head from 'next/head';
import Layout from '../../components/Layout';
import LeadTable from '../../components/LeadTable';
import SearchForm from '../../components/SearchForm';
import Stats from '../../components/Stats';
import ProtectedRoute from '../../components/ProtectedRoute';
import { useAuth } from '../../contexts/AuthContext';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  EnvelopeIcon, 
  SparklesIcon,
  MagnifyingGlassCircleIcon,
  ArrowPathIcon,
  XMarkIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

// Mock data for initial development
const MOCK_LEADS = [
  { id: 1, name: 'John Doe', title: 'CEO', company: 'Acme Inc', email: 'john@acme.com', score: 92, status: 'New' },
  { id: 2, name: 'Jane Smith', title: 'CTO', company: 'Tech Solutions', email: 'jane@techsolutions.com', score: 88, status: 'Contacted' },
  { id: 3, name: 'Robert Johnson', title: 'VP Sales', company: 'Global Corp', email: 'robert@globalcorp.com', score: 78, status: 'New' },
  { id: 4, name: 'Emily Chen', title: 'Marketing Director', company: 'Innovate LLC', email: 'emily@innovatellc.com', score: 85, status: 'Qualified' },
  { id: 5, name: 'Michael Brown', title: 'Product Manager', company: 'Future Systems', email: 'michael@futuresystems.com', score: 81, status: 'New' },
];

const Dashboard = () => {
  // Get the logout function from AuthContext
  const { logout, user } = useAuth();
  
  const [searchCriteria, setSearchCriteria] = useState({
    industry: '',
    title: '',
    location: '',
    companySize: '',
  });
  const [showSearchPanel, setShowSearchPanel] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // In a real implementation, this would fetch data from the API
  const { data: leads, isLoading, error, refetch } = useQuery(
    ['leads', searchCriteria],
    () => {
      // This would be a real API call in production
      // return axios.get('/api/leads', { params: searchCriteria });
      
      // Using mock data for now
      return Promise.resolve({ data: MOCK_LEADS });
    },
    {
      enabled: true,
      initialData: { data: MOCK_LEADS },
    }
  );

  const handleSearch = (criteria) => {
    setSearchCriteria(criteria);
    setShowSearchPanel(false);
  };
  
  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setTimeout(() => setRefreshing(false), 800); // simulate loading time
  };

  return (
    <ProtectedRoute>
      <Layout>
        <Head>
          <title>Dashboard | LeadGen AI</title>
          <link rel="icon" href="/logo-icon.svg" />
        </Head>
      
      <div className="py-4 sm:py-6">
        {/* Page header */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-5">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Dashboard</h1>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
              {user && (
                <div className="flex items-center mr-4 text-sm text-gray-700">
                  <span className="font-medium mr-2">Welcome, {user.full_name || user.username}</span>
                </div>
              )}
              <button 
                onClick={() => setShowSearchPanel(!showSearchPanel)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <MagnifyingGlassCircleIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                Search Leads
              </button>
              <button 
                onClick={handleRefresh}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                disabled={refreshing}
              >
                <ArrowPathIcon 
                  className={`-ml-1 mr-2 h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} 
                  aria-hidden="true" 
                />
                Refresh
              </button>
              <button 
                onClick={logout}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <ArrowRightOnRectangleIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                Logout
              </button>
            </div>
          </div>
        </div>
        
        {/* Content area */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Stats section */}
          <div className="mt-2">
            <Stats 
              stats={[
                { 
                  name: 'Total Leads', 
                  value: leads?.data?.length || 0,
                  icon: 'users',
                  change: 12,
                  description: 'from last month'
                },
                { 
                  name: 'Quality Leads', 
                  value: leads?.data?.filter(l => l.score >= 85).length || 0,
                  icon: 'quality',
                  change: 8,
                  description: 'from last month'
                },
                { 
                  name: 'Campaigns', 
                  value: 3,
                  icon: 'email',
                  description: '2 active, 1 draft'
                },
                { 
                  name: 'Email Performance', 
                  value: '36%',
                  icon: 'chart',
                  change: -2,
                  description: 'open rate'
                },
              ]} 
            />
          </div>
          
          {/* Search panel */}
          {showSearchPanel && (
            <div className="mt-6 bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200">
              <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <h2 className="text-lg font-medium text-gray-900">Advanced Search</h2>
                <button 
                  onClick={() => setShowSearchPanel(false)}
                  className="text-gray-400 hover:text-gray-500 focus:outline-none"
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>
              <div className="px-4 py-5 sm:p-6 bg-gray-50">
                <SearchForm onSearch={handleSearch} />
              </div>
            </div>
          )}
          
          {/* Lead results */}
          <div className="mt-6 bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
              <h2 className="text-lg font-medium text-gray-900">Lead Results</h2>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">{leads?.data?.length || 0} leads found</span>
            </div>
            <div className="px-4 py-5 sm:p-6">
              {isLoading ? (
                <div className="flex justify-center py-8">
                  <ArrowPathIcon className="h-8 w-8 text-primary-500 animate-spin" aria-hidden="true" />
                </div>
              ) : error ? (
                <div className="text-center py-8">
                  <p className="text-red-500 font-medium">Error loading leads</p>
                  <p className="text-gray-500 text-sm mt-1">Please try refreshing the page</p>
                </div>
              ) : (
                <LeadTable leads={leads?.data || []} />
              )}
            </div>
          </div>
        </div>
      </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default Dashboard;
