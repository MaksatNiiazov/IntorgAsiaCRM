from django.contrib import admin

from crm_warehouse.models import Product, EmployerProduct, SetOfServices, ServiceInSet, ProductService

# Register your models here.


admin.site.register(Product)
admin.site.register(EmployerProduct)
admin.site.register(SetOfServices)
admin.site.register(ServiceInSet)
admin.site.register(ProductService)


