from django import forms

from .models import Service, Cashbox, Order, CustomUser, CashboxOperation, ServiceType, EmployerOrder, \
    Consumables, ServiceOrder


class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = ['type', ]


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'type', 'discount', 'single', 'cost_price']


class ConsumablesForm(forms.ModelForm):
    class Meta:
        model = Consumables
        fields = ['name', 'count', 'price', 'cost_price']


class CashboxForm(forms.ModelForm):
    class Meta:
        model = Cashbox
        fields = ['name', 'balance']


class CashboxOperationForm(forms.ModelForm):
    class Meta:
        model = CashboxOperation
        fields = ['category', 'user', 'cashbox_from', 'cashbox_to', 'money', 'comment']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('stage', 'cashbox', 'date', 'time', 'client')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = CustomUser.objects.filter(user_type='client')


class AddServiceForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ('order', 'service', 'count',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.all()

