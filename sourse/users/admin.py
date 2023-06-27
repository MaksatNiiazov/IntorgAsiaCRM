from django.contrib import admin

# Register your models here.

from django.contrib import admin
from users.models import User, DiscountType

admin.site.register(DiscountType)
admin.site.register(User)
