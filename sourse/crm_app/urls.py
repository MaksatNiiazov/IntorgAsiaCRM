from django.urls import path
from crm_app.views import *

urlpatterns = [
    path('statistic/', StatisticView.as_view(), name='statistic_page'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:order_id>/add/service/', OrderServiceCreateView.as_view(), name='add_service'),
    path('order/<int:pk>/delete/service/', OrderServiceDeleteView.as_view(), name='delete_service'),

    path('services/', ServiceListView.as_view(), name='service_list'),
    path('service/create/', ServiceCreateView.as_view(), name='service_create'),
    path('service-type/create/', ServiceTypeCreateView.as_view(), name='service_type_create'),

    path('service/update/<int:pk>/', ServiceUpdateView.as_view(), name='service_update'),
    path('service/delete/<int:pk>/', ServiceDeleteView.as_view(), name='service_delete'),

    path('employers/', EmployerListView.as_view(), name='employer_list'),
    path('employer/<int:pk>/', EmployerDetailView.as_view(), name='employer_detail'),
    path('employer/<int:pk>/order/<int:order_id>/', EmployerDetailView.as_view(), name='employer_order_detail'),
    path('employer/pay_a_salary/<int:pk>/', PayASalaryView.as_view(), name='pay_a_salary'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),

    path('cashboxes/', CashboxListView.as_view(), name='cashbox_list'),
    path('cashbox/<int:pk>/', CashboxDetailView.as_view(), name='cashbox_detail'),
    path('cashbox/create/', CashboxCreateView.as_view(), name='cashbox_create'),
    path('cashbox/update/<int:pk>/', CashboxUpdateView.as_view(), name='cashbox_update'),
    path('cashbox/delete/<int:pk>/', CashboxDeleteView.as_view(), name='cashbox_delete'),
    path('cashbox/add/operation/', CashBoxAddOperationView.as_view(), name='add_operation'),

]
