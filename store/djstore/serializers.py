from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import *
from pydantic import BaseModel


# class ListViewModel(BaseModel):
#     name: str
#     price: int
#     description: str
#     in_stock: int
#
#
# class SearchModel(BaseModel):
#     product_name: str


class ListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ("name", "price", "description", "in_stock")


class SearchSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)


class AddToCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    user_id = serializers.IntegerField()