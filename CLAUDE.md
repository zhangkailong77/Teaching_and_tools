# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Educational technology platform with Vue 3 frontend and FastAPI backend. Role-based access (teacher/student) with homework management, course organization, and content delivery.

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async SQLAlchemy
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT with role validation
- **Caching**: Redis for course chapters and teacher data
- **Key Directories**:
  - `app/api/v1/endpoints/` - API routes
  - `app/models/` - SQLAlchemy models
  - `app/schemas/` - Pydantic schemas
  - `app/core/` - Config, security, Redis

### Frontend (Vue 3)
- **Framework**: Vue 3 Composition API + TypeScript
- **Build**: Vite
- **UI**: Element Plus
- **State**: Pinia
- **Key Directories**:
  - `src/views/dashboard/student/` - Student pages
  - `src/views/dashboard/teacher/` - Teacher pages
  - `src/api/` - API service layer
  - `src/stores/` - Pinia stores

## Development Commands

### Backend (Local)
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Local)
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker logs -f teaching-backend

# Restart service
docker restart teaching-backend
```

### Admin Scripts (after deployment)
```bash
# Create teacher with course access
docker exec -it teaching-backend python /app/create_teacher.py

# Create student
docker exec -it teaching-backend python /app/create_user.py

# Re-import course content
docker exec -it teaching-backend python /app/import_course.py
```

## Environment Configuration

### Backend (.env)
- `DATABASE_URL`: MySQL connection string
- `SECRET_KEY`: JWT secret
- `REDIS_HOST`, `REDIS_PORT`: Redis config

### Frontend (.env.development)
- `VITE_API_URL`: Backend URL (http://localhost:8000)

## Key API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/content/courses/me` | All courses + is_locked (for resource library) |
| `GET /api/v1/content/courses/available` | Only authorized courses (for class creation) |
| `GET /api/v1/content/courses/{id}/chapters` | Course chapters (cached 5 min) |

## Important Notes

- Course chapters use Redis caching (5 min). Run `import_course.py` clears cache automatically.
- `TeacherCourseAccess` table controls which courses a teacher can access.
- Use `encode_id()`/`decode_id()` for public-facing course IDs.
