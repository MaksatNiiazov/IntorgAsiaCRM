from django.urls import path
from client_app.views import *

urlpatterns = [
    path('unpacking/client/<int:pk>/', UnpackingClientView.as_view(), name='unpacking_client'),
    path('my/orders/', OrderListClientView.as_view(), name='my_orders'),
    path('my/order/<int:pk>/', OrderDetailClientView.as_view(), name='my_order'),

]
