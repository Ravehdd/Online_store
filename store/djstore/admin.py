from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "in_stock", "description", "price")
    list_display_links = ("id", "name", "in_stock",)
    # list_editable = ("is_published",)
    # list_filter = ("title", "time_create")
    # prepopulated_fields = {"slug": ("title",)}
    # fields = ("title", "slug", "cat", "content", "photo", "get_html_photo", "is_published", "time_create")
    # readonly_fields = ("time_create","get_html_photo")
    # save_on_top = True
#
#     def get_html_photo(self, object):
#         if object.photo:
#             return mark_safe(f"<img src='{object.photo.url}' width=200>")
#
#     get_html_photo.short_description = "Photo"
#
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ("id", "name")
#     list_display_links = ("name",)
#     prepopulated_fields = {"slug": ("name",)}
#
#
admin.site.register(Products, ProductsAdmin)
# admin.site.register(Cart, CategoryAdmin)