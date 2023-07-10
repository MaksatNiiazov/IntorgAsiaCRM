import calendar
import os
import time
from urllib.parse import quote

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

from crm_app.forms import ServiceForm, CashboxForm, OrderForm, AddServiceForm, CashboxOperationForm, ServiceTypeForm, \
    ConsumablesForm
from crm_app.models import Order, Service, Cashbox, OrderService, CustomUser, CashboxOperation, CashboxCategory, \
    ServiceType, ServiceOrder, EmployerOrder, Consumables
from datetime import date, timedelta, datetime
from django.db.models import Sum, Count, Q

from crm_warehouse.models import ProductInEP


class StatisticView(ListView):
    model = Order
    template_name = 'crmapp/сhart.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.GET.get('filter_type')
        filter_start = self.request.GET.get('start_date')
        filter_end = self.request.GET.get('end_date') or date.today()

        if filter_type == 'week':
            if not filter_start or not filter_end:
                today = date.today()
                start_date = today - timedelta(days=today.weekday())
                end_date = start_date + timedelta(days=6)
                self.request.GET = self.request.GET.copy()
                self.request.GET['start_date'] = start_date.strftime('%Y-%m-%d')
                self.request.GET['end_date'] = end_date.strftime('%Y-%m-%d')
        elif filter_type == 'month':
            if not filter_start:
                today = date.today()
                start_date = date(today.year, today.month, 1)
                end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
                self.request.GET = self.request.GET.copy()
                self.request.GET['start_date'] = start_date.strftime('%Y-%m-%d')
                self.request.GET['end_date'] = end_date.strftime('%Y-%m-%d')
        elif filter_type == 'quarter':
            if not filter_start:
                today = date.today()
                quarter_start_month = ((today.month - 1) // 3) * 3 + 1
                start_date = date(today.year, quarter_start_month, 1)
                end_date = date(today.year, quarter_start_month + 2,
                                calendar.monthrange(today.year, quarter_start_month + 2)[1])
                self.request.GET = self.request.GET.copy()
                self.request.GET['start_date'] = start_date.strftime('%Y-%m-%d')
                self.request.GET['end_date'] = end_date.strftime('%Y-%m-%d')
        elif filter_type == 'year':
            if not filter_start:
                today = date.today()
                start_date = date(today.year, 1, 1)
                end_date = date(today.year, 12, 31)
                self.request.GET = self.request.GET.copy()
                self.request.GET['start_date'] = start_date.strftime('%Y-%m-%d')
                self.request.GET['end_date'] = end_date.strftime('%Y-%m-%d')

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date') or date.today()

        queryset = queryset.filter(date__range=[start_date, end_date]).values('year', 'month', 'day').annotate(
            total_count=Count('id'), total_amount=Sum('amount'), total_cost_price=Sum('cost_price'), profit=(
                    Sum('amount') - Sum('cost_price'))).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        total_amount = queryset.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_cost_price = queryset.aggregate(total_cost_price=Sum('total_cost_price'))['total_cost_price'] or 0
        total_count = queryset.aggregate(total_count=Count('id'))['total_count'] or 0
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date') or ""
        end_date = self.request.GET.get('end_date') or date.today().strftime('%Y-%m-%d')
        filter_type = self.request.GET.get('filter_type')
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['filter_type'] = filter_type
        context['total_amount'] = total_amount
        context['total_cost_price'] = total_cost_price
        context['total_count'] = total_count
        context['profit'] = total_amount - total_cost_price or 0

        return context


class OrderListView(ListView):
    model = Order
    template_name = 'crmapp/order_list.html'
    ordering = ['-date']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset


class OrderDetailView(DetailView):
    model = Order
    template_name = 'crmapp/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = OrderService.objects.filter(order=self.object.id)
        return context


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'crmapp/order_create.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = date.today()
        initial['day'] = date.today().day
        initial['month'] = date.today().month
        initial['year'] = date.today().year
        initial['time'] = datetime.now().strftime('%H:%M')
        return initial

    def form_valid(self, form):
        order = form.save(commit=False)
        total_price, total_cost_price = order.calculate_price()
        order.amount = total_price
        order.cost_price = total_cost_price
        order.month = date.today().month
        order.year = date.today().year
        order.day = date.today().day
        order.save()

        return redirect('invoice_generation', pk=order.pk)


class SertviceToOrderView(View):

    def get(self, request):
        context = {
            'services': Service.objects.filter(acceptance=False, single=False),
            'employers': CustomUser.objects.filter(user_type='worker')
        }
        return render(request, 'crmapp/service_add.html', context)

    def post(self, request):
        pass


class AddServiceView(CreateView):
    form_class = AddServiceForm
    template_name = 'crmapp/service_add.html'

    def form_valid(self, form):
        order = form.cleaned_data['order']
        service = form.cleaned_data['service']
        count = form.cleaned_data['count']
        update_order = Order.objects.get(id=order.pk)
        service_order, _ = ServiceOrder.objects.get_or_create(order=order, service=service)
        client = update_order.client

        old_count = service_order.count or 0
        old_amount = old_count * service.price or 0
        old_cost = old_count * service.cost_price or 0
        new_count = count
        new_amount = count * service.price
        new_cost = count * service.cost_price

        count_diff = new_count - old_count
        amount_diff = new_amount - old_amount
        cost_diff = new_cost - old_cost

        update_order.count += count_diff
        update_order.amount += amount_diff
        update_order.cost_price += cost_diff

        service_order.count += count_diff
        service_order.amount += amount_diff

        client.money += amount_diff
        client.profit += amount_diff - cost_diff

        update_order.save(update_fields=['count', 'amount', 'cost_price'])
        service_order.save(update_fields=['count', 'amount'])
        client.save(update_fields=['money', 'profit'])
        return redirect('invoice_generation', pk=order.pk)

    def form_invalid(self, form):
        order = form.cleaned_data['order']
        print(form.errors)
        return redirect('invoice_generation', pk=order.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.kwargs['order_id']
        context['services'] = Service.objects.all()
        context['employers'] = CustomUser.objects.filter(user_type='worker')
        return context


class OrderServiceDeleteView(DeleteView):
    model = OrderService

    def form_valid(self, form):
        order = Order.objects.get(pk=self.object.order.id)
        order.amount -= self.object.salary
        order.count -= self.object.count
        order.cost_price -= self.object.service.cost_price
        order.save()
        client = CustomUser.objects.get(id=order.client_id)
        client.money -= self.object.salary
        client.product_count -= self.object.count
        client.save()
        worker = CustomUser.objects.get(id=self.object.employer_id)
        worker.money -= self.object.salary
        worker.product_count -= self.object.count
        worker.save()
        cashbox = Cashbox.objects.get(id=order.cashbox_id)
        cashbox.balance -= self.object.salary
        cashbox.save()
        self.object.delete()
        return redirect('order_detail', pk=self.object.order.pk)


class ServiceListView(ListView):
    model = Service
    template_name = 'crmapp/service_list.html'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ServiceListView, self).get_context_data()
        context['types'] = ServiceType.objects.all()
        return context


class ServiceTypeCreateView(CreateView):
    model = ServiceType
    form_class = ServiceTypeForm
    template_name = 'crmapp/servise_type_create.html'
    success_url = '/services/'


class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'crmapp/service_list.html'
    success_url = '/services/'

    def form_valid(self, form):

        response = super().form_valid(form)
        object = self.object
        object.before_defective = (self.request.POST.get('gender'))
        object.save()
        return response


class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'crmapp/service_list.html'
    success_url = '/services/'

    def form_valid(self, form):
        object = self.object
        object.before_defective = (self.request.POST.get('gender'))
        object.save()
        response = super().form_valid(form)
        return response


class ServiceDeleteView(DeleteView):
    model = Service
    success_url = '/services/'


class ConsumablesListView(ListView):
    model = Consumables
    template_name = 'crmapp/consumable_list.html'


class ConsumablesCreateView(CreateView):
    model = Consumables
    form_class = ConsumablesForm
    success_url = '/consumables/'


class ConsumablesUpdateView(UpdateView):
    model = Consumables
    form_class = ConsumablesForm
    template_name = 'crmapp/consumable_list.html'
    success_url = '/consumables/'


class ConsumablesDeleteView(DeleteView):
    model = Consumables
    success_url = '/consumables/'


class EmployerListView(ListView):
    model = CustomUser
    template_name = 'crmapp/employer_list.html'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='worker')


