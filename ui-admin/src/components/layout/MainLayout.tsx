import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import FloatingChatbot from '@/components/chatbot/FloatingChatbot';

const MainLayout = () => {
  return (
    <div className="min-h-screen gradient-subtle">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
      <FloatingChatbot />
    </div>
  );
};

export default MainLayout;