from django.contrib import admin
from crm_warehouse.models import Product, EmployerProduct, ProductInEP
# Register your models here.


admin.site.register(Product)
admin.site.register(EmployerProduct)
admin.site.register(ProductInEP)
