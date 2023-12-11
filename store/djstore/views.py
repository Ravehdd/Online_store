import sqlite3
import os
from dotenv import load_dotenv
import requests
from django.db.models import Max, Min, Q
from django.http import HttpResponseNotFound, HttpResponse
from django.template.loader import render_to_string
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from .config import sender_email, sender_password


def getToken(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    auth_type, auth_token = auth_header.split(" ")
    return auth_token


class ProductsAPIView(generics.ListAPIView):
    queryset = Products.objects.filter(is_published=True).all()
    serializer_class = ListViewSerializer
    # permission_classes = (IsAuthenticated,)


class AddToCartAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        auth_token = getToken(request)
        # auth_header = request.META.get("HTTP_AUTHORIZATION")
        # auth_type, auth_token = auth_header.split(" ")
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
            same_product.amount = amount + 1
            same_product.save()
            return Response({"status": 204, "response": "Updated successfully"})
        except:
            Cart.objects.create(product_id=product_id, user_id=user_id, amount=1)
            return Response({"status": 200, "response": "The product has been successfully added to the cart"})


class SearchAPI(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

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

        return Response({"status": 200, "data": unique_matches})


class SearchFilterAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        categories = Category.objects.values_list("cat_name", flat=True)
        price_interval = Products.objects.aggregate(Min("price"), Max("price")).values()
        countries = Country.objects.all().values_list("country_name", flat=True)
        wars = War.objects.all().values_list("war_name", flat=True)
        return Response({"status": 200, "data": [{"categories": categories}, {"price_interval": price_interval},
                                                 {"countries": countries}, {"wars": wars}]})


    def post(self, request):
        serializer = SearchFilterSerializer(data=request.data)
        serializer.is_valid()
        selected_categories = request.data["category"]
        price_interval = request.data["price_interval"]

        if selected_categories:
            category_ids = Category.objects.filter(cat_name__in=selected_categories).values_list("id", flat=True)
            products_sort_id = Products.objects.filter(category_id__in=category_ids).order_by()

            if price_interval:
                products_sort_price = Products.objects.filter(
                    Q(price__gte=sorted(price_interval)[0]) & Q(price__lte=sorted(price_interval)[1])).order_by()
                products = products_sort_id.intersection(products_sort_price).values()
                print(products)

                return Response({"status": 200, "data": products})

        if price_interval:
            products_sort_price = Products.objects.filter(
                Q(price__gte=sorted(price_interval)[0]) & Q(price__lte=sorted(price_interval)[1]))

            return Response({"status": 200, "data": products_sort_price})

        products = Products.objects.all().values()
        return Response({"status": 200, "data": products})


class RemoveFromCartAPI(APIView):
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        auth_token = getToken(request)

        with (sqlite3.connect("db.sqlite3") as connection):
            cursor = connection.cursor()
            cursor.execute(f"SELECT user_id FROM authtoken_token WHERE key='{auth_token}'")
            user_id = cursor.fetchone()[0]
        products = Cart.objects.filter(user_id=user_id).values("product_id", "amount")
        products_info = []
        for product in products:
            product_id = product["product_id"]
            product_amount = product["amount"]
            product_info = dict(Products.objects.filter(id=product_id).values("name", "price", "description", "photo")[0])
            product_info["amount"] = product_amount
            products_info.append(product_info)
        return Response({"status": 200, "data": products_info})


class MakeOrderAPI(APIView):
    def post(self, request):

        with (sqlite3.connect("db.sqlite3") as connection):
            auth_token = getToken(request)
            cursor = connection.cursor()
            cursor.execute(f"SELECT user_id FROM authtoken_token WHERE key='{auth_token}'")
            user_id = cursor.fetchone()[0]

        receiver_email = User.objects.filter(id=user_id).values("email")[0]["email"]


        serializer = MakeOrderSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["product_id"]
        if not product_id:
            return Response({"status": "pizda"})
        products = Products.objects.filter(id__in=product_id).values()
        # print(products)

        smtp_server = 'smtp.gmail.com'
        port = 587
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
        # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
        sender_email = os.getenv("EMAIL_HOST_USER")
        sender_password = os.getenv("EMAIL_HOST_PASSWORD")
        try:
            server.login(sender_email, sender_password)

            table = '<table><tr><th>Название</th><th>Цена</th></tr>'
            for product in products:
                table += f'<tr><td>{product["name"]}</td><td>{product["price"]}</td></tr>'
            table += '</table>'
            table += "Контакты заказчика: " + receiver_email
            # print(table)
            # server.sendmail(sender_email, sender_email, table)
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email
            msg['Subject'] = "Заявка на заказ"
            body = MIMEText(table, "html")
            msg.attach(body)
            server.send_message(msg)
            print('Сообщение отправлено успешно!')

        except Exception as e:
            print('Произошла ошибка при отправке сообщения:', e)

        finally:
            server.quit()

        return Response({"status": 200, "response": "Request to order have been sent successfully! Wait for response on your email."})




def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found!</h1>")



