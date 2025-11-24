# Backend - Portfolio API

## Overview
This Django + Django REST Framework backend powers a portfolio application exposing Profiles, Skills, Projects, and Media assets. It provides session and token-based authentication, browsable API, filtering, pagination, and auto-generated API documentation via Swagger UI and Redoc.

## Environment Variables
The backend runs with sane defaults for local development. You may override these via environment variables:

- DJANGO_DEBUG: Set to "True" or "False" (default: True).
- DJANGO_SECRET_KEY: Secret key; defaults to a development key in settings.py. Provide a secure value in production.
- DJANGO_ALLOWED_HOSTS: Comma-separated hostnames (default in settings.py includes localhost, 127.0.0.1, testserver and .kavia.ai).
- DATABASE_URL: Not currently used; project defaults to SQLite (db.sqlite3). For production, configure DATABASES accordingly in settings or via a settings override.
- PORT: Optional; when using runserver you can bind to your desired port (example below uses 3001).

Static/Media:
- MEDIA_URL: /media/ (configured)
- MEDIA_ROOT: <project>/backend/media (auto-created by Django when files are uploaded in DEBUG)

Note: The current settings.py includes:
- REST authentication: SessionAuthentication and TokenAuthentication
- CORS_ALLOW_ALL_ORIGINS=True (development convenience)
- X_FRAME_OPTIONS='ALLOWALL' (documentation viewing convenience)

## Setup
1) Create and activate a virtual environment, then install dependencies:
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt

2) Apply migrations:
   python manage.py makemigrations
   python manage.py migrate

3) Create a superuser (optional but recommended for admin access):
   python manage.py createsuperuser

4) Seed demo data (creates user demo with password demo1234 and example content):
   python manage.py seed_data

5) Run the development server:
   python manage.py runserver 0.0.0.0:3001

Project root for backend:
- professional-portfolio-showcase-45999-46008/backend

## Admin Access
- Django admin: /admin/
- Login using your superuser created via createsuperuser.
- You will see and can manage Profiles, Skills, Projects, and Media Assets with inline relations for convenience.

## Authentication
- Session Authentication: Works with the DRF browsable API in your browser once you log into /admin/ or a session-based login.
- Token Authentication endpoint: POST /api/auth/token/
  Use with header: Authorization: Token <token>

Example to obtain a token:
curl -X POST http://localhost:3001/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'

Example request with token:
curl http://localhost:3001/api/projects/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

## API Base and Health
- API base path: /api/
- Health endpoint: GET /api/health/ returns {"message": "Server is up!"}

Example:
curl http://localhost:3001/api/health/

## API Endpoints
Router-registered viewsets under /api/:
- Profiles: /api/profiles/
  - Methods: GET list/retrieve for public; authenticated users can create/update their profile.
  - Search fields: display_name, title, bio, location
- Skills: /api/skills/
  - Methods: GET list/retrieve; authenticated users can create/update.
  - Query params: owner=<user_id> (optional)
  - Search fields: name, category, description; order by: name, proficiency, created_at
- Projects: /api/projects/
  - Methods: GET list/retrieve (public projects by default); authenticated owners can create/update their own.
  - Query params:
    - mine=1 to list your own (requires auth)
    - owner=<user_id>
    - skill=<skill name exact>
    - q=<search query for title/description>
  - Custom actions:
    - /api/projects/featured/ (GET)
    - /api/projects/public/ (GET)
  - Order by: created_at, updated_at, title
  - Media uploads supported via multipart form data for create/update using write-optimized serializer.
- Media assets: /api/media/
  - Methods: GET/POST/PUT/PATCH/DELETE; query param project=<project_id>
  - Orders by: order

Authentication endpoints:
- Token: POST /api/auth/token/

## Example curl Requests

- List public projects:
curl http://localhost:3001/api/projects/

- List featured projects:
curl http://localhost:3001/api/projects/featured/

- List my projects (requires token):
curl "http://localhost:3001/api/projects/?mine=1" \
  -H "Authorization: Token YOUR_TOKEN_HERE"

- Filter projects by owner and search:
curl "http://localhost:3001/api/projects/?owner=1&q=api"

- Create a skill (requires token):
curl -X POST http://localhost:3001/api/skills/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Docker","category":"DevOps","proficiency":75,"description":"Containers"}'

- Create a project with skills (JSON body, requires token):
curl -X POST http://localhost:3001/api/projects/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "My New Project",
        "description": "Short description",
        "live_url": "https://example.com",
        "source_url": "https://github.com/me/project",
        "is_published": true,
        "featured": false,
        "skills": [
          {"skill_id": 1, "role": "Backend", "weight": 10},
          {"skill_id": 2, "role": "API", "weight": 8}
        ]
      }'

- Upload a media asset for a project (multipart, requires token):
curl -X POST http://localhost:3001/api/media/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -F "project=<project_id>" \
  -F "type=image" \
  -F "file=@/path/to/image.png" \
  -F "caption=Cover" \
  -F "alt_text=Alt" \
  -F "order=0"

- List skills with ordering and search:
curl "http://localhost:3001/api/skills/?search=python&ordering=-proficiency"

## API Documentation
- Swagger UI: /docs
- Redoc: /redoc
- Raw OpenAPI JSON: /swagger.json

Notes:
- The documentation base URL dynamically respects forwarded scheme/host/port in reverse proxy setups.
- If running on a non-default port locally (e.g., 3001), access: http://localhost:3001/docs and http://localhost:3001/redoc

## Media Files in Development
When DEBUG=True, Django serves uploaded files from MEDIA_ROOT at MEDIA_URL. This is convenient for local development and testing image/file uploads associated with projects and skills.

## Testing
A basic health endpoint test exists. To run tests:
   python -m pytest
or using Django’s test runner:
   python manage.py test

## Tech Stack
- Django 5.2, Django REST Framework, drf-yasg for API docs, django-cors-headers
- SQLite for local dev
- Token and Session authentication
