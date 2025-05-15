import React from 'react';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  EnvelopeIcon, 
  SparklesIcon 
} from '@heroicons/react/24/outline';

type StatItem = {
  name: string;
  value: number | string;
  description?: string;
  change?: number;
  icon?: 'chart' | 'users' | 'email' | 'quality';
};

type StatsProps = {
  stats: StatItem[];
};

const Stats = ({ stats }: StatsProps) => {
  // Get appropriate icon component based on the icon type
  const getIcon = (iconType?: string) => {
    switch(iconType) {
      case 'users': return <UserGroupIcon className="h-8 w-8 text-primary-600" />;
      case 'email': return <EnvelopeIcon className="h-8 w-8 text-primary-600" />;
      case 'quality': return <SparklesIcon className="h-8 w-8 text-primary-600" />;
      case 'chart': 
      default: return <ChartBarIcon className="h-8 w-8 text-primary-600" />;
    }
  };

  return (
    <div className="px-2 py-4">
      <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div 
            key={stat.name} 
            className="relative overflow-hidden bg-white p-6 rounded-xl shadow-md border border-gray-100 transition-all duration-300 hover:shadow-lg hover:border-primary-200"
          >
            <div className="flex items-start justify-between">
              <dt>
                <div className="absolute rounded-md p-3 bg-primary-50">
                  {getIcon(stat.icon)}
                </div>
                <p className="ml-16 text-sm font-medium text-gray-500 truncate">{stat.name}</p>
              </dt>
              {stat.change !== undefined && (
                <div className={`inline-flex items-baseline px-2.5 py-0.5 rounded-full text-sm font-medium ${stat.change >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {stat.change >= 0 ? '↑' : '↓'}
                  {Math.abs(stat.change)}%
                </div>
              )}
            </div>
            <dd className="ml-16 flex items-baseline pb-6 sm:pb-2">
              <p className="text-3xl font-semibold text-primary-800">{stat.value}</p>
              {stat.description && (
                <p className="ml-2 text-xs text-gray-400">{stat.description}</p>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
};

export default Stats;
