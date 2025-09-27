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
  const { toast } = useToast();

  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    console.log('AuthContext: Checking token...', !!token);
    
    // Development bypass - if no backend, create a dummy token and admin
    if (!token) {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname.includes('lovable.app');
      if (isDevelopment) {
        console.log('AuthContext: Development mode, creating dummy authentication');
        localStorage.setItem('adminToken', 'dev-token-123');
        setAdmin({
          id: 'dev-admin',
          name: 'Development Admin',
          email: 'admin@dev.local'
        });
        setLoading(false);
        return;
      }
    }
    
    if (token) {
      fetchAdminInfo();
    } else {
      console.log('AuthContext: No token found, setting loading to false');
      setLoading(false);
    }
  }, []);

  const fetchAdminInfo = async () => {
    try {
      console.log('AuthContext: Fetching admin info...');
      const adminData = await apiClient.getAdminInfo();
      console.log('AuthContext: Admin data received:', adminData);
      setAdmin(adminData);
    } catch (error) {
      console.error('AuthContext: Failed to fetch admin info:', error);
      localStorage.removeItem('adminToken');
      // Set a dummy admin for development if backend is not available
      if (error instanceof Error && error.message.includes('fetch')) {
        console.log('AuthContext: Backend unavailable, using dummy admin');
        setAdmin({
          id: 'dev-admin',
          name: 'Development Admin',
          email: 'admin@dev.local'
        });
      }
    } finally {
      console.log('AuthContext: Setting loading to false');
      setLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const data = await apiClient.login(email, password);
      localStorage.setItem('adminToken', data.access_token);
      await fetchAdminInfo();
      toast({
        title: "Login successful",
        description: "Welcome to the admin console!",
      });
      return true;
    } catch (error) {
      toast({
        title: "Login failed",
        description: error instanceof Error ? error.message : "Invalid credentials",
        variant: "destructive",
      });
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('adminToken');
    setAdmin(null);
    toast({
      title: "Logged out",
      description: "You have been successfully logged out",
    });
  };

  return (
    <AuthContext.Provider value={{ admin, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};