
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("saint_joseph.urls")),
    path("admin/", admin.site.urls),

]
