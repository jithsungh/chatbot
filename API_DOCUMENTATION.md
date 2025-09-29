# Chatbot Backend API Documentation

## Overview

This FastAPI backend provides a comprehensive chatbot system with admin management, file upload capabilities, question handling, and user query processing. The system supports role-based authentication with three levels: Read-Only Admin, Admin, and Super Admin.

## Base URL

- Development: `http://localhost:8000`
- Production: (Your production URL)

## Authentication

The API uses Bearer Token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Role-Based Access Control

- **Read-Only Admin**: Can view data and change their own password
- **Admin**: Can upload files, manage questions, and perform administrative tasks
- **Super Admin**: Full system access including user management and data deletion

---

## API Endpoints

### 🏠 General Endpoints

#### GET `/`

**Description**: Root endpoint for basic API health check
**Authentication**: None required

**Response Schema**:

```json
{
  "message": "Hello World"
}
```

#### GET `/health`

**Description**: Runtime health check endpoint to verify database connectivity
**Authentication**: None required

**Response Schema**:

```json
{
  "status": "healthy" | "unhealthy",
  "database": "connected" | "disconnected",
  "message": "All systems operational",
  "error": "string (only present if unhealthy)"
}
```

---

### 👤 User Endpoints

#### POST `/api/user/query`

**Description**: Handle user query and return response from the chatbot
**Authentication**: None required
**Tags**: [query]

**Request Body**:

```json
{
  "query": "What is Techmojo?", // User's question or input
  "userid": "user123" // Unique identifier for session management
}
```

**Response Schema**:

```json
{
  "response": "string", // Bot's response to the query
  "department": "string", // Determined department (HR, IT, Finance, etc.)
  "confidence": "number", // Confidence score for the response
  "sources": ["string"], // List of sources used for the response
  "timestamp": "string" // ISO timestamp of response
}
```

#### POST `/api/user/department`

**Description**: Determine the department for a given query (Admin access required)
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [query]

**Request Body**:

```json
{
  "query": "What is Techmojo?" // User's question for department routing
}
```

**Response Schema**:

```json
{
  "department": "HR" | "IT" | "Finance" | "Security",  // Determined department
  "requested_by": "uuid"                               // Admin ID who made the request
}
```

#### DELETE `/api/user/history/{userid}`

**Description**: Clear conversation history for a specific user
**Authentication**: None required
**Tags**: [query]

**Path Parameters**:

- `userid` (string): Unique identifier for the user

**Response Schema**:

```json
{
  "message": "Conversation history cleared for user {userid}"
}
```

---

### 👨‍💼 Admin Endpoints

#### POST `/api/admin/upload/files/{dept}`

**Description**: Upload single or multiple files for processing and storage
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `dept` (string): Department (HR, IT, Finance, Security)

**Query Parameters**:

- `concurrent_limit` (integer, 1-5, default: 3): Number of files to process concurrently

**Request Body**: `multipart/form-data`

- `files`: Array of files to upload

**Response Schema**:

```json
{
  "message": "Processed {total} files",
  "successful_uploads": "number",      // Count of successfully uploaded files
  "failed_uploads": "number",          // Count of failed uploads
  "results": [
    {
      "filename": "string",
      "status": "success" | "failed",
      "file_id": "uuid",              // Only present for successful uploads
      "error": "string"               // Only present for failed uploads
    }
  ],
  "department": "string",
  "uploaded_by": "uuid"               // Admin ID who uploaded
}
```

#### POST `/api/admin/upload/text/{dept}`

**Description**: Upload raw text to be processed and stored in vector database
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `dept` (string): Department name

**Request Body**:

```json
{
  "title": "Document Title", // Title for the text knowledge
  "text": "Content to be stored" // Text content to process and store
}
```

**Response Schema**:

```json
{
  "message": "Text uploaded successfully",
  "text_id": "uuid", // ID of created text knowledge record
  "department": "string",
  "title": "string",
  "chunks_created": "number", // Number of text chunks created
  "uploaded_by": "uuid"
}
```

#### POST `/api/admin/summarize`

