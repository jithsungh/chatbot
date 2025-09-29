import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/utils/api";
import {
  Database,
  Shield,
  Trash2,
  RefreshCw,
  FileText,
  MessageSquare,
  Users,
  Loader2,
  UserPlus,
  Edit,
  Key,
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  Settings,
  UserCog,
  Activity,
} from "lucide-react";

interface Admin {
  id: string;
  name: string;
  email: string;
  role: string;
  enabled: boolean;
  verified: boolean;
  last_login?: string;
  created_at: string;
}

interface DashboardStats {
  total_user_questions: number;
  total_admin_questions: number;
  total_text_knowledge: number;
  total_file_knowledge: number;
  pending_questions: number;
  processed_questions: number;
  avg_response_time: number;
  active_users: number;
  requested_by: string;
}

interface DatabaseDeleteDialogProps {
  type:
    | "files"
    | "text"
    | "user-questions"
    | "admin-questions"
    | "dept-failures"
    | "response-times"
    | "vector-db"
    | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  loading: boolean;
}

interface AdminDialogProps {
  admin: Admin | null;
  mode: "create" | "edit";
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (adminData: any) => void;
  loading: boolean;
}

interface PasswordResetDialogProps {
  admin: Admin | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onReset: (newPassword: string) => void;
  loading: boolean;
}

