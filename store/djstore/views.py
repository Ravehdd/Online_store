import sqlite3
import os

from django.db.models import Max, Min, Q
from django.http import HttpResponseNotFound
import random
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def getToken(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    auth_type, auth_token = auth_header.split(" ")

    with (sqlite3.connect("db.sqlite3") as connection):
        cursor = connection.cursor()
        cursor.execute(f"SELECT user_id FROM authtoken_token WHERE key='{auth_token}'")
        user_id = cursor.fetchone()[0]
    return user_id


class ProductsAPIView(generics.ListAPIView):
    queryset = Products.objects.filter(is_published=True).all()
    serializer_class = ListViewSerializer
    # permission_classes = (IsAuthenticated,)


class ProductPageAPI(APIView):
    def post(self, request):
        serializer = ProductViewSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["id"]
        product = Products.objects.filter(id=product_id).values()
        feedback = Feedback.objects.filter(id=product_id).values()
        return Response({"status": 200, "data": {"product": product, "feedback": feedback}})


class AddToCartAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = getToken(request)
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["id"]

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
        countries = request.data["countries"]
        wars = request.data["wars"]

        if price_interval:
            products_sort_price = Products.objects.filter(
                Q(price__gte=sorted(price_interval)[0]) & Q(price__lte=sorted(price_interval)[1])).order_by()
        else:
            products_sort_price = Products.objects.all().order_by()
        if selected_categories:
            category_ids = Category.objects.filter(cat_name__in=selected_categories).values_list("id", flat=True)
            products_sort_id = Products.objects.filter(category_id__in=category_ids).order_by()
        else:
            products_sort_id = Products.objects.all().order_by()
        if wars:
            war_ids = War.objects.filter(war_name__in=wars).values_list("id", flat=True)
            product_ids = Products.objects.all().values_list("id", flat=True)
            product_ids_match = []
            for product_id in product_ids:
                with (sqlite3.connect("db.sqlite3") as connection):
                    cursor = connection.cursor()

                    cursor.execute(f"SELECT war_id FROM djstore_products_war WHERE products_id = {product_id}")
                    war_id_found_tuple = cursor.fetchall()
                    war_id_found = [w[0] for w in war_id_found_tuple]

                    war_set_1 = set(war_ids)
                    war_set_2 = set(war_id_found)

                    if war_set_1.issubset(war_set_2):
                        product_ids_match.append(product_id)

            products_sort_war = Products.objects.filter(id__in=product_ids_match).order_by()
        else:
            products_sort_war = Products.objects.all().order_by()

        if countries:
            country_ids = Country.objects.filter(country_name__in=countries).values_list("id", flat=True)
            products_sort_country = Products.objects.filter(country_id__in=country_ids).order_by()
        else:
            products_sort_country = Products.objects.all().order_by()

        products = products_sort_id.intersection(products_sort_country).values()
        products2 = products_sort_war.intersection(products_sort_price).values()
        products3 = products.intersection(products2)

        return Response({"status": 200, "data": products3})


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
        user_id = getToken(request)

        products = Cart.objects.filter(user_id=user_id).values("product_id", "amount")
        products_info = []
        for product in products:
            product_id = product["product_id"]
            product_amount = product["amount"]
            product_info = dict(Products.objects.filter(id=product_id).values("name", "price", "description", "photo")[0])
            product_info["amount"] = product_amount
            products_info.append(product_info)
        return Response({"status": 200, "data": products_info})


class OrderViewAPI(APIView):
    def get(self, request):
        user_id = getToken(request)
        products_id = Order.objects.filter(user_id=user_id).values_list("product_id", flat=True)

        if not products_id:
            return Response({"status": 404, "response": "Orders is not found"})

        products = Products.objects.filter(id__in=products_id).values("name", "price", "photo")
        return Response({"status": 200, "data": products})


class MakeOrderAPI(APIView):
    def get(self, request):
        user_id = getToken(request)
        is_verify = Verify.objects.filter(user_id=user_id).values("verify")[0]["verify"]
        if not is_verify:
            return Response({"status": 403, "response": "User is not verify"})
        receiver_email = User.objects.filter(id=user_id).values("email")[0]["email"]

        product_id = Cart.objects.filter(user_id=user_id).values_list("product_id", flat=True)
        print(product_id)

        # serializer = MakeOrderSerializer(data=request.data)
        # serializer.is_valid()
        # product_id = request.data["product_id"]
        if not product_id:
            return Response({"status": "pizda", "response": "Cart is empty"})
        products = Products.objects.filter(id__in=product_id).values()

        smtp_server = 'smtp.gmail.com'
        port = 587
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()

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

            for p in product_id:
                Order.objects.create(user_id=user_id, product_id=p)
            products = Cart.objects.filter(user_id=user_id)
            products.delete()

        except Exception as e:
            print('Произошла ошибка при отправке сообщения:', e)

        finally:
            server.quit()

        return Response({"status": 200, "response": "Request to order have been sent successfully! Wait for response on your email."})


class EmailVerify(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = getToken(request)
        user = Verify.objects.filter(user_id=user_id)
        if user:
            return Response({"status": 400, "response": "User already verify"})

        email = User.objects.filter(id=user_id).values("email")[0]["email"]

        smtp_server = 'smtp.gmail.com'
        port = 587
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        sender_email = os.getenv("EMAIL_HOST_USER")
        sender_password = os.getenv("EMAIL_HOST_PASSWORD")
        try:
            server.login(sender_email, sender_password)

            table = '<table><tr><th>Код подтверждения</th></tr>'
            verify_code = random.randint(1000, 9999)
            EmailVerifyCode.objects.create(user_id=user_id, verify_code=verify_code)
            table += f'<tr><td>{verify_code}</td></tr>'

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "Подтверждение почты"
            body = MIMEText(table, "html")
            msg.attach(body)
            server.send_message(msg)
            print('Сообщение отправлено успешно!')

        except Exception as e:
            print('Произошла ошибка при отправке сообщения:', e)

        finally:
            server.quit()

        return Response({"email": email})

    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid()
        user_id = getToken(request)
        user_code = int(request.data["code"])
        verify_code = EmailVerifyCode.objects.filter(user_id=user_id).values("verify_code")[0]["verify_code"]

        if user_code == verify_code:
            Verify.objects.create(verify=True, user_id=user_id)
            return Response({"status": "200", "response": "The user has been successfully verified"})
        else:
            return Response({"status": "400", "response": "Verify code is wrong"})


class FeedbackAPI(APIView):
    def post(self, request):
        user_id = getToken(request)
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid()
        product_id = request.data["product_id"]
        feedback = request.data["feedback"]
        is_order = Order.objects.filter(Q(user_id=user_id) & Q(product_id=product_id))
        if is_order:
            Feedback.objects.create(user_id=user_id, product_id=product_id, feedback=feedback)
            return Response({"status": 201, "response": "Feedback has been added successfully"})
        else:
            return Response({"status": 400, "response": "Order with this product is not found"})


def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found!</h1>")



