# Todo App DevOps Assignment

This repository contains a multi-service todo application prepared for a DevOps CI/CD assignment.

The deployed web application is made of:

- React/Vite frontend
- Node.js/Express backend API
- PostgreSQL database
- Docker Compose local deployment

The original Python CLI/Tkinter todo app is still preserved in `src/todo_app` and `todo_app.py`, but it is not part of the Docker Compose deployment or web CI/CD pipeline.

## Architecture

The React frontend serves the browser UI and calls the backend through REST API endpoints. In Docker Compose, Nginx serves the built frontend and proxies `/api` requests to the backend service.

The Express backend owns all todo API routes and connects to PostgreSQL with the `pg` package. On startup, it creates the `todos` table automatically if it does not already exist.

PostgreSQL stores todo records in a named Docker volume so data persists across container restarts.

## Run With Docker Compose

From the repository root:

```bash
docker compose up --build
```

Open the app at:

```text
http://localhost
```

The backend is also exposed directly at:

```text
http://localhost:5000
```

## API Endpoints

### Health

```http
GET /api/health
```

Response:

```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### Todos

```http
GET /api/todos
POST /api/todos
PUT /api/todos/:id
DELETE /api/todos/:id
```

Create request body:

```json
{
  "title": "some todo"
}
```

Update request body:

```json
{
  "title": "updated title",
  "completed": true
}
```

## Local Development Without Docker

Start PostgreSQL locally or through Docker, then configure the backend environment using `backend/.env.example`.

Backend:

```bash
cd backend
npm install
npm start
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

For local Vite development, `VITE_API_URL` should point to the backend:

```text
VITE_API_URL=http://localhost:5000
```

## Testing And Linting

Backend:

```bash
cd backend
npm test
npm run lint
```

Frontend:

```bash
cd frontend
npm run build
npm run lint
```

## DevOps Purpose

This structure supports a basic CI/CD workflow where the frontend and backend can be linted, tested, built, containerized, and deployed as separate services with PostgreSQL as the database layer.
