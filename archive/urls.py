from django.contrib import admin
from django.urls import path, include
from saint_joseph.views import user_login

urlpatterns = [
    path("", include("saint_joseph.urls")),
    path("admin/", admin.site.urls),
    path("login/", user_login, name="login"),
]
