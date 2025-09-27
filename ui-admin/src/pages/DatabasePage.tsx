import React from 'react';
import DatabaseManagement from '@/components/database/DatabaseManagement';

const DatabasePage = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Database Management
        </h1>
        <p className="text-muted-foreground mt-1">
          Monitor database status and perform maintenance operations
        </p>
      </div>

      <DatabaseManagement />
    </div>
  );
};

export default DatabasePage;