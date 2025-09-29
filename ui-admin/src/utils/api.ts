// API utility functions with proper error handling
export const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? window.location.origin
    : "http://localhost:8000";

export interface ApiError {
  detail:
    | string
    | Array<{
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
    return this.handleResponse<{
      id: string;
      name: string;
      email: string;
      role: string;
    }>(response);
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
  async getUploadedFiles(
    params: {
      dept?: string;
      admin?: string;
      sort_by?: string;
      limit?: number;
      offset?: number;
    } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.dept) searchParams.append("dept", params.dept);
    if (params.admin) searchParams.append("admin", params.admin);
    if (params.sort_by) searchParams.append("sort_by", params.sort_by);
    if (params.limit) searchParams.append("limit", params.limit.toString());
    if (params.offset) searchParams.append("offset", params.offset.toString());

    const response = await fetch(
      `${API_BASE_URL}/api/read/upload/list?${searchParams.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<{
      files: Array<{
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
      }>;
      total_count: number;
      total_size: number;
      page_info: {
        limit: number;
        offset: number;
        has_more: boolean;
      };
    }>(response);
  }
  async getTextKnowledge(
    params: {
      dept?: string;
      adminid?: string;
      sort_by?: boolean;
      limit?: number;
      offset?: number;
    } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.dept) searchParams.append("dept", params.dept);
    if (params.adminid) searchParams.append("adminid", params.adminid);
    if (params.sort_by !== undefined)
      searchParams.append("sort_by", params.sort_by.toString());
    if (params.limit) searchParams.append("limit", params.limit.toString());
    if (params.offset) searchParams.append("offset", params.offset.toString());

    const response = await fetch(
      `${API_BASE_URL}/api/read/upload/text?${searchParams.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<{
      text_knowledge: Array<{
        id: string;
        title: string;
        text: string;
        department: string;
        uploaded_by: string;
        uploaded_by_name: string;
        created_at: string;
        updated_at: string;
        chunk_count: number;
      }>;
      total_count: number;
      page_info: {
        limit: number;
        offset: number;
        has_more: boolean;
      };
    }>(response);
  } // Dashboard stats
  async getDashboardStats() {
    const headers = this.getAuthHeaders();
    console.log("API: Getting dashboard stats with headers:", headers);
    console.log(
      "API: Dashboard stats URL:",
      `${API_BASE_URL}/api/read/dashboard/stats`
    );

    const response = await fetch(`${API_BASE_URL}/api/read/dashboard/stats`, {
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
    });

    console.log("API: Dashboard stats response status:", response.status);

    return this.handleResponse<{
      total_user_questions: number;
      total_admin_questions: number;
      total_text_knowledge: number;
      total_file_knowledge: number;
      pending_questions: number;
      processed_questions: number;
      avg_response_time: number;
      active_users: number;
      requested_by: string;
    }>(response);
  }

  async getAvgResponseTimes(interval?: string, n?: number) {
    const params = new URLSearchParams();
    if (interval) params.append("interval", interval);
    if (n) params.append("n", n.toString());

    const response = await fetch(
      `${API_BASE_URL}/api/read/avg-response-times?${params.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<{
      average_response_time: number;
      data_points: number;
      interval?: string;
      time_series: Array<{
        timestamp: string;
        avg_response_time: number;
      }>;
    }>(response);
  }

  async getUserQuestions(
    params: {
      status?: string;
      dept?: string;
      admin?: string;
      sort_by?: boolean;
      limit?: number;
      offset?: number;
    } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.append("status", params.status);
    if (params.dept) searchParams.append("dept", params.dept);
    if (params.admin) searchParams.append("admin", params.admin);
    if (params.sort_by !== undefined)
      searchParams.append("sort_by", params.sort_by.toString());
    if (params.limit) searchParams.append("limit", params.limit.toString());
    if (params.offset) searchParams.append("offset", params.offset.toString());

    const response = await fetch(
      `${API_BASE_URL}/api/read/getuserquestions?${searchParams.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    const data = await this.handleResponse<{
      questions: Array<{
        id: string;
        question: string;
        user_id: string;
        department: string;
        status: string;
        admin_assigned: string;
        created_at: string;
        processed_at?: string;
      }>;
      total_count: number;
      page_info: {
        limit: number;
        offset: number;
        has_more: boolean;
      };
    }>(response);

    return {
      questions: data.questions,
      total_count: data.total_count,
      page_info: data.page_info,
    };
  }
  async getAdminQuestions(
    params: {
      status?: string;
      dept?: string;
      admin?: string;
      sort_by?: boolean;
      limit?: number;
      offset?: number;
    } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.append("status", params.status);
    if (params.dept) searchParams.append("dept", params.dept);
    if (params.admin) searchParams.append("admin", params.admin);
    if (params.sort_by !== undefined)
      searchParams.append("sort_by", params.sort_by.toString());
    if (params.limit) searchParams.append("limit", params.limit.toString());
    if (params.offset) searchParams.append("offset", params.offset.toString());

    const response = await fetch(
      `${API_BASE_URL}/api/read/getadminquestions?${searchParams.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    const data = await this.handleResponse<{
      questions: Array<{
        id: string;
        question: string;
        department: string;
        status: string;
        priority: string;
        asked_by: string;
        assigned_to: string;
        answer?: string;
        answered_by?: string;
        created_at: string;
        answered_at?: string;
      }>;
      total_count: number;
      page_info: {
        limit: number;
        offset: number;
        has_more: boolean;
      };
    }>(response);

    return {
      questions: data.questions,
      total_count: data.total_count,
      page_info: data.page_info,
    };
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

    return this.handleResponse<{
      summary: string;
      total_pending: number;
      categories: Array<{
        category: string;
        count: number;
        examples: string[];
      }>;
      generated_at: string;
    }>(response);
  }

  // Department management
  async getDepartmentKeywords(deptName?: string) {
    const params = new URLSearchParams();
    if (deptName) params.append("dept_name", deptName);

    const response = await fetch(
      `${API_BASE_URL}/api/read/departments/keywords?${params.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<
      Record<
        string,
        Array<{
          id: string;
          keyword: string;
        }>
      >
    >(response);
  }

  async getDepartmentDescriptions(deptName?: string) {
    const params = new URLSearchParams();
    if (deptName) params.append("dept_name", deptName);

    const response = await fetch(
      `${API_BASE_URL}/api/read/departments/descriptions?${params.toString()}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<
      Record<
        string,
        {
          name: string;
          description: string;
          updated_at: string;
        }
      >
    >(response);
  }

  async addDepartmentKeywords(deptName: string, keywords: string[]) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/departments/keywords`,
      {
        method: "POST",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dept_name: deptName,
          keywords: keywords,
        }),
      }
    );

    return this.handleResponse(response);
  }

  async updateDepartmentKeyword(keywordId: string, newKeyword: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/departments/keywords/${keywordId}`,
      {
        method: "PUT",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          new_keyword: newKeyword,
        }),
      }
    );

    return this.handleResponse(response);
  }

  async deleteDepartmentKeyword(keywordId: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/departments/keywords/${keywordId}`,
      {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse(response);
  }

  async updateDepartmentDescription(deptName: string, newDescription: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/departments/${deptName}`,
      {
        method: "PUT",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          new_description: newDescription,
        }),
      }
    );

    return this.handleResponse(response);
  }

  // File management
  async deleteFile(fileId: string) {
    const response = await fetch(`${API_BASE_URL}/api/admin/files/${fileId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }
  async updateTextKnowledge(
    textId: string,
    data: {
      title?: string;
      text?: string;
      dept?: string;
    }
  ) {
    const response = await fetch(`${API_BASE_URL}/api/admin/text/${textId}`, {
      method: "PUT",
      headers: {
        ...this.getAuthHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  }

  async deleteTextKnowledge(textId: string) {
    const response = await fetch(`${API_BASE_URL}/api/admin/text/${textId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  // Authentication - change password
  async changePassword(currentPassword: string, newPassword: string) {
    const response = await fetch(`${API_BASE_URL}/api/read/changepassword`, {
      method: "PUT",
      headers: {
        ...this.getAuthHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    return this.handleResponse(response);
  }

  // Super admin endpoints
  async getAllAdmins() {
    const response = await fetch(`${API_BASE_URL}/api/superadmin/admins`, {
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<{
      admins: Array<{
        id: string;
        name: string;
        email: string;
        role: string;
        enabled: boolean;
        email_verified: boolean;
        last_login?: string;
        created_at: string;
        updated_at: string;
      }>;
      total_count: number;
    }>(response);
  }

  async createAdmin(data: {
    name: string;
    email: string;
    password: string;
    role: string;
  }) {
    const response = await fetch(
      `${API_BASE_URL}/api/superadmin/admin/create`,
      {
        method: "POST",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }
    );

    return this.handleResponse(response);
  }

  async updateAdmin(
    adminId: string,
    data: {
      name?: string;
      email?: string;
      role?: string;
      enabled?: boolean;
    }
  ) {
    const response = await fetch(
      `${API_BASE_URL}/api/superadmin/admin/${adminId}`,
      {
        method: "PUT",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }
    );

    return this.handleResponse(response);
  }

  async deleteAdmin(adminId: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/superadmin/admin/${adminId}`,
      {
        method: "DELETE",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          confirmation: "DELETE_ADMIN",
        }),
      }
    );

    return this.handleResponse(response);
  }

  async resetAdminPassword(adminId: string, newPassword: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/superadmin/admin/resetpassword/${adminId}`,
      {
        method: "PUT",
        headers: {
          ...this.getAuthHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newPassword),
      }
    );

    return this.handleResponse(response);
  }

  // User query for testing department detection
  async testDepartmentDetection(query: string) {
    const response = await fetch(`${API_BASE_URL}/api/user/department`, {
      method: "POST",
      headers: {
        ...this.getAuthHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    return this.handleResponse<{
      department: string;
      requested_by: string;
    }>(response);
  }

  // Refresh router data
  async refreshRouterData() {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/refresh-router-data`,
      {
        method: "POST",
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse(response);
  }

  // Purge user history
  async purgeUserHistory(timeHours: number = 24) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/history/purge?time_hours=${timeHours}`,
      {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse(response);
  }
}

export const apiClient = new ApiClient();
