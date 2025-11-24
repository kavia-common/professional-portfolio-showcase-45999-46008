# Backend - Portfolio API

Key features:
- Django + DRF with Session and Token auth (/api/auth/token/)
- Models: Profile, Skill, Project, ProjectSkill, MediaAsset
- Nested read serializers and write-optimized ProjectCreateUpdateSerializer
- ViewSets with search/order filters and ownership permission
- Router-based URLs and health endpoint at /api/health/
- Swagger docs at /docs and Redoc at /redoc
- Media upload support (MEDIA_URL=/media/)
- Seed data command

Quick start:
1) Apply migrations:
   python manage.py makemigrations
   python manage.py migrate

2) Seed demo data (creates demo/demo1234):
   python manage.py seed_data

3) Run server:
   python manage.py runserver 0.0.0.0:3001

4) Explore:
   - /docs
   - /api/health/
   - /api/projects/
   - /api/auth/token/ (POST username, password) to get token

Notes:
- Use SessionAuthentication in browser. For API clients, use TokenAuthentication: Authorization: Token <token>.
- In DEBUG, media files are served by Django from MEDIA_ROOT.
