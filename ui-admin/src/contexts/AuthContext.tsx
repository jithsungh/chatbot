import React, { createContext, useContext, useState, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/utils/api';

interface Admin {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  admin: Admin | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = useState<Admin | null>(null);
  const [loading, setLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const { toast } = useToast();

  // Check if user is authenticated
  const isAuthenticated = admin !== null;

  // Initialize authentication state on app load
  useEffect(() => {
    if (isInitialized) return; // Prevent re-initialization

    const initializeAuth = async () => {
      console.log('AuthContext: Initializing authentication...');
      
      try {
        const token = localStorage.getItem('adminToken');
        console.log('AuthContext: Token found:', !!token);
        
        if (!token) {
          console.log('AuthContext: No token found, user not authenticated');
          setLoading(false);
          setIsInitialized(true);
          return;
        }

        // // Check if we're in development mode
        // const isDevelopment = window.location.hostname === 'localhost';
        
        // if (isDevelopment) {
        //   console.log('AuthContext: Development mode detected');
        //   // In development, create a dummy admin if token exists
        //   setAdmin({
        //     id: 'dev-admin',
        //     name: 'Development Admin',
        //     email: 'admin@dev.local'
        //   // }
        // );
        //   setLoading(false);
        //   setIsInitialized(true);
        //   return;
        // }

        // In production, validate token with backend
        await validateTokenAndSetAdmin();
        
      } catch (error) {
        console.error('AuthContext: Error during initialization:', error);
        handleAuthError();
      } finally {
        setLoading(false);
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, [isInitialized]);

  const validateTokenAndSetAdmin = async () => {
    try {
      console.log('AuthContext: Validating token with backend...');
      const adminData = await apiClient.getAdminInfo();
      console.log('AuthContext: Token valid, admin data received:', adminData);
      setAdmin(adminData);
    } catch (error) {
      console.error('AuthContext: Token validation failed:', error);
      handleAuthError();
      throw error;
    }
  };

  const handleAuthError = () => {
    console.log('AuthContext: Handling auth error - clearing token and admin data');
    localStorage.removeItem('adminToken');
    setAdmin(null);
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      console.log('AuthContext: Attempting login...');
      
      const data = await apiClient.login(email, password);
      
      // Store token in localStorage
      localStorage.setItem('adminToken', data.access_token);
      console.log('AuthContext: Token stored successfully');
      
      // Fetch and set admin info
      await validateTokenAndSetAdmin();
      
      toast({
        title: "Login successful",
        description: "Welcome to the admin console!",
      });
      
      return true;
    } catch (error) {
      console.error('AuthContext: Login failed:', error);
      
      // Clean up on login failure
      localStorage.removeItem('adminToken');
      setAdmin(null);
      
      toast({
        title: "Login failed",
        description: error instanceof Error ? error.message : "Invalid credentials",
        variant: "destructive",
      });
      
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    console.log('AuthContext: Logging out...');
    
    // Clear token from localStorage
    localStorage.removeItem('adminToken');
    
    // Clear admin state
    setAdmin(null);
    
    // Call API logout (optional, for cleanup on server)
    apiClient.logout().catch(err => 
      console.warn('AuthContext: Server logout failed:', err)
    );
    
    toast({
      title: "Logged out",
      description: "You have been successfully logged out",
    });
  };

  return (
    <AuthContext.Provider value={{ 
      admin, 
      login, 
      logout, 
      loading, 
      isAuthenticated 
    }}>
      {children}
    </AuthContext.Provider>
  );
};