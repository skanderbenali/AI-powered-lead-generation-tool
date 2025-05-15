import { useState } from 'react';
import { useQuery } from 'react-query';
import Head from 'next/head';
import Layout from '../../components/Layout';
import LeadTable from '../../components/LeadTable';
import SearchForm from '../../components/SearchForm';
import Stats from '../../components/Stats';

// Mock data for initial development
const MOCK_LEADS = [
  { id: 1, name: 'John Doe', title: 'CEO', company: 'Acme Inc', email: 'john@acme.com', score: 92 },
  { id: 2, name: 'Jane Smith', title: 'CTO', company: 'Tech Solutions', email: 'jane@techsolutions.com', score: 88 },
  { id: 3, name: 'Robert Johnson', title: 'VP Sales', company: 'Global Corp', email: 'robert@globalcorp.com', score: 78 },
  { id: 4, name: 'Emily Chen', title: 'Marketing Director', company: 'Innovate LLC', email: 'emily@innovatellc.com', score: 85 },
  { id: 5, name: 'Michael Brown', title: 'Product Manager', company: 'Future Systems', email: 'michael@futuresystems.com', score: 81 },
];

const Dashboard = () => {
  const [searchCriteria, setSearchCriteria] = useState({
    industry: '',
    title: '',
    location: '',
    companySize: '',
  });

  // In a real implementation, this would fetch data from the API
  const { data: leads, isLoading, error } = useQuery(
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
  };

  return (
    <Layout>
      <Head>
        <title>Lead Generation Dashboard</title>
      </Head>
      
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
          <h1 className="text-2xl font-semibold text-gray-900">Lead Generation Dashboard</h1>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
          <div className="py-4">
            <Stats 
              stats={[
                { name: 'Total Leads', value: leads?.data?.length || 0 },
                { name: 'High Quality Leads', value: leads?.data?.filter(l => l.score >= 85).length || 0 },
                { name: 'Campaigns Active', value: 3 },
                { name: 'Emails Sent', value: 125 },
              ]} 
            />
            
            <div className="mt-6 card">
              <h2 className="text-lg font-medium mb-4">Search Leads</h2>
              <SearchForm onSearch={handleSearch} />
            </div>
            
            <div className="mt-6 card">
              <h2 className="text-lg font-medium mb-4">Lead Results</h2>
              {isLoading ? (
                <p>Loading leads...</p>
              ) : error ? (
                <p className="text-red-500">Error loading leads</p>
              ) : (
                <LeadTable leads={leads?.data || []} />
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
