from django.shortcuts import render, HttpResponse
from django.http import HttpResponseNotFound


def index(request):
    return HttpResponse("<h1>Main page</h1>")


def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found!</h1>")

