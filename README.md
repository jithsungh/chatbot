# 🤖 Enterprise Chatbot System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange.svg)

An intelligent, department-aware chatbot system with advanced RAG (Retrieval-Augmented Generation) capabilities, role-based admin management, and comprehensive analytics.

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [System Components](#-system-components)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Admin Dashboard](#-admin-dashboard)
- [Database Schema](#-database-schema)
- [Development](#-development)
- [Deployment](#-deployment)

---

## 🌟 Overview

This enterprise-grade chatbot system provides intelligent, context-aware responses by leveraging advanced NLP techniques and a sophisticated RAG pipeline. The system automatically routes queries to appropriate departments (HR, IT, Security, etc.) and retrieves relevant context from a vector database to generate accurate responses.

### Core Capabilities

- **Intelligent Department Routing**: Hybrid routing using semantic embeddings and keyword matching
- **Context-Aware Responses**: RAG pipeline with ChromaDB vector store for relevant context retrieval
- **Conversation History**: Maintains multi-turn conversations with up to 25 turns per user
- **Security Features**: Organization name anonymization and PII protection
- **Admin Management**: Three-tier role-based access control (Read-Only, Admin, Super Admin)
- **Knowledge Management**: Upload and manage documents (PDF, DOCX), text knowledge, and Q&A pairs
- **Analytics Dashboard**: Comprehensive statistics, response time tracking, and department performance metrics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│  ┌──────────────────┐              ┌──────────────────────┐     │
│  │   User Chat UI   │              │  Admin Dashboard     │     │
│  │   (Frontend)     │              │  (React + TypeScript)│     │
│  └────────┬─────────┘              └──────────┬───────────┘     │
└───────────┼────────────────────────────────────┼─────────────────┘
            │                                    │
            ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ User Routes  │  │ Admin Routes │  │ Super Admin Routes   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │               │
│         └─────────────────┼──────────────────────┘               │
│                           ▼                                      │
│              ┌────────────────────────┐                          │
│              │  Inference Pipeline    │                          │
│              │  ┌──────────────────┐  │                          │
│              │  │ Hybrid Router    │  │ (Department Detection)   │
│              │  └──────────────────┘  │                          │
│              │  ┌──────────────────┐  │                          │
│              │  │Context Retriever │  │ (RAG from ChromaDB)      │
│              │  └──────────────────┘  │                          │
│              │  ┌──────────────────┐  │                          │
│              │  │ History Manager  │  │ (Conversation Context)   │
│              │  └──────────────────┘  │                          │
│              │  ┌──────────────────┐  │                          │
│              │  │ Prompt Generator │  │ (Context Augmentation)   │
│              │  └──────────────────┘  │                          │
│              │  ┌──────────────────┐  │                          │
│              │  │   LLM Client     │  │ (Groq/Google AI)         │
│              │  └──────────────────┘  │                          │
│              │  ┌──────────────────┐  │                          │
│              │  │Response Formatter│  │ (Output Processing)      │
│              │  └──────────────────┘  │                          │
│              └────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
            │                                    │
            ▼                                    ▼
┌───────────────────────┐          ┌───────────────────────────┐
│   PostgreSQL Database │          │  ChromaDB Vector Store    │
│  ┌─────────────────┐  │          │  ┌─────────────────────┐  │
│  │ User Questions  │  │          │  │ Document Embeddings │  │
│  │ Admin Questions │  │          │  │ Text Embeddings     │  │
│  │ File Knowledge  │  │          │  │ Q&A Embeddings      │  │
│  │ Text Knowledge  │  │          │  │ Department Metadata │  │
│  │ Admins          │  │          │  └─────────────────────┘  │
│  │ Departments     │  │          └───────────────────────────┘
│  │ Dept Keywords   │  │
│  │ Dept Failures   │  │
│  │ Response Times  │  │
│  └─────────────────┘  │
└───────────────────────┘
```

---

## ✨ Key Features

### 🎯 Intelligent Query Processing

#### 1. **Hybrid Department Router**
- Combines semantic embeddings with keyword-based matching
- Dynamically loads department descriptions and keywords from database
- Fallback mechanism ensures robust classification
- Supports custom departments: HR, IT, Security, Finance, General Inquiry
- **Implementation**: [HybridRouter.py](src/inference/HybridRouter.py)

#### 2. **RAG Pipeline**
- **Context Retrieval**: Fetches top-K relevant documents from ChromaDB
- **Semantic Search**: Uses SentenceTransformers (all-MiniLM-L6-v2) for embeddings
- **Department Filtering**: Contextual retrieval based on detected department
- **Fallback Strategy**: Retrieves from all departments if specific department yields insufficient results
- **Implementation**: [Pipeline.py](src/inference/Pipeline.py), [ContextRetriever.py](src/inference/ContextRetriever.py)

#### 3. **Conversation History Management**
- Maintains up to 25 conversation turns per user
- Automatic purging of conversations older than 48 hours
- Stores last context and follow-up questions for continuity
- Async operations with user-level locking for thread safety
- **Implementation**: [HistoryManager.py](src/inference/HistoryManager.py)

#### 4. **Security & Anonymization**
- Organization name replacement in prompts and responses
- Protects sensitive organizational information when using external LLMs
- Bidirectional anonymization (request/response)
- Configurable organization mappings
- **Implementation**: [SecurityAnonymizer.py](src/utils/SecurityAnonymizer.py)

### 🔐 Authentication & Authorization

#### Three-Tier Role System

1. **Read-Only Admin**
   - View all data (queries, questions, knowledge base)
   - Access analytics and dashboards
   - Download files
   - Change own password

2. **Admin** (includes all Read-Only permissions)
   - Upload files and text knowledge
   - Answer admin questions
   - Manage department keywords and descriptions
   - Process department routing failures
   - Refresh router data
   - Purge conversation history

3. **Super Admin** (includes all Admin permissions)
   - Create, update, and delete admin accounts
   - Delete all files, text, questions, or failures (bulk operations)
   - Reset admin passwords
   - Purge entire vector database
   - Full system access

#### Authentication Features
- JWT-based token authentication
- Bcrypt password hashing with secure truncation handling
- Email verification system (configurable)
- Manual admin creation with bypass key
- Token expiration management
- **Implementation**: [AdminAuthRoutes.py](src/app/routes/AdminAuthRoutes.py), [role_auth.py](src/dependencies/role_auth.py)

### 📤 Knowledge Management

#### File Upload System
- **Supported Formats**: PDF, DOCX
- **Concurrent Processing**: Configurable concurrent upload limits (1-5 files)
- **Size Limits**: 10MB per file, 50 files max per batch
- **Processing Pipeline**:
  1. Text extraction (PyMuPDF for PDF, python-docx for DOCX)
  2. Text cleaning and preprocessing
  3. Smart chunking with overlap
  4. Vector embedding generation
  5. ChromaDB storage with metadata
  6. PostgreSQL record creation
- **Department Association**: Each file tagged with department
- **Implementation**: [UploadService.py](src/service/UploadService.py), [TextExtraction.py](src/ingestion/TextExtraction.py)

#### Text Knowledge Upload
- Direct text input with title and content
- Minimum validation (10 characters, 255 char title limit)
- Same processing pipeline as file uploads
- Immediate vector database indexing
- **API Endpoint**: `POST /api/admin/upload/text/{dept}`

#### Q&A Management
- Admin questions from user query deduplication
- Answer storage with vector indexing
- Status tracking (pending/processed)
- Department classification
- **Implementation**: [AdminRoutes.py](src/app/routes/AdminRoutes.py)

### 🔍 Question Processing & Deduplication

#### Automatic Question Summarization
- **Semantic Clustering**: Groups similar questions using cosine similarity
- **Similarity Threshold**: Configurable (default 0.4)
- **Deduplication**: Identifies and groups duplicate/similar questions
- **Representative Selection**: Chooses most representative question from each cluster
- **Admin Question Creation**: Converts clusters to admin questions for review
- **Detailed Analytics**: Provides similarity matrices and clustering statistics
- **Implementation**: [question_deduplicator.py](src/service/question_deduplicator.py), [QuestionFilter](src/admin/filter.py)

#### Question Summarizer
- Generates concise summaries for question clusters
- Uses LLM to create representative questions
- **API Endpoint**: `POST /api/admin/summarize`

### 📊 Analytics & Monitoring

#### Dashboard Statistics
- **Total Queries**: Count of all user questions
- **Admin Questions**: Pending and processed counts
- **Knowledge Base**: File and text knowledge counts
- **Department Distribution**: Query breakdown by department
- **Response Time Metrics**: Average response times with trends
- **Active Users**: Count of users with active conversations
- **Department Failures**: Misrouted query tracking
- **API Endpoint**: `GET /api/read/dashboard/stats`

#### Response Time Tracking
- Real-time response time measurement
- In-memory storage with periodic database persistence
- Hourly and daily average calculations
- Historical data with timestamps
- Trend analysis support
- **Implementation**: [avg_response_cal.py](src/admin/avg_response_cal.py), [response_time.py](src/models/response_time.py)

#### Department Failure Tracking
- Logs queries routed to wrong department
- Tracks detected vs expected department
- Status management (pending/accepted/discarded)
- Keyword improvement workflow
- Bulk update capabilities
- **API Endpoints**: 
  - `GET /api/read/departments/failures`
  - `PUT /api/admin/departments/failures`
  - `PUT /api/admin/departments/failures/discard`

### 🏢 Department Management

#### Dynamic Department Configuration
- Database-driven department definitions
- Custom descriptions for semantic routing
- Keyword management (add, update, delete)
- Department-specific metadata
- **Database Models**: [department.py](src/models/department.py), [dept_keyword.py](src/models/dept_keyword.py)

#### Department Keywords
- Custom keyword lists per department
- CRUD operations for keywords
- Real-time router data refresh
- Supports routing accuracy improvements
- **API Endpoints**:
  - `GET /api/read/departments/keywords`
  - `POST /api/admin/departments/keywords`
  - `PUT /api/admin/departments/keywords/{keyword_id}`
  - `DELETE /api/admin/departments/keywords/{keyword_id}`

#### Department Descriptions
- Semantic descriptions for embedding-based routing
- Update descriptions to improve routing
- Immediate router refresh on update
- **API Endpoints**:
  - `GET /api/read/departments/descriptions`
  - `PUT /api/admin/departments/{dept_name}`

### 🖥️ Admin Dashboard (React + TypeScript)

#### Pages & Features

1. **Dashboard** (`/`)
   - Real-time statistics overview
   - Query distribution charts
   - Response time trends
   - Active users count

2. **Upload** (`/upload`)
   - File upload interface (drag & drop, multi-select)
   - Text knowledge input form
   - Department selection
   - Upload progress tracking
   - Success/failure notifications

3. **Queries** (`/queries`)
   - User question browser
   - Filtering by department, date
   - Pagination support
   - Export capabilities

4. **Questions** (`/questions`)
   - Admin question management
   - Answer submission interface
   - Status filtering (pending/processed)
   - Search and filter options

5. **FAQs** (`/faqs`)
   - Knowledge base viewer
   - File and text knowledge lists
   - Edit/delete capabilities
   - Download uploaded files

6. **Department Management** (`/departments`)
   - Keyword management interface
   - Description editor
   - Failure review and correction
   - Router data refresh

7. **Admin Management** (`/admin`) - Super Admin Only
   - Admin account creation
   - Role assignment
   - Password reset
   - Account deletion

#### UI Components
- **Framework**: React 18 with TypeScript
- **UI Library**: Shadcn/ui (Radix UI components)
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11
- **Database**: PostgreSQL 14
- **ORM**: SQLAlchemy
- **Vector Store**: ChromaDB (persistent)
- **Authentication**: JWT (python-jose), bcrypt
- **LLM Integration**: 
  - Groq API (llama models)
  - Google Generative AI (Gemini)
  - Llama.cpp (local models)

### AI/ML
- **Embeddings**: SentenceTransformers
  - Primary: `all-MiniLM-L6-v2` (384 dimensions)
  - Deputy: `all-mpnet-base-v2` (768 dimensions)
- **LLM Providers**: Groq, Google AI, Local Llama
- **RAG Framework**: LangChain, LangChain Community
- **Vector Operations**: ChromaDB with cosine similarity

### Frontend
- **Framework**: React 18.3+
- **Language**: TypeScript 5
- **Build Tool**: Vite
- **UI Components**: Shadcn/ui (Radix UI)
- **Styling**: Tailwind CSS 3
- **State Management**: TanStack Query 5
- **Routing**: React Router 6
- **HTTP Client**: Fetch API with TanStack Query

### DevOps
- **Containerization**: Docker
- **WSGI Server**: Uvicorn
- **Environment Management**: python-dotenv
- **Version Control**: Git

---

## 🧩 System Components

### Core Modules

#### Inference Pipeline
- **Pipeline.py**: Main query processing orchestrator
- **HybridRouter.py**: Department routing with hybrid approach
- **ContextRetriever.py**: ChromaDB context retrieval
- **PromptGenerator.py**: Prompt augmentation with context
- **HistoryManager.py**: Conversation history management
- **EnhancedPipeline.py**: Extended pipeline with advanced features

#### LLM Clients (Modular Architecture)
- **LLMClient.py**: Base LLM client interface
- **LLMClientServer.py**: Production server client
- **LLMClientGoogle.py**: Google Gemini integration
- **LLMClientGemma.py**: Gemma model client
- **LLMClientllama.py**: Llama model client
- **LLMClientOpenAI.py**: OpenAI-compatible client
- **Llama3o1_8b.py**, **Llama3o2_3b.py**: Specific model clients

#### Ingestion Services
- **TextExtraction.py**: Document text extraction
- **TextCleaning.py**: Text preprocessing and normalization
- **TextChuncking.py**: Intelligent text chunking with overlap
- **VectorEmbedding.py**: Embedding generation and storage

#### Admin Services
- **UploadService.py**: File and text upload processing
- **question_deduplicator.py**: Question clustering and deduplication
- **question_summarizer.py**: Question summary generation
- **avg_response_cal.py**: Response time calculation

#### Database Models
- **admin.py**: Admin user model with roles
- **user_question.py**: User query records
- **admin_question.py**: Admin Q&A management
- **file_knowledge.py**: Uploaded file metadata
- **text_knowledge.py**: Text knowledge records
- **department.py**: Department definitions
- **dept_keyword.py**: Department keywords
- **dept_failure.py**: Routing failure logs
- **response_time.py**: Response time metrics

### API Routes

#### User Routes (`/api/user`)
- `POST /query` - Process user query
- `POST /department` - Get department for query (requires auth)
- `DELETE /history/{userid}` - Clear user conversation history

#### Admin Routes (`/api/admin`)
- `POST /upload/files/{dept}` - Upload files
- `POST /upload/text/{dept}` - Upload text knowledge
- `POST /summarize` - Summarize pending questions
- `POST /answer` - Answer admin question
- `DELETE /files/{file_id}` - Delete file
- `DELETE /text/{text_id}` - Delete text knowledge
- `PUT /text/{text_id}` - Update text knowledge
- `POST /departments/keywords` - Add keyword
- `PUT /departments/keywords/{keyword_id}` - Update keyword
- `DELETE /departments/keywords/{keyword_id}` - Delete keyword
- `PUT /departments/{dept_name}` - Update department description
- `PUT /departments/failures` - Update department failures
- `PUT /departments/failures/discard` - Discard department failures
- `DELETE /history/purge` - Purge old conversation history
- `POST /refresh-router-data` - Refresh router data from database

#### Read-Only Admin Routes (`/api/read`)
- `GET /avg-response-times` - Get response time statistics
- `PUT /changepassword` - Change own password
- `GET /getuserquestions` - Get user questions with pagination
- `GET /getadminquestions` - Get admin questions with pagination
- `GET /upload/text` - List text knowledge
- `GET /upload/list` - List uploaded files
- `GET /download/{file_id}` - Download file
- `GET /departments/keywords` - Get all keywords
- `GET /departments/descriptions` - Get department descriptions
- `GET /departments/failures` - Get department failures
- `GET /dashboard/stats` - Get dashboard statistics
- `GET /router-data-summary` - Get router configuration summary

#### Super Admin Routes (`/api/superadmin`)
- `DELETE /files/all` - Delete all files (requires confirmation)
- `DELETE /text/all` - Delete all text knowledge
- `DELETE /user-questions/all` - Delete all user questions
- `DELETE /admin-questions/all` - Delete all admin questions
- `DELETE /dept-failures/all` - Delete all department failures
- `DELETE /response-times/all` - Delete all response time records
- `POST /admin/create` - Create new admin
- `GET /admins` - List all admins
- `DELETE /admin/{admin_id}` - Delete admin
- `PUT /admin/{admin_id}` - Update admin details
- `PUT /admin/resetpassword/{admin_id}` - Reset admin password
- `DELETE /vector-db/purge` - Purge entire vector database

#### Auth Routes (`/api/auth`)
- `POST /signup` - User signup (with email verification)
- `GET /verify-email` - Verify email address
- `POST /resend-verification` - Resend verification email
- `POST /create/manual` - Manual admin creation (requires bypass key)
- `POST /login` - Admin login
- `GET /me` - Get current admin details

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (for frontend)
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd chatbot
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create PostgreSQL database**
```bash
psql -U postgres
CREATE DATABASE postgres;
\q
```

5. **Run database schema**
```bash
psql -U postgres -d postgres -f schema.sql
```

6. **Configure environment variables**
Create a `.env` file in the root directory:
```env
# API Keys
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

# Organization Settings
ORGANIZATION=Your Company Name
DUMMY_ORGANIZATION=Placeholder Company Name
DEPARTMENTS=HR,IT,Security,Finance
ORGANIZATION_DOMAIN=yourcompany.com

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
SECRET_PASSWORD=your-bypass-key-for-manual-admin-creation
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
POSTGRES=postgresql://postgres:password@localhost:5432/postgres

# Storage Paths
DOCUMENTS_PATH=./documents
CHROMADB_PATH=./chromadb
COLLECTION_NAME=YOUR-DOCS

# Email (Optional - for signup verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
BASE_URL=http://localhost:8000
```

7. **Initialize departments (optional)**
```bash
python -m src.utils.populate_departments
```

8. **Run the backend**
```bash
uvicorn src.app.index:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ui-admin
```

2. **Install dependencies**
```bash
npm install
# or with bun
bun install
```

3. **Configure API endpoint**
Create `.env` file in `ui-admin` directory:
```env
VITE_API_URL=http://localhost:8000
```

4. **Run development server**
```bash
npm run dev
# or with bun
bun run dev
```

5. **Build for production**
```bash
npm run build
# or with bun
bun run build
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM access | Required |
| `GOOGLE_API_KEY` | Google AI API key | Optional |
| `ORGANIZATION` | Your organization name | "Techmojo Solutions Pvt Ltd" |
| `DUMMY_ORGANIZATION` | Anonymization placeholder | "Panexus Solutions Pvt Ltd" |
| `DEPARTMENTS` | Comma-separated department list | "HR,IT,Security" |
| `ORGANIZATION_DOMAIN` | Organization domain | "techmojo.in" |
| `SECRET_KEY` | JWT secret key | Required (change in production) |
| `SECRET_PASSWORD` | Bypass key for manual admin creation | Required |
| `POSTGRES` | PostgreSQL connection URL | Required |
| `DOCUMENTS_PATH` | File storage path | "./documents" |
| `CHROMADB_PATH` | Vector DB storage path | "./chromadb" |
| `COLLECTION_NAME` | ChromaDB collection name | "TM-DOCS" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | 30 |

### Model Configuration

**Embedding Models** (Lazy loaded):
- Primary: `all-MiniLM-L6-v2` (Fast, 384 dimensions)
- Deputy: `all-mpnet-base-v2` (Higher quality, 768 dimensions)

**LLM Models** (Configurable):
- Default: Groq (llama-3.1-70b or similar)
- Alternative: Google Gemini
- Local: Llama.cpp models

### ChromaDB Configuration
- **Persistence**: Enabled by default
- **Path**: Configurable via `CHROMADB_PATH`
- **Collection**: Single collection per deployment
- **Metadata**: Department, source, file_id, knowledge_id

---

## 📚 API Documentation

### Complete API documentation is available in [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### Quick Reference

#### User Endpoints
```bash
# Query the chatbot
curl -X POST http://localhost:8000/api/user/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the leave policy?", "userid": "user123"}'

# Clear conversation history
curl -X DELETE http://localhost:8000/api/user/history/user123
```

#### Admin Endpoints (requires Bearer token)
```bash
# Upload a file
curl -X POST http://localhost:8000/api/admin/upload/files/HR \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf"

# Upload text knowledge
curl -X POST http://localhost:8000/api/admin/upload/text/IT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "VPN Setup", "text": "Steps to setup VPN..."}'

# Get dashboard statistics
curl -X GET http://localhost:8000/api/read/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "password"}'

# Get current admin info
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎨 Admin Dashboard

### Access the Dashboard

1. **Navigate to the UI**
```
http://localhost:5173
```

2. **Login with admin credentials**
- Email: Your admin email
- Password: Your admin password

### Dashboard Features

#### Dashboard Overview
- **Statistics Cards**: Total queries, admin questions, knowledge base size
- **Department Distribution**: Visual breakdown of queries by department
- **Response Time Chart**: Historical response time trends
- **Active Users**: Current active conversation count

#### File Management
- **Upload**: Drag & drop or click to upload multiple files
- **Department Selection**: Assign files to specific departments
- **Progress Tracking**: Real-time upload progress
- **File List**: View, download, or delete uploaded files

#### Question Management
- **User Questions**: Browse all user queries with filtering
- **Admin Questions**: Review and answer pending questions
- **Status Tracking**: Monitor processed vs pending questions
- **Search & Filter**: Find specific questions quickly

#### Department Configuration
- **Keywords**: Add, edit, or remove department keywords
- **Descriptions**: Update semantic descriptions for better routing
- **Failure Review**: Analyze and correct routing errors
- **Refresh Router**: Apply changes immediately

#### Admin Management (Super Admin)
- **Create Admins**: Add new admin accounts with role assignment
- **Manage Users**: View, edit, or delete admin accounts
- **Reset Passwords**: Force password resets for admins
- **Role Assignment**: Change admin roles

---

## 🗄️ Database Schema

### Tables Overview

#### Admins
- `id`: UUID primary key
- `name`: Admin name
- `email`: Unique email (username)
- `password`: Bcrypt hashed password
- `role`: Enum (read_only_admin, admin, super_admin)
- `created_at`, `updated_at`: Timestamps

#### User Questions
- `id`: UUID primary key
- `userid`: User identifier (session)
- `query`: User question text
- `answer`: Generated answer
- `context`: Retrieved context
- `dept`: Department enum
- `created_at`: Timestamp

#### Admin Questions
- `id`: UUID primary key
- `question`: Question text
- `answer`: Answer text (nullable)
- `dept`: Department enum
- `status`: Enum (pending, processed)
- `adminid`: Foreign key to admins
- `document_id`: ChromaDB document reference
- `created_at`, `updated_at`: Timestamps

#### File Knowledge
- `id`: UUID primary key
- `adminid`: Foreign key to admins
- `file_name`: Original filename
- `file_path`: Storage path
- `dept`: Department enum
- `created_at`, `updated_at`: Timestamps

#### Text Knowledge
- `id`: UUID primary key
- `adminid`: Foreign key to admins
- `title`: Text title
- `text`: Content
- `dept`: Department enum
- `created_at`, `updated_at`: Timestamps

#### Departments
- `id`: UUID primary key
- `name`: Department name (enum)
- `description`: Semantic description
- `created_at`, `updated_at`: Timestamps

#### Department Keywords
- `id`: UUID primary key
- `dept_id`: Foreign key to departments
- `keyword`: Keyword text
- `created_at`: Timestamp

#### Department Failures
- `id`: UUID primary key
- `query`: Misrouted question
- `detected`: Detected department
- `expected`: Correct department
- `status`: Enum (pending, accepted, discarded)
- `created_at`, `updated_at`: Timestamps

#### Response Times
- `id`: Serial primary key
- `timestamp`: Measurement timestamp
- `avg_response_time_1h`: 1-hour average (seconds)
- `avg_response_time_1d`: 1-day average (seconds)

---

## 👨‍💻 Development

### Project Structure
```
chatbot/
├── src/
│   ├── app/
│   │   ├── index.py                 # FastAPI application
│   │   └── routes/                  # API route handlers
│   │       ├── UserRoutes.py
│   │       ├── AdminRoutes.py
│   │       ├── ReadOnlyAdminRoutes.py
│   │       ├── SuperAdminRoutes.py
│   │       └── AdminAuthRoutes.py
│   ├── inference/                   # AI/ML pipeline
│   │   ├── Pipeline.py
│   │   ├── HybridRouter.py
│   │   ├── ContextRetriever.py
│   │   ├── HistoryManager.py
│   │   └── PromptGenerator.py
│   ├── ingestion/                   # Document processing
│   │   ├── TextExtraction.py
│   │   ├── TextCleaning.py
│   │   ├── TextChuncking.py
│   │   └── VectorEmbedding.py
│   ├── models/                      # Database models
│   ├── service/                     # Business logic
│   ├── utils/                       # Utilities & LLM clients
│   ├── admin/                       # Admin utilities
│   ├── dependencies/                # Auth dependencies
│   ├── middleware/                  # Middleware
│   └── config.py                    # Configuration
├── ui-admin/                        # React frontend
│   ├── src/
│   │   ├── pages/                   # Page components
│   │   ├── components/              # Reusable components
│   │   ├── contexts/                # React contexts
│   │   ├── hooks/                   # Custom hooks
│   │   └── utils/                   # Utilities
│   └── package.json
├── documents/                       # Uploaded files storage
├── chromadb/                        # Vector database storage
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── schema.sql                       # Database schema
└── README.md                        # This file
```

### Development Workflow

1. **Feature Development**
   - Create feature branch
   - Implement backend changes in `src/`
   - Add corresponding frontend UI in `ui-admin/`
   - Test API endpoints with FastAPI docs (`/docs`)

2. **Testing**
   - Unit tests for individual components
   - Integration tests for API endpoints
   - Frontend component testing
   - Manual testing via admin dashboard

3. **Database Changes**
   - Update SQLAlchemy models in `src/models/`
   - Create migration scripts if needed
   - Update `schema.sql` for fresh installations

4. **Code Quality**
   - Follow PEP 8 style guide for Python
   - Use TypeScript strict mode for frontend
   - Document all public functions
   - Add type hints to Python code

### Adding New Features

#### Adding a New Department
1. Update `.env` with new department
2. Add enum value to `src/models/user_question.py` (`DeptType`)
3. Run `populate_departments.py` to add to database
4. Add keywords and description via admin dashboard

#### Adding a New LLM Provider
1. Create new client in `src/utils/LLMClient*.py`
2. Implement base `LLMClient` interface
3. Update `Pipeline.py` to use new client
4. Add API keys to `.env`

#### Adding a New API Endpoint
1. Choose appropriate route file (`*Routes.py`)
2. Add function with `@router.{method}` decorator
3. Implement role-based auth with `Depends(require_*)`
4. Update API documentation
5. Add frontend integration in corresponding page

---

## 🚀 Deployment

### Docker Deployment

1. **Build the image**
```bash
docker build -t chatbot-api .
```

2. **Run the container**
```bash
docker run -d \
  --name chatbot \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/documents:/app/documents \
  -v $(pwd)/chromadb:/app/chromadb \
  chatbot-api
```

3. **Deploy frontend**
```bash
cd ui-admin
npm run build
# Deploy dist/ folder to static hosting (Vercel, Netlify, etc.)
```

### Production Considerations

#### Security
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS for all endpoints
- [ ] Configure CORS for production domains
- [ ] Set up rate limiting
- [ ] Implement IP whitelisting for admin routes
- [ ] Use secure PostgreSQL credentials
- [ ] Enable database connection pooling

#### Performance
- [ ] Use production WSGI server (Gunicorn with Uvicorn workers)
- [ ] Enable Redis for caching (optional)
- [ ] Configure CDN for frontend assets
- [ ] Optimize ChromaDB index size
- [ ] Set up database read replicas
- [ ] Implement request queuing for heavy loads

#### Monitoring
- [ ] Set up application logging (structured logs)
- [ ] Configure error tracking (Sentry, Rollbar)
- [ ] Monitor API response times
- [ ] Track database query performance
- [ ] Monitor vector database operations
- [ ] Set up health check endpoints
- [ ] Configure alerting for failures

#### Backup & Recovery
- [ ] Regular PostgreSQL backups
- [ ] ChromaDB snapshot backups
- [ ] Document storage backups
- [ ] Disaster recovery plan
- [ ] Test backup restoration

#### Scaling
- [ ] Horizontal scaling with load balancer
- [ ] Separate read/write database instances
- [ ] Distributed vector database (if needed)
- [ ] Message queue for async tasks (Celery)
- [ ] Microservices architecture (optional)

### Environment-Specific Configuration

#### Development
```env
DEBUG=True
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:5173
```

#### Staging
```env
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yourapp.com
```

#### Production
```env
DEBUG=False
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourapp.com
SENTRY_DSN=your-sentry-dsn
```

---

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors
```
Error: could not connect to PostgreSQL
```
**Solution**: Verify PostgreSQL is running and connection string is correct
```bash
psql -U postgres -c "SELECT 1"
```

#### ChromaDB Initialization Fails
```
Error: Failed to initialize ChromaDB
```
**Solution**: Check ChromaDB path permissions
```bash
chmod -R 755 ./chromadb
```

#### Model Loading Errors
```
Error: Failed to load primary model
```
**Solution**: Models are lazy-loaded. Clear cache and retry
```bash
rm -rf ~/.cache/huggingface
```

#### Token Expiration
```
Error: Token expired or invalid
```
**Solution**: Re-login to get new token. Adjust `ACCESS_TOKEN_EXPIRE_MINUTES` if needed.

#### File Upload Fails
```
Error: File too large
```
**Solution**: Check `max_file_size` in AdminRoutes.py (default 10MB)

### Debug Mode

Enable detailed logging:
```python
# In config.py
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

**Slow query responses**:
1. Check vector database size (may need indexing)
2. Monitor LLM API latency
3. Review context retrieval performance
4. Check database query optimization

**High memory usage**:
1. Reduce `max_turns` in HistoryManager
2. Clear old conversation history more frequently
3. Monitor embedding model memory usage

---

## 📝 API Endpoint Summary

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### User Operations (Public)
- `POST /api/user/query` - Submit query
- `DELETE /api/user/history/{userid}` - Clear history

### Read-Only Admin (Auth Required)
- `GET /api/read/*` - All read operations
- `PUT /api/read/changepassword` - Change own password

### Admin (Auth Required)
- All Read-Only endpoints
- `POST /api/admin/upload/*` - Upload operations
- `POST /api/admin/answer` - Answer questions
- `POST /api/admin/summarize` - Summarize questions
- `PUT /api/admin/text/*` - Update knowledge
- `DELETE /api/admin/files/*` - Delete files
- Department management endpoints

### Super Admin (Auth Required)
- All Admin endpoints
- `POST /api/superadmin/admin/create` - Create admin
- `DELETE /api/superadmin/*/all` - Bulk delete operations
- `PUT /api/superadmin/admin/*` - Admin management
- `DELETE /api/superadmin/vector-db/purge` - Purge vector DB

### Authentication
- `POST /api/auth/signup` - Register admin
- `POST /api/auth/login` - Admin login
- `POST /api/auth/create/manual` - Manual admin creation
- `GET /api/auth/me` - Get current admin

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
Follow the [Installation](#-installation) section for local setup.

### Code Standards
- Python: PEP 8, type hints, docstrings
- TypeScript: ESLint configuration
- Commit messages: Conventional commits format

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework
- **LangChain**: RAG framework and LLM abstractions
- **ChromaDB**: Efficient vector database
- **SentenceTransformers**: High-quality embeddings
- **Shadcn/ui**: Beautiful React components
- **Groq**: Fast LLM inference
- **PostgreSQL**: Robust relational database

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API info

---

<div align="center">

**Built with ❤️ by the Chatbot Development Team**

</div>