**Description**: Summarize pending admin questions using AI
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Response Schema**:

```json
{
  "summary": "string", // AI-generated summary of pending questions
  "total_pending": "number", // Count of pending questions
  "categories": [
    {
      "category": "string", // Question category
      "count": "number", // Number of questions in this category
      "examples": ["string"] // Sample questions from this category
    }
  ],
  "generated_at": "string" // ISO timestamp
}
```

#### POST `/api/admin/answer`

**Description**: Store answer to an admin question and mark as processed
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Request Body**:

```json
{
  "question_id": "uuid", // ID of the admin question
  "answer": "Detailed answer text" // Answer to the question
}
```

**Response Schema**:

```json
{
  "message": "Question answered successfully",
  "question_id": "uuid",
  "answer_id": "uuid", // ID of the created answer
  "answered_by": "uuid", // Admin ID who answered
  "answered_at": "string" // ISO timestamp
}
```

#### DELETE `/api/admin/files/{file_id}`

**Description**: Delete a specific uploaded file
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `file_id` (string): UUID of the file to delete

**Response Schema**:

```json
{
  "message": "File deleted successfully",
  "file_id": "uuid",
  "filename": "string",
  "deleted_by": "uuid" // Admin ID who deleted the file
}
```

#### PUT `/api/admin/text/{text_id}`

**Description**: Edit existing text knowledge record
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `text_id` (string): UUID of the text knowledge record

**Request Body**:

```json
{
  "title": "New Title", // Optional: Update title
  "text": "Updated content", // Optional: Update text content
  "dept": "HR" // Optional: Update department
}
```

**Response Schema**:

```json
{
  "message": "Text knowledge updated successfully",
  "text_id": "uuid",
  "changes_made": ["title", "text", "department"], // List of fields that were updated
  "vectors_updated": "boolean", // Whether vector embeddings were regenerated
  "updated_by": "uuid"
}
```

#### POST `/api/admin/departments/keywords`

**Description**: Add keywords to a department for better routing
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Request Body**:

```json
{
  "dept_name": "HR", // Department name
  "keywords": ["benefits", "leave", "policy"] // Array of keywords to add
}
```

**Response Schema**:

```json
{
  "message": "Keywords added successfully",
  "department": "string",
  "keywords_added": ["string"], // List of successfully added keywords
  "keywords_skipped": ["string"], // List of keywords that already existed
  "added_by": "uuid"
}
```

#### PUT `/api/admin/departments/keywords/{keyword_id}`

**Description**: Update an existing keyword
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `keyword_id` (string): UUID of the keyword to update

**Request Body**:

```json
{
  "new_keyword": "updated keyword" // New keyword value
}
```

**Response Schema**:

```json
{
  "message": "Keyword updated successfully",
  "keyword_id": "uuid",
  "old_keyword": "string",
  "new_keyword": "string",
  "updated_by": "uuid"
}
```

#### DELETE `/api/admin/departments/keywords/{keyword_id}`

**Description**: Delete a department keyword
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `keyword_id` (string): UUID of the keyword to delete

**Response Schema**:

```json
{
  "message": "Keyword deleted successfully",
  "keyword_id": "uuid",
  "keyword": "string",
  "department": "string",
  "deleted_by": "uuid"
}
```

#### PUT `/api/admin/departments/{dept_name}`

**Description**: Update department description
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Path Parameters**:

- `dept_name` (string): Name of the department

**Request Body**:

```json
{
  "new_description": "Updated department description"
}
```

**Response Schema**:

```json
{
  "message": "Department description updated successfully",
  "department": "string",
  "old_description": "string",
  "new_description": "string",
  "updated_by": "uuid"
}
```

#### DELETE `/api/admin/history/purge`

**Description**: Purge user conversation history older than specified hours
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Query Parameters**:

- `time_hours` (integer, 1-168, default: 24): Hours threshold for purging

**Response Schema**:

```json
{
  "message": "User history purged successfully",
  "records_deleted": "number", // Number of conversation records deleted
  "cutoff_time": "string", // ISO timestamp of cutoff
  "purged_by": "uuid"
}
```

