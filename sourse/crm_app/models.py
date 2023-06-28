from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from users.models import User as CustomUser


class OrderStages(models.TextChoices):
    ACCEPTANCE = 'acceptance', 'Приемка'
    DATABASE_LOADING = 'database_loading', 'Загрузка в базу'
    UNPACKING = 'unpacking', 'Распаковка'
    QUALITY_CHECK = 'quality_check', 'Выдача ОТК'
    INVOICE_GENERATION = 'invoice_generation', 'Выставка счета'
    DISPATCH = 'dispatch', 'Отправка'


class Order(models.Model):
    stage = models.CharField(max_length=20, choices=OrderStages.choices, default=OrderStages.ACCEPTANCE)
    name = models.CharField(max_length=50, blank=True)
    cashbox = models.ForeignKey("Cashbox", on_delete=models.PROTECT, blank=True, null=True)
    amount = models.IntegerField(default=0)
    cost_price = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    day = models.IntegerField(validators=[MaxValueValidator(31), MinValueValidator(1)], default=1)
    month = models.IntegerField(validators=[MaxValueValidator(12), MinValueValidator(1)], default=1)
    year = models.IntegerField(validators=[MaxValueValidator(2070), MinValueValidator(2020)], default=2023)
    time = models.TimeField(default=timezone.now)
    client = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    defective = models.IntegerField(default=0, blank=True)
    good_quality = models.IntegerField(default=0, blank=True)

    def calculate_price(self):
        order_services = OrderService.objects.filter(order=self)
        total_price = 0
        total_cost_price = 0

        for order_service in order_services:
            service_price = order_service.service.price
            service_cost_price = order_service.service.cost_price
            count = order_service.count
            employers_count = order_service.employers.count()
            total_price += service_price * count * employers_count
            total_cost_price += service_cost_price * count * employers_count

        return total_price, total_cost_price

    def transition_to_next_stage(self):
        current_stage = self.stage

        if current_stage == OrderStages.ACCEPTANCE:
            self.stage = OrderStages.DATABASE_LOADING
        elif current_stage == OrderStages.DATABASE_LOADING:
            self.stage = OrderStages.UNPACKING
        elif current_stage == OrderStages.UNPACKING:
            self.stage = OrderStages.QUALITY_CHECK
        elif current_stage == OrderStages.QUALITY_CHECK:
            self.stage = OrderStages.INVOICE_GENERATION
        elif current_stage == OrderStages.INVOICE_GENERATION:
            self.stage = OrderStages.DISPATCH

        self.save()


class Consumables(models.Model):
    name = models.CharField(max_length=50)
    count = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    cost_price = models.IntegerField(default=0)


class Service(models.Model):
    name = models.CharField(max_length=124)
    before_defective = models.BooleanField(default=False)
    price = models.IntegerField()
    cost_price = models.IntegerField()
    consumables = models.ForeignKey(Consumables, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=0)
    salary = models.IntegerField(default=0)
    confirmed = models.BooleanField(default=False)

    def confirmed_switch(self):
        confirmed = self.confirmed
        if not confirmed:
            self.confirmed = True
        # elif confirmed:
        #     self.confirmed = False


class Cashbox(models.Model):
    name = models.CharField(max_length=54)
    balance = models.IntegerField()

    def __str__(self):
        return f'{self.name}'


class CashboxCategory(models.Model):
    category = models.CharField(max_length=124)

    def __str__(self):
        return f'{self.category}'


class CashboxOperation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    category = models.ForeignKey(CashboxCategory, on_delete=models.PROTECT)
    money = models.IntegerField()
    comment = models.CharField(max_length=255)
    cashbox_from = models.ForeignKey(Cashbox, on_delete=models.PROTECT, blank=True, null=True,
                                     related_name='cashbox_from')
    cashbox_to = models.ForeignKey(Cashbox, on_delete=models.PROTECT, blank=True, null=True, related_name='cashbox_to')
    time = models.TimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)


class ModelChangeLog(models.Model):
    MODEL_CHOICES = (
        ('Created', 'Created'),
        ('Updated', 'Updated'),
        ('Deleted', 'Deleted'),
    )
    model_name = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    change_type = models.CharField(max_length=10, choices=MODEL_CHOICES)
    old_value = models.CharField(max_length=100, blank=True)
    new_value = models.CharField(max_length=100, blank=True)
    change_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.change_type} {self.model_name} at {self.change_timestamp}'

    @classmethod
    def add_log(cls, model_name, user, change_type, old_value='', new_value=''):
        log_entry = cls(
            model_name=model_name,
            user=user,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value
        )
        log_entry.save()
