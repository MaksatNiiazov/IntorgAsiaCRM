from django.contrib import admin
from .models import Service, OrderService, Cashbox, Order, ModelChangeLog, CashboxCategory, CashboxOperation, \
    ServiceOrder, ServiceType, Consumables, OrderConsumables
# Register your models here.

admin.site.register(ServiceType)
admin.site.register(Service)
admin.site.register(OrderService)
admin.site.register(Cashbox)
admin.site.register(Order)
admin.site.register(ModelChangeLog)
admin.site.register(CashboxCategory)
admin.site.register(CashboxOperation)
admin.site.register(ServiceOrder)
admin.site.register(Consumables)
admin.site.register(OrderConsumables)