#### POST `/api/admin/refresh-router-data`

**Description**: Refresh department routing data from database
**Authentication**: Bearer Token (Admin or above)
**Tags**: [admin]

**Response Schema**:

```json
{
  "message": "Router data refreshed successfully",
  "departments_loaded": "number",
  "keywords_loaded": "number",
  "last_refresh": "string", // ISO timestamp
  "refreshed_by": "uuid"
}
```

---

### 📖 Read-Only Admin Endpoints

#### GET `/api/read/avg-response-times`

**Description**: Get average response times with optional filtering
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**:

- `interval` (string, optional): Time interval (daily, weekly, monthly)
- `n` (integer, optional): Number of recent records to analyze

**Response Schema**:

```json
{
  "average_response_time": "number", // Average response time in seconds
  "data_points": "number", // Number of data points used
  "interval": "string",
  "time_series": [
    {
      "timestamp": "string", // ISO timestamp
      "avg_response_time": "number"
    }
  ]
}
```

#### PUT `/api/read/changepassword`

**Description**: Change password for current logged-in admin
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Request Body**:

```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

**Response Schema**:

```json
{
  "message": "Password changed successfully",
  "admin_id": "uuid",
  "changed_at": "string" // ISO timestamp
}
```

#### GET `/api/read/getuserquestions`

**Description**: Retrieve user questions with filtering and pagination
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**:

- `status` (string, optional): Filter by status (pending, processed)
- `dept` (string, optional): Filter by department
- `admin` (string, optional): Filter by admin ('self' or admin UUID)
- `sort_by` (boolean, default: false): Sort order (false=asc, true=desc)
- `limit` (integer, 1-1000, default: 100): Maximum results
- `offset` (integer, default: 0): Pagination offset

**Response Schema**:

```json
{
  "questions": [
    {
      "id": "uuid",
      "question": "string",         // Original user question
      "user_id": "string",          // User who asked the question
      "department": "string",       // Determined department
      "status": "pending" | "processed",
      "admin_assigned": "uuid",     // Admin assigned to handle this
      "created_at": "string",       // ISO timestamp
      "processed_at": "string"      // ISO timestamp (if processed)
    }
  ],
  "total_count": "number",          // Total matching records
  "page_info": {
    "limit": "number",
    "offset": "number",
    "has_more": "boolean"
  }
}
```

#### GET `/api/read/getadminquestions`

**Description**: Retrieve admin questions with filtering and pagination
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**: Same as `/api/read/getuserquestions`

**Response Schema**:

```json
{
  "questions": [
    {
      "id": "uuid",
      "question": "string",         // Admin's question
      "department": "string",
      "status": "pending" | "processed" | "answered",
      "priority": "low" | "medium" | "high",
      "asked_by": "uuid",           // Admin who asked
      "assigned_to": "uuid",        // Admin assigned to answer
      "answer": "string",           // Answer (if answered)
      "answered_by": "uuid",        // Admin who answered
      "created_at": "string",
      "answered_at": "string"
    }
  ],
  "total_count": "number",
  "page_info": {
    "limit": "number",
    "offset": "number",
    "has_more": "boolean"
  }
}
```

#### GET `/api/read/upload/text`

**Description**: Retrieve text knowledge records with filtering
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**:

- `dept` (string, optional): Filter by department
- `adminid` (string, optional): Filter by admin ('self' or UUID)
- `sort_by` (boolean, default: false): Sort order
- `limit` (integer, 1-1000, default: 100): Maximum results
- `offset` (integer, default: 0): Pagination offset

**Response Schema**:

```json
{
  "text_knowledge": [
    {
      "id": "uuid",
      "title": "string",
      "text": "string", // Full text content
      "department": "string",
      "uploaded_by": "uuid",
      "uploaded_by_name": "string",
      "created_at": "string",
      "updated_at": "string",
      "chunk_count": "number" // Number of vector chunks created
    }
  ],
  "total_count": "number",
  "page_info": {
    "limit": "number",
    "offset": "number",
    "has_more": "boolean"
  }
}
```

#### GET `/api/read/upload/list`

**Description**: List uploaded files with filtering and pagination
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**:

- `dept` (string, optional): Filter by department
- `admin` (string, optional): Filter by admin ('self' or admin_id)
- `sort_by` (string, default: 'desc'): Sort by created date ('asc' or 'desc')
- `limit` (integer, 1-1000, default: 100): Maximum results
- `offset` (integer, default: 0): Pagination offset

**Response Schema**:

```json
{
  "files": [
    {
      "id": "uuid",
      "filename": "string",
      "original_filename": "string",
      "file_size": "number",        // Size in bytes
      "file_type": "string",        // MIME type
      "department": "string",
      "uploaded_by": "uuid",
      "uploaded_by_name": "string",
      "created_at": "string",
      "processing_status": "completed" | "processing" | "failed",
      "download_url": "string"      // URL for downloading the file
    }
  ],
  "total_count": "number",
  "total_size": "number",           // Total size of all files in bytes
  "page_info": {
    "limit": "number",
    "offset": "number",
    "has_more": "boolean"
  }
}
```

#### GET `/api/read/download/{file_id}`

**Description**: Download a specific file
**Authentication**: None required
**Tags**: [readonlyadmin]

**Path Parameters**:

- `file_id` (string): UUID of the file to download

**Response**: File download (binary data)

#### GET `/api/read/departments/keywords`

**Description**: Retrieve department keywords grouped by department
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**:

- `dept_name` (string, optional): Filter by department name

**Response Schema**:

```json
{
  "HR": [
    {
      "id": "uuid",
      "keyword": "benefits"
    },
    {
      "id": "uuid",
      "keyword": "leave"
    }
  ],
  "IT": [
    {
      "id": "uuid",
      "keyword": "password"
    }
  ]
}
```

#### GET `/api/read/departments/descriptions`

**Description**: Retrieve department descriptions
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Query Parameters**:

- `dept_name` (string, optional): Filter by department name

**Response Schema**:

```json
{
  "HR": {
    "name": "HR",
    "description": "Human Resources department handling employee relations",
    "updated_at": "string"
  },
  "IT": {
    "name": "IT",
    "description": "Information Technology support and infrastructure",
    "updated_at": "string"
  }
}
```

#### GET `/api/read/dashboard/stats`

**Description**: Retrieve dashboard statistics
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Response Schema**:

```json
{
  "questions_processed": "number", // Total processed questions
  "questions_pending": "number", // Total pending questions
  "avg_response_time": "number", // Average response time in seconds
  "files_stored": "number", // Total uploaded files
  "text_knowledge_records": "number", // Total text knowledge records
  "active_users": "number", // Number of active users (last 24h)
  "departments": {
    "HR": {
      "questions": "number",
      "files": "number"
    },
    "IT": {
      "questions": "number",
      "files": "number"
    }
  },
  "last_updated": "string" // ISO timestamp
}
```

#### GET `/api/read/router-data-summary`

**Description**: Get summary of current router data
**Authentication**: Bearer Token (Read-Only Admin or above)
**Tags**: [readonlyadmin]

**Response Schema**:

```json
{
  "departments": [
    {
      "name": "HR",
      "keyword_count": "number",
      "description": "string",
      "last_updated": "string"
    }
  ],
  "total_keywords": "number",
  "last_refresh": "string" // ISO timestamp
}
```

---

### 🔒 Super Admin Endpoints

#### DELETE `/api/superadmin/files/all`

**Description**: Delete all uploaded files from database and vector store
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "confirmation": "DELETE_ALL_FILES" // Required confirmation string
}
```

