import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/utils/api';
import { Upload as UploadIcon, FileText, Loader2, File, Eye } from 'lucide-react';

interface UploadedFile {
  id: string;
  filename: string;
  department: string;
  upload_date: string;
  file_size?: number;
}

interface TextKnowledge {
  id: string;
  title: string;
  department: string;
  created_at: string;
  text: string;
}

const Upload = () => {
  const [department, setDepartment] = useState('');
  const [uploadType, setUploadType] = useState<'file' | 'text'>('file');
  const [files, setFiles] = useState<FileList | null>(null);
  const [textTitle, setTextTitle] = useState('');
  const [textContent, setTextContent] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [textKnowledge, setTextKnowledge] = useState<TextKnowledge[]>([]);
  const [viewMode, setViewMode] = useState<'file' | 'text'>('file');
  const [filterDepartment, setFilterDepartment] = useState('');
  const { toast } = useToast();

  const departments = ['HR', 'IT', 'Security'];

  useEffect(() => {
    fetchUploadedData();
  }, []);

  const fetchUploadedData = async () => {
    try {
      const [files, textData] = await Promise.all([
        apiClient.getUploadedFiles().catch(() => []),
        apiClient.getTextKnowledge().catch(() => []),
      ]);

      setUploadedFiles(Array.isArray(files) ? files : []);
      setTextKnowledge(Array.isArray(textData) ? textData : []);
    } catch (error) {
      console.error('Failed to fetch uploaded data:', error);
      setUploadedFiles([]);
      setTextKnowledge([]);
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
      setDepartment('');
      fetchUploadedData();
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload files. Please try again.",
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
      setTextTitle('');
      setTextContent('');
      setDepartment('');
      fetchUploadedData();
    } catch (error) {
      console.error('Text upload error:', error);
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload text. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const filteredFiles = uploadedFiles.filter(file => 
    !filterDepartment || filterDepartment === 'all' || file.department === filterDepartment
  );

  const filteredTexts = textKnowledge.filter(text => 
    !filterDepartment || filterDepartment === 'all' || text.department === filterDepartment
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Upload Management
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage your knowledge base by uploading files or adding text content
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <UploadIcon className="w-5 h-5 text-primary" />
              <span>Upload Content</span>
            </CardTitle>
            <CardDescription>
              Add new files or text to your knowledge base
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Department</Label>
              <Select value={department} onValueChange={setDepartment}>
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map(dept => (
                    <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Tabs value={uploadType} onValueChange={(value) => setUploadType(value as 'file' | 'text')}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="file">Upload Files</TabsTrigger>
                <TabsTrigger value="text">Add Text</TabsTrigger>
              </TabsList>

              <TabsContent value="file" className="space-y-4">
                <div className="space-y-2">
                  <Label>Select Files</Label>
                  <Input 
                    type="file" 
                    multiple 
                    onChange={(e) => setFiles(e.target.files)}
                    accept=".pdf,.doc,.docx,.txt,.md"
                  />
                  <p className="text-xs text-muted-foreground">
                    Supported formats: PDF, DOC, DOCX, TXT, MD
                  </p>
                </div>
                <Button 
                  onClick={handleFileUpload}
                  disabled={!files || !department || isUploading}
                  className="w-full gradient-primary"
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
              </TabsContent>

              <TabsContent value="text" className="space-y-4">
                <div className="space-y-2">
                  <Label>Title</Label>
                  <Input 
                    value={textTitle}
                    onChange={(e) => setTextTitle(e.target.value)}
                    placeholder="Enter content title"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Content</Label>
                  <Textarea 
                    value={textContent}
                    onChange={(e) => setTextContent(e.target.value)}
                    placeholder="Enter text content"
                    rows={8}
                  />
                </div>
                <Button 
                  onClick={handleTextUpload}
                  disabled={!textTitle || !textContent || !department || isUploading}
                  className="w-full gradient-accent"
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
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* View Section */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="w-5 h-5 text-accent" />
              <span>View Uploaded Content</span>
            </CardTitle>
            <CardDescription>
              Browse and manage your uploaded content
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex space-x-2">
              <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                <SelectTrigger className="flex-1">
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

            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'file' | 'text')}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="file">Files ({filteredFiles.length})</TabsTrigger>
                <TabsTrigger value="text">Text ({filteredTexts.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="file" className="space-y-2 max-h-96 overflow-y-auto">
                {filteredFiles.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <File className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No files uploaded yet</p>
                  </div>
                ) : (
                  filteredFiles.map((file) => (
                    <div key={file.id} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium text-sm">{file.filename}</p>
                        <p className="text-xs text-muted-foreground">
                          {file.department} • {new Date(file.upload_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="ghost" className="text-primary">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </TabsContent>

              <TabsContent value="text" className="space-y-2 max-h-96 overflow-y-auto">
                {filteredTexts.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No text content added yet</p>
                  </div>
                ) : (
                  filteredTexts.map((text) => (
                    <div key={text.id} className="p-3 bg-secondary rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{text.title}</p>
                          <p className="text-xs text-muted-foreground mb-2">
                            {text.department} • {new Date(text.created_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-muted-foreground line-clamp-2">
                            {text.text}
                          </p>
                        </div>
                        <Button size="sm" variant="ghost" className="text-accent">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Upload;