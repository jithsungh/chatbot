import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/utils/api';
import { 
  HelpCircle, 
  Filter,
  MessageCircle,
  User,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Users,
  Shield
} from 'lucide-react';

interface Question {
  id: string;
  question: string;
  user_id?: string;
  admin_id?: string;
  department: string;
  status: string;
  created_at: string;
  answer?: string;
  answered_at?: string;
}

const Questions = () => {
  const [userQuestions, setUserQuestions] = useState<Question[]>([]);
  const [adminQuestions, setAdminQuestions] = useState<Question[]>([]);
  const [questionType, setQuestionType] = useState<"user" | "admin">("user");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const [filterDept, setFilterDept] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const departments = ["HR", "IT", "Security"];
  const statuses = ["pending", "processed"];
  const pageSize = 10;

  useEffect(() => {
    fetchQuestions();
  }, [questionType, filterDept, filterStatus, currentPage]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const offset = (currentPage - 1) * pageSize;

      const questions =
        questionType === "user"
          ? await apiClient.getUserQuestions({
              status:
                filterStatus && filterStatus !== "all"
                  ? filterStatus
                  : undefined,
              dept: filterDept && filterDept !== "all" ? filterDept : undefined,
              limit: pageSize,
              offset,
            })
          : await apiClient.getAdminQuestions({
              status:
                filterStatus && filterStatus !== "all"
                  ? filterStatus
                  : undefined,
              dept: filterDept && filterDept !== "all" ? filterDept : undefined,
              limit: pageSize,
              offset,
            });

      // Ensure questions is always an array
      const questionsArray = Array.isArray(questions) ? questions : [];

      if (questionType === "user") {
        setUserQuestions(questionsArray);
      } else {
        setAdminQuestions(questionsArray);
      }

      // Calculate total pages (estimate based on returned results)
      setTotalPages(
        Math.max(
          1,
          Math.ceil(questionsArray.length / pageSize) +
            (questionsArray.length === pageSize ? 1 : 0)
        )
      );
    } catch (error) {
      console.error("Failed to fetch questions:", error);
      // Reset to empty arrays on error
      if (questionType === "user") {
        setUserQuestions([]);
      } else {
        setAdminQuestions([]);
      }
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to fetch questions",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestInChat = (question: string) => {
    window.dispatchEvent(
      new CustomEvent("setChatbotQuestion", {
        detail: { question },
      })
    );
    toast({
      title: "Question copied",
      description: "Question has been added to the chatbot test window",
      duration: 2000, // Optional: shorter duration for this specific toast
      className: "fixed top-4 right-4 z-[100] w-auto max-w-sm", // Position it in top-right
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return "bg-warning/10 text-warning border-warning/20";
      case "processed":
        return "bg-success/10 text-success border-success/20";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  // Ensure currentQuestions is always an array
  const currentQuestions =
    questionType === "user" ? userQuestions : adminQuestions;
  const safeCurrentQuestions = Array.isArray(currentQuestions)
    ? currentQuestions
    : [];

    // ...existing code...
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Questions Overview
            </h1>
            <p className="text-muted-foreground mt-1">
              Browse and analyze all questions from users and admins
            </p>
          </div>
        </div>
  
        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-medium">Filters:</span>
              </div>
  
              <Select value={filterDept} onValueChange={setFilterDept}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="All departments" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map((dept) => (
                    <SelectItem key={dept} value={dept}>
                      {dept}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
  
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {statuses.map((status) => (
                    <SelectItem key={status} value={status}>
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
  
              <Button
                variant="outline"
                onClick={() => {
                  setFilterDept("all");
                  setFilterStatus("all");
                  setCurrentPage(1);
                }}
              >
                Clear Filters
              </Button>
            </div>
          </CardContent>
        </Card>
  
        {/* Question Type Tabs */}
        <Tabs
          value={questionType}
          onValueChange={(value) => {
            setQuestionType(value as "user" | "admin");
            setCurrentPage(1);
          }}
        >
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="user" className="flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>User Questions</span>
            </TabsTrigger>
            <TabsTrigger value="admin" className="flex items-center space-x-2">
              <Shield className="w-4 h-4" />
              <span>Admin Questions</span>
            </TabsTrigger>
          </TabsList>
  
          <TabsContent value="user">
            <Card className="card-hover">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-primary" />
                  <span>User Questions</span>
                  <Badge variant="outline">{userQuestions.length}</Badge>
                </CardTitle>
                <CardDescription>
                  Questions submitted by end users through the chatbot
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-20 bg-muted rounded-lg"></div>
                      </div>
                    ))}
                  </div>
                ) : safeCurrentQuestions.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium mb-2">No questions found</p>
                    <p>Try adjusting your filters or check back later</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {safeCurrentQuestions.map((question) => (
                      <div
                        key={question.id}
                        className="p-4 bg-secondary rounded-lg border space-y-3 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium mb-2 line-clamp-2">
                              {question.question}
                            </p>
                            {question.answer && (
                              <div className="bg-success/10 p-3 rounded-md mb-3">
                                <p className="text-xs font-medium text-success mb-1">
                                  Answer:
                                </p>
                                <p className="text-xs text-success/80 line-clamp-2">
                                  {question.answer}
                                </p>
                              </div>
                            )}
                            <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                              <div className="flex items-center space-x-1">
                                <User className="w-3 h-3" />
                                <span>
                                  {questionType === "user"
                                    ? question.user_id
                                    : question.admin_id}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Calendar className="w-3 h-3" />
                                <span>
                                  {new Date(
                                    question.created_at
                                  ).toLocaleDateString()}
                                </span>
                              </div>
                              <Badge variant="outline" className="text-xs">
                                {question.department}
                              </Badge>
                            </div>
                          </div>
                          <div className="flex flex-col items-end space-y-2">
                            <Badge className={getStatusColor(question.status)}>
                              {question.status}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center justify-end">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleTestInChat(question.question)}
                            className="text-xs"
                          >
                            <MessageCircle className="w-3 h-3 mr-1" />
                            Test in Chat
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
  
          <TabsContent value="admin">
            <Card className="card-hover">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-accent" />
                  <span>Admin Questions</span>
                  <Badge variant="outline">{adminQuestions.length}</Badge>
                </CardTitle>
                <CardDescription>
                  Internal questions from admin users requiring responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-20 bg-muted rounded-lg"></div>
                      </div>
                    ))}
                  </div>
                ) : safeCurrentQuestions.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium mb-2">No questions found</p>
                    <p>Try adjusting your filters or check back later</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {safeCurrentQuestions.map((question) => (
                      <div
                        key={question.id}
                        className="p-4 bg-secondary rounded-lg border space-y-3 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium mb-2 line-clamp-2">
                              {question.question}
                            </p>
                            {question.answer && (
                              <div className="bg-success/10 p-3 rounded-md mb-3">
                                <p className="text-xs font-medium text-success mb-1">
                                  Answer:
                                </p>
                                <p className="text-xs text-success/80 line-clamp-2">
                                  {question.answer}
                                </p>
                              </div>
                            )}
                            <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                              <div className="flex items-center space-x-1">
                                <User className="w-3 h-3" />
                                <span>
                                  {questionType === "user"
                                    ? question.user_id
                                    : question.admin_id}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Calendar className="w-3 h-3" />
                                <span>
                                  {new Date(
                                    question.created_at
                                  ).toLocaleDateString()}
                                </span>
                              </div>
                              <Badge variant="outline" className="text-xs">
                                {question.department}
                              </Badge>
                            </div>
                          </div>
                          <div className="flex flex-col items-end space-y-2">
                            <Badge className={getStatusColor(question.status)}>
                              {question.status}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center justify-end">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleTestInChat(question.question)}
                            className="text-xs"
                          >
                            <MessageCircle className="w-3 h-3 mr-1" />
                            Test in Chat
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
  
        {/* Pagination */}
        {!loading && safeCurrentQuestions.length > 0 && (
          <div className="flex items-center justify-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </Button>
  
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </span>
            </div>
  
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        )}
      </div>
    );
  };
  
  export default Questions;