# SmartBudget API

Backend for SmartBudget application built with FastAPI, PostgreSQL and Docker.

---

## 📦 Project Structure

```text
backend/
  app/
    api/             # API endpoints (routers)
    core/            # Config, logging, i18n, dependencies
    db/              # Database setup
    models/          # SQLAlchemy models
    repositories/    # Data access layer
    schemas/         # Pydantic schemas
    static/          # CSS, JS
    templates/       # HTML (Jinja2)
    main.py          # FastAPI entrypoint
  alembic/           # Migrations
  tests/             # Tests
  uploads/           # Stored files (local storage)
  docs/              # Dev notes
  .env*              # Environment configs
  docker-compose.yml
  requirements.txt
  alembic.ini
```

## 🚀 Features

### Feedback system
- Multiple message types:
  - Site issue
  - General question
  - Product feedback
- Purchase verification for product feedback
- Dynamic form behavior on frontend

### Attachments
- Multiple file upload (max 5 files)
- Drag & drop support
- File picker fallback
- Client-side validation (file type)
- Server-side validation:
  - file type
  - file size (max 20 MB)
  - max files count
- Files stored locally with unique names
- Metadata stored in database

### Internationalization
- English / Russian UI support

---

## 🛠 Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Vanilla JS (frontend)

---

## ⚙️ Environment

Environment variables are configured via:

- `.env`
- `.env.dev`
- `.env.prod`
- `.env.example`

## Key variables:
```text
DATABASE_URL=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
SECRET_KEY=
UPLOAD_DIR=uploads
```

## ▶️ Run locally

```bash
docker-compose up -d
```
```bash
docker-compose down
```
or
```bash
uvicorn app.main:app --reload
```

🔐 Validation rules
```text
Files Allowed:
.png
.jpg
.jpeg
.webp
.pdf
Max size: 20 MB per file
Max files: 5
```

📁 Storage

Current implementation:

Local disk (/uploads)
Unique filenames (UUID)

Future improvement:

S3-compatible storage (scalable & production-ready)
🧪 API
Create feedback

POST /v1/feedback

multipart/form-data
supports attachments
Check purchase

POST /v1/check-purchase

💡 Notes
Backend is designed with layered architecture (router → service → repository)
File handling is isolated and ready for migration to cloud storage