from django.urls import path, include

from users.views import activate, RegisterView, RegisterWorkerView, CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('register/', RegisterView.as_view(), name='register'),
    path('register-worker/', RegisterWorkerView.as_view(), name='register_worker'),
    path('activate/<str:uidb64>/<str:token>/', activate, name='activate'),

]
