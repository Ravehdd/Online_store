import sqlite3

from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponseNotFound
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *


class ProductsAPIView(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ListViewSerializer
    permission_classes = (IsAuthenticated,)

    # def get(self, request):
    #     data = Products.objects.values()
    #     products = [ListViewModel(**item) for item in data]
    #     result = [model.model_dump() for model in products]
    #     print(result)
    #     return Response(result)


class AddToCartAPI(APIView):
    def post(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        auth_type, auth_token = auth_header.split(" ")

        # data = SearchModel(**request.data)
        # print(data)
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["id"]

        with (sqlite3.connect("db.sqlite3") as connection):
            cursor = connection.cursor()
            cursor.execute(f"SELECT user_id FROM authtoken_token WHERE key='{auth_token}'")
            user_id = cursor.fetchone()[0]

        try:
            same_product = Cart.objects.get(product_id=product_id, user_id=user_id)
            amount = same_product.amount
            same_product.amount = amount + 10
            same_product.save()
            return Response({"status": 204, "response": "Updated successfully"})
        except:
            Cart.objects.create(product_id=product_id, user_id=user_id, amount=1)
            return Response({"status": 200, "response": "The product has been successfully added to the cart"})


class SearchAPI(generics.ListAPIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid()
        product_name = request.data["product_name"]
        product_name_split = product_name.split(" ")
        matches = []
        unique_matches = []
        for name in product_name_split:
            match = Products.objects.filter(name__icontains=name).values()
            matches.extend(match)
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)

        return Response({"status": 200, "search_result": unique_matches})


class RemoveFromCartAPI(APIView):
    def post(self, request):
        serializer = RemoveFromCartSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["product_id"]
        user_id = request.data["user_id"]
        try:
            product_on_delete = Cart.objects.get(product_id=product_id, user_id=user_id)
            product_on_delete.delete()
            return Response({"status": 204, "response": "Deleted successfully"})
        except:
            return Response({"status": 404, "response": "Record not found"})


class CartViewAPI(APIView):
    def get(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        auth_type, auth_token = auth_header.split(" ")
        with (sqlite3.connect("db.sqlite3") as connection):
            cursor = connection.cursor()
            cursor.execute(f"SELECT user_id FROM authtoken_token WHERE key='{auth_token}'")
            user_id = cursor.fetchone()[0]
        products = Cart.objects.filter(user_id=user_id).values()
        return Response(products)


def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found!</h1>")