class EmployerDetailView(DetailView):
    model = CustomUser
    template_name = 'crmapp/employer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = EmployerOrder.objects.filter(user_id=self.object.id)
        context['cashboxes'] = Cashbox.objects.all()
        return context


class PayASalaryView(View):

    def post(self, request, pk):
        emp_order = EmployerOrder.objects.get(id=pk)
        user = CustomUser.objects.get(id=emp_order.user.id)
        num = int(self.request.POST.get('num'))
        cashbox = Cashbox.objects.get(id=int(self.request.POST.get('cashbox')))
        category = CashboxCategory.objects.get_or_create(category="Зарплата")[0]
        balance_check =  cashbox.balance - num

        if balance_check < 0:
            messages.error(self.request, "В кассе недостаточно средств!")
            return redirect('employer_detail', emp_order.user.id)
        CashboxOperation.objects.create(user_id=3, category=category, cashbox_from=cashbox, money=num, comment='')


        cashbox.balance -= num
        user.money -= num
        emp_order.salary -= num
        cashbox.save()
        user.save()
        emp_order.save()

        return redirect('employer_detail', emp_order.user.id)


class EmployerOrderView(ListView):
    model = ProductInEP
    template_name = 'crmapp/employer_order.html'

    def get_queryset(self):
        query_set = ProductInEP.objects.filter(ep__order_id=self.kwargs['order_id'], user=self.kwargs['pk'])


        return query_set


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(EmployerOrderView, self).get_context_data()
        context['order_id'] = self.kwargs['order_id']
        context['user'] = CustomUser.objects.get(id=self.kwargs['pk'])
        return context


