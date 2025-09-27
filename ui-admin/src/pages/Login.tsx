import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Bot, Loader2 } from 'lucide-react';
import adminHeroBg from '@/assets/admin-hero-bg.jpg';
import ConnectionStatus from '@/components/debug/ConnectionStatus';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showConnectionStatus, setShowConnectionStatus] = useState(false);
  const { isAuthenticated, login, loading: authLoading } = useAuth();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  // If user is already authenticated, redirect to intended page
  if (isAuthenticated && !authLoading) {
    console.log('Login: User already authenticated, redirecting to:', from);
    return <Navigate to={from} replace />;
  }

  // Show loading while auth is being determined
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center gradient-subtle">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim() || !password.trim()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const success = await login(email, password);
      if (success) {
        console.log('Login: Success, will redirect to:', from);
        // Navigation will be handled by the Navigate component above
      }
    } catch (error) {
      console.error('Login: Unexpected error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative"
      style={{
        backgroundImage: `url(${adminHeroBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      <div className="absolute inset-0 bg-black/50" />
      <div className="relative z-10 w-full max-w-md">
        <Card className="shadow-2xl border-0 bg-card/95 backdrop-blur-sm">
          <CardHeader className="text-center pb-2">
            <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 gradient-primary rounded-full shadow-lg">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Admin Console
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              Sign in to manage your chatbot
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  className="bg-background/50"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="bg-background/50"
                  required
                />
              </div>
              <Button
                type="submit"
                className="w-full gradient-primary hover:opacity-90 transition-opacity"
                disabled={isLoading || !email.trim() || !password.trim()}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>
            
            <div className="text-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowConnectionStatus(!showConnectionStatus)}
                className="text-muted-foreground hover:text-foreground"
              >
                {showConnectionStatus ? 'Hide' : 'Show'} Connection Status
              </Button>
            </div>
            
            {showConnectionStatus && (
              <div className="mt-4">
                <ConnectionStatus />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;