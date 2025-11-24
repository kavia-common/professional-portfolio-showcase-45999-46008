from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ProfileSerializer,
    SkillSerializer,
    ProjectSerializer,
    ProjectCreateUpdateSerializer,
    MediaAssetSerializer,
)


@api_view(['GET'])
def health(request):
    """Health endpoint returning simple status."""
    return Response({"message": "Server is up!"})


class DefaultPermissionMixin:
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class ProfileViewSet(DefaultPermissionMixin, viewsets.ModelViewSet):
    """
    PUBLIC_INTERFACE
    """
    serializer_class = ProfileSerializer
    queryset = ProfileSerializer.Meta.model.objects.select_related("user").all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["display_name", "title", "bio", "location"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SkillViewSet(DefaultPermissionMixin, viewsets.ModelViewSet):
    """
    PUBLIC_INTERFACE
    """
    serializer_class = SkillSerializer
    queryset = SkillSerializer.Meta.model.objects.select_related("owner").all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "category", "description"]
    ordering_fields = ["name", "proficiency", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        qs = super().get_queryset()
        # Optional owner filter
        owner = self.request.query_params.get("owner")
        if owner:
            qs = qs.filter(owner_id=owner)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectViewSet(DefaultPermissionMixin, viewsets.ModelViewSet):
    """
    PUBLIC_INTERFACE
    Provides list/retrieve with nested media and skills. Uses a write-optimized
    serializer for create/update operations.
    """
    queryset = ProjectSerializer.Meta.model.objects.select_related("owner").prefetch_related("media", "project_skills__skill")
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "slug"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        # Allow unauthenticated reads; owner required for writes
        if self.action in ["list", "retrieve", "public", "featured"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProjectCreateUpdateSerializer
        return ProjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Public filter by default unless viewing own
        if self.request.user.is_authenticated and self.request.query_params.get("mine") == "1":
            qs = qs.filter(owner=self.request.user)
        else:
            qs = qs.filter(is_published=True)
        # Optional filtering
        owner = self.request.query_params.get("owner")
        if owner:
            qs = qs.filter(owner_id=owner)
        skill = self.request.query_params.get("skill")
        if skill:
            qs = qs.filter(project_skills__skill__name__iexact=skill)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        qs = self.get_queryset().filter(featured=True)
        page = self.paginate_queryset(qs)
        serializer = ProjectSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def public(self, request):
        qs = self.get_queryset().filter(is_published=True)
        page = self.paginate_queryset(qs)
        serializer = ProjectSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class MediaAssetViewSet(DefaultPermissionMixin, viewsets.ModelViewSet):
    """
    PUBLIC_INTERFACE
    """
    serializer_class = MediaAssetSerializer
    queryset = MediaAssetSerializer.Meta.model.objects.select_related("project", "project__owner").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["order", "created_at", "updated_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if not self.request.user.is_authenticated:
            qs = qs.filter(project__is_published=True)
        return qs

    def perform_create(self, serializer):
        serializer.save()