**Response Schema**:

```json
{
  "message": "All files deleted successfully",
  "files_deleted": "number",
  "vector_records_deleted": "number",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### DELETE `/api/superadmin/text/all`

**Description**: Delete all text knowledge from database and vector store
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "confirmation": "DELETE_ALL_TEXT" // Required confirmation string
}
```

**Response Schema**:

```json
{
  "message": "All text knowledge deleted successfully",
  "records_deleted": "number",
  "vector_records_deleted": "number",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### DELETE `/api/superadmin/user-questions/all`

**Description**: Delete all user questions from database
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "confirmation": "DELETE_ALL_USER_QUESTIONS"
}
```

**Response Schema**:

```json
{
  "message": "All user questions deleted successfully",
  "records_deleted": "number",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### DELETE `/api/superadmin/admin-questions/all`

**Description**: Delete all admin questions from database
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "confirmation": "DELETE_ALL_ADMIN_QUESTIONS"
}
```

**Response Schema**:

```json
{
  "message": "All admin questions deleted successfully",
  "records_deleted": "number",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### DELETE `/api/superadmin/dept-failures/all`

**Description**: Delete all department failure records
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "confirmation": "DELETE_ALL_DEPT_FAILURES"
}
```

**Response Schema**:

```json
{
  "message": "All department failures deleted successfully",
  "records_deleted": "number",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### DELETE `/api/superadmin/response-times/all`

**Description**: Delete all response time records
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "confirmation": "DELETE_ALL_RESPONSE_TIMES"
}
```

