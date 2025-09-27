# Chatbot Admin UI

A professional admin console for managing AI chatbot systems, built with React, TypeScript, and Tailwind CSS.

## Features

### 🔐 Authentication
- Secure JWT-based login system
- Protected routes with automatic token refresh
- Professional login interface with hero background

### 📊 Dashboard
- Real-time statistics and metrics
- System status monitoring
- Recent activity feed
- Beautiful stats cards with animations

### 📤 Upload Management
- File upload support (PDF, DOCX, TXT, MD)
- Text content addition via rich editor
- Department-based organization (HR, IT, Security)
- File and text content browser with filtering

### 💬 Query Management
- Pending questions requiring admin response
- Answered questions archive
- Department and status filtering
- Answer submission with rich text editor

### ❓ Questions Overview
- User and admin question browsing  
- Advanced filtering and pagination
- Status tracking and management
- Export and analysis capabilities

### 🗄️ Database Management
- Database status monitoring
- Vector database purge operations
- Complete data purge with safety confirmations
- Record count statistics

### 🤖 Built-in Chatbot Tester
- Floating action button for easy access
- Real-time chat interface
- "Test in Chat" buttons throughout the interface
- Message history and session management

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: shadcn/ui with custom variants
- **State Management**: React Context + Hooks
- **API Client**: Custom TypeScript client with error handling
- **Icons**: Lucide React
- **Routing**: React Router 6

## API Integration

The frontend integrates with a FastAPI backend providing:

- **Authentication**: JWT-based login/logout
- **File Management**: Upload and manage knowledge base files
- **Query Processing**: Handle user questions and admin responses
- **Database Operations**: Monitor and maintain data integrity
- **Vector Search**: AI-powered question answering

## Design System

### Colors & Gradients
- **Primary**: Professional blue (#4F46E5)
- **Accent**: Purple accent (#8B5CF6) 
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Destructive**: Red (#EF4444)

### Components
- Custom button variants with gradients
- Animated cards with hover effects
- Professional form controls
- Status badges and indicators

### Animations
- Smooth transitions and micro-interactions
- Loading states and skeleton loaders
- Hover effects and scale transforms
- Gradient animations

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables
Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
```

### Backend Connection
The frontend expects a FastAPI backend running on `http://localhost:8000` (configurable via `VITE_API_URL`).

Key endpoints:
- `POST /api/auth/login` - User authentication  
- `GET /api/auth/me` - Get current user info
- `POST /api/user/query/` - Send chatbot queries
- `GET /api/admin/getuserquestions` - Fetch user questions
- `POST /api/admin/upload/files/batch/{dept}` - Upload files
- `POST /api/admin/answer` - Answer admin questions

## Production Deployment

### Build
```bash
npm run build
```

### Environment Setup
- Configure `VITE_API_URL` to point to production API
- Ensure CORS is properly configured on the backend
- Set up HTTPS for secure authentication

### Deployment Options
- **Static Hosting**: Netlify, Vercel, AWS S3
- **Server Deployment**: Nginx, Apache
- **Containerization**: Docker with multi-stage builds

## Security Features

- JWT token validation and automatic refresh
- Protected API endpoints with Bearer authentication  
- Input validation and sanitization
- Secure password handling
- CORS configuration for cross-origin requests

## Browser Support

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.