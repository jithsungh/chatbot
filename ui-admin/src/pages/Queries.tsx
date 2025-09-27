import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/utils/api';
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
  Calendar
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

const Queries = () => {
  const [pendingQuestions, setPendingQuestions] = useState<Question[]>([]);
  const [answeredQuestions, setAnsweredQuestions] = useState<Question[]>([]);
  const [filterDept, setFilterDept] = useState('');
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState('');
  const [isAnswering, setIsAnswering] = useState(false);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const departments = ['HR', 'IT', 'Security'];

  useEffect(() => {
    fetchQuestions();
  }, [filterDept]);

  const fetchQuestions = async () => {
    try {
      const [pendingData, answeredData] = await Promise.all([
        apiClient.getAdminQuestions({ 
          status: 'pending',
          dept: (filterDept && filterDept !== 'all') ? filterDept : undefined,
          limit: 100 
        }).catch(() => []),
        apiClient.getAdminQuestions({ 
          status: 'processed',
          dept: (filterDept && filterDept !== 'all') ? filterDept : undefined,
          limit: 100 
        }).catch(() => []),
      ]);

      setPendingQuestions(Array.isArray(pendingData) ? pendingData : []);
      setAnsweredQuestions(Array.isArray(answeredData) ? answeredData : []);
    } catch (error) {
      console.error('Failed to fetch questions:', error);
      setPendingQuestions([]);
      setAnsweredQuestions([]);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch questions",
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
      setAnswer('');
      fetchQuestions();
    } catch (error) {
      console.error('Error submitting answer:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit answer",
        variant: "destructive",
      });
    } finally {
      setIsAnswering(false);
    }
  };

  const handleTestInChat = (question: string) => {
    window.dispatchEvent(new CustomEvent('setChatbotQuestion', {
      detail: { question }
    }));
    toast({
      title: "Question copied",
      description: "Question has been added to the chatbot test window",
      duration: 2000, // Optional: shorter duration for this specific toast
      className: "fixed top-4 right-4 z-[100] w-auto max-w-sm", // Position it in top-right
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'processed':
        return 'bg-success/10 text-success border-success/20';
      default:
        return 'bg-muted text-muted-foreground';
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
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <Select value={filterDept} onValueChange={setFilterDept}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {departments.map(dept => (
                <SelectItem key={dept} value={dept}>{dept}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Questions */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-warning" />
                <span>Pending Questions</span>
              </div>
              <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">
                {pendingQuestions.length}
              </Badge>
            </CardTitle>
            <CardDescription>
              Questions awaiting admin response
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {pendingQuestions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No pending questions</p>
                </div>
              ) : (
                pendingQuestions.map((question) => (
                  <div key={question.id} className="p-4 bg-secondary rounded-lg border border-warning/20 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium mb-2">{question.question}</p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>{question.user_id || question.admin_id}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(question.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <Badge className={getStatusColor(question.status)}>
                        {question.status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        onClick={() => setSelectedQuestion(question)}
                        className="gradient-primary"
                      >
                        <Send className="w-3 h-3 mr-1" />
                        Answer
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTestInChat(question.question)}
                      >
                        <MessageCircle className="w-3 h-3 mr-1" />
                        Test in Chat
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Answered Questions */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-success" />
                <span>Answered Questions</span>
              </div>
              <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                {answeredQuestions.length}
              </Badge>
            </CardTitle>
            <CardDescription>
              Previously answered questions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {answeredQuestions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <CheckCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No answered questions yet</p>
                </div>
              ) : (
                answeredQuestions.map((question) => (
                  <div key={question.id} className="p-4 bg-secondary rounded-lg border border-success/20 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium mb-2">{question.question}</p>
                        {question.answer && (
                          <div className="bg-success/10 p-2 rounded text-xs text-success mb-2">
                            <strong>Answer:</strong> {question.answer}
                          </div>
                        )}
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>{question.user_id || question.admin_id}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(question.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <Badge className={getStatusColor(question.status)}>
                        {question.status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTestInChat(question.question)}
                      >
                        <MessageCircle className="w-3 h-3 mr-1" />
                        Test in Chat
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Answer Dialog */}
      <Dialog open={!!selectedQuestion} onOpenChange={(open) => !open && setSelectedQuestion(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Answer Question</DialogTitle>
            <DialogDescription>
              Provide a comprehensive answer to this question
            </DialogDescription>
          </DialogHeader>
          
          {selectedQuestion && (
            <div className="space-y-4">
              <div className="p-4 bg-muted rounded-lg">
                <p className="font-medium text-sm mb-2">Question:</p>
                <p className="text-sm">{selectedQuestion.question}</p>
                <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-2">
                  <span>Department: {selectedQuestion.department}</span>
                  <span>Asked: {new Date(selectedQuestion.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Your Answer:</label>
                <Textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  rows={6}
                  className="resize-none"
                />
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

export default Queries;