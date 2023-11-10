from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import *


class ListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ("name", "price", "description", "in_stock")


class SearchSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)


class AddToCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
