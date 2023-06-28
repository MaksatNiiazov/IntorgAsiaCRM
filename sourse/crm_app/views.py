import calendar

from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from crm_app.forms import ServiceForm, CashboxForm, OrderForm, AddServiceForm, CashboxOperationForm
from crm_app.models import Order, Service, Cashbox, OrderService, CustomUser, CashboxOperation, CashboxCategory
from datetime import date, timedelta, datetime
from django.db.models import Sum, Count


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


class OrderServiceCreateView(CreateView):
    template_name = 'crmapp/service_add.html'
    form_class = AddServiceForm

    def form_valid(self, form):
        order = form.cleaned_data['order']
        service = form.cleaned_data['service']
        count = form.cleaned_data['count']
        employer = form.cleaned_data['employer']
        update_order = Order.objects.get(id=order.pk)
        emp_serv = OrderService.objects.get_or_create(order=order, service=service, employer=employer)[0]
        worker = CustomUser.objects.get(id=employer.pk)
        client = CustomUser.objects.get(id=order.client_id)
        emp_serv.confirmed_switch()

        old_count = emp_serv.count or 0
        old_amount = old_count * service.price or 0
        old_cost = old_count * service.cost_price or 0
        new_count = count
        new_amount = count * service.price
        new_cost = count * service.cost_price

        update_order.count -= old_count
        update_order.amount -= old_amount
        update_order.cost_price -= old_cost
        update_order.save()
        emp_serv.count -= old_count
        emp_serv.salary -= old_count * service.price
        emp_serv.save()
        worker.money -= old_cost
        worker.services_count -= old_count
        worker.save()
        client.money -= old_amount
        client.services_count -= old_count
        client.save()


        update_order.count += new_count
        update_order.amount += new_amount
        update_order.cost_price += new_cost
        update_order.save()
        emp_serv.count += new_count
        emp_serv.salary += new_count * service.price
        emp_serv.save()
        worker.money += new_cost
        worker.services_count += new_count
        worker.save()
        client.money += new_amount
        client.services_count += new_count
        client.save()


        return redirect('order_detail', pk=order.pk)

    def form_invalid(self, form):
        print(form.errors)

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
        client.services_count -= self.object.count
        client.save()
        worker = CustomUser.objects.get(id=self.object.employer_id)
        worker.money -= self.object.salary
        worker.services_count -= self.object.count
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


class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'crmapp/service_list.html'
    success_url = '/services/'


class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'crmapp/service_list.html'
    success_url = '/services/'


class ServiceDeleteView(DeleteView):
    model = Service
    success_url = '/services/'


class EmployerListView(ListView):
    model = CustomUser
    template_name = 'crmapp/employer_list.html'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='worker')


class EmployerDetailView(DetailView):
    model = CustomUser
    template_name = 'crmapp/employer_detail.html'

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='worker')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = OrderService.objects.filter(employer=self.object.id)
        print(OrderService.objects.filter(employer=self.object.id))
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
        context['operations_from'] = CashboxOperation.objects.filter(cashbox_from=self.object).order_by('date')
        context['operations_to'] = CashboxOperation.objects.filter(cashbox_to=self.object).order_by('date')
        context['users'] = CustomUser.objects.filter(user_type='worker')
        context['categories'] = CashboxCategory.objects.all()
        context['cashboxes_from'] = Cashbox.objects.exclude(id=self.object.id)
        context['cashboxes_to'] = Cashbox.objects.exclude(id=self.object.id)
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

    # def form_valid(self, form):
        # cashbox = Cashbox.objects.get()

    def form_invalid(self, form):
        print(form.errors)


class CashBoxSubtractOperationView(CreateView):
    model = CashboxOperation
    form_class = CashboxOperationForm
    template_name = 'crmapp/cashbox_detail.html'

    # def form_valid(self, form):
    #     cashbox = Cashbox.objects.get(order=self.object.order)

    def form_invalid(self, form):
        print(form.errors)



# def send_excel_document(request):
#     # Создаем новый Excel-документ с помощью библиотеки openpyxl
#     workbook = Workbook()
#     sheet = workbook.active
#
#     # Заполняем документ данными (пример)
#     sheet['A1'] = 'Hello'
#     sheet['B1'] = 'World!'
#
#     # Создаем файл-объект в памяти (io.BytesIO) и сохраняем в него Excel-документ
#     file_object = io.BytesIO()
#     workbook.save(file_object)
#     file_object.seek(0)
#
#     # Возвращаем файл-объект как HTTP-ответ с соответствующим заголовком
#     response = FileResponse(file_object, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename="example.xlsx"'
#
#
#
