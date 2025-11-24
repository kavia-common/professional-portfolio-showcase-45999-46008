from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from api.models import Profile, Skill, Project, ProjectSkill, MediaAsset

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with a demo user, skills, projects, and media."

    def handle(self, *args, **options):
        # Create demo user
        user, created = User.objects.get_or_create(username="demo")
        if created:
            user.set_password("demo1234")  # For local dev only
            user.email = "demo@example.com"
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user 'demo' with password 'demo1234'"))
        else:
            self.stdout.write("Demo user already exists")

        # Create profile
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                "display_name": "Demo User",
                "title": "Software Engineer",
                "bio": "Passionate about building clean APIs and delightful UIs.",
                "location": "Remote",
                "website": "https://example.com",
                "github": "https://github.com/demo",
                "linkedin": "https://linkedin.com/in/demo",
                "twitter": "https://twitter.com/demo",
            },
        )

        # Create skills
        skills_data = [
            ("Python", "Programming", 90),
            ("Django", "Framework", 85),
            ("REST", "API", 80),
            ("React", "Frontend", 70),
        ]
        skills = []
        for name, category, prof in skills_data:
            s, _ = Skill.objects.get_or_create(
                owner=user, name=name, defaults={"category": category, "proficiency": prof}
            )
            skills.append(s)

        # Create project
        project, _ = Project.objects.get_or_create(
            owner=user,
            title="Portfolio API",
            defaults={
                "description": "A modern portfolio backend built with Django REST Framework.",
                "live_url": "https://example.com/portfolio",
                "source_url": "https://github.com/demo/portfolio",
                "featured": True,
                "is_published": True,
            },
        )

        # Link skills to project
        ProjectSkill.objects.get_or_create(project=project, skill=skills[0], defaults={"role": "Backend", "weight": 10})
        ProjectSkill.objects.get_or_create(project=project, skill=skills[1], defaults={"role": "Web", "weight": 9})
        ProjectSkill.objects.get_or_create(project=project, skill=skills[2], defaults={"role": "API", "weight": 8})

        # Add placeholder media
        placeholder_png = ContentFile(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"  # just a tiny header to act like a file; not a valid image
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01E\x9c\xd9r"
            b"\x00\x00\x00\x00IEND\xaeB`\x82",
            name="placeholder.png",
        )
        MediaAsset.objects.get_or_create(
            project=project, type=MediaAsset.IMAGE, defaults={"file": placeholder_png, "caption": "Cover", "order": 0}
        )

        self.stdout.write(self.style.SUCCESS("Seed data created or updated successfully."))
