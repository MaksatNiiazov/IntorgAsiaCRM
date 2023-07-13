from django.urls import path
from crm_app.views import *

urlpatterns = [
    path('statistic/', StatisticView.as_view(), name='statistic_page'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    # path('order/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/add/service/', AddServiceView.as_view(), name='add_service'),
    path('order/add/service/employer/', AddServiceEmployerView.as_view(), name='add_service_employer'),

    path('order/<int:pk>/delete/service/', OrderServiceDeleteView.as_view(), name='delete_service'),
    path('order/add/to/order/', SertviceToOrderView.as_view(), name='add_to_order'),

    path('services/', ServiceListView.as_view(), name='service_list'),
    path('service/create/', ServiceCreateView.as_view(), name='service_create'),
    path('service-type/create/', ServiceTypeCreateView.as_view(), name='service_type_create'),
    path('service/update/<int:pk>/', ServiceUpdateView.as_view(), name='service_update'),
    path('service/delete/<int:pk>/', ServiceDeleteView.as_view(), name='service_delete'),

    path('consumables/', ConsumablesListView.as_view(), name='consumable_list'),
    path('consumable/create/', ConsumablesCreateView.as_view(), name='consumable_create'),
    path('consumable/update/<int:pk>/', ConsumablesUpdateView.as_view(), name='consumable_update'),
    path('consumable/delete/<int:pk>/', ConsumablesDeleteView.as_view(), name='consumable_delete'),

    path('employers/', EmployerListView.as_view(), name='employer_list'),
    path('employer/<int:pk>/', EmployerDetailView.as_view(), name='employer_detail'),
    path('employer/<int:pk>/order/<int:order_id>/', EmployerOrderView.as_view(), name='employer_order_detail'),
    path('employer/pay_a_salary/<int:pk>/', PayASalaryView.as_view(), name='pay_a_salary'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),

    path('cashboxes/', CashboxListView.as_view(), name='cashbox_list'),
    path('cashbox/<int:pk>/', CashboxDetailView.as_view(), name='cashbox_detail'),
    path('cashbox/create/', CashboxCreateView.as_view(), name='cashbox_create'),
    path('cashbox/update/<int:pk>/', CashboxUpdateView.as_view(), name='cashbox_update'),
    path('cashbox/delete/<int:pk>/', CashboxDeleteView.as_view(), name='cashbox_delete'),
    path('cashbox/add/operation/', CashBoxAddOperationView.as_view(), name='add_operation'),
    path('cashbox/<int:pk>/operation/list/to/', CashboxOperationToListView.as_view(), name='cashbox_operation_list_to'),
    path('cashbox/<int:pk>/operation/list/from/', CashboxOperationFromListView.as_view(),
         name='cashbox_operation_list_from'),
    path('cashbox/export/operation/', CashboxExport.as_view(), name='cashbox_export'),

    path('show/logs/', ShowLogsView.as_view(), name='show_logs'),

]