class ClientListView(ListView):
    model = CustomUser
    template_name = 'crmapp/client_list.html'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='client')


class ClientDetailView(DetailView):
    model = CustomUser
    template_name = 'crmapp/client_detail.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ClientDetailView, self).get_context_data()
        context['orders'] = Order.objects.filter(client_id=self.object.id)
        return context


class CashboxListView(ListView):
    model = Cashbox
    template_name = 'crmapp/cashbox_list.html'
    paginate_by = 20


class CashboxDetailView(DetailView):
    model = Cashbox
    template_name = 'crmapp/cashbox_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CashboxDetailView, self).get_context_data()
        operations = CashboxOperation.objects.all()
        context['operations_from'] = operations.filter(cashbox_from=self.object).order_by('-id')[:10]
        context['operations_to'] = operations.filter(cashbox_to=self.object).order_by('-id')[:10]
        context['users'] = CustomUser.objects.filter(user_type='worker')
        cashboxes = Cashbox.objects.all()
        context['cashboxes'] = cashboxes.exclude(id=self.object.id)
        context['categories'] = CashboxCategory.objects.all()
        return context


class CashboxCreateView(CreateView):
    model = Cashbox
    form_class = CashboxForm
    template_name = 'crmapp/cashbox_list.html'
    success_url = '/cashboxes/'


class CashboxUpdateView(UpdateView):
    model = Cashbox
    form_class = CashboxForm
    template_name = 'crmapp/cashbox_list.html'
    success_url = '/cashboxes/'


class CashboxDeleteView(DeleteView):
    model = Cashbox
    success_url = '/cashboxes/'


class CashBoxAddOperationView(CreateView):
    model = CashboxOperation
    form_class = CashboxOperationForm
    template_name = 'crmapp/cashbox_detail.html'

    def form_valid(self, form):
        print(form.cleaned_data)
        cashbox_to = form.cleaned_data['cashbox_to']
        if not cashbox_to:
            cashbox_to = None
        cashbox_from = form.cleaned_data['cashbox_from']
        if not cashbox_from:
            cashbox_from = None
        category = form.cleaned_data['category']
        if self.request.POST.get('check') == 'to':
            money = form.cleaned_data['money']
            if money <= 0:
                messages.error(self.request, "Вы пытаетесь сделать приход на 0!")
                return redirect(self.request.META.get('HTTP_REFERER'))
            comment = form.cleaned_data['comment']
            if not comment:
                comment = ''
            operation = CashboxOperation.objects.create(
                user_id=3,
                category=category,
                money=form.cleaned_data['money'],
                comment=comment,
                cashbox_from=cashbox_from,
                cashbox_to=cashbox_to,
            )
            cashbox = Cashbox.objects.get(id=cashbox_to.id)
            cashbox.balance += money
            cashbox.save()

        elif self.request.POST.get('check') == 'from':
            money = form.cleaned_data['money']
            if money <= 0:
                messages.error(self.request, "Вы пытаетесь сделать расход на 0!")
                return redirect(self.request.META.get('HTTP_REFERER'))
            comment = form.cleaned_data['comment']
            if not comment:
                comment = ''
            operation = CashboxOperation.objects.create(
                user_id=3,
                category=form.cleaned_data['category'],
                money=money,
                comment=comment,
                cashbox_from=cashbox_from,
                cashbox_to=cashbox_to,
            )
            cashbox = Cashbox.objects.get(id=cashbox_from.id)
            result = cashbox.balance - money
            if result < 0:
                messages.error(self.request, "В кассе недостаточно средств!")
                return redirect(self.request.META.get('HTTP_REFERER'))
            cashbox.balance = result
            cashbox.save()

        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        print(form.errors)
        return redirect(self.request.META.get('HTTP_REFERER'))


