"""
URL configuration for gridflow_cloud_backend project.
"""
from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from devices.views import DeviceViewSet
from organizations.views import OrganizationViewSet
from users.views import UserViewSet
from .views import dashboard_view

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"devices", DeviceViewSet, basename="device")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", dashboard_view, name="dashboard-template"),
    path("api/", include(router.urls)),
    path("api/", include("telemetry.urls")),
    path("api/integrations/", include("integrations.urls")),
]
