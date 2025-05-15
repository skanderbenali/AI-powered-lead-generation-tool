import React, { useState } from 'react';
import { 
  EnvelopeIcon, 
  PhoneIcon, 
  UserPlusIcon,
  ChatBubbleLeftRightIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';

type Lead = {
  id: number;
  name: string;
  title: string;
  company: string;
  email: string;
  score: number;
  status?: string; // Accept any string value for status
};

type LeadTableProps = {
  leads: Lead[];
};

const LeadTable = ({ leads }: LeadTableProps) => {
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-blue-600 bg-blue-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getStatusColor = (status?: string) => {
    switch(status) {
      case 'New': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'Contacted': return 'text-purple-700 bg-purple-50 border-purple-200';
      case 'Qualified': return 'text-green-700 bg-green-50 border-green-200';
      case 'Negotiating': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'Converted': return 'text-indigo-700 bg-indigo-50 border-indigo-200';
      case 'Lost': return 'text-gray-700 bg-gray-50 border-gray-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const toggleRowExpand = (id: number) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  return (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:pl-6">
              Lead
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Company
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Score
            </th>
            <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {leads.map((lead) => (
            <React.Fragment key={lead.id}>
              <tr className={`${expandedRow === lead.id ? 'bg-gray-50' : 'hover:bg-gray-50'} transition-colors duration-150`}>
                <td className="whitespace-nowrap py-4 pl-4 pr-3 sm:pl-6">
                  <div className="flex items-center">
                    <div className="h-10 w-10 flex-shrink-0 rounded-full bg-primary-100 flex items-center justify-center">
                      <span className="font-medium text-primary-800">{lead.name.split(' ').map(n => n[0]).join('')}</span>
                    </div>
                    <div className="ml-4">
                      <div className="font-medium text-gray-900">{lead.name}</div>
                      <div className="text-gray-500">{lead.email}</div>
                    </div>
                  </div>
                </td>
                <td className="whitespace-nowrap px-3 py-4">
                  <div className="text-sm text-gray-900">{lead.company}</div>
                  <div className="text-sm text-gray-500">{lead.title}</div>
                </td>
                <td className="whitespace-nowrap px-3 py-4">
                  {lead.status && (
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium border ${getStatusColor(lead.status)}`}>
                      {lead.status}
                    </span>
                  )}
                </td>
                <td className="whitespace-nowrap px-3 py-4">
                  <div className="flex items-center">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getScoreColor(lead.score)}`}>
                      {lead.score}
                    </span>
                    <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${lead.score >= 90 ? 'bg-green-500' : lead.score >= 80 ? 'bg-blue-500' : lead.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${lead.score}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                  <div className="flex justify-end space-x-3">
                    <button 
                      type="button"
                      className="inline-flex items-center rounded-md p-1.5 text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                      title="Send Email"
                    >
                      <EnvelopeIcon className="h-5 w-5" aria-hidden="true" />
                    </button>
                    <button 
                      type="button"
                      className="inline-flex items-center rounded-md p-1.5 text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                      title="Call"
                    >
                      <PhoneIcon className="h-5 w-5" aria-hidden="true" />
                    </button>
                    <button 
                      type="button"
                      className="inline-flex items-center rounded-md p-1.5 text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                      onClick={() => toggleRowExpand(lead.id)}
                      title="View Details"
                    >
                      <EllipsisVerticalIcon className="h-5 w-5" aria-hidden="true" />
                    </button>
                  </div>
                </td>
              </tr>
              {expandedRow === lead.id && (
                <tr>
                  <td colSpan={5} className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                    <div className="text-sm">
                      <div className="font-medium text-gray-900 mb-2">Lead Details</div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Contact Information</h4>
                          <p className="text-gray-700 flex items-center">
                            <EnvelopeIcon className="h-4 w-4 mr-1 text-gray-400" />
                            {lead.email}
                          </p>
                          <p className="text-gray-700 flex items-center">
                            <PhoneIcon className="h-4 w-4 mr-1 text-gray-400" />
                            Not available
                          </p>
                        </div>
                        <div>
                          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Company</h4>
                          <p className="text-gray-700">{lead.company}</p>
                          <p className="text-gray-700">{lead.title}</p>
                        </div>
                        <div>
                          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Actions</h4>
                          <div className="flex space-x-2 mt-1">
                            <button
                              type="button"
                              className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                              <UserPlusIcon className="-ml-0.5 mr-1 h-4 w-4" aria-hidden="true" />
                              Add to CRM
                            </button>
                            <button
                              type="button"
                              className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                            >
                              <ChatBubbleLeftRightIcon className="-ml-0.5 mr-1 h-4 w-4" aria-hidden="true" />
                              Add Note
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
      
      {leads.length === 0 && (
        <div className="text-center py-10 bg-white">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No leads found</h3>
          <p className="mt-1 text-sm text-gray-500">Try adjusting your search criteria.</p>
        </div>
      )}
    </div>
  );
};

export default LeadTable;
