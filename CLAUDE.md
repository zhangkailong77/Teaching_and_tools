# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an educational technology platform with a Vue 3 frontend and FastAPI backend. The system supports role-based access for teachers and students with comprehensive homework management, course organization, and content delivery features.

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async capabilities
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT-based with role validation (student/teacher)
- **Security**: BCrypt password hashing, JWT tokens
- **Structure**:
  - `app/api/v1/endpoints/` - API route handlers
  - `app/models/` - SQLAlchemy database models
  - `app/schemas/` - Pydantic validation schemas
  - `app/core/` - Configuration and security
  - `app/db/` - Database session management

### Frontend (Vue 3)
- **Framework**: Vue 3 with Composition API and TypeScript
- **Build Tool**: Vite
- **UI Library**: Element Plus
- **State Management**: Pinia
- **Routing**: Vue Router with role-based routes
- **Structure**:
  - `src/views/dashboard/student/` - Student-specific pages
  - `src/views/dashboard/teacher/` - Teacher-specific pages
  - `src/api/` - API service layer
  - `src/components/` - Reusable Vue components
  - `src/stores/` - Pinia state management

## Key Features

### Homework Management System
- Students can submit assignments with rich text content and images
- Teachers can grade submissions with annotations, scoring, and feedback
- Supports detailed content review with highlighting and comments

### Course Management
- Role-based course organization
- Teacher-student enrollment system
- Content delivery with various file types (PDF, PPTX)

## Development Commands

### Backend
```bash
# Start backend server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
pip install -r requirements.txt
```

### Frontend
```bash
# Start frontend development server
cd frontend
npm install
npm run dev

# Build for production
npm run build
```

## Environment Configuration

### Backend (.env)
- `DATABASE_URL`: MySQL connection string
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend (.env.development)
- `VITE_API_URL`: Backend API URL (typically http://localhost:8000)
- `VITE_IMAGE_BASE_URL`: Base URL for image assets

## Critical Files

### Backend
- `backend/app/main.py` - Application entry point
- `backend/app/api/v1/endpoints/homework.py` - Homework management API
- `backend/app/api/v1/endpoints/auth.py` - Authentication endpoints
- `backend/app/models/user.py` - User model with role-based access

### Frontend
- `frontend/src/App.vue` - Root application component
- `frontend/src/router/index.ts` - Route configuration
- `frontend/src/components/HomeworkDrawer.vue` - Homework submission/review component
- `frontend/src/views/dashboard/teacher/homeworksGrading.vue` - Teacher homework grading interface
- `frontend/src/api/` - API service definitions
- `frontend/src/stores/modules/user.ts` - User state management

## Recent Development Focus

Recent changes have focused on:
- Teacher-side homework publishing and grading functionality
- Student-side homework center with grade display
- Annotation and commenting features for homework review
- Enhanced homework drawer component with improved functionality