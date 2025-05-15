import React from 'react';
import Link from 'next/link';
import { 
  HomeIcon, 
  UserGroupIcon, 
  ChartBarIcon, 
  EnvelopeIcon, 
  Cog6ToothIcon 
} from '@heroicons/react/24/outline';

type LayoutProps = {
  children: React.ReactNode;
};

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Leads', href: '/leads', icon: UserGroupIcon },
  { name: 'Campaigns', href: '/campaigns', icon: EnvelopeIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="h-screen flex overflow-hidden bg-gray-100">
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-primary-800">
            <div className="flex items-center h-16 flex-shrink-0 px-4 bg-primary-900">
              <h1 className="text-xl font-bold text-white">LeadGen AI</h1>
            </div>
            <div className="flex-1 flex flex-col overflow-y-auto">
              <nav className="flex-1 px-2 py-4 space-y-1">
                {navigation.map((item) => (
                  <Link href={item.href} key={item.name}>
                    <a className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-white hover:bg-primary-700">
                      <item.icon className="mr-3 h-6 w-6 text-primary-300" aria-hidden="true" />
                      {item.name}
                    </a>
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <main className="flex-1 relative z-0 overflow-y-auto focus:outline-none">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
