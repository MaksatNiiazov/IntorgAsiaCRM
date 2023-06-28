from django.db import models
from django.utils import timezone
from users.models import User as CustomUser
from crm_app.models import Order, Service


# Create your models here.


class Product(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    barcode = models.CharField(max_length=50)
    article = models.CharField(max_length=50)
    name = models.CharField(max_length=50, null=True)
    count = models.IntegerField(default=0, blank=True, null=True)
    declared_quantity = models.IntegerField(default=0, null=True)
    actual_quantity = models.IntegerField(default=0, null=True)
    size = models.CharField(max_length=30, blank=True, null=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    composition = models.CharField(max_length=150, blank=True, null=True)
    brand = models.CharField(max_length=90, blank=True, null=True)
    defective = models.IntegerField(null=True, blank=True)
    good_quality = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    confirmation = models.BooleanField(default=False)
    defective_check = models.BooleanField(default=False)
    in_work = models.BooleanField(default=False)


class EmployerProduct(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='employer_products')
    count = models.IntegerField(default=0)


class ProductInEP(models.Model):
    ep = models.ForeignKey(EmployerProduct, on_delete=models.CASCADE, related_name='products')
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='employer_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='emp')
    count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)


class SetOfServices(models.Model):
    name = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class ServiceInSet(models.Model):
    set = models.ForeignKey(SetOfServices, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
