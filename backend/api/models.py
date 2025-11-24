from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """Abstract model providing created and updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    """
    Represents a user's public portfolio profile.
    One-to-one with Django's User model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.display_name} ({self.user.username})"


class Skill(TimeStampedModel):
    """
    A skill that can be linked to projects or shown on a profile.
    """
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=120, blank=True)
    proficiency = models.PositiveSmallIntegerField(default=0, help_text="0-100 scale")
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="skills/", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Project(TimeStampedModel):
    """
    A portfolio project.
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True, blank=True)
    description = models.TextField(blank=True)
    live_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    started_on = models.DateField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner", "featured"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:50] or "project"
            candidate = base
            idx = 1
            while Project.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                idx += 1
                candidate = f"{base}-{idx}"
                if len(candidate) > 220:
                    candidate = f"{base[:200]}-{idx}"
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class ProjectSkill(models.Model):
    """
    Through model connecting Project and Skill with optional role/weight.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skill_projects")
    role = models.CharField(max_length=120, blank=True)
    weight = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("project", "skill")
        ordering = ["-weight", "skill__name"]

    def __str__(self) -> str:
        return f"{self.project.title} - {self.skill.name}"


def media_upload_path(instance, filename):
    return f"projects/{instance.project.slug}/{filename}"


class MediaAsset(TimeStampedModel):
    """
    An uploaded media asset related to a project. Could be image, video, or file.
    """
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    TYPE_CHOICES = (
        (IMAGE, "Image"),
        (VIDEO, "Video"),
        (FILE, "File"),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="media")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=IMAGE)
    file = models.FileField(upload_to=media_upload_path)
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.type} for {self.project.title}"
