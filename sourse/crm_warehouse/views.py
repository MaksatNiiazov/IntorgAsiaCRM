import math
import os
from datetime import date

import pandas as pd
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib import messages

from crm_warehouse.forms import UploadForm, AcceptanceForm, ProductForm, ProductUnpackingForm, EmployerProductForm, \
    DefectiveCheckForm, BarcodeForm
from crm_warehouse.models import Product, EmployerProduct, ProductInEP, SetOfServices, ServiceInSet
from crm_app.models import Order, OrderStages, Service, OrderService
from users.models import User as CustomUser


class DashboardView(ListView):
    model = Order
    template_name = 'stages/dashboard.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stages = OrderStages.choices
        context['stages'] = stages
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(total_declared_quantity=Sum('products__declared_quantity'))
        queryset = queryset.annotate(total_actual_quantity=Sum('products__actual_quantity'))

        return queryset


class AcceptanceView(View):
    template_name = 'stages/acceptance.html'

    def get(self, request):
        users = CustomUser.objects.filter(user_type='client')
        context = {
            'users': users,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = AcceptanceForm(request.POST)
        if form.is_valid():
            # Обработка данных из формы POST
            client = form.cleaned_data['client']
            name = form.cleaned_data['name']
            count = form.cleaned_data['count']
            order = Order.objects.create(name=name, client=client, count=count)
            order.month = date.today().month
            order.year = date.today().year
            order.day = date.today().day
            return redirect('dashboard')

        users = CustomUser.objects.filter(user_type='client')
        context = {
            'users': users,
            'form': form,
        }
        return render(request, redirect('dashboard'), context)

class ImportExcelView(View):
    template_name = 'stages/database_loading.html'

    def get(self, request, order_id):
        form = UploadForm()
        products = Product.objects.filter(order_id=order_id)
        context = {
            'order_id': order_id,
            'products': products,
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, order_id):
        form = UploadForm(request.POST, request.FILES)
        products = Product.objects.filter(order_id=order_id)
        context = {
            'order_id': order_id,
            'products': products,
            'form': form
        }

        if form.is_valid():
            excel_file = form.cleaned_data['file']

            try:
                file_path = 'crm_warehouse/exel/'
                file_full_path = os.path.join(file_path, excel_file.name)
                with open(file_full_path, 'wb') as file:
                    for chunk in excel_file.chunks():
                        file.write(chunk)
                df = pd.read_excel(file_full_path, skiprows=1)

                # Fill NaN values with previous non-null values per column
                columns_to_ffill = ['Цвет ', 'Название товара', 'Страна', 'Состав (Материал)', 'Бренд',
                                    'Комментарий (Тех задание)']  # Specify the columns to apply ffill
                df[columns_to_ffill] = df[columns_to_ffill].ffill()

                products_to_create = []

                for _, row in df.iterrows():
                    barcode = row.get('Баркод (Штрихкод)', None)
                    if barcode and not math.isnan(barcode):
                        count = row.get('Факт', 0)
                        if isinstance(count, (float, int)) and math.isnan(count):
                            count = 0
                        declared_quantity = row.get('Заявленное количество', 0)
                        if isinstance(declared_quantity, (float, int)) and math.isnan(declared_quantity):
                            declared_quantity = 0

                        size = row['Размер ']
                        color = row['Цвет ']
                        composition = row['Состав (Материал)']
                        brand = row['Бренд']
                        country = row['Страна']
                        comment = row['Комментарий (Тех задание)']

                        # Check if any field has the value "nan" and replace it with an empty string
                        size = '' if pd.isna(size) else size
                        color = '' if pd.isna(color) else color
                        composition = '' if pd.isna(composition) else composition
                        brand = '' if pd.isna(brand) else brand
                        country = '' if pd.isna(country) else country
                        comment = '' if pd.isna(comment) else comment

                        product = Product(
                            barcode=barcode,
                            article=row['Артикул ВБ (Номенклатура)'],
                            order_id=order_id,
                            name=row['Название товара'],
                            count=count,
                            declared_quantity=declared_quantity,
                            actual_quantity=declared_quantity,
                            size=size,
                            color=color,
                            composition=composition,
                            brand=brand,
                            defective=0,
                            good_quality=0,
                            country=country,
                            comment=comment,

                            confirmation=False,
                            in_work=False
                        )
                        products_to_create.append(product)

                Product.objects.bulk_create(products_to_create)

                os.remove(file_full_path)

                return redirect(reverse('import_excel', args=[order_id]))

            except Exception as e:
                error_message = f"Произошла ошибка при обработке файла Excel: {str(e)}"
                context['error_message'] = error_message

        return render(request, self.template_name, context)

class ProductDeleteView(View):

    def post(self, request, pk):
        product = Product.objects.get(id=pk)
        order = product.order.id
        product.delete()
        return redirect('import_excel', order)


class ProductAddView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'stages/database_loading.html'

    def form_valid(self, form):
        print(form.cleaned_data)
        product = Product(
            order=form.cleaned_data['order'] or 1,
            name=form.cleaned_data['name'],
            count=form.cleaned_data['count'] or 0,
            declared_quantity=form.cleaned_data['declared_quantity'] or 0,
            size=form.cleaned_data['size'] or '',
            color=form.cleaned_data['color'] or '',
            composition=form.cleaned_data['composition'] or '',
            brand=form.cleaned_data['brand'] or '',
            country=form.cleaned_data['country'] or '',
            confirmation=False,
            in_work=False
        )

        product.save()
        return redirect('import_excel', product.order.id)

    def form_invalid(self, form):
        print(form.errors)
        return self.success_url

    def get_success_url(self):
        product_id = self.kwargs['order_id']
        return reverse('product_detail', args=[product_id])


class UnpackingView(DetailView):
    template_name = 'stages/unpacking.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(UnpackingView, self).get_context_data()
        context['products'] = Product.objects.filter(order_id=self.object.id)
        # confirmation = all(product.confirmation for product in self.object.products.all())
        # if confirmation:
        #     context['confirmation'] = True
        #     print(123)

        return context


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductUnpackingForm
    template_name = 'stages/unpacking.html'

    def get_success_url(self):
        return reverse('unpacking', self.object.order.id)

    def form_valid(self, form):
        product = self.object
        product.actual_quantity = form.cleaned_data['actual_quantity']
        product.good_quality = form.cleaned_data['actual_quantity']
        product.comment = form.cleaned_data['comment']
        product.confirmation = form.cleaned_data['confirmation']
        product.save()

        return redirect('unpacking', self.object.order.id)

    def form_invalid(self, form):
        print(form.errors)
        return redirect('unpacking', self.object.order.id)


class QualityCheckView(DetailView):
    template_name = 'stages/quality_check.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['products_in_work'] = Product.objects.filter(order=self.object, in_work=True)
        context['products'] = Product.objects.filter(order=self.object, in_work=False)
        context['workers'] = CustomUser.objects.filter(user_type='worker')
        context['services'] = Service.objects.all()
        context['order_id'] = self.object.id
        context['sets_of_services'] = SetOfServices.objects.filter(order_id=self.object.id)

        return context


class QualityUpdateView(CreateView):
    model = Order
    form_class = EmployerProductForm
    template_name = 'stages/quality_check.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['products'] = Product.objects.filter(order=self.object, in_work=False)
        context['products_in_work'] = Product.objects.filter(order=self.object, in_work=True)
        context['workers'] = CustomUser.objects.filter(user_type='worker')
        context['order_id'] = self.object.order.id
        return context

    def form_valid(self, form):
        print(self.request.POST.getlist('sets'))
        product_id = self.request.POST.get('product')
        product = Product.objects.get(id=product_id)
        product.in_work = True
        product.save()
        order = form.cleaned_data['order']
        user = form.cleaned_data['user']
        emp_product = EmployerProduct.objects.get_or_create(
            order=order,
            user=user,
        )[0]
        emp_product.count += product.good_quality
        emp_product.save()
        ProductInEP.objects.get_or_create(
            ep=emp_product,
            product=product,
            user=user,
            count=product.good_quality
        )

        return redirect('quality_check', order.id)

    def form_invalid(self, form):
        return redirect('quality_check', self.object.id)


class SetOfServiceCreateView(View):
    def get(self, request, pk):
        services_before = Service.objects.filter(before_defective=True)
        services_after = Service.objects.filter(before_defective=False)
        sets = SetOfServices.objects.filter(order_id=pk)

        context = {
            'order_id': pk,
            'services_before': services_before,
            'services_after': services_after,
            'sets': sets,
        }
        return render(request, 'stages/sets_of_services/set_of_srvices.html', context)

    def post(self, request, pk):
        services = Service.objects.filter(before_defective__in=[True, False])
        services_before = services.filter(before_defective=True)
        services_after = services.filter(before_defective=False)

        name = self.request.POST.get('name')
        services = self.request.POST.getlist('services')
        set_of_services, _ = SetOfServices.objects.get_or_create(order_id=pk, name=name)

        service_ids = [int(service) for service in services]
        service_objects = Service.objects.in_bulk(service_ids)
        service_in_set_objects = [ServiceInSet(set=set_of_services, service=service_objects[int(service)]) for service
                                  in services]
        ServiceInSet.objects.bulk_create(service_in_set_objects)

        sets = SetOfServices.objects.filter(order_id=pk)

        context = {
            'order_id': pk,
            'services_before': services_before,
            'services_after': services_after,
            'sets': sets
        }
        return render(request, 'stages/sets_of_services/set_of_srvices.html', context)


class InvoiceGenerationView(DetailView):
    model = Order
    template_name = 'stages/invoice_generation.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceGenerationView, self).get_context_data()
        context['order'] = self.object
        context['services_before'] = Service.objects.filter(before_defective=True)
        context['services_after'] = Service.objects.filter(before_defective=False)
        context['workers'] = CustomUser.objects.filter(user_type='worker')
        total_count = self.total_count()
        context['total_count'] = total_count
        return context

    def total_count(self):
        order_products = Order.objects.get(pk=self.object.id)
        products = order_products.products.all()
        total_count = 0

        for product in products:
            total_count += product.actual_quantity

        return total_count


class DefectiveCheckUpdateView(UpdateView):
    model = Product
    form_class = DefectiveCheckForm

    def form_valid(self, form):
        print(self.request.POST)
        set_id = self.request.POST.get('set')
        set = SetOfServices.objects.get(id=set_id)
        services = set.services.all()
        order_id = self.request.POST['order']
        order = Order.objects.get(id=order_id)
        employer_id = self.request.POST['employer']
        employer = CustomUser.objects.get(id=employer_id)
        worker = CustomUser.objects.get(id=employer_id)
        client = CustomUser.objects.get(id=order.client_id)

        product = self.object
        if not product.defective_check:
            good_quality = product.actual_quantity - form.cleaned_data['defective']
            product.good_quality = good_quality
            product.defective = form.cleaned_data['defective']
            product.count = good_quality
            product.defective_check = True
            product.save()

            order_items = Product.objects.filter(order=order)
            total_good_quality = sum(item.good_quality for item in order_items)
            total_defective = sum(item.defective for item in order_items)
            order.good_quality = total_good_quality
            order.defective = total_defective
            order.count = total_good_quality + total_defective
            order.save()

            for service_id in services:
                service = Service.objects.get(id=service_id.service.id)
                order_service, _ = OrderService.objects.get_or_create(order=order, service=service, employer=employer)
                emp_serv = order_service
                emp_serv.confirmed_switch()

                if service.before_defective:
                    new_count = product.good_quality + product.defective
                else:
                    new_count = product.good_quality
                new_amount = new_count * service.price
                new_cost = new_count * service.cost_price

                update_order = Order.objects.get(id=order.pk)

                update_order.count += new_count
                update_order.amount += new_amount
                update_order.cost_price += new_cost

                emp_serv.count += new_count
                emp_serv.salary += new_count * service.price

                worker.money += new_cost
                worker.services_count += new_count

                client.money += new_amount
                client.services_count += new_count
                update_order.save()
                emp_serv.save()
                worker.save()
                client.save()

            return redirect('quality_check', self.object.order.id)



class DispatchView(DetailView):
    model = Order
    template_name = 'stages/dispatch.html'

    def get_context_data(self, **kwargs):
        context = super(DispatchView, self).get_context_data()
        context['products'] = Product.objects.filter(order=self.object)

        return context


class DecreaseProductCountView(UpdateView):
    model = Order
    form_class = BarcodeForm

    def form_valid(self, form):
        order = self.object
        barcode = form.cleaned_data['barcode']
        print(barcode)
        product = Product.objects.get(barcode=barcode, order=order)

        if product.count > 0:
            product.count -= 1
            product.save()
            return redirect('dispatch', order.id)
        else:
            messages.error(self.request, 'Product count is already 0.')
            return redirect('dispatch', order.id)


class AcceptanceNextStage(View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.stage == 'acceptance':
            order.transition_to_next_stage()

        return redirect(reverse('dashboard'))


class DatabaseLoadingNextStage(View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.products.count() > 0:
            if order.stage == 'acceptance':
                order.transition_to_next_stage()
            return redirect(reverse('dashboard'))

        else:
            messages.error(self.request, 'Не добавлен ни один продукт!')
            return redirect('import_excel', order.id)


class UnpackingNextStage(View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        products = order.products.all()

        all_confirmed = all(product.confirmation for product in products)

        if all_confirmed:
            if order.stage == 'database_loading':
                order.transition_to_next_stage()
                return redirect(reverse('dashboard'))

        else:
            messages.error(self.request, "Не все продукты в заказе подтверждены.")

            return redirect("unpacking", order.id)


class QualityCheckNextStage(View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        products = order.products.all()

        all_in_work = all(product.in_work for product in products)

        if all_in_work:
            all_defective_checked = all(product.defective_check for product in products)
            if all_defective_checked:
                if order.stage == 'unpacking':
                    order.transition_to_next_stage()
                return redirect(reverse('dashboard'))
            else:
                messages.error(self.request, "Не все проверены на брак.")

                return redirect("quality_check", order.id)
        else:
            messages.error(self.request, "Не все продукты переданы работнкам.")

            return redirect("quality_check", order.id)


class InvoiceGenerationNextStage(View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.stage == 'quality_check':
            order.transition_to_next_stage()
        return redirect(reverse('dashboard'))


class DispatchNextStage(View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.stage == 'invoice_generation':
            order.transition_to_next_stage()
        return redirect(reverse('dashboard'))
