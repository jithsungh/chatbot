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
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/utils/api";
import {
  MessageSquare,
  Clock,
  CheckCircle,
  AlertCircle,
  Filter,
  MessageCircle,
  Send,
  Loader2,
  User,
  Calendar,
  TrendingUp,
  Lightbulb,
  Users,
  Shield,
  Search,
  SortAsc,
  SortDesc,
} from "lucide-react";

interface Question {
  id: string;
  question: string;
  adminid?: string;
  admin_name?: string;
  answer?: string;
  acceptance?: string;
  department: string;
  status: string;
  frequency?: number;
  vectordbid?: string;
  createdAt: string;
  user_id?: string;
  admin_id?: string;
  created_at?: string;
  answered_at?: string;
}

const Queries = () => {
  const [pendingQuestions, setPendingQuestions] = useState<Question[]>([]);
  const [answeredQuestions, setAnsweredQuestions] = useState<Question[]>([]);
  const [activeTab, setActiveTab] = useState<"pending" | "answered">("pending");
  const [filterDept, setFilterDept] = useState("all");
  const [filterByMe, setFilterByMe] = useState("all");
  const [sortBy, setSortBy] = useState<"date" | "priority" | "department">(
    "date"
  );
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(
    null
  );
  const [answer, setAnswer] = useState("");
  const [isAnswering, setIsAnswering] = useState(false);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const departments = ["HR", "IT", "Security"];

  useEffect(() => {
    fetchQuestions();
  }, [filterDept, filterByMe, sortBy, sortOrder]);
  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const [pendingResponse, answeredResponse] = await Promise.all([
        apiClient
          .getAdminQuestions({
            status: "pending",
            dept: filterDept && filterDept !== "all" ? filterDept : undefined,
            admin: filterByMe && filterByMe !== "all" ? filterByMe : undefined,
            sort_by: sortOrder === "desc",
            limit: 100,
          })
          .catch(() => ({ questions: [] })),
        apiClient
          .getAdminQuestions({
            status: "processed",
            dept: filterDept && filterDept !== "all" ? filterDept : undefined,
            admin: filterByMe && filterByMe !== "all" ? filterByMe : undefined,
            sort_by: sortOrder === "desc",
            limit: 100,
          })
          .catch(() => ({ questions: [] })),
      ]);

      // Handle both old and new API response formats
      const pendingData = Array.isArray(pendingResponse)
        ? pendingResponse
        : pendingResponse?.questions || [];
      const answeredData = Array.isArray(answeredResponse)
        ? answeredResponse
        : answeredResponse?.questions || [];

      // Sort questions based on selected criteria
      const sortQuestions = (questions: Question[]) => {
        return [...questions].sort((a, b) => {
          let aValue, bValue;

          switch (sortBy) {
            case "priority":
              aValue = a.frequency || 0;
              bValue = b.frequency || 0;
              break;
            case "department":
              aValue = a.department;
              bValue = b.department;
              break;
            case "date":
            default:
              aValue = new Date(a.createdAt || a.created_at || "").getTime();
              bValue = new Date(b.createdAt || b.created_at || "").getTime();
              break;
          }

          if (sortOrder === "asc") {
            return aValue > bValue ? 1 : -1;
          } else {
            return aValue < bValue ? 1 : -1;
          }
        });
      };

      setPendingQuestions(sortQuestions(pendingData));
      setAnsweredQuestions(sortQuestions(answeredData));
    } catch (error) {
      console.error("Failed to fetch questions:", error);
      setPendingQuestions([]);
      setAnsweredQuestions([]);
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

  const handleAnswerQuestion = async () => {
    if (!selectedQuestion || !answer.trim()) return;

    setIsAnswering(true);
    try {
      await apiClient.answerQuestion(selectedQuestion.id, answer.trim());
      toast({
        title: "Answer submitted",
        description: "Your answer has been saved successfully",
      });
      setSelectedQuestion(null);
      setAnswer("");
      fetchQuestions();
    } catch (error) {
      console.error("Error submitting answer:", error);
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to submit answer",
        variant: "destructive",
      });
    } finally {
      setIsAnswering(false);
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Queries</h1>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-40 bg-muted rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Query Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Review and answer pending queries from the chatbot
          </p>
        </div>
      </div>
      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <Select value={filterDept} onValueChange={setFilterDept}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by department" />
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
            </div>

            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-muted-foreground" />
              <Select value={filterByMe} onValueChange={setFilterByMe}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by admin" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Admins</SelectItem>
                  <SelectItem value="self">Answered by me</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-muted-foreground" />
              <Select
                value={sortBy}
                onValueChange={(value: "date" | "priority" | "department") =>
                  setSortBy(value)
                }
              >
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">Date</SelectItem>
                  <SelectItem value="priority">Priority/Frequency</SelectItem>
                  <SelectItem value="department">Department</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
            >
              {sortOrder === "asc" ? (
                <SortAsc className="w-4 h-4" />
              ) : (
                <SortDesc className="w-4 h-4" />
              )}
            </Button>

            <Button
              variant="outline"
              onClick={() => {
                setFilterDept("all");
                setFilterByMe("all");
                setSortBy("date");
                setSortOrder("desc");
              }}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>{" "}
      {/* Tabbed Layout */}
      <Tabs
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as "pending" | "answered")}
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="pending" className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4" />
            <span>Pending Questions</span>
            <Badge
              variant="outline"
              className="bg-warning/10 text-warning border-warning/20 ml-2"
            >
              {pendingQuestions.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="answered" className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4" />
            <span>Answered Questions</span>
            <Badge
              variant="outline"
              className="bg-success/10 text-success border-success/20 ml-2"
            >
              {answeredQuestions.length}
            </Badge>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="mt-6">
          <Card className="card-hover">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-5 h-5 text-warning" />
                  <span>Questions Awaiting Response</span>
                </div>
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    Priority based on frequency
                  </span>
                </div>
              </CardTitle>
              <CardDescription>
                Questions that need admin attention and responses
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-24 bg-muted rounded-lg"></div>
                    </div>
                  ))}
                </div>
              ) : pendingQuestions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">
                    No pending questions
                  </p>
                  <p>All questions have been answered!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {pendingQuestions.map((question) => (
                    <QuestionCard
                      key={question.id}
                      question={question}
                      onAnswer={setSelectedQuestion}
                      onTestInChat={handleTestInChat}
                      isPending={true}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="answered" className="mt-6">
          <Card className="card-hover">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-success" />
                <span>Resolved Questions</span>
              </CardTitle>
              <CardDescription>
                Questions that have been answered and resolved
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-24 bg-muted rounded-lg"></div>
                    </div>
                  ))}
                </div>
              ) : answeredQuestions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckCircle className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">
                    No answered questions yet
                  </p>
                  <p>Questions you answer will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {answeredQuestions.map((question) => (
                    <QuestionCard
                      key={question.id}
                      question={question}
                      onTestInChat={handleTestInChat}
                      isPending={false}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>{" "}
      {/* Answer Dialog */}
      <Dialog
        open={!!selectedQuestion}
        onOpenChange={(open) => !open && setSelectedQuestion(null)}
      >
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Send className="w-5 h-5 text-primary" />
              <span>Answer Question</span>
            </DialogTitle>
            <DialogDescription>
              Provide a comprehensive answer based on the acceptance criteria
              below
            </DialogDescription>
          </DialogHeader>

          {selectedQuestion && (
            <div className="space-y-6">
              {/* Question Section */}
              <div className="p-4 bg-muted rounded-lg">
                <p className="font-medium text-sm mb-2 text-primary">
                  Question:
                </p>
                <p className="text-sm leading-relaxed">
                  {selectedQuestion.question}
                </p>
                <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-3">
                  <div className="flex items-center space-x-1">
                    <Badge variant="outline">
                      {selectedQuestion.department}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>
                      Asked:{" "}
                      {new Date(
                        selectedQuestion.createdAt ||
                          selectedQuestion.created_at ||
                          ""
                      ).toLocaleDateString()}
                    </span>
                  </div>
                  {selectedQuestion.frequency && (
                    <div className="flex items-center space-x-1">
                      <TrendingUp className="w-3 h-3" />
                      <span>Asked {selectedQuestion.frequency} times</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Acceptance Criteria Section */}
              {selectedQuestion.acceptance && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-2 mb-3">
                    <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm text-blue-900 mb-1">
                        Answer Guidelines & Acceptance Criteria:
                      </p>
                      <p className="text-sm text-blue-800 leading-relaxed whitespace-pre-line">
                        {selectedQuestion.acceptance}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Answer Input Section */}
              <div className="space-y-3">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <Send className="w-4 h-4" />
                  <span>Your Answer:</span>
                </label>
                <Textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Based on the acceptance criteria above, provide a detailed and comprehensive answer..."
                  rows={8}
                  className="resize-none"
                />
                <p className="text-xs text-muted-foreground">
                  Tip: Follow the acceptance criteria to ensure your answer
                  meets all requirements.
                </p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setSelectedQuestion(null)}
              disabled={isAnswering}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAnswerQuestion}
              disabled={!answer.trim() || isAnswering}
              className="gradient-primary"
            >
              {isAnswering ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Submit Answer
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Question Card Component
interface QuestionCardProps {
  question: Question;
  onAnswer?: (question: Question) => void;
  onTestInChat: (question: string) => void;
  isPending: boolean;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onAnswer,
  onTestInChat,
  isPending,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const maxPreviewLines = 2;

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

  const getPriorityColor = (frequency?: number) => {
    if (!frequency) return "text-muted-foreground";
    if (frequency >= 5) return "text-red-600";
    if (frequency >= 3) return "text-orange-600";
    return "text-blue-600";
  };

  const truncateText = (text: string, maxLines: number) => {
    const words = text.split(" ");
    const wordsPerLine = 15; // Approximate words per line
    const maxWords = maxLines * wordsPerLine;

    if (words.length <= maxWords) return text;
    return words.slice(0, maxWords).join(" ") + "...";
  };

  return (
    <div
      className={`p-4 bg-secondary rounded-lg border space-y-3 hover:shadow-md transition-all duration-200 ${
        isPending
          ? "border-warning/20 hover:border-warning/40"
          : "border-success/20 hover:border-success/40"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-3">
          {" "}
          {/* Question Text */}
          <div>
            <p
              className={`text-sm font-medium leading-relaxed ${
                isExpanded ? "" : "overflow-hidden"
              }`}
              style={
                !isExpanded
                  ? {
                      display: "-webkit-box",
                      WebkitLineClamp: maxPreviewLines,
                      WebkitBoxOrient: "vertical",
                    }
                  : {}
              }
            >
              {question.question}
            </p>
            {question.question.length > 100 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-auto p-0 mt-1 text-xs text-primary hover:text-primary/80"
              >
                {isExpanded ? "Show less" : "Show more"}
              </Button>
            )}
          </div>
          {/* Answer Preview (for answered questions) */}
          {!isPending && question.answer && (
            <div className="bg-success/10 p-3 rounded-md border border-success/20">
              <p className="text-xs font-medium text-success mb-1 flex items-center space-x-1">
                <CheckCircle className="w-3 h-3" />
                <span>Answer:</span>
              </p>
              <p
                className="text-xs text-success/80 leading-relaxed overflow-hidden"
                style={{
                  display: "-webkit-box",
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: "vertical",
                }}
              >
                {question.answer}
              </p>
            </div>
          )}
          {/* Metadata */}
          <div className="flex items-center flex-wrap gap-3 text-xs text-muted-foreground">
            <div className="flex items-center space-x-1">
              <User className="w-3 h-3" />
              <span>
                {question.adminid ||
                  question.user_id ||
                  question.admin_id ||
                  "Anonymous"}
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar className="w-3 h-3" />
              <span>
                {new Date(
                  question.createdAt || question.created_at || ""
                ).toLocaleDateString()}
              </span>
            </div>
            <Badge variant="outline" className="text-xs">
              {question.department}
            </Badge>
            {question.frequency && (
              <div
                className={`flex items-center space-x-1 ${getPriorityColor(
                  question.frequency
                )}`}
              >
                <TrendingUp className="w-3 h-3" />
                <span className="font-medium">
                  Frequency: {question.frequency}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col items-end space-y-2 ml-4">
          <Badge className={getStatusColor(question.status)}>
            {question.status}
          </Badge>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-2 border-t border-border/50">
        <div className="flex items-center space-x-2">
          {isPending && onAnswer && (
            <Button
              size="sm"
              onClick={() => onAnswer(question)}
              className="gradient-primary"
            >
              <Send className="w-3 h-3 mr-1" />
              Answer
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={() => onTestInChat(question.question)}
          >
            <MessageCircle className="w-3 h-3 mr-1" />
            Test in Chat
          </Button>
        </div>

        {question.frequency && question.frequency >= 3 && (
          <div className="flex items-center space-x-1 text-xs text-orange-600">
            <AlertCircle className="w-3 h-3" />
            <span>High Priority</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Queries;
