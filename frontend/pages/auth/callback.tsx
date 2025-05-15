import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../../contexts/AuthContext';

const OAuthCallback = () => {
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);
  const router = useRouter();
  const { handleOAuthCallback } = useAuth();

  useEffect(() => {
    // Process the OAuth callback once the query parameters are available
    if (router.isReady) {
      const { token, provider, new_user } = router.query;
      
      if (!token || !provider) {
        setError('Invalid callback parameters. Authentication failed.');
        setIsProcessing(false);
        return;
      }

      const processOAuthCallback = async () => {
        try {
          await handleOAuthCallback(
            token as string,
            provider as 'google' | 'github',
            new_user === 'true'
          );
          // Redirect happens in the handleOAuthCallback function
        } catch (err: any) {
          setError(err.message || 'Failed to complete authentication. Please try again.');
          setIsProcessing(false);
        }
      };

      processOAuthCallback();
    }
  }, [router.isReady, router.query, handleOAuthCallback]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
                <div className="mt-4">
                  <button
                    onClick={() => router.push('/auth/login')}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  >
                    Return to login
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
          Completing authentication...
        </h2>
        <div className="mt-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <p className="mt-4 text-sm text-gray-600">
          You will be redirected to the dashboard shortly.
        </p>
      </div>
    </div>
  );
};

export default OAuthCallback;
