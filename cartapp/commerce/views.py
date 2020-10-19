from django.shortcuts import render, redirect
from django.http import HttpResponse
#from django.forms import inlineformset_factory
from .models import *
from .forms import orderForm, creationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_user, admin_only
from django.contrib.auth.models import Group

# Create your views here.

@unauthenticated_user
def register(request):
    form = creationForm()
    print(request)
    if request.method == 'POST':
        form = creationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}")
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
         username = request.POST.get('username')
         password = request.POST.get('password')

         user = authenticate(request, username=username, password=password)
         if user is not None:
             login(request, user)
             return redirect('home')
         else:
             messages.info(request,'Incorrect username/password')

    context = {}
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url="login")
@allowed_user(allowed_roles=['customer'])
def userPage(request):
    order = request.user.customer.order_set.all()
    context = {
            'order': order,
            'total_order': Order.objects.all().count(), 
            'delivered': Order.objects.filter(status='Delivered').count(),
            'pending': Order.objects.filter(status='Pending').count()
            }

    return render(request, 'user.html', context)

@login_required(login_url="login")
@admin_only
def home(request):
    context = {
            'product': Product.objects.all(),
            'order': Order.objects.all(),
            'customers': Customer.objects.all(),
            'total_customer': Customer.objects.all().count(),
            'total_order': Order.objects.all().count(),
            'delivered': Order.objects.filter(status='Delivered').count(),
            'pending': Order.objects.filter(status='Pending').count()
        }
    return render(request, 'dashboard.html', context)

@login_required(login_url="login")
@allowed_user(allowed_roles=['admin'])
def product(request):
    context = {
            'product':Product.objects.all()
        }
    return render(request, 'product.html', context)

@login_required(login_url="login")
@allowed_user(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)

    order = customer.order_set.all()

    order_count = order.count()
    context = {
            'customer': customer,
            'order': order,
            'order_count': order_count
            }
    return render(request, 'customer.html', context)

@login_required(login_url="login")
@allowed_user(allowed_roles=['admin'])
def createOrder(request, pk):
    #OrderFormSet = inlineformset_factory(Customer, Order, fields=('order', 'status'), extra=10)
    #formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    customer = Customer.objects.get(id=pk)
    form = orderForm(initial={'customer': customer})
    if request.method == "POST":
        form = orderForm(request.POST)
        print(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
            'form': form
            }
    return render(request, 'order.html', context)

@login_required(login_url="login")
@allowed_user(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = orderForm(instance=order)
    if request.method == "POST":
        form = orderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
            'form': form
            }

    return render(request, 'order.html', context)

@login_required(login_url="login")
@allowed_user(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('home')

    context = {
            'items':order
            }
    return render(request, 'delete.html', context)