const DatabaseDeleteDialog: React.FC<DatabaseDeleteDialogProps> = ({
  type,
  open,
  onOpenChange,
  onConfirm,
  loading,
}) => {
  const [confirmationText, setConfirmationText] = useState("");

  const getDialogContent = () => {
    switch (type) {
      case "files":
        return {
          title: "Delete All Files",
          description:
            "This will permanently delete all uploaded files and their vector embeddings.",
          action: "Delete All Files",
          confirmText: "DELETE_ALL_FILES",
        };
      case "text":
        return {
          title: "Delete All Text Knowledge",
          description:
            "This will permanently delete all text knowledge entries and their vector embeddings.",
          action: "Delete All Text",
          confirmText: "DELETE_ALL_TEXT",
        };
      case "user-questions":
        return {
          title: "Delete All User Questions",
          description:
            "This will permanently delete all questions submitted by users.",
          action: "Delete All User Questions",
          confirmText: "DELETE_ALL_USER_QUESTIONS",
        };
      case "admin-questions":
        return {
          title: "Delete All Admin Questions",
          description:
            "This will permanently delete all admin-generated questions.",
          action: "Delete All Admin Questions",
          confirmText: "DELETE_ALL_ADMIN_QUESTIONS",
        };
      case "dept-failures":
        return {
          title: "Delete All Department Failures",
          description:
            "This will permanently delete all department detection failure records.",
          action: "Delete All Failures",
          confirmText: "DELETE_ALL_DEPT_FAILURES",
        };
      case "response-times":
        return {
          title: "Delete All Response Times",
          description:
            "This will permanently delete all response time tracking data.",
          action: "Delete All Response Times",
          confirmText: "DELETE_ALL_RESPONSE_TIMES",
        };
      case "vector-db":
        return {
          title: "Purge Entire Vector Database",
          description:
            "This will permanently delete the entire vector database and all embeddings. This operation affects all departments and cannot be undone.",
          action: "Purge Vector Database",
          confirmText: "PURGE_ENTIRE_VECTOR_DB",
        };
      default:
        return { title: "", description: "", action: "", confirmText: "" };
    }
  };

  const { title, description, action, confirmText } = getDialogContent();

  const handleConfirm = () => {
    if (confirmationText === confirmText) {
      onConfirm();
      setConfirmationText("");
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setConfirmationText("");
    }
    onOpenChange(open);
  };
  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-10 h-10 bg-destructive/10 rounded-full">
              <AlertTriangle className="w-5 h-5 text-destructive" />
            </div>
            <div>
              <DialogTitle className="text-destructive">{title}</DialogTitle>
            </div>
          </div>
          <DialogDescription className="text-left">
            {description}
            <br />
            <br />
            <strong className="text-destructive">
              This action cannot be undone.
            </strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="confirmation">
              Type{" "}
              <code className="bg-muted px-1 rounded text-sm">
                {confirmText}
              </code>{" "}
              to confirm:
            </Label>
            <Input
              id="confirmation"
              value={confirmationText}
              onChange={(e) => setConfirmationText(e.target.value)}
              placeholder={confirmText}
              disabled={loading}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={loading || confirmationText !== confirmText}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {type === "vector-db" ? "Purging..." : "Deleting..."}
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                {action}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const AdminDialog: React.FC<AdminDialogProps> = ({
  admin,
  mode,
  open,
  onOpenChange,
  onSave,
  loading,
}) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "admin",
    enabled: true,
  });

  useEffect(() => {
    if (admin && mode === "edit") {
      setFormData({
        name: admin.name,
        email: admin.email,
        password: "",
        role: admin.role,
        enabled: admin.enabled,
      });
    } else {
      setFormData({
        name: "",
        email: "",
        password: "",
        role: "admin",
        enabled: true,
      });
    }
  }, [admin, mode, open]);

  const handleSave = () => {
    const dataToSave =
      mode === "edit"
        ? {
            name: formData.name,
            email: formData.email,
            role: formData.role,
            enabled: formData.enabled,
          }
        : formData;
    onSave(dataToSave);
  };

  const isValid =
    formData.name && formData.email && (mode === "edit" || formData.password);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            {mode === "create" ? (
              <UserPlus className="w-5 h-5" />
            ) : (
              <Edit className="w-5 h-5" />
            )}
            <span>{mode === "create" ? "Create New Admin" : "Edit Admin"}</span>
          </DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "Add a new administrator to the system"
              : "Update administrator details and permissions"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="Enter full name"
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="Enter email address"
              disabled={loading}
            />
          </div>

          {mode === "create" && (
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                placeholder="Enter password"
                disabled={loading}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select
              value={formData.role}
              onValueChange={(value) =>
                setFormData({ ...formData, role: value })
              }
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="super_admin">Super Admin</SelectItem>
                <SelectItem value="read_only">Read Only</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="enabled"
              checked={formData.enabled}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, enabled: checked })
              }
              disabled={loading}
            />
            <Label htmlFor="enabled">Account Enabled</Label>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!isValid || loading}
            className="gradient-primary"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {mode === "create" ? "Creating..." : "Updating..."}
              </>
            ) : (
              <>
                {mode === "create" ? (
                  <UserPlus className="w-4 h-4 mr-2" />
                ) : (
                  <Edit className="w-4 h-4 mr-2" />
                )}
                {mode === "create" ? "Create Admin" : "Update Admin"}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const PasswordResetDialog: React.FC<PasswordResetDialogProps> = ({
  admin,
  open,
  onOpenChange,
  onReset,
  loading,
}) => {
  const [newPassword, setNewPassword] = useState("");

  useEffect(() => {
    if (!open) {
      setNewPassword("");
    }
  }, [open]);

  const handleReset = () => {
    onReset(newPassword);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Key className="w-5 h-5" />
            <span>Reset Password</span>
          </DialogTitle>
          <DialogDescription>
            Reset password for <strong>{admin?.name}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="newPassword">New Password</Label>
            <Input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new password"
              disabled={loading}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleReset}
            disabled={!newPassword || loading}
            className="gradient-primary"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Resetting...
              </>
            ) : (
              <>
                <Key className="w-4 h-4 mr-2" />
                Reset Password
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const AdminDeleteDialog: React.FC<{
  admin: Admin | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  loading: boolean;
}> = ({ admin, open, onOpenChange, onConfirm, loading }) => {
  const [confirmationText, setConfirmationText] = useState("");
  const confirmText = "DELETE_ADMIN";

  const handleConfirm = () => {
    if (confirmationText === confirmText) {
      onConfirm();
      setConfirmationText("");
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setConfirmationText("");
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-10 h-10 bg-destructive/10 rounded-full">
              <AlertTriangle className="w-5 h-5 text-destructive" />
            </div>
            <div>
              <DialogTitle className="text-destructive">
                Delete Admin
              </DialogTitle>
            </div>
          </div>
          <DialogDescription className="text-left">
            This will permanently delete the admin account for{" "}
            <strong>{admin?.name}</strong> ({admin?.email}).
            <br />
            <br />
            <strong className="text-destructive">
              This action cannot be undone.
            </strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="confirmation">
              Type{" "}
              <code className="bg-muted px-1 rounded text-sm">
                {confirmText}
              </code>{" "}
              to confirm:
            </Label>
            <Input
              id="confirmation"
              value={confirmationText}
              onChange={(e) => setConfirmationText(e.target.value)}
              placeholder={confirmText}
              disabled={loading}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={loading || confirmationText !== confirmText}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Admin
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const SuperAdminPanel = () => {
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [adminLoading, setAdminLoading] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<{
    type:
      | "files"
      | "text"
      | "user-questions"
      | "admin-questions"
      | "dept-failures"
      | "response-times"
      | "vector-db"
      | null;
    open: boolean;
  }>({
    type: null,
    open: false,
  });
  const [adminDialog, setAdminDialog] = useState<{
    admin: Admin | null;
    mode: "create" | "edit";
    open: boolean;
  }>({
    admin: null,
    mode: "create",
    open: false,
  });
  const [passwordDialog, setPasswordDialog] = useState<{
    admin: Admin | null;
    open: boolean;
  }>({
    admin: null,
    open: false,
  });
  const [deleteLoading, setDeleteLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);
  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsData, adminsData] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getAllAdmins(),
      ]);
      setStats(statsData);
      setAdmins(adminsData.admins);
    } catch (error) {
      console.error("Failed to fetch data:", error);
      toast({
        title: "Error",
        description: "Failed to fetch admin panel data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };
  const handleDatabaseDelete = async () => {
    if (!deleteDialog.type) return;

    setDeleteLoading(true);
    try {
      switch (deleteDialog.type) {
        case "files":
          await apiClient.deleteAllFiles();
          break;
        case "text":
          await apiClient.deleteAllTextKnowledge();
          break;
        case "user-questions":
          await apiClient.deleteAllUserQuestions();
          break;
        case "admin-questions":
          await apiClient.deleteAllAdminQuestions();
          break;
        case "dept-failures":
          await apiClient.deleteAllDeptFailures();
          break;
        case "response-times":
          await apiClient.deleteAllResponseTimes();
          break;
        case "vector-db":
          await apiClient.purgeEntireVectorDb();
          break;
      }

      toast({
        title: "Operation completed",
        description: `Successfully ${
          deleteDialog.type === "vector-db"
            ? "purged vector database"
            : `deleted all ${deleteDialog.type.replace("-", " ")}`
        }`,
      });

      setDeleteDialog({ type: null, open: false });
      fetchData();
    } catch (error) {
      toast({
        title: "Operation failed",
        description:
          error instanceof Error
            ? error.message
            : "Failed to complete operation",
        variant: "destructive",
      });
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleAdminSave = async (adminData: any) => {
    setAdminLoading(true);
    try {
      if (adminDialog.mode === "create") {
        await apiClient.createAdmin(adminData);
        toast({
          title: "Admin created",
          description: `Successfully created admin: ${adminData.name}`,
        });
      } else if (adminDialog.admin) {
        await apiClient.updateAdmin(adminDialog.admin.id, adminData);
        toast({
          title: "Admin updated",
          description: `Successfully updated admin: ${adminData.name}`,
        });
      }

      setAdminDialog({ admin: null, mode: "create", open: false });
      fetchData();
    } catch (error) {
      toast({
        title: `${adminDialog.mode === "create" ? "Create" : "Update"} failed`,
        description:
          error instanceof Error
            ? error.message
            : `Failed to ${adminDialog.mode} admin`,
        variant: "destructive",
      });
    } finally {
      setAdminLoading(false);
    }
  };

  const handlePasswordReset = async (newPassword: string) => {
    if (!passwordDialog.admin) return;

    setAdminLoading(true);
    try {
      await apiClient.resetAdminPassword(passwordDialog.admin.id, newPassword);
      toast({
        title: "Password reset",
        description: `Successfully reset password for ${passwordDialog.admin.name}`,
      });

      setPasswordDialog({ admin: null, open: false });
    } catch (error) {
      toast({
        title: "Password reset failed",
        description:
          error instanceof Error ? error.message : "Failed to reset password",
        variant: "destructive",
      });
    } finally {
      setAdminLoading(false);
    }
  };
  const [adminDeleteDialog, setAdminDeleteDialog] = useState<{
    admin: Admin | null;
    open: boolean;
  }>({
    admin: null,
    open: false,
  });

  const handleDeleteAdmin = async (admin: Admin) => {
    setAdminDeleteDialog({ admin, open: true });
  };

  const confirmDeleteAdmin = async () => {
    if (!adminDeleteDialog.admin) return;

    setAdminLoading(true);
    try {
      await apiClient.deleteAdmin(adminDeleteDialog.admin.id);
      toast({
        title: "Admin deleted",
        description: `Successfully deleted admin: ${adminDeleteDialog.admin.name}`,
      });
      setAdminDeleteDialog({ admin: null, open: false });
      fetchData();
    } catch (error) {
      toast({
        title: "Delete failed",
        description:
          error instanceof Error ? error.message : "Failed to delete admin",
        variant: "destructive",
      });
    } finally {
      setAdminLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-32 bg-muted rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="database" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="database" className="flex items-center space-x-2">
            <Database className="w-4 h-4" />
            <span>Database Management</span>
          </TabsTrigger>
          <TabsTrigger value="admins" className="flex items-center space-x-2">
            <Users className="w-4 h-4" />
            <span>Admin Management</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="database" className="space-y-6">
          {/* Database Status Overview */}
          <Card className="card-hover">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="w-5 h-5 text-primary" />
                <span>Database Status</span>
              </CardTitle>
              <CardDescription>
                Current database statistics and health status
              </CardDescription>
            </CardHeader>
            <CardContent>
              {" "}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <FileText className="w-6 h-6 mx-auto mb-2 text-primary" />
                  <p className="text-2xl font-bold">
                    {stats?.total_file_knowledge || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Files</p>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <Database className="w-6 h-6 mx-auto mb-2 text-accent" />
                  <p className="text-2xl font-bold">
                    {stats?.total_text_knowledge || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Text Records</p>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <Users className="w-6 h-6 mx-auto mb-2 text-success" />
                  <p className="text-2xl font-bold">
                    {stats?.total_user_questions || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    User Questions
                  </p>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <MessageSquare className="w-6 h-6 mx-auto mb-2 text-warning" />
                  <p className="text-2xl font-bold">
                    {stats?.total_admin_questions || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Admin Questions
                  </p>
                </div>
              </div>
              {/* Additional Stats */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <Clock className="w-6 h-6 mx-auto mb-2 text-info" />
                  <p className="text-2xl font-bold">
                    {stats?.pending_questions || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Pending</p>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <CheckCircle className="w-6 h-6 mx-auto mb-2 text-success" />
                  <p className="text-2xl font-bold">
                    {stats?.processed_questions || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Processed</p>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg">
                  <Activity className="w-6 h-6 mx-auto mb-2 text-primary" />
                  <p className="text-2xl font-bold">
                    {stats?.active_users || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Active Users</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Database Deletion Operations */}
          <Card className="card-hover">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Trash2 className="w-5 h-5 text-destructive" />
                <span>Database Operations</span>
              </CardTitle>
              <CardDescription>
                Dangerous operations - use with extreme caution
              </CardDescription>
            </CardHeader>
            <CardContent>
              {" "}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setDeleteDialog({ type: "vector-db", open: true })
                  }
                  className="justify-start text-red-600 hover:bg-red-50 border-red-200 col-span-full"
                >
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Purge Entire Vector Database
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDeleteDialog({ type: "files", open: true })}
                  className="justify-start text-destructive hover:bg-destructive/10"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Delete All Files
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDeleteDialog({ type: "text", open: true })}
                  className="justify-start text-destructive hover:bg-destructive/10"
                >
                  <Database className="w-4 h-4 mr-2" />
                  Delete All Text Knowledge
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setDeleteDialog({ type: "user-questions", open: true })
                  }
                  className="justify-start text-destructive hover:bg-destructive/10"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Delete All User Questions
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setDeleteDialog({ type: "admin-questions", open: true })
                  }
                  className="justify-start text-destructive hover:bg-destructive/10"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Delete All Admin Questions
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setDeleteDialog({ type: "dept-failures", open: true })
                  }
                  className="justify-start text-destructive hover:bg-destructive/10"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  Delete All Dept Failures
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setDeleteDialog({ type: "response-times", open: true })
                  }
                  className="justify-start text-destructive hover:bg-destructive/10"
                >
                  <Clock className="w-4 h-4 mr-2" />
                  Delete All Response Times
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="admins" className="space-y-6">
          {/* Admin Management Header */}
          <Card className="card-hover">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <UserCog className="w-5 h-5 text-primary" />
                    <span>Administrator Management</span>
                  </CardTitle>
                  <CardDescription>
                    Manage system administrators and their permissions
                  </CardDescription>
                </div>
                <Button
                  onClick={() =>
                    setAdminDialog({ admin: null, mode: "create", open: true })
                  }
                  className="gradient-primary"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Add Admin
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {admins.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No administrators found</p>
                  </div>
                ) : (
                  admins.map((admin) => (
                    <div
                      key={admin.id}
                      className="flex items-center justify-between p-4 bg-secondary rounded-lg border hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                          <Shield className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <p className="font-medium">{admin.name}</p>
                            <Badge
                              variant={
                                admin.role === "super_admin"
                                  ? "default"
                                  : "secondary"
                              }
                            >
                              {admin.role.replace("_", " ")}
                            </Badge>
                            {!admin.enabled && (
                              <Badge variant="destructive">Disabled</Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {admin.email}
                          </p>
                          <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-1">
                            {" "}
                            <div className="flex items-center space-x-1">
                              {admin.verified ? (
                                <CheckCircle className="w-3 h-3 text-success" />
                              ) : (
                                <XCircle className="w-3 h-3 text-destructive" />
                              )}
                              <span>
                                {admin.verified ? "Verified" : "Unverified"}
                              </span>
                            </div>
                            {admin.last_login && (
                              <div className="flex items-center space-x-1">
                                <Clock className="w-3 h-3" />
                                <span>
                                  Last login:{" "}
                                  {new Date(
                                    admin.last_login
                                  ).toLocaleDateString()}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            setAdminDialog({ admin, mode: "edit", open: true })
                          }
                        >
                          <Edit className="w-3 h-3 mr-1" />
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            setPasswordDialog({ admin, open: true })
                          }
                        >
                          <Key className="w-3 h-3 mr-1" />
                          Reset Password
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteAdmin(admin)}
                        >
                          <Trash2 className="w-3 h-3 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      {/* Dialogs */}
      <DatabaseDeleteDialog
        type={deleteDialog.type}
        open={deleteDialog.open}
        onOpenChange={(open) => setDeleteDialog({ ...deleteDialog, open })}
        onConfirm={handleDatabaseDelete}
        loading={deleteLoading}
      />
      <AdminDialog
        admin={adminDialog.admin}
        mode={adminDialog.mode}
        open={adminDialog.open}
        onOpenChange={(open) => setAdminDialog({ ...adminDialog, open })}
        onSave={handleAdminSave}
        loading={adminLoading}
      />{" "}
      <PasswordResetDialog
        admin={passwordDialog.admin}
        open={passwordDialog.open}
        onOpenChange={(open) => setPasswordDialog({ ...passwordDialog, open })}
        onReset={handlePasswordReset}
        loading={adminLoading}
      />
      <AdminDeleteDialog
        admin={adminDeleteDialog.admin}
        open={adminDeleteDialog.open}
        onOpenChange={(open) =>
          setAdminDeleteDialog({ ...adminDeleteDialog, open })
        }
        onConfirm={confirmDeleteAdmin}
        loading={adminLoading}
      />
    </div>
  );
};

export default SuperAdminPanel;
