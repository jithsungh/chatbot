import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, Loader2, RefreshCw, AlertTriangle } from 'lucide-react';

interface ConnectionStatusProps {
  onRetry?: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ onRetry }) => {
  const [status, setStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [errorMessage, setErrorMessage] = useState('');
  const [backendUrl, setBackendUrl] = useState('');

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    setStatus('checking');
    setErrorMessage('');
    
    // Determine the backend URL
    const url = process.env.NODE_ENV === 'production' 
      ? window.location.origin 
      : 'http://localhost:8000';
    
    setBackendUrl(url);

    try {
      console.log('Checking connection to:', `${url}/`);
      
      const response = await fetch(`${url}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        setStatus('connected');
      } else {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Connection check failed:', error);
      setStatus('error');
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        setErrorMessage('Cannot connect to backend server. Please ensure it is running.');
      } else {
        setErrorMessage(error instanceof Error ? error.message : 'Unknown connection error');
      }
    }
  };

  const handleRetry = () => {
    checkConnection();
    onRetry?.();
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'checking':
        return <Loader2 className="w-5 h-5 animate-spin text-primary" />;
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-success" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-destructive" />;
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'checking':
        return <Badge variant="outline">Checking...</Badge>;
      case 'connected':
        return <Badge className="bg-success/10 text-success border-success/20">Connected</Badge>;
      case 'error':
        return <Badge variant="destructive">Connection Failed</Badge>;
    }
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          {getStatusIcon()}
          <span>Backend Connection</span>
          {getStatusBadge()}
        </CardTitle>
        <CardDescription>
          Status of connection to FastAPI backend server
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Backend URL:</span>
          <code className="bg-muted px-2 py-1 rounded text-xs">{backendUrl}</code>
        </div>

        {status === 'error' && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Connection Error:</strong> {errorMessage}
            </AlertDescription>
          </Alert>
        )}

        {status === 'error' && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Troubleshooting Steps:</p>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>Ensure your FastAPI backend is running</li>
              <li>Check that the backend is accessible at: <code>{backendUrl}</code></li>
              <li>Verify CORS settings allow requests from this domain</li>
              <li>Check your network connection</li>
            </ul>
          </div>
        )}

        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={checkConnection}
            disabled={status === 'checking'}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Check Connection
          </Button>
          
          {onRetry && status === 'error' && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRetry}
            >
              Retry Login
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ConnectionStatus;