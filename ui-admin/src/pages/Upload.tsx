import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/utils/api";
import {
  Upload as UploadIcon,
  FileText,
  Loader2,
  File,
  Eye,
  Trash2,
  Edit,
  Download,
  Filter,
  Search,
  Calendar,
  User,
  FolderOpen,
  Plus,
  RefreshCw,
} from "lucide-react";

interface UploadedFile {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  department: string;
  uploaded_by: string;
  uploaded_by_name: string;
  created_at: string;
  processing_status: string;
  download_url: string;
}

interface TextKnowledge {
  id: string;
  title: string;
  text: string;
  department: string;
  uploaded_by: string;
  uploaded_by_name: string;
  created_at: string;
  updated_at: string;
  chunk_count: number;
}

const Upload = () => {
  /*
   * FILTERING STRATEGY:
   * - Server-side: Department filter, Admin filter (mine/all), Sort order (desc/asc)
   * - Client-side: Search functionality (filename, title, content, uploader names)
   * This hybrid approach optimizes API calls while providing responsive search
   */

  // Upload states
  const [department, setDepartment] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [textTitle, setTextTitle] = useState("");
  const [textContent, setTextContent] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  // Knowledge store states
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [textKnowledge, setTextKnowledge] = useState<TextKnowledge[]>([]);
  const [loading, setLoading] = useState(false);
  // Filter and search states
  const [fileFilter, setFileFilter] = useState<"all" | "mine">("all");
  const [textFilter, setTextFilter] = useState<"all" | "mine">("all");
  const [fileDeptFilter, setFileDeptFilter] = useState("all");
  const [textDeptFilter, setTextDeptFilter] = useState("all");
  const [fileSearch, setFileSearch] = useState("");
  const [textSearch, setTextSearch] = useState("");
  const [fileSortBy, setFileSortBy] = useState<boolean>(true); // true = latest first, false = oldest first
  const [textSortBy, setTextSortBy] = useState<boolean>(true); // true = latest first, false = oldest first

  // Preview and edit states
  const [previewText, setPreviewText] = useState<TextKnowledge | null>(null);
  const [editingText, setEditingText] = useState<TextKnowledge | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editDept, setEditDept] = useState("");
  const { toast } = useToast();
  const departments = ["HR", "IT", "Security"];

  // Get current user info for filtering
  const currentUser = JSON.parse(localStorage.getItem("adminInfo") || "{}");

  // Utility function to clean department filter values
  const cleanDeptFilter = (filter: string) => {
    if (!filter || filter === "all" || filter === "") {
      return undefined;
    }
    return filter;
  };

  useEffect(() => {
    fetchUploadedData();
  }, []);
  // Refetch data when filters or sort order changes
  useEffect(() => {
    fetchUploadedData();
  }, [
    fileSortBy,
    textSortBy,
    fileFilter,
    textFilter,
    fileDeptFilter,
    textDeptFilter,
  ]);
  const fetchUploadedData = async () => {
    setLoading(true);
    try {
      // Debug logging
      console.log("Fetching uploaded data with filters:", {
        fileDeptFilter,
        textDeptFilter,
        fileFilter,
        textFilter,
      });
      const filesParams = {
        limit: 1000,
        sort_by: fileSortBy ? "desc" : "asc",
        admin: fileFilter === "mine" ? "self" : undefined,
        dept: cleanDeptFilter(fileDeptFilter),
      };

      const textParams = {
        limit: 1000,
        sort_by: textSortBy,
        adminid: textFilter === "mine" ? "self" : undefined,
        dept: cleanDeptFilter(textDeptFilter),
      };

      console.log("Files API params:", filesParams);
      console.log("Text API params:", textParams);
      let filesResponse, textResponse;

      try {
        filesResponse = await apiClient.getUploadedFiles(filesParams);
        console.log("Files API response:", filesResponse);
      } catch (error) {
        console.error("Files API error:", error);
        filesResponse = { records: [] };
      }

      try {
        textResponse = await apiClient.getTextKnowledge(textParams);
        console.log("Text API response:", textResponse);
      } catch (error) {
        console.error("Text API error:", error);
        textResponse = { records: [] };
      } // Map the API response to match the component interface
      const mappedFiles = (filesResponse?.records || []).map((record) => ({
        id: record.id || "",
        filename: record.file_name || "Unknown File",
        original_filename: record.file_name || "Unknown File",
        file_size: 0, // Not provided in API response
        file_type: "", // Not provided in API response
        department: record.dept || "Unknown",
        uploaded_by: record.adminid || "",
        uploaded_by_name: record.admin_name || "Unknown User",
        created_at: record.createdat || new Date().toISOString(),
        processing_status: "success", // Assume success if not provided
        download_url: record.file_url || "",
      }));
      const mappedTexts = (textResponse?.records || []).map((record) => ({
        id: record.id || "",
        title: record.title || "Untitled",
        text: record.text || "",
        department: record.dept || "Unknown",
        uploaded_by: record.adminid || "",
        uploaded_by_name: record.admin_name || "Unknown User",
        created_at: record.createdat || new Date().toISOString(),
        updated_at: record.createdat || new Date().toISOString(), // Use createdat as fallback
        chunk_count: 0, // Not provided in API response
      }));
      setUploadedFiles(mappedFiles);
      setTextKnowledge(mappedTexts);
      console.log("Data fetched successfully");
    } catch (error) {
      console.error("Failed to fetch uploaded data:", error);

      // Reset to empty arrays on error to prevent UI issues
      setUploadedFiles([]);
      setTextKnowledge([]);

      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to load uploaded content",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };
  const handleFileUpload = async () => {
    if (!files || !department) {
      toast({
        title: "Missing information",
        description: "Please select department and files",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    try {
      await apiClient.uploadFiles(files, department);
      toast({
        title: "Upload successful",
        description: `${files.length} file(s) uploaded successfully`,
      });
      setFiles(null);
      setDepartment("");
      const fileInput = document.querySelector(
        'input[type="file"]'
      ) as HTMLInputElement;
      if (fileInput) fileInput.value = "";
      fetchUploadedData();
    } catch (error) {
      console.error("Upload error:", error);
      toast({
        title: "Upload failed",
        description:
          error instanceof Error
            ? error.message
            : "Failed to upload files. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleTextUpload = async () => {
    if (!textTitle || !textContent || !department) {
      toast({
        title: "Missing information",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    try {
      await apiClient.uploadText(textTitle, textContent, department);
      toast({
        title: "Text uploaded",
        description: "Text content added successfully",
      });
      setTextTitle("");
      setTextContent("");
      setDepartment("");
      fetchUploadedData();
    } catch (error) {
      console.error("Text upload error:", error);
      toast({
        title: "Upload failed",
        description:
          error instanceof Error
            ? error.message
            : "Failed to upload text. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteFile = async (fileId: string, filename: string) => {
    try {
      await apiClient.deleteFile(fileId);
      toast({
        title: "File deleted",
        description: `${filename} has been deleted successfully`,
      });
      fetchUploadedData();
    } catch (error) {
      console.error("Delete file error:", error);
      toast({
        title: "Delete failed",
        description:
          error instanceof Error ? error.message : "Failed to delete file",
        variant: "destructive",
      });
    }
  };

  const handleDeleteText = async (textId: string, title: string) => {
    try {
      await apiClient.deleteTextKnowledge(textId);
      toast({
        title: "Text deleted",
        description: `${title} has been deleted successfully`,
      });
      fetchUploadedData();
    } catch (error) {
      console.error("Delete text error:", error);
      toast({
        title: "Delete failed",
        description:
          error instanceof Error ? error.message : "Failed to delete text",
        variant: "destructive",
      });
    }
  };

  const openEditDialog = (text: TextKnowledge) => {
    setEditingText(text);
    setEditTitle(text.title);
    setEditContent(text.text);
    setEditDept(text.department);
  };

  const handleUpdateText = async () => {
    if (!editingText || !editTitle || !editContent || !editDept) {
      toast({
        title: "Missing information",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    try {
      await apiClient.updateTextKnowledge(editingText.id, {
        title: editTitle,
        text: editContent,
        dept: editDept,
      });
      toast({
        title: "Text updated",
        description: "Text content has been updated successfully",
      });
      setEditingText(null);
      fetchUploadedData();
    } catch (error) {
      console.error("Update text error:", error);
      toast({
        title: "Update failed",
        description:
          error instanceof Error ? error.message : "Failed to update text",
        variant: "destructive",
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Client-side filtering for search functionality
  // Note: Department, admin, and sort filters are handled server-side via API calls
  const filteredAndSortedFiles = uploadedFiles.filter((file) => {
    // Search filter (client-side only - searches filename and uploader name)
    if (fileSearch) {
      const searchLower = fileSearch.toLowerCase();
      const filenameMatch = file.original_filename
        .toLowerCase()
        .includes(searchLower);
      const uploaderMatch = file.uploaded_by_name
        .toLowerCase()
        .includes(searchLower);
      if (!filenameMatch && !uploaderMatch) return false;
    }

    return true;
  });

  const filteredAndSortedTexts = textKnowledge.filter((text) => {
    // Search filter (client-side only - searches title, content, and uploader name)
    if (textSearch) {
      const searchLower = textSearch.toLowerCase();
      const titleMatch = text.title.toLowerCase().includes(searchLower);
      const contentMatch = text.text.toLowerCase().includes(searchLower);
      const uploaderMatch = text.uploaded_by_name
        .toLowerCase()
        .includes(searchLower);
      if (!titleMatch && !contentMatch && !uploaderMatch) return false;
    }

    return true;
  });
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Upload Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage your knowledge base by uploading files or adding text content
          </p>
        </div>{" "}
        <Button
          onClick={fetchUploadedData}
          variant="outline"
          size="sm"
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Loading...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </>
          )}
        </Button>
      </div>

      {/* File Upload Section */}
      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <UploadIcon className="w-5 h-5 text-primary" />
            <span>File Upload</span>
          </CardTitle>
          <CardDescription>
            Upload documents and files to your knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Department</Label>
              <Select value={department} onValueChange={setDepartment}>
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
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
              <Label>Select Files</Label>
              <Input
                type="file"
                multiple
                onChange={(e) => setFiles(e.target.files)}
                accept=".pdf,.doc,.docx,.txt,.md"
              />
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Supported formats: PDF, DOC, DOCX, TXT, MD
          </p>
          <Button
            onClick={handleFileUpload}
            disabled={!files || !department || isUploading}
            className="w-full md:w-auto gradient-primary"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <UploadIcon className="mr-2 h-4 w-4" />
                Upload Files
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Text Upload Section */}
      <Card className="card-hover" id="text-upload">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="w-5 h-5 text-accent" />
            <span>Add Text Content</span>
          </CardTitle>
          <CardDescription>
            Add text-based knowledge directly to your knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Department</Label>
              <Select value={department} onValueChange={setDepartment}>
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
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
              <Label>Title</Label>
              <Input
                value={textTitle}
                onChange={(e) => setTextTitle(e.target.value)}
                placeholder="Enter content title"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Content</Label>
            <Textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="Enter text content"
              rows={6}
            />
          </div>
          <Button
            onClick={handleTextUpload}
            disabled={!textTitle || !textContent || !department || isUploading}
            className="w-full md:w-auto gradient-accent"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Adding...
              </>
            ) : (
              <>
                <FileText className="mr-2 h-4 w-4" />
                Add Text Content
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Knowledge Store Section */}
      <Card className="card-hover" id="knowledge-store">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FolderOpen className="w-5 h-5 text-green-600" />
            <span>Knowledge Store</span>
          </CardTitle>
          <CardDescription>
            Browse and manage your uploaded files and text content
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="files" className="space-y-4">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="files">
                Files ({filteredAndSortedFiles.length})
              </TabsTrigger>
              <TabsTrigger value="texts">
                Text Content ({filteredAndSortedTexts.length})
              </TabsTrigger>
            </TabsList>

            {/* Files Tab */}
            <TabsContent value="files" className="space-y-4">
              {/* File Filters */}
              <div className="flex flex-wrap gap-4">
                <Select
                  value={fileFilter}
                  onValueChange={(value) =>
                    setFileFilter(value as "all" | "mine")
                  }
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Files</SelectItem>
                    <SelectItem value="mine">Uploaded by me</SelectItem>
                  </SelectContent>
                </Select>

                <Select
                  value={fileDeptFilter}
                  onValueChange={setFileDeptFilter}
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
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
                <Select
                  value={fileSortBy.toString()}
                  onValueChange={(value) => setFileSortBy(value === "true")}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Latest First</SelectItem>
                    <SelectItem value="false">Oldest First</SelectItem>
                  </SelectContent>
                </Select>

                <div className="relative flex-1 min-w-48">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search files..."
                    value={fileSearch}
                    onChange={(e) => setFileSearch(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>

              {/* Files List */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="text-center py-8">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                    <p className="text-muted-foreground">Loading files...</p>
                  </div>
                ) : filteredAndSortedFiles.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <File className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No files found</p>
                  </div>
                ) : (
                  filteredAndSortedFiles.map((file) => (
                    <div
                      key={file.id}
                      className="flex items-center justify-between p-4 bg-secondary rounded-lg hover:bg-secondary/80 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <File className="w-4 h-4 text-primary flex-shrink-0" />
                          <p className="font-medium text-sm truncate">
                            {file.original_filename}
                          </p>
                          <span
                            className={`px-2 py-1 text-xs rounded-full ${
                              file.processing_status === "success"
                                ? "bg-green-100 text-green-800"
                                : file.processing_status === "processing"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-red-100 text-red-800"
                            }`}
                          >
                            {file.processing_status}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
                          <span className="flex items-center space-x-1">
                            <FolderOpen className="w-3 h-3" />
                            <span>{file.department}</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>{file.uploaded_by_name}</span>
                          </span>{" "}
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDate(file.created_at)}</span>
                          </span>
                        </div>
                      </div>
                      <div className="flex space-x-2 flex-shrink-0">
                        {file.download_url && (
                          <Button size="sm" variant="ghost" asChild>
                            <a
                              href={file.download_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <Download className="w-4 h-4" />
                            </a>
                          </Button>
                        )}
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete File</AlertDialogTitle>
                              <AlertDialogDescription>
                                Are you sure you want to delete "
                                {file.original_filename}"? This action cannot be
                                undone.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() =>
                                  handleDeleteFile(
                                    file.id,
                                    file.original_filename
                                  )
                                }
                                className="bg-red-600 hover:bg-red-700"
                              >
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Text Content Tab */}
            <TabsContent value="texts" className="space-y-4">
              {/* Text Filters */}
              <div className="flex flex-wrap gap-4">
                <Select
                  value={textFilter}
                  onValueChange={(value) =>
                    setTextFilter(value as "all" | "mine")
                  }
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Text</SelectItem>
                    <SelectItem value="mine">Created by me</SelectItem>
                  </SelectContent>
                </Select>

                <Select
                  value={textDeptFilter}
                  onValueChange={setTextDeptFilter}
                >
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="All Departments" />
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
                <Select
                  value={textSortBy.toString()}
                  onValueChange={(value) => setTextSortBy(value === "true")}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Latest First</SelectItem>
                    <SelectItem value="false">Oldest First</SelectItem>
                  </SelectContent>
                </Select>

                <div className="relative flex-1 min-w-48">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search text content..."
                    value={textSearch}
                    onChange={(e) => setTextSearch(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>

              {/* Text Content List */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="text-center py-8">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                    <p className="text-muted-foreground">
                      Loading text content...
                    </p>
                  </div>
                ) : filteredAndSortedTexts.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No text content found</p>
                  </div>
                ) : (
                  filteredAndSortedTexts.map((text) => (
                    <div
                      key={text.id}
                      className="p-4 bg-secondary rounded-lg hover:bg-secondary/80 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <Dialog>
                            <DialogTrigger asChild>
                              <button
                                className="font-medium text-sm text-left hover:text-primary transition-colors cursor-pointer truncate block"
                                onClick={() => setPreviewText(text)}
                              >
                                {text.title}
                              </button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                              <DialogHeader>
                                <DialogTitle>{text.title}</DialogTitle>
                                <DialogDescription>
                                  {text.department} • Created by{" "}
                                  {text.uploaded_by_name} •{" "}
                                  {formatDate(text.created_at)}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="mt-4">
                                <div className="whitespace-pre-wrap text-sm">
                                  {text.text}
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>

                          <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
                            <span className="flex items-center space-x-1">
                              <FolderOpen className="w-3 h-3" />
                              <span>{text.department}</span>
                            </span>
                            <span className="flex items-center space-x-1">
                              <User className="w-3 h-3" />
                              <span>{text.uploaded_by_name}</span>
                            </span>{" "}
                            <span className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>{formatDate(text.created_at)}</span>
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                            {text.text}
                          </p>
                        </div>
                        <div className="flex space-x-2 flex-shrink-0">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => openEditDialog(text)}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl">
                              <DialogHeader>
                                <DialogTitle>Edit Text Content</DialogTitle>
                                <DialogDescription>
                                  Update the text content details
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4 mt-4">
                                <div className="space-y-2">
                                  <Label>Title</Label>
                                  <Input
                                    value={editTitle}
                                    onChange={(e) =>
                                      setEditTitle(e.target.value)
                                    }
                                    placeholder="Enter title"
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label>Department</Label>
                                  <Select
                                    value={editDept}
                                    onValueChange={setEditDept}
                                  >
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
                                  <Label>Content</Label>
                                  <Textarea
                                    value={editContent}
                                    onChange={(e) =>
                                      setEditContent(e.target.value)
                                    }
                                    rows={10}
                                    placeholder="Enter content"
                                  />
                                </div>
                                <div className="flex justify-end space-x-2">
                                  <Button
                                    variant="outline"
                                    onClick={() => setEditingText(null)}
                                  >
                                    Cancel
                                  </Button>
                                  <Button
                                    onClick={handleUpdateText}
                                    className="gradient-accent"
                                  >
                                    Update
                                  </Button>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>

                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>
                                  Delete Text Content
                                </AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to delete "{text.title}
                                  "? This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() =>
                                    handleDeleteText(text.id, text.title)
                                  }
                                  className="bg-red-600 hover:bg-red-700"
                                >
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default Upload;
