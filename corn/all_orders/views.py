from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import ExpenseOrder
from .forms import ExpenseOrderForm, ExpenseOrderApproveForm

class ExpenseOrderListView(LoginRequiredMixin, ListView):
    model = ExpenseOrder
    template_name = 'all_orders/expense_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class ExpenseOrderCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseOrder
    form_class = ExpenseOrderForm
    template_name = 'all_orders/expense_order_form.html'
    success_url = reverse_lazy('expense_order_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Расходный ордер успешно создан')
        return super().form_valid(form)

class ExpenseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseOrder
    form_class = ExpenseOrderForm
    template_name = 'all_orders/expense_order_form.html'
    success_url = reverse_lazy('expense_order_list')

    def form_valid(self, form):
        if form.instance.status != 'draft':
            messages.error(self.request, 'Редактирование возможно только для черновиков')
            return super().form_invalid(form)
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)

class ExpenseOrderDetailView(LoginRequiredMixin, DetailView):
    model = ExpenseOrder
    template_name = 'all_orders/expense_order_detail.html'
    context_object_name = 'order'

class ExpenseOrderApproveView(LoginRequiredMixin, UpdateView):
    model = ExpenseOrder
    form_class = ExpenseOrderApproveForm
    template_name = 'all_orders/expense_order_approve.html'
    success_url = reverse_lazy('expense_order_list')

    def form_valid(self, form):
        form.instance.status = 'approved'
        form.instance.approved_by = self.request.user
        messages.success(self.request, 'Ордер утвержден')
        return super().form_valid(form)

def execute_order(request, pk):
    order = get_object_or_404(ExpenseOrder, pk=pk)
    if order.status != 'approved':
        messages.error(request, 'Можно исполнять только утвержденные ордера')
    else:
        order.status = 'executed'
        order.save()
        messages.success(request, 'Ордер исполнен')
    return redirect('expense_order_list')