from django.contrib import admin

from .models import Profile, Skill, Project, ProjectSkill, MediaAsset


class MediaInline(admin.TabularInline):
    model = MediaAsset
    extra = 0


class ProjectSkillInline(admin.TabularInline):
    model = ProjectSkill
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "title", "location", "website", "created_at")
    search_fields = ("display_name", "title", "bio", "location", "user__username")
    list_filter = ("created_at",)
    autocomplete_fields = ("user",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "owner", "created_at")
    search_fields = ("name", "category", "description", "owner__username")
    list_filter = ("category", "proficiency", "created_at")
    autocomplete_fields = ("owner",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "slug", "featured", "is_published", "created_at")
    list_editable = ("featured", "is_published")
    search_fields = ("title", "description", "slug", "owner__username")
    list_filter = ("featured", "is_published", "created_at", "updated_at")
    readonly_fields = ("slug",)
    inlines = [ProjectSkillInline, MediaInline]
    autocomplete_fields = ("owner",)


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("project", "type", "order", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("project__title", "caption", "alt_text")
    autocomplete_fields = ("project",)
