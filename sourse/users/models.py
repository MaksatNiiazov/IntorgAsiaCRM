from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def _create_user(self, username, password, is_staff, is_superuser, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        now = timezone.now()
        username = self.model.normalize_username(username)
        user = self.model(
            username=username,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        return self._create_user(username, password, False, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        user = self._create_user(username, password, True, True, **extra_fields)
        return user


class DiscountType(models.Model):
    name = models.CharField(max_length=54)
    percent = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name} - {self.percent}%'


class UserType(models.TextChoices):
    WORKER = 'worker', 'Worker'
    CLIENT = 'client', 'Client'
    MANAGER = 'manager', 'Manager'
    ADMIN = 'admin', 'Admin'


class User(AbstractBaseUser, PermissionsMixin):
    disabled = models.BooleanField(default=False)
    username = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text='Номер телефона')
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(null=True, auto_now=True)
    joined_date = models.DateTimeField(default=timezone.now)
    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.CLIENT)
    discount = models.ForeignKey(DiscountType, on_delete=models.PROTECT, blank=True, null=True)
    money = models.IntegerField(default=0)
    profit = models.IntegerField(default=0)
    product_count = models.IntegerField(default=0, blank=True, null=True)
    # service_count = models.IntegerField(default=0, blank=True, null=True)
    referal_money = models.IntegerField(default=0, blank=True, null=True)

    referral = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ('disabled','-product_count')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_product_count(self):
        from crm_app.models import EmployerOrder
        order_services = EmployerOrder.objects.filter(user=self)
        product_count = 0

        for order_service in order_services:
            product_count += order_service.product_count

        return product_count


