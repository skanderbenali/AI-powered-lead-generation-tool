import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';

// Higher-order component to protect routes
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If auth is initialized (not loading) and user is not authenticated
    if (!loading && !isAuthenticated) {
      // Redirect to login page
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  // Show nothing while loading or redirecting
  if (loading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
          </div>
          <p className="text-center mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If authenticated, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
