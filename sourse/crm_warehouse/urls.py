from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('acceptance/', AcceptanceView.as_view(), name='acceptance'),

    path('import/<int:order_id>/', ImportExcelView.as_view(), name='import_excel'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/add/', ProductAddView.as_view(), name='product_add'),


    path('unpacking/<int:pk>/', UnpackingView.as_view(), name='unpacking'),
    path('unpacking/update/<int:pk>/', ProductUpdateView.as_view(), name='unpacking_update'),

    path('quality_check/<int:pk>/', QualityCheckView.as_view(), name='quality_check'),
    path('quality_check/update/<int:pk>/', QualityUpdateView.as_view(), name='quality_check_update'),

    path('invoice_generation/<int:pk>/', InvoiceGenerationView.as_view(), name='invoice_generation'),
    path('defective_check/update/<int:pk>/', DefectiveCheckUpdateView.as_view(), name='defective_check_update'),

    # path('invoice_generation/create/<int:pk>/', InvoiceGenerationCreateView.as_view(), name='invoice_generation_create'),

    path('dispatch/<int:pk>/', DispatchView.as_view(), name='dispatch'),
    path('product/decrease/<int:pk>/', DecreaseProductCountView.as_view(), name='decrease_product_count'),

    path('nextstage/<int:order_id>', DatabaseLoadingNextStage.as_view(), name='database_loading_next'),
    path('nextstage/unp/<int:order_id>', UnpackingNextStage.as_view(), name='unpacking_next'),
    path('nextstage/quality_check/<int:order_id>', QualityCheckNextStage.as_view(), name='quality_check_next'),
    path('nextstage/invoice_generation/<int:order_id>', InvoiceGenerationNextStage.as_view(), name='invoice_generation_next'),
    path('nextstage/dispatch/<int:order_id>', DispatchNextStage.as_view(), name='dispatch_next'),

]
