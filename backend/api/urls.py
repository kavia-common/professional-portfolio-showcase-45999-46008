from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import health, ProfileViewSet, SkillViewSet, ProjectViewSet, MediaAssetViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profiles")
router.register(r"skills", SkillViewSet, basename="skills")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"media", MediaAssetViewSet, basename="media")

urlpatterns = [
    path("health/", health, name="Health"),
    path("", include(router.urls)),
    path("auth/token/", obtain_auth_token, name="api_token_auth"),
]
