import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/utils/api";
import {
  HelpCircle,
  Filter,
  MessageCircle,
  User,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Users,
  Shield,
  Eye,
  FileText,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowUpDown,
  SortAsc,
  SortDesc,
  Loader2,
  X,
  Bot,
  UserX,
  ArrowDownUp,
} from "lucide-react";

interface Question {
  id: string;
  query?: string; // For user questions
  question?: string; // For admin questions
  user_id?: string;
  admin_id?: string;
  adminid?: string;
  admin_name?: string;
  asked_by?: string;
  assigned_to?: string;
  answered_by?: string;
  department: string;
  status: string;
  priority?: string;
  context?: string;
  acceptance?: string;
  frequency?: number;
  vectordbid?: string;
  created_at?: string;
  createdAt?: string;
  answer?: string;
  answered_at?: string;
  processed_at?: string;
}

interface QuestionPopupProps {
  question: Question | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  questionType: "user" | "admin";
}

interface SummaryData {
  success: boolean;
  questions_added: number;
  questions_processed: number;
  errors: string[];
  processed_by: string;
}

// Question Popup Component
const QuestionPopup: React.FC<QuestionPopupProps> = ({
  question,
  open,
  onOpenChange,
  questionType,
}) => {
  const { toast } = useToast();

  if (!question) return null;

  const getQuestionTypeLabel = () => {
    if (questionType === "user") {
      // For user questions, check if there's context or if user was satisfied
      if (
        !question.context ||
        question.context.toLowerCase().includes("no context")
      ) {
        return {
          label: "No Context",
          color: "bg-warning/10 text-warning border-warning/20",
          icon: AlertCircle,
        };
      }
      if (question.status === "pending") {
        return {
          label: "Not Satisfied",
          color: "bg-destructive/10 text-destructive border-destructive/20",
          icon: UserX,
        };
      }
      return {
        label: "Resolved",
        color: "bg-success/10 text-success border-success/20",
        icon: CheckCircle,
      };
    } else {
      // For admin questions
      return {
        label: "Admin Question",
        color: "bg-primary/10 text-primary border-primary/20",
        icon: Shield,
      };
    }
  };

  const typeInfo = getQuestionTypeLabel();
  const TypeIcon = typeInfo.icon;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Eye className="w-5 h-5" />
            <span>Question Details</span>
          </DialogTitle>
          <DialogDescription>
            {questionType === "user"
              ? "User submitted question"
              : "Admin question"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Question Type Badge */}
          <div className="flex items-center space-x-2">
            <Badge className={typeInfo.color}>
              <TypeIcon className="w-3 h-3 mr-1" />
              {typeInfo.label}
            </Badge>
            {question.priority && (
              <Badge variant="outline">Priority: {question.priority}</Badge>
            )}
            {question.frequency && (
              <Badge variant="secondary">Frequency: {question.frequency}</Badge>
            )}
          </div>

          {/* Question Content */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Question</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-wrap">
                {question.query || question.question}
              </p>
            </CardContent>
          </Card>

          {/* Context (for user questions) */}
          {question.context && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Context</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {question.context}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Answer */}
          {question.answer && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-success" />
                  <span>Answer</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap">{question.answer}</p>
                {question.answered_by && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Answered by: {question.answered_by}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-muted-foreground" />
                <span className="font-medium">
                  {questionType === "user"
                    ? `User: ${question.user_id}`
                    : `Asked by: ${
                        question.asked_by ||
                        question.admin_name ||
                        question.adminid
                      }`}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span>
                  {new Date(
                    question.created_at || question.createdAt || ""
                  ).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  {question.department}
                </Badge>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <Badge
                  className={
                    question.status === "pending"
                      ? "bg-warning/10 text-warning"
                      : "bg-success/10 text-success"
                  }
                >
                  {question.status}
                </Badge>
              </div>
              {question.answered_at && (
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-success" />
                  <span className="text-xs">
                    Answered: {new Date(question.answered_at).toLocaleString()}
                  </span>
                </div>
              )}
              {questionType === "admin" && question.assigned_to && (
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-muted-foreground" />
                  <span className="text-xs">
                    Assigned to: {question.assigned_to}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Test in Chat Button */}
          <div className="flex justify-end pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => {
                window.dispatchEvent(
                  new CustomEvent("setChatbotQuestion", {
                    detail: { question: question.query || question.question },
                  })
                );
                toast({
                  title: "Question copied",
                  description:
                    "Question has been added to the chatbot test window",
                  duration: 2000,
                });
                onOpenChange(false);
              }}
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              Test in Chat
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

const Questions = () => {
  const [userQuestions, setUserQuestions] = useState<Question[]>([]);
  const [adminQuestions, setAdminQuestions] = useState<Question[]>([]);
  const [questionType, setQuestionType] = useState<"user" | "admin">("user");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [summarizing, setSummarizing] = useState(false);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(
    null
  );
  const [showQuestionPopup, setShowQuestionPopup] = useState(false);
  const { toast } = useToast();
  const [filterDept, setFilterDept] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterAdmin, setFilterAdmin] = useState("all");
  const [sortBy, setSortBy] = useState<"date" | "dept" | "status" | "priority">(
    "date"
  );
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const departments = ["HR", "IT", "Security"];
  const statuses = ["pending", "processed"];
  const adminOptions = ["all", "self"];
  const pageSize = 10;

  useEffect(() => {
    fetchQuestions();
  }, [
    questionType,
    filterDept,
    filterStatus,
    filterAdmin,
    sortBy,
    sortOrder,
    currentPage,
  ]);
  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const offset = (currentPage - 1) * pageSize;

      const response =
        questionType === "user"
          ? await apiClient.getUserQuestions({
              status:
                filterStatus && filterStatus !== "all"
                  ? filterStatus
                  : undefined,
              dept: filterDept && filterDept !== "all" ? filterDept : undefined,
              sort_by: sortBy === "date" ? "createdAt" : sortBy,
              order: sortOrder,
              limit: pageSize,
              offset,
            })
          : await apiClient.getAdminQuestions({
              status:
                filterStatus && filterStatus !== "all"
                  ? filterStatus
                  : undefined,
              dept: filterDept && filterDept !== "all" ? filterDept : undefined,
              admin:
                filterAdmin && filterAdmin !== "all" ? filterAdmin : undefined,
              sort_by: sortBy === "date" ? "createdAt" : sortBy,
              order: sortOrder,
              limit: pageSize,
              offset,
            });

      // Handle the API response structure
      const questionsArray = response?.questions || [];
      const totalCount = response?.total_count || 0;

      if (questionType === "user") {
        setUserQuestions(questionsArray);
      } else {
        setAdminQuestions(questionsArray);
      }

      // Calculate total pages based on total count
      setTotalPages(Math.max(1, Math.ceil(totalCount / pageSize)));
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
  const handleSummarizeQuestions = async () => {
    setSummarizing(true);
    try {
      const result = await apiClient.summarizePendingQuestions();
      setSummaryData(result);
      setShowSummary(true);

      if (result.success) {
        toast({
          title: "Processing completed",
          description: `Added: ${result.questions_added}, Processed: ${result.questions_processed}`,
        });
      } else {
        toast({
          title: "Processing completed with issues",
          description: `Errors: ${result.errors.length}`,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Failed to process questions:", error);
      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to process questions",
        variant: "destructive",
      });
    } finally {
      setSummarizing(false);
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
      duration: 2000,
      className: "fixed top-4 right-4 z-[100] w-auto max-w-sm",
    });
  };

  const handleQuestionClick = (question: Question) => {
    setSelectedQuestion(question);
    setShowQuestionPopup(true);
  };

  const getQuestionTypeInfo = (question: Question) => {
    if (questionType === "user") {
      if (
        !question.context ||
        question.context.toLowerCase().includes("no context")
      ) {
        return {
          label: "No Context",
          color: "bg-warning/10 text-warning border-warning/20",
          icon: AlertCircle,
        };
      }
      if (question.status === "pending") {
        return {
          label: "Not Satisfied",
          color: "bg-destructive/10 text-destructive border-destructive/20",
          icon: UserX,
        };
      }
      return {
        label: "Resolved",
        color: "bg-success/10 text-success border-success/20",
        icon: CheckCircle,
      };
    } else {
      return {
        label: "Admin Question",
        color: "bg-primary/10 text-primary border-primary/20",
        icon: Shield,
      };
    }
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

  const renderQuestionCard = (question: Question) => {
    const typeInfo = getQuestionTypeInfo(question);
    const TypeIcon = typeInfo.icon;

    return (
      <div
        key={question.id}
        className="p-4 bg-secondary rounded-lg border space-y-3 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => handleQuestionClick(question)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <Badge className={typeInfo.color}>
                <TypeIcon className="w-3 h-3 mr-1" />
                {typeInfo.label}
              </Badge>
              {question.priority && (
                <Badge variant="outline" className="text-xs">
                  P: {question.priority}
                </Badge>
              )}
              {question.frequency && question.frequency > 1 && (
                <Badge variant="secondary" className="text-xs">
                  {question.frequency}x
                </Badge>
              )}
            </div>{" "}
            <p className="text-sm font-medium mb-2 line-clamp-2">
              {question.query || question.question}
            </p>
            {question.answer && (
              <div className="bg-success/10 p-3 rounded-md mb-3">
                <p className="text-xs font-medium text-success mb-1">Answer:</p>
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
                    : question.asked_by ||
                      question.admin_name ||
                      question.adminid}
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />{" "}
                <span>
                  {new Date(
                    question.created_at || question.createdAt || ""
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
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                handleQuestionClick(question);
              }}
              className="text-xs p-1 h-6"
            >
              <Eye className="w-3 h-3" />
            </Button>
          </div>
        </div>
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="text-xs text-muted-foreground">
            Click for full details
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              handleTestInChat(question.query || question.question || "");
            }}
            className="text-xs"
          >
            <MessageCircle className="w-3 h-3 mr-1" />
            Test in Chat
          </Button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Question Popup */}
      <QuestionPopup
        question={selectedQuestion}
        open={showQuestionPopup}
        onOpenChange={setShowQuestionPopup}
        questionType={questionType}
      />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Questions Overview
          </h1>
          <p className="text-muted-foreground mt-1">
            Browse and analyze all questions from users and admins
          </p>
        </div>{" "}
        {questionType === "user" && (
          <Button
            onClick={handleSummarizeQuestions}
            disabled={
              summarizing ||
              !safeCurrentQuestions ||
              safeCurrentQuestions.length === 0
            }
            className="gradient-primary"
          >
            {summarizing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 mr-2" />
                Process Questions
              </>
            )}
          </Button>
        )}
      </div>

      {/* Summary Dialog */}
      <Dialog open={showSummary} onOpenChange={setShowSummary}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          {" "}
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span>Questions Processing Results</span>
            </DialogTitle>
            <DialogDescription>
              Results of the questions processing operation
            </DialogDescription>
          </DialogHeader>
          {summaryData && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">
                    Processing Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-secondary rounded-lg">
                        <p className="text-sm font-medium">Questions Added</p>
                        <p className="text-2xl font-bold text-primary">
                          {summaryData.questions_added}
                        </p>
                      </div>
                      <div className="p-4 bg-secondary rounded-lg">
                        <p className="text-sm font-medium">
                          Questions Processed
                        </p>
                        <p className="text-2xl font-bold text-green-600">
                          {summaryData.questions_processed}
                        </p>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg border">
                      <div className="flex items-center space-x-2 mb-2">
                        {summaryData.success ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-600" />
                        )}
                        <p className="text-sm font-medium">
                          Status:{" "}
                          {summaryData.success
                            ? "Success"
                            : "Completed with errors"}
                        </p>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Processed by: {summaryData.processed_by}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>{" "}
              {summaryData.errors &&
                Array.isArray(summaryData.errors) &&
                summaryData.errors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-red-600" />
                        <span>Errors ({summaryData.errors.length})</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {summaryData.errors.map((error, index) => (
                          <div
                            key={index}
                            className="p-3 bg-red-50 border border-red-200 rounded-lg"
                          >
                            <p className="text-sm text-red-800">{error}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Filters and Sorting */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">Filters</span>
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

            {questionType === "admin" && (
              <Select value={filterAdmin} onValueChange={setFilterAdmin}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by admin" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Admins</SelectItem>
                  <SelectItem value="self">Answered by Me</SelectItem>
                </SelectContent>
              </Select>
            )}
            <div className="flex items-center space-x-2">
              <ArrowDownUp className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">Sort</span>
            </div>
            <Select
              value={sortBy}
              onValueChange={(value: "date" | "dept" | "status" | "priority") =>
                setSortBy(value)
              }
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Sort by Date</SelectItem>
                <SelectItem value="dept">Sort by Department</SelectItem>
                <SelectItem value="status">Sort by Status</SelectItem>
                {questionType === "admin" && (
                  <SelectItem value="frequency">Sort by frequency</SelectItem>
                )}
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
            >
              {sortOrder === "desc" ? (
                <SortDesc className="w-4 h-4 mr-1" />
              ) : (
                <SortAsc className="w-4 h-4 mr-1" />
              )}
              {sortOrder === "desc" ? "Desc" : "Asc"}
            </Button>

            <Button
              variant="outline"
              onClick={() => {
                setFilterDept("all");
                setFilterStatus("all");
                setFilterAdmin("all");
                setSortBy("date");
                setSortOrder("desc");
                setCurrentPage(1);
              }}
            >
              Clear All
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
                <Badge variant="outline">
                  {questionType === "user"
                    ? safeCurrentQuestions?.length || 0
                    : userQuestions.length}
                </Badge>
              </CardTitle>{" "}
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
              ) : !safeCurrentQuestions || safeCurrentQuestions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">No questions found</p>
                  <p>Try adjusting your filters or check back later</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {safeCurrentQuestions &&
                    safeCurrentQuestions.map(renderQuestionCard)}
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
                <Badge variant="outline">
                  {questionType === "admin"
                    ? safeCurrentQuestions?.length || 0
                    : adminQuestions.length}
                </Badge>
              </CardTitle>{" "}
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
              ) : !safeCurrentQuestions || safeCurrentQuestions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">No questions found</p>
                  <p>Try adjusting your filters or check back later</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {safeCurrentQuestions &&
                    safeCurrentQuestions.map(renderQuestionCard)}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      {/* Pagination */}
      {!loading && safeCurrentQuestions && safeCurrentQuestions.length > 0 && (
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
