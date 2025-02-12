from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'model', 'release_date']


class NetworkNodeSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=NetworkNode.objects.all(), allow_null=True)

    class Meta:
        model = NetworkNode
        fields = ['id', 'name', 'level', 'email', 'country', 'city', 'street', 'house_number', 'products', 'supplier', 'debt', 'created_at']
        read_only_fields = ['debt', 'created_at']

    def update(self, instance, validated_data):
        validated_data.pop('debt', None)  # Удаляем поле debt из данных обновления
        return super().update(instance, validated_data)