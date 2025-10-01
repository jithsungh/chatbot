import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Bot,
  Upload,
  MessageSquare,
  HelpCircle,
  User,
  LogOut,
  MessageCircle,
  Database,
  Building,
  BookOpen,
} from "lucide-react";
import LogoutDialog from "@/components/dialogs/LogoutDialog";

const Navbar = () => {
  const { admin, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const navItems = [
    { path: "/", label: "Dashboard", icon: Bot },
    { path: "/upload", label: "Upload", icon: Upload },
    { path: "/queries", label: "Queries", icon: MessageSquare },
    { path: "/questions", label: "Questions", icon: HelpCircle },
    { path: "/departments", label: "Departments", icon: Building },
    { path: "/faqs", label: "Help & FAQs", icon: BookOpen },
    // Only show Admin panel for super admins
    ...(admin?.role === "super_admin"
      ? [{ path: "/admin", label: "Admin", icon: Database }]
      : []),
  ];

  const isActive = (path: string) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    setShowLogoutDialog(false);
    logout();
    navigate("/login");
  };

  return (
    <>
      <nav className="bg-card/80 backdrop-blur-md border-b border-border shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 gradient-primary rounded-lg shadow-md">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Chatbot Admin UI
                </h1>
              </div>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Link key={path} to={path}>
                  <Button
                    variant={isActive(path) ? "default" : "ghost"}
                    size="sm"
                    className={`flex items-center space-x-2 transition-smooth ${
                      isActive(path)
                        ? "gradient-primary text-white shadow-md"
                        : "hover:bg-secondary text-foreground"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{label}</span>
                  </Button>
                </Link>
              ))}
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                className="hidden md:flex items-center space-x-2 hover:gradient-accent hover:text-white transition-smooth"
                onClick={() => {
                  // Trigger chatbot opening
                  window.dispatchEvent(new CustomEvent("toggleChatbot"));
                }}
              >
                <MessageCircle className="w-4 h-4" />
                <span>Test Chatbot</span>
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-10 w-10 rounded-full"
                  >
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="gradient-secondary text-foreground font-semibold">
                        {admin?.name?.charAt(0).toUpperCase() || "A"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <div className="flex flex-col space-y-1 p-2">
                    <p className="text-sm font-medium leading-none">
                      {admin?.name}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {admin?.email}
                    </p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="cursor-pointer hover:bg-destructive/10 hover:text-destructive"
                    onClick={() => setShowLogoutDialog(true)}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden flex items-center justify-center space-x-1 pb-4">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link key={path} to={path}>
                <Button
                  variant={isActive(path) ? "default" : "ghost"}
                  size="sm"
                  className={`flex flex-col items-center space-y-1 h-auto py-2 px-3 transition-smooth ${
                    isActive(path)
                      ? "gradient-primary text-white shadow-md"
                      : "hover:bg-secondary text-foreground"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-xs">{label}</span>
                </Button>
              </Link>
            ))}
          </div>
        </div>
      </nav>

      <LogoutDialog
        open={showLogoutDialog}
        onOpenChange={setShowLogoutDialog}
        onConfirm={handleLogout}
      />
    </>
  );
};

export default Navbar;
