import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/router';

// Define the auth provider type
type AuthProvider = 'local' | 'google' | 'github';

// Define the user type
interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  auth_provider: AuthProvider;
  avatar_url?: string;
}

// Define the auth context state
interface AuthContextState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  loginWithOAuth: (provider: AuthProvider) => void;
  logout: () => void;
  handleOAuthCallback: (token: string, provider: AuthProvider, isNewUser: boolean) => Promise<void>;
}

// Create the auth context
const AuthContext = createContext<AuthContextState | undefined>(undefined);

// Auth provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Load user from localStorage on initial render
  useEffect(() => {
    const loadUser = async () => {
      setLoading(true);
      try {
        const savedToken = localStorage.getItem('auth_token');
        const savedUser = localStorage.getItem('user');

        if (savedToken && savedUser) {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
        }
      } catch (error) {
        console.error('Failed to load user from localStorage', error);
        // Clear invalid data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  // Regular login with username and password
  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      // Add a fallback URL if environment variable is not available
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log('Login using API URL:', apiUrl); // Debug log
      
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Save token
      setToken(data.access_token);
      localStorage.setItem('auth_token', data.access_token);
      
      // Fetch user profile with the token
      await fetchUserProfile(data.access_token);
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Login with OAuth provider (Google or GitHub)
  const loginWithOAuth = (provider: AuthProvider) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    console.log('OAuth login using API URL:', apiUrl); // Debug log
    window.location.href = `${apiUrl}/auth/${provider.toLowerCase()}`;
  };

  // Handle OAuth callback
  const handleOAuthCallback = async (token: string, provider: AuthProvider, isNewUser: boolean) => {
    setLoading(true);
    try {
      setToken(token);
      localStorage.setItem('auth_token', token);
      
      // Fetch user profile with the token
      await fetchUserProfile(token);
      
      // Redirect to dashboard or profile completion for new users
      if (isNewUser) {
        router.push('/profile/complete');
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('OAuth callback failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fetch user profile with token
  const fetchUserProfile = async (accessToken: string) => {
    try {
      // Add a fallback URL if environment variable is not available
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log('Fetching user profile using API URL:', apiUrl); // Debug log
      
      const response = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const userData = await response.json();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      throw error;
    }
  };

  // Logout
  const logout = () => {
    // Clear token and user data
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    
    // Redirect to login page
    router.push('/auth/login');
  };

  // Auth context value
  const value: AuthContextState = {
    isAuthenticated: !!token,
    user,
    token,
    loading,
    login,
    loginWithOAuth,
    logout,
    handleOAuthCallback,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
