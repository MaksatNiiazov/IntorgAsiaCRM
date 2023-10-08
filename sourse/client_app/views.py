from django.views.generic import DetailView, ListView
from crm_app.models import Order, ServiceOrder, OrderConsumables, Cashbox
from crm_app.views import Locked
from crm_warehouse.models import Product, EmployerProduct


class UnpackingClientView(Locked, DetailView):
    template_name = 'client/unpacking.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(UnpackingClientView, self).get_context_data()
        context['products'] = Product.objects.filter(order_id=self.object.id)
        return context


class OrderListClientView(Locked, ListView):
    model = Order
    template_name = 'client/my_orders.html'
    ordering = ['-date']
    paginate_by = 20

    def get_queryset(self):
        return Order.objects.filter(client_id=self.request.user.id)


class OrderDetailClientView(Locked, DetailView):
    model = Order
    template_name = 'client/my_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = ServiceOrder.objects.filter(order=self.object.id)
        context['products'] = EmployerProduct.objects.filter(product__order_id=self.object.id)
        context['consumables_in_order'] = OrderConsumables.objects.filter(order=self.object)
        context['cashboxes'] = Cashbox.objects.all()
        if self.object.amount == 0 and self.object.stage == 'dispatched':
            context['next_stage'] = True
        order = self.get_object()
        revenue = order.amount - order.cost_price

        context['revenue'] = revenue
        return context


class ReferalListView(ListView):
    model = Order
    template_name = 'client/referal.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.filter(client__referral__isnull=False)
        return Order.objects.filter(client__referral_id=self.request.user.id,)# stage='closed')
