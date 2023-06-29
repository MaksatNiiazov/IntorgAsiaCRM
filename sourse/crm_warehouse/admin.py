from django.contrib import admin

from crm_warehouse.models import Product, EmployerProduct, ProductInEP, SetOfServices, ServiceInSet

# Register your models here.


admin.site.register(Product)
admin.site.register(EmployerProduct)
admin.site.register(ProductInEP)
admin.site.register(SetOfServices)
admin.site.register(ServiceInSet)

# SetOfServices
# ServiceInSet