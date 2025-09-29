import React, { useEffect, useState, useCallback } from "react";
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
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/utils/api";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import DatabaseManagement from "@/components/database/DatabaseManagement";
import {
  MessageSquare,
  FileText,
  Users,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Upload,
  RefreshCw,
  Eye,
  BarChart3,
  Activity,
  Database,
  Calendar,
  Timer,
  BookOpen,
} from "lucide-react";

interface DashboardStats {
  total_user_questions: number;
  total_admin_questions: number;
  total_text_knowledge: number;
  total_file_knowledge: number;
  pending_questions: number;
  processed_questions: number;
  avg_response_time: number;
  active_users: number;
  requested_by: string;
}

interface ResponseTimeData {
  interval?: string;
  n: number;
  data: Array<{
    timestamp: string;
    avg_response_time: number;
    requests_count: number;
  }>;
}

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [responseTimeData, setResponseTimeData] =
    useState<ResponseTimeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [timeInterval, setTimeInterval] = useState<string>("1min");
  const [dataPoints, setDataPoints] = useState<number>(20);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { admin } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const fetchDashboardStats = useCallback(async () => {
    try {
      console.log("Fetching dashboard stats...");
      const [dashboardStats, responseStats] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getAvgResponseTimes(timeInterval, dataPoints),
      ]);

      console.log("Dashboard stats received:", dashboardStats);
      console.log("Response time data received:", responseStats);

      setStats(dashboardStats);
      setResponseTimeData(responseStats);
    } catch (error) {
      console.error("Failed to fetch dashboard stats:", error);
      toast({
        title: "Error loading dashboard",
        description: `Unable to fetch the latest statistics: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeInterval, toast]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardStats();
  };

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  // Auto-refresh every minute for response time
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      if (stats) {
        // Only refresh response time data to avoid full page reload
        apiClient
          .getAvgResponseTimes(timeInterval, dataPoints)
          .then(setResponseTimeData)
          .catch(console.error);
      }
    }, 60000); // 1 minute

    return () => clearInterval(interval);
  }, [autoRefresh, stats, timeInterval]); // Format response time for display
  const formatResponseTime = (time: number) => {
    if (time < 1) return `${(time * 1000).toFixed(0)}ms`;
    return `${time.toFixed(2)}s`;
  }; // Mock data for testing (remove when API is working)
  const getMockStats = (): DashboardStats => ({
    total_user_questions: 1234,
    total_admin_questions: 56,
    total_text_knowledge: 89,
    total_file_knowledge: 234,
    pending_questions: 12,
    processed_questions: 1278,
    avg_response_time: 0.85,
    active_users: 45,
    requested_by: "mock-admin",
  });

  // Helper to get current stats (real or mock)
  const getCurrentStats = () => stats || getMockStats();
  const getStatItems = () => {
    const currentStats = getCurrentStats();

    if (!currentStats) return [];

    return [
      {
        title: "Answered Questions",
        value: currentStats.processed_questions,
        description: "Successfully resolved",
        icon: CheckCircle,
        gradient: "from-green-500 to-green-600",
        bgGradient: "from-green-50 to-green-100",
        action: () => navigate("/queries"),
      },
      {
        title: "Pending Questions",
        value: currentStats.pending_questions,
        description: "Awaiting response",
        icon: AlertCircle,
        gradient: "from-orange-500 to-orange-600",
        bgGradient: "from-orange-50 to-orange-100",
        action: () => navigate("/questions"),
      },
      {
        title: "Avg Response Time",
        value: formatResponseTime(currentStats.avg_response_time),
        description: "System performance",
        icon: Clock,
        gradient: "from-teal-500 to-teal-600",
        bgGradient: "from-teal-50 to-teal-100",
      },
      {
        title: "Total Files in Database",
        value: currentStats.total_file_knowledge,
        description: "Knowledge base files",
        icon: FileText,
        gradient: "from-purple-500 to-purple-600",
        bgGradient: "from-purple-50 to-purple-100",
        action: () => navigate("/upload"),
        hasViewButton: true,
      },
      {
        title: "Total Uploaded Texts",
        value: currentStats.total_text_knowledge,
        description: "Text Knowledge Entries",
        icon: MessageSquare,
        gradient: "from-blue-500 to-blue-600",
        bgGradient: "from-blue-50 to-blue-100",
        action: () => navigate("/upload"),
      },
      {
        title: "Total Users",
        value: currentStats.active_users,
        description: "From history manager",
        icon: Users,
        gradient: "from-indigo-500 to-indigo-600",
        bgGradient: "from-indigo-50 to-indigo-100",
      },
    ];
  };
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-96" />
          </div>
          <div className="flex items-center space-x-4">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-9 w-20" />
          </div>
        </div>

        {/* Stats Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card
              key={i}
              className="animate-pulse bg-gradient-to-br from-muted/50 to-muted/30"
            >
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Skeleton className="h-10 w-10 rounded-xl" />
                    <Skeleton className="h-6 w-16" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-8 w-24" />
                    <Skeleton className="h-3 w-28" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Chart Skeleton */}
        <Card className="animate-pulse">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Skeleton className="h-6 w-48" />
                <div className="flex space-x-2">
                  <Skeleton className="h-9 w-32" />
                  <Skeleton className="h-9 w-9" />
                </div>
              </div>
              <Skeleton className="h-64 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Mock Data Banner */}
      {!stats && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4 text-center">
            <p className="text-blue-800 text-sm">
              <strong>Debug Mode:</strong> Showing mock data while API
              connection is being established. Use the "Test API" button to
              check the backend connection.
            </p>
          </CardContent>
        </Card>
      )}
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-purple-500 to-accent bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Welcome back! Here's what's happening with your chatbot.
          </p>{" "}
          {getCurrentStats() && (
            <p className="text-sm text-muted-foreground mt-1 flex items-center gap-2">
              <Database className="w-4 h-4" />
              {(
                getCurrentStats().total_user_questions +
                getCurrentStats().total_admin_questions
              ).toLocaleString()}{" "}
              total questions • {getCurrentStats().active_users} active users
            </p>
          )}
          {/* Debug Info */}
          <div className="text-xs text-muted-foreground mt-2 space-y-1">
            <p>
              Admin: {admin?.name} ({admin?.role})
            </p>
            <p>
              Token:{" "}
              {localStorage.getItem("adminToken") ? "Present" : "Missing"}
            </p>
            <p>Loading: {loading ? "Yes" : "No"}</p>
            <p>Stats: {stats ? "Loaded" : "Not loaded"}</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-success/10 px-3 py-2 rounded-lg border border-success/20">
            <div className="h-2 w-2 bg-success rounded-full animate-pulse"></div>
            <span className="text-sm text-success font-medium">
              System Online
            </span>
          </div>{" "}
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 h-10"
            >
              {refreshing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Refreshing...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </>
              )}
            </Button>

            {/* Debug Test Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                try {
                  console.log("Manual API test starting...");
                  const token = localStorage.getItem("adminToken");
                  console.log(
                    "Token for manual test:",
                    token ? "Present" : "Missing"
                  );

                  const response = await fetch(
                    "http://localhost:8000/api/read/dashboard/stats",
                    {
                      headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                      },
                    }
                  );

                  console.log("Manual test response status:", response.status);
                  const data = await response.json();
                  console.log("Manual test response data:", data);

                  toast({
                    title: "API Test Result",
                    description: `Status: ${response.status}. Check console for details.`,
                    variant: response.ok ? "default" : "destructive",
                  });
                } catch (error) {
                  console.error("Manual API test error:", error);
                  toast({
                    title: "API Test Failed",
                    description:
                      error instanceof Error ? error.message : "Unknown error",
                    variant: "destructive",
                  });
                }
              }}
              className="text-xs h-10"
            >
              Test API
            </Button>
          </div>
        </div>
      </div>{" "}
      {/* Stats Grid - Beautiful 2x3 Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {getStatItems().length > 0 ? (
          getStatItems().map((item, index) => {
            const Icon = item.icon;
            return (
              <Card
                key={item.title}
                className={`stats-card group hover:scale-[1.02] hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br ${
                  item.bgGradient
                } ${item.action ? "cursor-pointer" : ""}`}
                onClick={item.action}
              >
                <CardContent className="p-6 relative overflow-hidden">
                  {/* Background Pattern */}
                  <div className="absolute top-0 right-0 -mr-4 -mt-4 w-24 h-24 opacity-10">
                    <Icon className="w-full h-full text-current" />
                  </div>

                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div
                        className={`p-3 rounded-xl bg-gradient-to-r ${item.gradient} group-hover:scale-110 transition-transform duration-300 shadow-lg`}
                      >
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      {item.hasViewButton && (
                        <Button
                          variant="secondary"
                          size="sm"
                          className="h-8 px-3 text-xs font-medium"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate("/upload");
                          }}
                        >
                          <Eye className="w-3 h-3 mr-1" />
                          View Files
                        </Button>
                      )}
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm font-medium text-muted-foreground">
                        {item.title}
                      </p>
                      <p className="text-3xl font-bold text-foreground tracking-tight">
                        {typeof item.value === "number"
                          ? item.value.toLocaleString()
                          : item.value}
                      </p>
                      <p className="text-xs text-muted-foreground/80">
                        {item.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        ) : (
          /* Debug fallback when no stats are available */
          <div className="col-span-full">
            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="p-6 text-center">
                <AlertCircle className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
                <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                  No Dashboard Stats Available
                </h3>
                <p className="text-yellow-700 mb-4">
                  Stats data is not loading. This could be due to:
                </p>
                <ul className="text-sm text-yellow-600 text-left max-w-md mx-auto space-y-1">
                  <li>• API authentication issues</li>
                  <li>• Backend server not running</li>
                  <li>• Network connectivity problems</li>
                  <li>• Database connection issues</li>
                </ul>
                <Button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="mt-4"
                  variant="outline"
                >
                  {refreshing ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Retrying...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Retry Loading Stats
                    </>
                  )}
                </Button>
                {stats && (
                  <div className="mt-4 p-2 bg-yellow-100 rounded text-xs text-left">
                    <strong>Debug Info:</strong>
                    <pre className="mt-1 whitespace-pre-wrap">
                      {JSON.stringify(stats, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
      {/* Response Time Graph */}
      <Card className="card-hover">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                <span>Response Time Graph</span>
              </CardTitle>
              <CardDescription>
                Visualize average response time over time
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Select value={timeInterval} onValueChange={setTimeInterval}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {/* 1min,5min,10min,30min,1h,3h,6h,12h,24h */}
                  <SelectItem value="1min">1 minute</SelectItem>
                  <SelectItem value="5min">5 minutes</SelectItem>
                  <SelectItem value="10min">10 minutes</SelectItem>
                  <SelectItem value="30min">30 minutes</SelectItem>
                  <SelectItem value="1h">1 hour</SelectItem>
                  <SelectItem value="3h">3 hours</SelectItem>
                  <SelectItem value="6h">6 hours</SelectItem>
                  <SelectItem value="12h">12 hours</SelectItem>
                  <SelectItem value="24h">24 hours</SelectItem>
                </SelectContent>
              </Select>
              {/* Add one more selector for n, - 10 ,20,50,100 */}
              <Select
                value={dataPoints.toString()}
                onValueChange={(val) => setDataPoints(Number(val))}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                {refreshing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {responseTimeData &&
          responseTimeData.data &&
          responseTimeData.data.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-4">
                  {" "}
                  <Badge
                    variant="outline"
                    className="bg-primary/10 text-primary border-primary/20"
                  >
                    Avg:{" "}
                    {formatResponseTime(
                      responseTimeData.data.reduce(
                        (sum, item) => sum + item.avg_response_time,
                        0
                      ) / responseTimeData.data.length
                    )}
                  </Badge>
                  <Badge variant="outline" className="bg-secondary">
                    Data Points: {responseTimeData.n}
                  </Badge>
                  <div className="flex items-center space-x-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        autoRefresh ? "bg-success animate-pulse" : "bg-muted"
                      }`}
                    ></div>
                    <span className="text-xs text-muted-foreground">
                      {autoRefresh
                        ? "Auto-refresh: 1 min"
                        : "Auto-refresh: Off"}
                    </span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className="h-6 px-2 text-xs"
                >
                  {autoRefresh ? "Turn Off" : "Turn On"} Auto-refresh
                </Button>
              </div>

              <div className="h-64">
                <ChartContainer
                  config={{
                    avg_response_time: {
                      label: "Response Time",
                      color: "hsl(var(--primary))",
                    },
                  }}
                  className="h-full w-full"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={responseTimeData.data.map((item) => ({
                        ...item,
                        formattedTime: new Date(
                          item.timestamp
                        ).toLocaleTimeString("en-US", {
                          hour: "2-digit",
                          minute: "2-digit",
                          ...(timeInterval === "daily"
                            ? {}
                            : {
                                month: "short",
                                day: "numeric",
                              }),
                        }),
                        displayValue: formatResponseTime(
                          item.avg_response_time
                        ),
                      }))}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        className="stroke-muted"
                      />
                      <XAxis
                        dataKey="formattedTime"
                        className="text-xs text-muted-foreground"
                        interval="preserveStartEnd"
                      />
                      <YAxis
                        className="text-xs text-muted-foreground"
                        tickFormatter={(value) => formatResponseTime(value)}
                      />{" "}
                      <ChartTooltip
                        content={
                          <ChartTooltipContent
                            labelFormatter={(value, payload) => {
                              if (payload && payload[0]) {
                                return new Date(
                                  payload[0].payload.timestamp
                                ).toLocaleString();
                              }
                              return value;
                            }}
                            formatter={(value, name, props) => {
                              if (name === "avg_response_time") {
                                const requestCount =
                                  props?.payload?.requests_count || 0;
                                return [
                                  <>
                                    <div className="text-xs text-muted-foreground">
                                      Response Time:{" "}
                                      {formatResponseTime(value as number)}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                      Requests: {requestCount}
                                    </div>
                                  </>,
                                ];
                              }
                              return [value, name];
                            }}
                          />
                        }
                      />
                      <Line
                        type="monotone"
                        dataKey="avg_response_time"
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        dot={{
                          fill: "hsl(var(--primary))",
                          strokeWidth: 2,
                          r: 4,
                        }}
                        activeDot={{
                          r: 6,
                          stroke: "hsl(var(--primary))",
                          strokeWidth: 2,
                        }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              <div className="text-center space-y-2">
                <Activity className="w-8 h-8 mx-auto opacity-50" />
                <p>No response time data available</p>
                <Button variant="outline" size="sm" onClick={handleRefresh}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh Data
                </Button>
              </div>
            </div>
          )}{" "}
        </CardContent>
      </Card>
      {/* Request Count Graph */}
      <Card className="card-hover">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-primary" />
                <span>Request Count Graph</span>
              </CardTitle>
              <CardDescription>Number of requests over time</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Select value={timeInterval} onValueChange={setTimeInterval}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1min">1 minute</SelectItem>
                  <SelectItem value="5min">5 minutes</SelectItem>
                  <SelectItem value="10min">10 minutes</SelectItem>
                  <SelectItem value="30min">30 minutes</SelectItem>
                  <SelectItem value="1h">1 hour</SelectItem>
                  <SelectItem value="3h">3 hours</SelectItem>
                  <SelectItem value="6h">6 hours</SelectItem>
                  <SelectItem value="12h">12 hours</SelectItem>
                  <SelectItem value="24h">24 hours</SelectItem>
                </SelectContent>
              </Select>
              <Select
                value={dataPoints.toString()}
                onValueChange={(val) => setDataPoints(Number(val))}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                {refreshing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {responseTimeData &&
          responseTimeData.data &&
          responseTimeData.data.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-4">
                  <Badge
                    variant="outline"
                    className="bg-primary/10 text-primary border-primary/20"
                  >
                    Total Requests:{" "}
                    {responseTimeData.data.reduce(
                      (sum, item) => sum + item.requests_count,
                      0
                    )}
                  </Badge>
                  <Badge variant="outline" className="bg-secondary">
                    Data Points: {responseTimeData.n}
                  </Badge>
                  <div className="flex items-center space-x-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        autoRefresh ? "bg-success animate-pulse" : "bg-muted"
                      }`}
                    ></div>
                    <span className="text-xs text-muted-foreground">
                      {autoRefresh
                        ? "Auto-refresh: 1 min"
                        : "Auto-refresh: Off"}
                    </span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className="h-6 px-2 text-xs"
                >
                  {autoRefresh ? "Turn Off" : "Turn On"} Auto-refresh
                </Button>
              </div>

              <div className="h-64">
                <ChartContainer
                  config={{
                    requests_count: {
                      label: "Request Count",
                      color: "hsl(var(--chart-2))",
                    },
                  }}
                  className="h-full w-full"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={responseTimeData.data.map((item) => ({
                        ...item,
                        formattedTime: new Date(
                          item.timestamp
                        ).toLocaleTimeString("en-US", {
                          hour: "2-digit",
                          minute: "2-digit",
                          ...(timeInterval === "daily"
                            ? {}
                            : {
                                month: "short",
                                day: "numeric",
                              }),
                        }),
                      }))}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        className="stroke-muted"
                      />
                      <XAxis
                        dataKey="formattedTime"
                        className="text-xs text-muted-foreground"
                        interval="preserveStartEnd"
                      />
                      <YAxis className="text-xs text-muted-foreground" />
                      <ChartTooltip
                        content={
                          <ChartTooltipContent
                            labelFormatter={(value, payload) => {
                              if (payload && payload[0]) {
                                return new Date(
                                  payload[0].payload.timestamp
                                ).toLocaleString();
                              }
                              return value;
                            }}
                            formatter={(value, name) => [value, "Requests"]}
                          />
                        }
                      />
                      <Line
                        type="monotone"
                        dataKey="requests_count"
                        stroke="hsl(var(--chart-2))"
                        strokeWidth={2}
                        dot={{
                          fill: "hsl(var(--chart-2))",
                          strokeWidth: 2,
                          r: 4,
                        }}
                        activeDot={{
                          r: 6,
                          stroke: "hsl(var(--chart-2))",
                          strokeWidth: 2,
                        }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              <div className="text-center space-y-2">
                <Activity className="w-8 h-8 mx-auto opacity-50" />
                <p>No request count data available</p>
                <Button variant="outline" size="sm" onClick={handleRefresh}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh Data
                </Button>
              </div>
            </div>
          )}{" "}
        </CardContent>
      </Card>
      {/* Database Management */}
      <DatabaseManagement /> {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5 text-primary" />
              <span>Quick Upload</span>
            </CardTitle>
            <CardDescription>
              Add new knowledge to your chatbot instantly
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              className="w-full justify-between h-auto p-4 bg-gradient-to-r from-primary/10 to-primary/5 hover:from-primary/20 hover:to-primary/10 border border-primary/20"
              variant="outline"
              onClick={() => navigate("/upload")}
            >
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-primary" />
                <div className="text-left">
                  <p className="text-sm font-medium">Upload Files</p>
                  <p className="text-xs text-muted-foreground">
                    PDF, DOCX, TXT
                  </p>
                </div>
              </div>
              <Upload className="w-4 h-4 text-primary" />
            </Button>

            <Button
              className="w-full justify-between h-auto p-4 bg-gradient-to-r from-blue-500/10 to-blue-500/5 hover:from-blue-500/20 hover:to-blue-500/10 border border-blue-500/20"
              variant="outline"
              onClick={() => navigate("/upload")}
            >
              <div className="flex items-center space-x-3">
                <BookOpen className="w-5 h-5 text-blue-500" />
                <div className="text-left">
                  <p className="text-sm font-medium">Add Text Content</p>
                  <p className="text-xs text-muted-foreground">Direct input</p>
                </div>
              </div>
              <MessageSquare className="w-4 h-4 text-blue-500" />
            </Button>
          </CardContent>
        </Card>{" "}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-accent" />
              <span>System Overview</span>
            </CardTitle>
            <CardDescription>
              System status and activity summary
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-success/10 to-success/5 rounded-lg border border-success/20">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-success">
                      System Active
                    </p>
                    <p className="text-xs text-muted-foreground">
                      All services operational
                    </p>
                  </div>
                </div>
                <Badge
                  variant="outline"
                  className="bg-success/10 text-success border-success/30"
                >
                  Online
                </Badge>
              </div>

              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg border border-primary/20">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Total Questions</p>{" "}
                    <p className="text-xs text-muted-foreground">
                      {(
                        getCurrentStats().total_user_questions +
                        getCurrentStats().total_admin_questions
                      ).toLocaleString()}{" "}
                      questions processed
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate("/questions")}
                  className="text-xs h-8 px-3"
                >
                  View All <Eye className="w-3 h-3 ml-1" />
                </Button>
              </div>

              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-500/10 to-blue-500/5 rounded-lg border border-blue-500/20">
                <div className="flex items-center space-x-3">
                  <Timer className="w-4 h-4 text-blue-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Auto-refresh Active</p>
                    <p className="text-xs text-muted-foreground">
                      Updates every minute
                    </p>
                  </div>
                </div>
                <Badge
                  variant="outline"
                  className="bg-blue-500/10 text-blue-500 border-blue-500/30"
                >
                  {autoRefresh ? "1 min" : "Off"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
