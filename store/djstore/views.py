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

    def post(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        auth_type, auth_token = auth_header.split(" ")

        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["id"]

        with (sqlite3.connect("db.sqlite3") as connection):
            cursor = connection.cursor()
            cursor.execute(f"SELECT user_id FROM authtoken_token WHERE key='{auth_token}'")
            user_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO djstore_cart(product_id, user_id, amount) VALUES(?, ?, ?)", (product_id, user_id, 1))

        return Response("Товар успешно добавлен в корзину")


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

        return Response({"search_result": unique_matches})


def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found!</h1>")