**Response Schema**:

```json
{
  "message": "All response times deleted successfully",
  "records_deleted": "number",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### POST `/api/superadmin/admin/create`

**Description**: Create a new admin with specified role
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Request Body**:

```json
{
  "name": "Admin Name",
  "email": "admin@example.com",
  "password": "securepassword",
  "role": "read_only" | "admin" | "super_admin"
}
```

**Response Schema**:

```json
{
  "message": "Admin created successfully",
  "admin_id": "uuid",
  "name": "string",
  "email": "string",
  "role": "string",
  "created_by": "uuid",
  "created_at": "string"
}
```

#### GET `/api/superadmin/admins`

**Description**: Get all admin accounts with their details
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Response Schema**:

```json
{
  "admins": [
    {
      "id": "uuid",
      "name": "string",
      "email": "string",
      "role": "read_only" | "admin" | "super_admin",
      "enabled": "boolean",
      "email_verified": "boolean",
      "last_login": "string",        // ISO timestamp
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "total_count": "number"
}
```

#### DELETE `/api/superadmin/admin/{admin_id}`

**Description**: Delete an admin account by ID
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Path Parameters**:

- `admin_id` (string): UUID of admin to delete

**Request Body**:

```json
{
  "confirmation": "DELETE_ADMIN" // Required confirmation
}
```

**Response Schema**:

```json
{
  "message": "Admin deleted successfully",
  "deleted_admin_id": "uuid",
  "deleted_admin_name": "string",
  "deleted_by": "uuid",
  "deleted_at": "string"
}
```

#### PUT `/api/superadmin/admin/{admin_id}`

**Description**: Update an admin account by ID
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Path Parameters**:

- `admin_id` (string): UUID of admin to update

**Request Body**:

```json
{
  "name": "New Name", // Optional
  "email": "newemail@example.com", // Optional
  "role": "admin", // Optional
  "enabled": true // Optional
}
```

**Response Schema**:

```json
{
  "message": "Admin updated successfully",
  "admin_id": "uuid",
  "changes_made": ["name", "email", "role", "enabled"],
  "updated_by": "uuid",
  "updated_at": "string"
}
```

#### PUT `/api/superadmin/admin/resetpassword/{admin_id}`

**Description**: Reset an admin's password by ID
**Authentication**: Bearer Token (Super Admin only)
**Tags**: [superadmin]

**Path Parameters**:

- `admin_id` (string): UUID of admin whose password to reset

**Request Body**:

```json
"newpassword123" // Plain string with new password
```

**Response Schema**:

```json
{
  "message": "Admin password reset successfully",
  "admin_id": "uuid",
  "admin_name": "string",
  "reset_by": "uuid",
  "reset_at": "string"
}
```

---

### 🔐 Authentication Endpoints

#### POST `/api/auth/signup`

**Description**: Register a new admin account with email verification
**Authentication**: None required
**Tags**: [auth]

**Request Body**:

```json
{
  "name": "Full Name",
  "email": "user@company.com", // Must be from organization domain
  "password": "securepassword" // Minimum 8 characters
}
```

**Response Schema**:

```json
{
  "message": "Admin registered successfully. Please check your email for verification.",
  "admin_id": "uuid",
  "email": "string",
  "verification_sent": "boolean"
}
```

#### GET `/api/auth/verify-email`

**Description**: Verify admin email using verification token
**Authentication**: None required
**Tags**: [auth]

**Query Parameters**:

- `token` (string): Email verification token

**Response Schema**:

```json
{
  "message": "Email verified successfully",
  "admin_id": "uuid",
  "email": "string",
  "verified_at": "string"
}
```

#### POST `/api/auth/resend-verification`

**Description**: Resend verification email
**Authentication**: None required
**Tags**: [auth]

**Request Body**:

```json
{
  "email": "user@company.com"
}
```

**Response Schema**:

```json
{
  "message": "Verification email sent successfully",
  "email": "string",
  "sent_at": "string"
}
```

#### POST `/api/auth/create/manual`

**Description**: Create admin manually without email verification (for initial setup)
**Authentication**: None required (requires bypass key)
**Tags**: [auth]

**Request Body**:

```json
{
  "name": "Admin Name",
  "email": "admin@company.com",
  "password": "password",
  "bypass_key": "secret_bypass_key" // System configuration bypass key
}
```

**Response Schema**:

```json
{
  "message": "Admin created successfully",
  "admin_id": "uuid",
  "name": "string",
  "email": "string",
  "role": "admin",
  "created_at": "string"
}
```

#### POST `/api/auth/login`

**Description**: Login and receive JWT access token
**Authentication**: None required
**Tags**: [auth]

**Request Body**: `application/x-www-form-urlencoded`

- `username` (string): Admin email
- `password` (string): Admin password
- `grant_type` (string): Must be "password"

**Response Schema**:

```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "expires_in": "number",           // Token expiry in seconds
  "admin_id": "uuid",
  "name": "string",
  "email": "string",
  "role": "read_only" | "admin" | "super_admin"
}
```

#### GET `/api/auth/me`

**Description**: Get current admin information
**Authentication**: Bearer Token
**Tags**: [auth]

**Response Schema**:

```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "role": "read_only" | "admin" | "super_admin",
  "enabled": "boolean",
  "email_verified": "boolean",
  "last_login": "string",
  "created_at": "string"
}
```

---

## Error Responses

All endpoints may return these standard error responses:

### 400 Bad Request

```json
{
  "detail": "Error message describing what went wrong"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

### 403 Forbidden

```json
{
  "detail": "Insufficient permissions for this operation"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error message"
}
```

---

## Usage Examples

### Frontend Authentication Flow

1. **Login**:

```javascript
const response = await fetch("/api/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: "username=admin@company.com&password=password&grant_type=password",
});
const data = await response.json();
localStorage.setItem("token", data.access_token);
```

2. **Authenticated Request**:

```javascript
const response = await fetch("/api/read/dashboard/stats", {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  },
});
```

### File Upload Example

```javascript
const formData = new FormData();
formData.append("files", file1);
formData.append("files", file2);

const response = await fetch("/api/admin/upload/files/HR", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
  },
  body: formData,
});
```

### Query Chatbot Example

```javascript
const response = await fetch("/api/user/query", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What is the leave policy?",
    userid: "user123",
  }),
});
```

---

## Rate Limiting

- File uploads are limited by concurrent processing (default: 3 files at once)
- Maximum file size: 10MB per file
- Maximum files per upload: 50 files
- Text uploads have no specific rate limits but are subject to processing time

## Department Types

The system supports these department types:

- `HR` - Human Resources
- `IT` - Information Technology
- `Finance` - Financial Operations
- `Security` - Security and Compliance

## Admin Roles

- `read_only` - Can view data and change own password
- `admin` - Can upload files, manage content, answer questions
- `super_admin` - Full system access including user management

---

_This documentation is current as of the API version 0.1.0. For the most up-to-date information, please refer to the `/docs` endpoint of your running API instance._
