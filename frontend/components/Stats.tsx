import React from 'react';

type StatItem = {
  name: string;
  value: number | string;
};

type StatsProps = {
  stats: StatItem[];
};

const Stats = ({ stats }: StatsProps) => {
  return (
    <div>
      <dl className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="relative bg-white pt-5 px-4 pb-6 sm:pt-6 sm:px-6 rounded-lg shadow">
            <dt>
              <p className="text-sm font-medium text-gray-500 truncate">{stat.name}</p>
            </dt>
            <dd className="mt-1 text-3xl font-semibold text-primary-800">{stat.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
};

export default Stats;
