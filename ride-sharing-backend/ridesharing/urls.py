"""
URL configuration for ridesharing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from riders.views import RiderViewSet
from drivers.views import DriverViewSet
from rides.views import RideViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", obtain_auth_token, name="api_token"),
    path("api/riders/", RiderViewSet.as_view({"post": "create", "get": "list"})),
    path("api/drivers/", DriverViewSet.as_view({"post": "create", "get": "list"})),
    path("api/request-ride/", RideViewSet.as_view({"post": "create"})),
    path("api/ride-status/<int:pk>/", RideViewSet.as_view({"get": "retrieve"})),


    
    path(
        "api/register/", RiderViewSet.as_view({"post": "create"}), name="user-register"
    ),
    path(
        "api/rides/",
        RideViewSet.as_view({"get": "list", "post": "create"}),
        name="ride-list",
    ),
    path(
        "api/rides/<int:pk>/",
        RideViewSet.as_view({"get": "retrieve"}),
        name="ride-detail",
    ),
    path(
        "api/rides/<int:pk>/cancel/",
        RideViewSet.as_view({"post": "cancel"}),
        name="ride-cancel",
    ),
]
