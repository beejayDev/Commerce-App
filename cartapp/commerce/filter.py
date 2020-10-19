import django-filters
from .models import *

class OrderFilter(django_filters.FilterSet):
    class Meta:
        models = Order
        fields =  '__all__'

