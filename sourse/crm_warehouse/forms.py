from django import forms
from .models import CustomUser
from crm_app.models import Order
from crm_warehouse.models import Product, EmployerProduct


class UploadForm(forms.Form):
    file = forms.FileField()


class AcceptanceForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('name', 'client', 'count',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = CustomUser.objects.filter(user_type='client')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['order', 'name', 'count', 'declared_quantity', 'size', 'color', 'composition',
                  'brand', 'country', 'comment']


class ProductUnpackingForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['actual_quantity', 'comment', 'confirmation']


class DefectiveCheckForm(forms.ModelForm):
    employer_id = forms.IntegerField()

    class Meta:
        model = Product
        fields = ['defective', 'employer_id']


class EmployerProductForm(forms.ModelForm):
    class Meta:
        model = EmployerProduct
        fields = ['product', 'employer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employer'].queryset = CustomUser.objects.filter(user_type='worker')


class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['barcode']