class CashboxOperationFromListView(ListView):
    model = CashboxOperation
    template_name = 'crmapp/cashbox_operation_list.html'
    paginate_by = 50

    def get_queryset(self):
        return CashboxOperation.objects.filter(cashbox_from_id=self.kwargs['pk'])


class CashboxOperationToListView(CashboxOperationFromListView):

    def get_queryset(self):
        return CashboxOperation.objects.filter(cashbox_to_id=self.kwargs['pk'])


class CashboxExport(View):
    def post(self, request):
        start_date = self.request.POST['start_date']
        end_date = self.request.POST['end_date']
        cashbox = self.request.POST['cashcox']
        cashbox_operations = CashboxOperation.objects.filter(
            Q(cashbox_from=cashbox) | Q(cashbox_to=cashbox),
            date__range=(start_date, end_date)
        )
        file_name = 'cashbox_operations_template.xlsx'  # Excel template file name
        root_directory = 'excel'  # Root directory to search for the template file
        file_path = None

        for root, dirs, files in os.walk(root_directory):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                break

        if not file_path:
            return HttpResponse('File not found')

        wb = load_workbook(file_path)
        sheet = wb.active

        # Set column headers
        sheet['A1'] = 'Дата'
        sheet['B1'] = 'Время'
        sheet['C1'] = 'От'
        sheet['D1'] = 'Сумма'
        sheet['E1'] = 'Куда'
        sheet['F1'] = 'Категория'
        sheet['G1'] = 'Сотрудник'
        sheet['H1'] = 'Комментарий'

        # Set column widths and formatting
        column_widths = [20, 20, 10, 30, 20, 20, 15, 15]
        for col_num, width in enumerate(column_widths, start=1):
            col_letter = chr(ord('A') + col_num - 1)
            sheet.column_dimensions[col_letter].width = width

        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                             bottom=Side(style='thin'))
        alignment = Alignment(horizontal='center')
        font = Font(color="000000")

        row = 2
        for operation in cashbox_operations:
            # Set cell values
            sheet[f'A{row}'] = operation.date.strftime('%Y-%m-%d')
            sheet[f'B{row}'] = operation.time.strftime('%H:%M')
            sheet[f'C{row}'] = operation.cashbox_from.name if operation.cashbox_from else ''
            sheet[f'D{row}'] = operation.money
            sheet[f'E{row}'] = operation.cashbox_to.name if operation.cashbox_to else ''
            sheet[f'F{row}'] = operation.category.category if operation.category else ''
            sheet[f'G{row}'] = operation.user.username if operation.user else ''
            sheet[f'H{row}'] = operation.comment if operation.comment else ''

            # Apply formatting to cells
            for col_num in range(1, 9):
                cell = sheet.cell(row=row, column=col_num)
                cell.border = thin_border
                cell.alignment = alignment


            row += 1

        # Save the workbook
        timestamp = int(time.time())  # Add a timestamp to the file name to make it unique
        new_file_path = f'excel/cashbox_operations_{timestamp}.xlsx'
        wb.save(new_file_path)
        wb.close()

        # Prepare the response for file download
        with open(new_file_path, 'rb') as f:
            response = HttpResponse(f.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = f'CashboxOperations_{date.today()}.xlsx'
            quoted_filename = quote(filename, encoding='utf-8')
            response['Content-Disposition'] = f'attachment; filename="{quoted_filename}"'

        # Delete the newly generated file
        max_retries = 3
        retry_delay = 1  # Delay in seconds
        retry_count = 0

        while retry_count < max_retries:
            try:
                os.remove(new_file_path)
                break
            except PermissionError:
                retry_count += 1
                time.sleep(retry_delay)

        return response