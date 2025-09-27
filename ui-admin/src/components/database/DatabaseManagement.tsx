import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/utils/api';
import { 
  Database, 
  AlertTriangle, 
  Trash2, 
  RefreshCw,
  FileText,
  MessageSquare,
  Users,
  Loader2
} from 'lucide-react';

interface PurgeStatus {
  total_files: number;
  total_text_records: number;
  total_user_questions: number;
  total_admin_questions: number;
  vector_db_status: string;
}

interface PurgeDialogProps {
  type: 'all' | 'vector';
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (password: string, confirmation?: string) => void;
  loading: boolean;
}

const PurgeDialog: React.FC<PurgeDialogProps> = ({ type, open, onOpenChange, onConfirm, loading }) => {
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');

  const handleConfirm = () => {
    if (type === 'all') {
      onConfirm(password, confirmation);
    } else {
      onConfirm(password);
    }
  };

  const isValid = type === 'all' 
    ? password && confirmation === 'DELETE_ALL_DATA_PERMANENTLY'
    : password;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-10 h-10 bg-destructive/10 rounded-full">
              <AlertTriangle className="w-5 h-5 text-destructive" />
            </div>
            <div>
              <DialogTitle className="text-destructive">
                {type === 'all' ? 'Purge All Data' : 'Purge Vector Database'}
              </DialogTitle>
            </div>
          </div>
          <DialogDescription>
            {type === 'all' 
              ? 'This will permanently delete ALL data including files, questions, and vector embeddings. This action cannot be undone.'
              : 'This will delete all vector embeddings but keep your files and questions in PostgreSQL.'}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Secret Password</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter secret password"
              disabled={loading}
            />
          </div>
          
          {type === 'all' && (
            <div className="space-y-2">
              <Label>Confirmation</Label>
              <Input
                value={confirmation}
                onChange={(e) => setConfirmation(e.target.value)}
                placeholder="Type: DELETE_ALL_DATA_PERMANENTLY"
                disabled={loading}
              />
              <p className="text-xs text-muted-foreground">
                Type exactly: <code className="bg-muted px-1 rounded">DELETE_ALL_DATA_PERMANENTLY</code>
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={!isValid || loading}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Purging...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                {type === 'all' ? 'Purge All Data' : 'Purge Vector DB'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const DatabaseManagement = () => {
  const [status, setStatus] = useState<PurgeStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [purgeDialog, setPurgeDialog] = useState<{ type: 'all' | 'vector'; open: boolean }>({
    type: 'all',
    open: false,
  });
  const [purgeLoading, setPurgeLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const data = await apiClient.getPurgeStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
      toast({
        title: "Error",
        description: "Failed to fetch database status",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePurge = async (password: string, confirmation?: string) => {
    setPurgeLoading(true);
    try {
      if (purgeDialog.type === 'all') {
        await apiClient.purgeAllData(password, confirmation!);
        toast({
          title: "All data purged",
          description: "All data has been permanently deleted",
        });
      } else {
        await apiClient.purgeVectorDbOnly(password);
        toast({
          title: "Vector database purged",
          description: "Vector embeddings have been deleted",
        });
      }
      
      setPurgeDialog({ type: 'all', open: false });
      fetchStatus();
    } catch (error) {
      toast({
        title: "Purge failed",
        description: error instanceof Error ? error.message : "Failed to purge data",
        variant: "destructive",
      });
    } finally {
      setPurgeLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="card-hover">
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-32">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-primary" />
            <span>Database Management</span>
          </CardTitle>
          <CardDescription>
            Monitor database status and perform maintenance operations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-secondary rounded-lg">
              <FileText className="w-6 h-6 mx-auto mb-2 text-primary" />
              <p className="text-2xl font-bold">{status?.total_files || 0}</p>
              <p className="text-xs text-muted-foreground">Files</p>
            </div>
            <div className="text-center p-4 bg-secondary rounded-lg">
              <Database className="w-6 h-6 mx-auto mb-2 text-accent" />
              <p className="text-2xl font-bold">{status?.total_text_records || 0}</p>
              <p className="text-xs text-muted-foreground">Text Records</p>
            </div>
            <div className="text-center p-4 bg-secondary rounded-lg">
              <Users className="w-6 h-6 mx-auto mb-2 text-success" />
              <p className="text-2xl font-bold">{status?.total_user_questions || 0}</p>
              <p className="text-xs text-muted-foreground">User Questions</p>
            </div>
            <div className="text-center p-4 bg-secondary rounded-lg">
              <MessageSquare className="w-6 h-6 mx-auto mb-2 text-warning" />
              <p className="text-2xl font-bold">{status?.total_admin_questions || 0}</p>
              <p className="text-xs text-muted-foreground">Admin Questions</p>
            </div>
          </div>

          {/* Vector DB Status */}
          <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
            <div>
              <p className="font-medium">Vector Database Status</p>
              <p className="text-sm text-muted-foreground">Current state of embeddings</p>
            </div>
            <Badge variant="outline" className="bg-success/10 text-success border-success/20">
              {status?.vector_db_status || 'Active'}
            </Badge>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Database Operations</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchStatus}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </Button>
            </div>

            <div className="grid gap-3">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium text-sm">Purge Vector Database Only</p>
                  <p className="text-xs text-muted-foreground">
                    Delete embeddings but keep files and questions
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPurgeDialog({ type: 'vector', open: true })}
                  className="text-warning hover:bg-warning/10"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Purge Vector DB
                </Button>
              </div>

              <div className="flex items-center justify-between p-3 border border-destructive/20 rounded-lg bg-destructive/5">
                <div>
                  <p className="font-medium text-sm text-destructive">Purge All Data</p>
                  <p className="text-xs text-muted-foreground">
                    DANGER: Permanently delete all data including files and questions
                  </p>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => setPurgeDialog({ type: 'all', open: true })}
                >
                  <AlertTriangle className="w-4 h-4 mr-1" />
                  Purge All
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <PurgeDialog
        type={purgeDialog.type}
        open={purgeDialog.open}
        onOpenChange={(open) => setPurgeDialog({ ...purgeDialog, open })}
        onConfirm={handlePurge}
        loading={purgeLoading}
      />
    </>
  );
};

export default DatabaseManagement;