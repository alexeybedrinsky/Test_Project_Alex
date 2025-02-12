import django_filters
from .models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    class Meta:
        model = NetworkNode
        fields = ['country']