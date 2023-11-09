from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import *


class ListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ("name", "price", "description", "in_stock")


class AddToCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()