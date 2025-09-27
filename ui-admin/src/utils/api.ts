// API utility functions with proper error handling
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? window.location.origin 
  : '';

export interface ApiError {
  detail: string | Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
}

export class ApiClient {
  private getAuthHeaders() {
    const token = localStorage.getItem("adminToken");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private handleLogout() {
    // Clear all auth-related data from localStorage
    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminInfo");
    
    // Redirect to login page
    window.location.href = "/login";
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    console.log(
      `API Response: ${response.status} ${response.statusText} for ${response.url}`
    );

    if (!response.ok) {
      // Handle 401 Unauthorized errors
      if (response.status === 401) {
        console.log("401 Unauthorized - Logging out user");
        this.handleLogout();
        throw new Error("Session expired. Please login again.");
      }

      let errorDetail = "An error occurred";
      try {
        const errorData: ApiError = await response.json();
        if (typeof errorData.detail === "string") {
          errorDetail = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorDetail = errorData.detail.map((err) => err.msg).join(", ");
        }
      } catch {
        errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorDetail);
    }

    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return response.json();
    }
    return response.text() as unknown as T;
  }

  // Auth endpoints
  async login(email: string, password: string) {
    console.log("Attempting login to:", `${API_BASE_URL}/api/auth/login`);

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        body: formData,
      });

      return this.handleResponse<{ access_token: string; token_type: string }>(
        response
      );
    } catch (error) {
      console.error("Login request failed:", error);
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          "Cannot connect to server. Please ensure your backend is running on the correct URL."
        );
      }
      throw error;
    }
  }

  // Add logout method for manual logout
  async logout() {
    try {
      // Optional: Call backend logout endpoint if it exists
      // await fetch(`${API_BASE_URL}/api/auth/logout`, {
      //   method: "POST",
      //   headers: this.getAuthHeaders(),
      // });
    } catch (error) {
      console.error("Logout request failed:", error);
    } finally {
      // Always clear local data regardless of backend response
      this.handleLogout();
    }
  }

  async getAdminInfo() {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<{ id: string; name: string; email: string }>(
      response
    );
  }
  
  async signup(name: string, email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    return this.handleResponse(response);
  }

  // Query endpoints
  async sendQuery(query: string, userid: string) {
    const response = await fetch(`${API_BASE_URL}/api/user/query/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, userid }),
    });

    return this.handleResponse<{ response: string }>(response);
  }

  // Upload endpoints
  async uploadFiles(files: FileList, department: string, concurrentLimit = 3) {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch(
      `${API_BASE_URL}/api/admin/upload/files/batch/${department}?concurrent_limit=${concurrentLimit}`,
      {
        method: "POST",
        headers: this.getAuthHeaders(),
        body: formData,
      }
    );

    return this.handleResponse(response);
  }

  async uploadText(title: string, text: string, department: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/upload/text/${department}`,
      {
        method: "POST",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, text }),
      }
    );

    return this.handleResponse(response);
  }

  async getUploadedFiles() {
    const response = await fetch(`${API_BASE_URL}/api/admin/upload/list`, {
      headers: this.getAuthHeaders(),
    });

    const data = await this.handleResponse<{
      files: string[];
      total_files: number;
      requested_by: string;
    }>(response);

    // Transform the response to match the expected format
    return data.files.map((filename, index) => ({
      id: `${index + 1}`, // Generate a simple ID
      filename: filename,
      department: "Unknown", // Not provided in response
      upload_date: new Date().toISOString(), // Not provided in response
      file_size: undefined, // Not provided in response
    }));
  }

  async getTextKnowledge(dept?: string, adminid?: string) {
    const params = new URLSearchParams();
    if (dept) params.append("dept", dept);
    if (adminid) params.append("adminid", adminid);

    const response = await fetch(
      `${API_BASE_URL}/api/admin/upload/text?${params.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    const data = await this.handleResponse<{
      records: Array<{
        id: string;
        adminid: string;
        title: string;
        text: string;
        dept: string;
        createdat: string;
      }>;
      total: number;
      requested_by: string;
    }>(response);

    // Transform the response to match the expected format
    return data.records.map((record) => ({
      id: record.id,
      title: record.title,
      text: record.text,
      department: record.dept, // Map 'dept' to 'department'
      created_at: record.createdat, // Map 'createdat' to 'created_at'
    }));
  }

     async getUserQuestions(
    params: {
      status?: string;
      dept?: string;
      limit?: number;
      offset?: number;
    } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.append("status", params.status);
    if (params.dept) searchParams.append("dept", params.dept);
    if (params.limit) searchParams.append("limit", params.limit.toString());
    if (params.offset) searchParams.append("offset", params.offset.toString());
  
    const response = await fetch(
      `${API_BASE_URL}/api/admin/getuserquestions?${searchParams.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );
  
    const data = await this.handleResponse<{
      questions: Array<{
        id: string;
        query: string;
        answer: string | null;
        context: string | null;
        department: string;
        status: string;
        createdAt: string;
      }>;
      total: number;
      limit: number;
      offset: number;
      requested_by: string;
    }>(response);
  
    // Transform the response to match the expected format
    return data.questions.map(question => ({
      id: question.id,
      question: question.query, // Map 'query' to 'question'
      user_id: 'user', // Default value since not provided
      department: question.department,
      status: question.status,
      created_at: question.createdAt, // Map createdAt to created_at
      answer: question.answer,
      answered_at: question.answer ? question.createdAt : undefined,
    }));
  }
  
  async getAdminQuestions(
    params: {
      status?: string;
      dept?: string;
      limit?: number;
      offset?: number;
    } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.append("status", params.status);
    if (params.dept) searchParams.append("dept", params.dept);
    if (params.limit) searchParams.append("limit", params.limit.toString());
    if (params.offset) searchParams.append("offset", params.offset.toString());
  
    const response = await fetch(
      `${API_BASE_URL}/api/admin/getadminquestions?${searchParams.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );
  
    const data = await this.handleResponse<{
      questions: Array<{
        id: string;
        adminid: string | null;
        question: string;
        answer: string | null;
        department: string;
        status: string;
        frequency: number;
        vectordbid: string | null;
        createdAt: string;
      }>;
      total: number;
      limit: number;
      offset: number;
      requested_by: string;
    }>(response);
  
    // Transform the response to match the expected format
    return data.questions.map(question => ({
      id: question.id,
      question: question.question,
      admin_id: question.adminid || 'unknown', // Map adminid to admin_id
      department: question.department,
      status: question.status,
      created_at: question.createdAt, // Map createdAt to created_at
      answer: question.answer,
      answered_at: question.answer ? question.createdAt : undefined, // Estimate answered_at
    }));
  }

  async answerQuestion(questionId: string, answer: string) {
    const response = await fetch(`${API_BASE_URL}/api/admin/answer`, {
      method: "POST",
      headers: {
        ...this.getAuthHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question_id: questionId,
        answer: answer,
      }),
    });

    return this.handleResponse(response);
  }

  // Purge endpoints
  async purgeAllData(secretPassword: string, confirmation: string) {
    const response = await fetch(`${API_BASE_URL}/api/admin/purge/all`, {
      method: "POST",
      headers: {
        ...this.getAuthHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        secret_password: secretPassword,
        confirmation: confirmation,
      }),
    });

    return this.handleResponse(response);
  }

  async purgeVectorDbOnly(secretPassword: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/purge/vector-only`,
      {
        method: "POST",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          secret_password: secretPassword,
        }),
      }
    );

    return this.handleResponse(response);
  }

  async getPurgeStatus() {
    const response = await fetch(`${API_BASE_URL}/api/admin/purge/status`, {
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<{
      total_files: number;
      total_text_records: number;
      total_user_questions: number;
      total_admin_questions: number;
      vector_db_status: string;
    }>(response);
  }

  async summarizePendingQuestions() {
    const response = await fetch(`${API_BASE_URL}/api/admin/summarize`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }
}

export const apiClient = new ApiClient();