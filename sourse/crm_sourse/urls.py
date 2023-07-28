from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('crm_app.urls')),
    path("", include('users.urls')),
    path("", include('crm_warehouse.urls')),
    path("", include('client_app.urls')),

]
