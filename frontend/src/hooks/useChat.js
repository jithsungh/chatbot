import { useState } from "react";
import apiService from "../services/apiService";

export const useChat = (userId) => {
  const [isConnected] = useState(true); // Always connected for API calls
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (message) => {
    if (!message.trim()) {
      return false;
    }

    try {
      // Add user message to state immediately
      const userMessage = {
        id: Date.now(),
        type: "user",
        content: message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsTyping(true);
      setError(null);

      console.log("Sending query:", message);

      // Make API call
      const response = await apiService.sendUserQuery(message, userId);
      const data = response.data;

      console.log("Full response:", data);

      // Add bot response to messages
      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: data.answer,
        followup: data.followup,
        timestamp: new Date().toISOString(),
        metadata: {
          org_related: data.org_related,
          has_context: data.has_context,
          std_question: data.std_question,
        },
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);

      return true;
    } catch (err) {
      console.error("Error sending message:", err);
      setError(err.response?.data?.message || "Failed to send message");
      setIsTyping(false);
      return false;
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setError(null);
  };

  const clearError = () => {
    setError(null);
  };

  return {
    isConnected,
    messages,
    isTyping,
    error,
    sendMessage,
    clearMessages,
    clearError,
  };
};
