from typing import List, Dict, Any
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile, Skill, Project, ProjectSkill, MediaAsset

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ["id", "type", "file", "caption", "alt_text", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SkillSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Skill
        fields = ["id", "name", "category", "proficiency", "description", "icon", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "display_name",
            "title",
            "bio",
            "location",
            "website",
            "github",
            "linkedin",
            "twitter",
            "profile_image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ProjectSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        source="skill", queryset=Skill.objects.all(), write_only=True
    )

    class Meta:
        model = ProjectSkill
        fields = ["skill", "skill_id", "role", "weight"]


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    media = MediaAssetSerializer(many=True, read_only=True)
    skills = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)

    def get_skills(self, obj):
        # Return a simplified list of linked skills with role and weight
        items = []
        for ps in obj.project_skills.select_related("skill").all():
            items.append(
                {
                    "id": ps.skill.id,
                    "name": ps.skill.name,
                    "category": ps.skill.category,
                    "proficiency": ps.skill.proficiency,
                    "role": ps.role,
                    "weight": ps.weight,
                }
            )
        return items

    class Meta:
        model = Project
        fields = [
            "id",
            "owner",
            "title",
            "slug",
            "description",
            "live_url",
            "source_url",
            "is_published",
            "featured",
            "started_on",
            "completed_on",
            "media",
            "skills",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "slug", "created_at", "updated_at"]


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write-optimized serializer allowing nested create/update for skills and media.
    For performance, expects IDs and simple payloads rather than full nested models.
    """
    # For skills, expect list of dicts: [{ "skill_id": <id>, "role": "...", "weight": 10 }]
    skills = serializers.ListField(child=serializers.DictField(), required=False)
    # For media, expect list of dicts: [{ "id": optional, "type": "image", "file": <InMemoryUpload>, "caption": "...", "alt_text": "...", "order": 1 }]
    media = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "live_url",
            "source_url",
            "is_published",
            "featured",
            "started_on",
            "completed_on",
            "skills",
            "media",
        ]

    def validate_skills(self, value: List[Dict[str, Any]]):
        for item in value:
            if "skill_id" not in item:
                raise serializers.ValidationError("Each skill entry must include 'skill_id'.")
        return value

    def create(self, validated_data):
        skills_data = validated_data.pop("skills", [])
        media_data = validated_data.pop("media", [])
        request = self.context.get("request")
        owner = getattr(request, "user", None)
        project = Project.objects.create(owner=owner, **validated_data)

        self._upsert_skills(project, skills_data)
        self._upsert_media(project, media_data, is_create=True)
        return project

    def update(self, instance, validated_data):
        skills_data = validated_data.pop("skills", None)
        media_data = validated_data.pop("media", None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if skills_data is not None:
            # replace entire skill set for clarity
            instance.project_skills.all().delete()
            self._upsert_skills(instance, skills_data)

        if media_data is not None:
            # simplistic approach: clear and recreate for ordered lists
            instance.media.all().delete()
            self._upsert_media(instance, media_data, is_create=False)

        return instance

    def _upsert_skills(self, project: Project, skills_data: List[Dict[str, Any]]):
        for item in skills_data:
            skill = Skill.objects.get(pk=item["skill_id"])
            ProjectSkill.objects.create(
                project=project,
                skill=skill,
                role=item.get("role", ""),
                weight=item.get("weight", 0),
            )

    def _upsert_media(self, project: Project, media_data: List[Dict[str, Any]], is_create: bool):
        # Only create new MediaAssets from the provided list
        for idx, item in enumerate(media_data):
            MediaAsset.objects.create(
                project=project,
                type=item.get("type", MediaAsset.IMAGE),
                file=item.get("file"),
                caption=item.get("caption", ""),
                alt_text=item.get("alt_text", ""),
                order=item.get("order", idx),
            )
