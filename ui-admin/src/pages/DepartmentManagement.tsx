import React, { useState, useEffect } from "react";
import { apiClient } from "@/utils/api";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Plus,
  Edit,
  Trash2,
  Search,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Filter,
  Eye,
  MessageSquare,
  Building,
  Tags,
  TestTube,
} from "lucide-react";

interface Keyword {
  id: string;
  keyword: string;
}

interface DepartmentDescription {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

interface DepartmentFailure {
  id: string;
  query: string;
  adminid?: string;
  admin_name?: string;
  comments?: string;
  detected: string;
  expected: string;
  status: string;
  created_at: string;
}

const DepartmentManagement = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("metadata");
  // Department Metadata State
  const [keywords, setKeywords] = useState<Record<string, Keyword[]>>({});
  const [descriptions, setDescriptions] = useState<DepartmentDescription[]>([]);
  const [selectedDept, setSelectedDept] = useState<string>("HR");
  const [newKeywords, setNewKeywords] = useState<string>("");
  const [editingKeyword, setEditingKeyword] = useState<{
    id: string;
    value: string;
  } | null>(null);
  const [editingDescription, setEditingDescription] = useState<{
    dept: string;
    value: string;
  } | null>(null);

  // Department Detection Test State
  const [testQuery, setTestQuery] = useState("");
  const [testResult, setTestResult] = useState<{
    department: string;
    requested_by: string;
  } | null>(null);
  const [testLoading, setTestLoading] = useState(false);

  // Department Failures State
  const [failures, setFailures] = useState<DepartmentFailure[]>([]);
  const [failuresLoading, setFailuresLoading] = useState(false);
  const [failuresFilters, setFailuresFilters] = useState({
    status: "all",
    dept: "all",
  });
  const [selectedFailure, setSelectedFailure] =
    useState<DepartmentFailure | null>(null);
  const [failureAction, setFailureAction] = useState<{
    type: "close" | "discard";
    comments: string;
  } | null>(null);

  const departments = ["HR", "IT", "Security", "General Inquiry"];

  useEffect(() => {
    fetchDepartmentMetadata();
    fetchDepartmentFailures();
  }, []);

