import React from "react";
import { useAuth } from "@/contexts/AuthContext";
import SuperAdminPanel from "@/components/admin/SuperAdminPanel";

const AdminPage = () => {
  const { admin } = useAuth();

  // Check if user is super admin
  if (!admin || admin.role !== "super_admin") {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto bg-destructive/10 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-destructive"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-destructive">
              Access Denied
            </h2>
            <p className="text-muted-foreground mt-1">
              This page is only accessible to Super Administrators.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Super Admin Panel
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage admins, database operations, and system-wide settings
        </p>
      </div>

      <SuperAdminPanel />
    </div>
  );
};

export default AdminPage;
