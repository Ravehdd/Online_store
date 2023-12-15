from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import *
from pydantic import BaseModel


class ListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ("id", "name", "price", "description", "photo") #убрал поле in_stock


class SearchSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)


class AddToCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class SearchFilterSerializer(serializers.Serializer):
    category = serializers.ListField()
    price_interval = serializers.ListField()


class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    user_id = serializers.IntegerField()


class MakeOrderSerializer(serializers.Serializer):
    product_id = serializers.ListField()


class EmailVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField(max_value=9999, min_value=1000)