  useEffect(() => {
    if (activeTab === "failures") {
      fetchDepartmentFailures();
    }
  }, [activeTab, failuresFilters]);
  const fetchDepartmentMetadata = async () => {
    setLoading(true);
    try {
      const [keywordsData, descriptionsData] = await Promise.all([
        apiClient.getDepartmentKeywords(),
        apiClient.getDepartmentDescriptions(),
      ]);
      setKeywords(keywordsData);
      setDescriptions(descriptionsData.departments);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch department metadata",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartmentFailures = async () => {
    setFailuresLoading(true);
    try {
      const response = await apiClient.getDepartmentFailures({
        status:
          failuresFilters.status !== "all" ? failuresFilters.status : undefined,
        dept: failuresFilters.dept !== "all" ? failuresFilters.dept : undefined,
        limit: 100,
        sort_by: true,
      });
      setFailures(response.failures);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch department failures",
        variant: "destructive",
      });
    } finally {
      setFailuresLoading(false);
    }
  };

  const handleAddKeywords = async () => {
    if (!newKeywords.trim()) return;

    const keywordList = newKeywords
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k);
    if (keywordList.length === 0) return;

    try {
      await apiClient.addDepartmentKeywords(selectedDept, keywordList);
      toast({
        title: "Success",
        description: `Added ${keywordList.length} keyword(s) to ${selectedDept}`,
      });
      setNewKeywords("");
      fetchDepartmentMetadata();
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to add keywords",
        variant: "destructive",
      });
    }
  };

  const handleUpdateKeyword = async () => {
    if (!editingKeyword) return;

    try {
      await apiClient.updateDepartmentKeyword(
        editingKeyword.id,
        editingKeyword.value
      );
      toast({
        title: "Success",
        description: "Keyword updated successfully",
      });
      setEditingKeyword(null);
      fetchDepartmentMetadata();
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to update keyword",
        variant: "destructive",
      });
    }
  };

  const handleDeleteKeyword = async (keywordId: string) => {
    try {
      await apiClient.deleteDepartmentKeyword(keywordId);
      toast({
        title: "Success",
        description: "Keyword deleted successfully",
      });
      fetchDepartmentMetadata();
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete keyword",
        variant: "destructive",
      });
    }
  };

  const handleUpdateDescription = async () => {
    if (!editingDescription) return;

    try {
      await apiClient.updateDepartmentDescription(
        editingDescription.dept,
        editingDescription.value
      );
      toast({
        title: "Success",
        description: "Description updated successfully",
      });
      setEditingDescription(null);
      fetchDepartmentMetadata();
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to update description",
        variant: "destructive",
      });
    }
  };

  const handleTestDepartmentDetection = async () => {
    if (!testQuery.trim()) return;

    setTestLoading(true);
    try {
      const result = await apiClient.testDepartmentDetection(testQuery);
      setTestResult(result);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to test department detection",
        variant: "destructive",
      });
    } finally {
      setTestLoading(false);
    }
  };

  const handleFailureAction = async () => {
    if (!selectedFailure || !failureAction) return;

    try {
      if (failureAction.type === "close") {
        await apiClient.closeDepartmentFailure(
          selectedFailure.id,
          failureAction.comments
        );
        toast({
          title: "Success",
          description: "Department failure closed successfully",
        });
      } else {
        await apiClient.discardDepartmentFailure(
          selectedFailure.id,
          failureAction.comments
        );
        toast({
          title: "Success",
          description: "Department failure discarded successfully",
        });
      }
      setSelectedFailure(null);
      setFailureAction(null);
      fetchDepartmentFailures();
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to process failure",
        variant: "destructive",
      });
    }
  };

  const refreshRouterData = async () => {
    try {
      setLoading(true);
      await apiClient.refreshRouterData();
      toast({
        title: "Success",
        description: "Router data refreshed successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to refresh router data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Pending
          </Badge>
        );
      case "processed":
        return (
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Processed
          </Badge>
        );
      case "discarded":
        return (
          <Badge variant="secondary" className="bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Discarded
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Department Management
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage department metadata, keywords, and routing failures
          </p>
        </div>
        <Button
          onClick={refreshRouterData}
          disabled={loading}
          className="gradient-primary text-white"
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`}
          />
          Refresh Router Data
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="metadata" className="flex items-center gap-2">
            <Building className="w-4 h-4" />
            Metadata Management
          </TabsTrigger>
          <TabsTrigger value="detection" className="flex items-center gap-2">
            <TestTube className="w-4 h-4" />
            Detection Testing
          </TabsTrigger>
          <TabsTrigger value="failures" className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Department Failures
          </TabsTrigger>
        </TabsList>

        <TabsContent value="metadata" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Keywords Management */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Tags className="w-5 h-5" />
                  Department Keywords
                </CardTitle>
                <CardDescription>
                  Manage keywords for department routing
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="dept-select">Select Department</Label>
                  <Select value={selectedDept} onValueChange={setSelectedDept}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((dept) => (
                        <SelectItem key={dept} value={dept}>
                          {dept}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new-keywords">
                    Add Keywords (comma-separated)
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="new-keywords"
                      value={newKeywords}
                      onChange={(e) => setNewKeywords(e.target.value)}
                      placeholder="e.g., server, database, IT support"
                      onKeyPress={(e) =>
                        e.key === "Enter" && handleAddKeywords()
                      }
                    />
                    <Button
                      onClick={handleAddKeywords}
                      disabled={!newKeywords.trim()}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Current Keywords for {selectedDept}</Label>
                  <div className="min-h-[200px] max-h-[300px] overflow-y-auto border rounded-md p-3">
                    {loading ? (
                      <div className="flex items-center justify-center py-8">
                        <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                        Loading...
                      </div>
                    ) : keywords[selectedDept]?.length > 0 ? (
                      <div className="space-y-2">
                        {keywords[selectedDept].map((keyword) => (
                          <div
                            key={keyword.id}
                            className="flex items-center justify-between p-2 border rounded"
                          >
                            {editingKeyword?.id === keyword.id ? (
                              <div className="flex items-center gap-2 flex-1">
                                <Input
                                  value={editingKeyword.value}
                                  onChange={(e) =>
                                    setEditingKeyword({
                                      ...editingKeyword,
                                      value: e.target.value,
                                    })
                                  }
                                  className="flex-1"
                                  onKeyPress={(e) =>
                                    e.key === "Enter" && handleUpdateKeyword()
                                  }
                                />
                                <Button size="sm" onClick={handleUpdateKeyword}>
                                  <CheckCircle className="w-3 h-3" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setEditingKeyword(null)}
                                >
                                  <XCircle className="w-3 h-3" />
                                </Button>
                              </div>
                            ) : (
                              <>
                                <span className="flex-1">
                                  {keyword.keyword}
                                </span>
                                <div className="flex gap-1">
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() =>
                                      setEditingKeyword({
                                        id: keyword.id,
                                        value: keyword.keyword,
                                      })
                                    }
                                  >
                                    <Edit className="w-3 h-3" />
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() =>
                                      handleDeleteKeyword(keyword.id)
                                    }
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </Button>
                                </div>
                              </>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center text-muted-foreground py-8">
                        No keywords found for {selectedDept}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Descriptions Management */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  Department Descriptions
                </CardTitle>
                <CardDescription>
                  Manage department descriptions and metadata
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                    Loading...
                  </div>
                ) : (
                  <div className="space-y-4">
                    {departments.map((deptName) => {
                      const dept = descriptions.find(
                        (d) => d.name === deptName
                      );
                      return (
                        <Card key={deptName} className="border-2">
                          <CardHeader className="pb-3">
                            <div className="flex items-center justify-between">
                              <CardTitle className="text-lg">
                                {deptName}
                              </CardTitle>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  setEditingDescription({
                                    dept: deptName,
                                    value: dept?.description || "",
                                  })
                                }
                              >
                                <Edit className="w-3 h-3 mr-1" />
                                Edit
                              </Button>
                            </div>
                          </CardHeader>
                          <CardContent>
                            {editingDescription?.dept === deptName ? (
                              <div className="space-y-3">
                                <Textarea
                                  value={editingDescription.value}
                                  onChange={(e) =>
                                    setEditingDescription({
                                      ...editingDescription,
                                      value: e.target.value,
                                    })
                                  }
                                  placeholder="Enter department description..."
                                  rows={3}
                                />
                                <div className="flex gap-2">
                                  <Button
                                    size="sm"
                                    onClick={handleUpdateDescription}
                                  >
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    Save
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() => setEditingDescription(null)}
                                  >
                                    <XCircle className="w-3 h-3 mr-1" />
                                    Cancel
                                  </Button>
                                </div>
                              </div>
                            ) : (
                              <div>
                                <p className="text-sm text-muted-foreground">
                                  {dept?.description ||
                                    "No description available"}
                                </p>
                                {dept?.created_at && (
                                  <p className="text-xs text-muted-foreground mt-2">
                                    Created:{" "}
                                    {new Date(
                                      dept.created_at
                                    ).toLocaleDateString()}
                                  </p>
                                )}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="detection" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="w-5 h-5" />
                Department Detection Playground
              </CardTitle>
              <CardDescription>
                Test department detection with custom queries
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="test-query">Test Query</Label>
                <div className="flex gap-2">
                  <Input
                    id="test-query"
                    value={testQuery}
                    onChange={(e) => setTestQuery(e.target.value)}
                    placeholder="Enter a query to test department detection..."
                    onKeyPress={(e) =>
                      e.key === "Enter" && handleTestDepartmentDetection()
                    }
                  />
                  <Button
                    onClick={handleTestDepartmentDetection}
                    disabled={!testQuery.trim() || testLoading}
                  >
                    {testLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>

              {testResult && (
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription className="flex items-center justify-between">
                    <div>
                      <strong>Detected Department:</strong>{" "}
                      {testResult.department}
                    </div>
                    <Badge variant="secondary">{testResult.department}</Badge>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="failures" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Department Routing Failures
              </CardTitle>
              <CardDescription>
                Review and process department routing failures
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4" />
                  <Label>Status:</Label>
                  <Select
                    value={failuresFilters.status}
                    onValueChange={(value) =>
                      setFailuresFilters({ ...failuresFilters, status: value })
                    }
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="processed">Processed</SelectItem>
                      <SelectItem value="discarded">Discarded</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <Label>Department:</Label>
                  <Select
                    value={failuresFilters.dept}
                    onValueChange={(value) =>
                      setFailuresFilters({ ...failuresFilters, dept: value })
                    }
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      {departments.map((dept) => (
                        <SelectItem key={dept} value={dept}>
                          {dept}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator className="my-4" />

              {/* Failures Table */}
              <div className="rounded-md border">
                <Table>
                  {" "}
                  <TableHeader>
                    <TableRow>
                      <TableHead>Query</TableHead>
                      <TableHead>Admin Info</TableHead>
                      <TableHead>Detected</TableHead>
                      <TableHead>Expected</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {failuresLoading ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8">
                          <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-2" />
                          Loading failures...
                        </TableCell>
                      </TableRow>
                    ) : failures.length === 0 ? (
                      <TableRow>
                        <TableCell
                          colSpan={7}
                          className="text-center py-8 text-muted-foreground"
                        >
                          No department failures found
                        </TableCell>
                      </TableRow>
                    ) : (
                      failures.map((failure) => (
                        <TableRow key={failure.id}>
                          <TableCell className="max-w-xs">
                            <div className="truncate" title={failure.query}>
                              {failure.query}
                            </div>
                          </TableCell>{" "}
                          <TableCell className="max-w-xs">
                            <div className="truncate">
                              {failure.admin_name || failure.adminid || "N/A"}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{failure.detected}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">
                              {failure.expected}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(failure.status)}
                          </TableCell>
                          <TableCell className="text-sm">
                            {new Date(failure.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() => setSelectedFailure(failure)}
                                  >
                                    <Eye className="w-3 h-3" />
                                  </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-2xl">
                                  <DialogHeader>
                                    <DialogTitle>
                                      Department Failure Details
                                    </DialogTitle>
                                    <DialogDescription>
                                      Review and process this department routing
                                      failure
                                    </DialogDescription>
                                  </DialogHeader>
                                  <div className="space-y-4">
                                    <div>
                                      <Label className="text-sm font-medium">
                                        Query
                                      </Label>
                                      <p className="text-sm bg-muted p-2 rounded">
                                        {failure.query}
                                      </p>
                                    </div>{" "}
                                    <div>
                                      <Label className="text-sm font-medium">
                                        Admin Info
                                      </Label>
                                      <p className="text-sm bg-muted p-2 rounded">
                                        {failure.admin_name ||
                                          failure.adminid ||
                                          "N/A"}
                                      </p>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                      <div>
                                        <Label className="text-sm font-medium">
                                          Detected Department
                                        </Label>{" "}
                                        <Badge
                                          variant="outline"
                                          className="mt-1"
                                        >
                                          {failure.detected}
                                        </Badge>
                                      </div>
                                      <div>
                                        <Label className="text-sm font-medium">
                                          Expected Department
                                        </Label>{" "}
                                        <Badge
                                          variant="secondary"
                                          className="mt-1"
                                        >
                                          {failure.expected}
                                        </Badge>
                                      </div>
                                    </div>
                                    <div>
                                      <Label className="text-sm font-medium">
                                        Status
                                      </Label>
                                      <div className="mt-1">
                                        {getStatusBadge(failure.status)}
                                      </div>
                                    </div>
                                    {failure.comments && (
                                      <div>
                                        <Label className="text-sm font-medium">
                                          Comments
                                        </Label>
                                        <p className="text-sm bg-muted p-2 rounded">
                                          {failure.comments}
                                        </p>
                                      </div>
                                    )}
                                  </div>
                                  {failure.status === "pending" && (
                                    <DialogFooter className="gap-2">
                                      <Dialog>
                                        <DialogTrigger asChild>
                                          <Button
                                            variant="outline"
                                            onClick={() =>
                                              setFailureAction({
                                                type: "discard",
                                                comments: "",
                                              })
                                            }
                                          >
                                            <XCircle className="w-4 h-4 mr-2" />
                                            Discard
                                          </Button>
                                        </DialogTrigger>
                                        <DialogContent>
                                          <DialogHeader>
                                            <DialogTitle>
                                              Discard Failure
                                            </DialogTitle>
                                            <DialogDescription>
                                              Add optional comments for
                                              discarding this failure
                                            </DialogDescription>
                                          </DialogHeader>
                                          <div className="space-y-4">
                                            <Textarea
                                              value={
                                                failureAction?.comments || ""
                                              }
                                              onChange={(e) =>
                                                setFailureAction(
                                                  failureAction
                                                    ? {
                                                        ...failureAction,
                                                        comments:
                                                          e.target.value,
                                                      }
                                                    : null
                                                )
                                              }
                                              placeholder="Optional comments..."
                                            />
                                          </div>
                                          <DialogFooter>
                                            <Button
                                              variant="outline"
                                              onClick={() =>
                                                setFailureAction(null)
                                              }
                                            >
                                              Cancel
                                            </Button>
                                            <Button
                                              onClick={handleFailureAction}
                                            >
                                              Discard
                                            </Button>
                                          </DialogFooter>
                                        </DialogContent>
                                      </Dialog>
                                      <Dialog>
                                        <DialogTrigger asChild>
                                          <Button
                                            onClick={() =>
                                              setFailureAction({
                                                type: "close",
                                                comments: "",
                                              })
                                            }
                                          >
                                            <CheckCircle className="w-4 h-4 mr-2" />
                                            Process
                                          </Button>
                                        </DialogTrigger>
                                        <DialogContent>
                                          <DialogHeader>
                                            <DialogTitle>
                                              Process Failure
                                            </DialogTitle>
                                            <DialogDescription>
                                              Add optional comments for
                                              processing this failure
                                            </DialogDescription>
                                          </DialogHeader>
                                          <div className="space-y-4">
                                            <Textarea
                                              value={
                                                failureAction?.comments || ""
                                              }
                                              onChange={(e) =>
                                                setFailureAction(
                                                  failureAction
                                                    ? {
                                                        ...failureAction,
                                                        comments:
                                                          e.target.value,
                                                      }
                                                    : null
                                                )
                                              }
                                              placeholder="Optional comments..."
                                            />
                                          </div>
                                          <DialogFooter>
                                            <Button
                                              variant="outline"
                                              onClick={() =>
                                                setFailureAction(null)
                                              }
                                            >
                                              Cancel
                                            </Button>
                                            <Button
                                              onClick={handleFailureAction}
                                            >
                                              Process
                                            </Button>
                                          </DialogFooter>
                                        </DialogContent>
                                      </Dialog>
                                    </DialogFooter>
                                  )}
                                </DialogContent>
                              </Dialog>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DepartmentManagement;
