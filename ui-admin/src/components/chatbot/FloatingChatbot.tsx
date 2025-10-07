import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  MessageCircle,
  X,
  Send,
  Loader2,
  Bot,
  User,
  Minimize2,
  Trash2,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  content: string;
  followup?: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatResponse {
  org_related: boolean;
  has_context: boolean;
  answer: string;
  followup: string;
  std_question: string;
}

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI assistant. How can I help you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isClearingHistory, setIsClearingHistory] = useState(false);
  const [userId] = useState(() => {
    let storedUserId = localStorage.getItem("chatbot_user_id");
    if (!storedUserId) {
      storedUserId = crypto.randomUUID();
      localStorage.setItem("chatbot_user_id", storedUserId);
    }
    return storedUserId;
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleToggleChatbot = () => {
      setIsOpen((prev) => !prev);
    };

    window.addEventListener("toggleChatbot", handleToggleChatbot);
    return () =>
      window.removeEventListener("toggleChatbot", handleToggleChatbot);
  }, []);

  // Listen for custom events to set questions from other components
  useEffect(() => {
    const handleSetQuestion = (event: CustomEvent) => {
      setInputValue(event.detail.question);
      setIsOpen(true);
      setIsMinimized(false);
      // Removed toast notification
    };

    window.addEventListener(
      "setChatbotQuestion",
      handleSetQuestion as EventListener
    );
    return () =>
      window.removeEventListener(
        "setChatbotQuestion",
        handleSetQuestion as EventListener
      );
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/user/query/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: currentInput,
          userid: userId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content:
          data.answer ||
          "I received your message but couldn't generate a response.",
        followup: data.followup,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Connection Error",
        description:
          "Unable to connect to the chatbot service. Make sure the backend is running on localhost:8000",
        variant: "destructive",
      });

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content:
          "Sorry, I'm having trouble connecting to the server. Please make sure the backend service is running and try again.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChatHistory = async () => {
    if (isClearingHistory) return;

    setIsClearingHistory(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/user/history/${userId}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Clear local messages (keep only the initial greeting)
      setMessages([
        {
          id: "1",
          content: "Hello! I'm your AI assistant. How can I help you today?",
          isUser: false,
          timestamp: new Date(),
        },
      ]);

      toast({
        title: "Chat History Cleared",
        description: "Your conversation history has been successfully cleared.",
        variant: "default",
      });
    } catch (error) {
      console.error("Error clearing chat history:", error);
      toast({
        title: "Clear History Failed",
        description: "Unable to clear chat history. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsClearingHistory(false);
    }
  };

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 h-16 w-16 rounded-full shadow-2xl hover:shadow-glow transition-all duration-300 z-50 gradient-primary"
        size="icon"
      >
        <MessageCircle className="h-7 w-7 text-white" />
      </Button>
    );
  }

  if (isMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Card
          className="w-80 shadow-2xl border-0 cursor-pointer hover:shadow-glow transition-all duration-300"
          onClick={() => setIsMinimized(false)}
        >
          <CardHeader className="gradient-primary text-white p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5" />
                <CardTitle className="text-lg">AI Assistant</CardTitle>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs opacity-90">Online</span>
              </div>
            </div>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className="w-full max-w-md h-[100vh] max-h-[90vh] flex flex-col shadow-2xl border-0 bg-background/95 backdrop-blur-md">
        {/* Header */}
        <CardHeader className="flex flex-row items-center justify-between gradient-primary text-white p-4 rounded-t-lg">
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6" />
            <div>
              <CardTitle className="text-lg">AI Assistant</CardTitle>
              <p className="text-xs opacity-90">Powered by TechMojo</p>
            </div>
          </div>{" "}
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={clearChatHistory}
              disabled={isClearingHistory || messages.length <= 1}
              className="h-8 w-8 text-white hover:bg-white/20 disabled:opacity-50"
              title="Clear chat history"
            >
              {isClearingHistory ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMinimized(true)}
              className="h-8 w-8 text-white hover:bg-white/20"
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 text-white hover:bg-white/20"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {/* Messages */}
        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea className="h-full p-6">
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.isUser ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`flex items-start space-x-3 max-w-[85%] ${
                      message.isUser ? "flex-row-reverse space-x-reverse" : ""
                    }`}
                  >
                    <div
                      className={`flex items-center justify-center w-10 h-10 rounded-full flex-shrink-0 ${
                        message.isUser ? "gradient-primary" : "bg-muted"
                      }`}
                    >
                      {message.isUser ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-foreground" />
                      )}
                    </div>
                    <div className="space-y-2">
                      <div
                        className={`rounded-2xl px-4 py-3 ${
                          message.isUser
                            ? "gradient-primary text-white"
                            : "bg-muted text-foreground border"
                        }`}
                      >
                        <p className="text-sm leading-relaxed">
                          {message.content}
                        </p>
                      </div>
                      {message.followup && !message.isUser && (
                        <div className="bg-accent/10 border border-accent/20 rounded-xl px-4 py-3 ml-2">
                          <p className="text-xs text-accent font-medium mb-1">
                            Follow-up suggestion:
                          </p>
                          <p className="text-sm text-foreground/80">
                            {message.followup}
                          </p>
                        </div>
                      )}
                      <p className="text-xs text-muted-foreground px-2">
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-3">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-muted">
                      <Bot className="w-5 h-5 text-foreground" />
                    </div>
                    <div className="bg-muted text-foreground rounded-2xl px-4 py-3 border">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>

        {/* Input */}
        <div className="p-4 border-t bg-background">
          <div className="flex space-x-3">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              disabled={isLoading}
              className="flex-1 rounded-full px-4 py-2 focus:ring-2 focus:ring-primary"
            />
            <Button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              size="icon"
              className="gradient-primary rounded-full w-10 h-10 flex-shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            User ID: {userId.slice(-8)}...
          </p>
        </div>
      </Card>
    </div>
  );
};

export default FloatingChatbot;
