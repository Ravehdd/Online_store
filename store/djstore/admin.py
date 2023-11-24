from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "price", "get_html_photo", "is_published")
    list_display_links = ("id", "name")
    list_editable = ("is_published",)
    # list_filter = ("title", "time_create")
    # prepopulated_fields = {"slug": ("title",)}
    # fields = ("title", "slug", "cat", "content", "photo", "get_html_photo", "is_published", "time_create")
    # readonly_fields = ("time_create","get_html_photo")
    # save_on_top = True

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=200>")

    get_html_photo.short_description = "Photo"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "cat_name")
    list_display_links = ("cat_name", )


admin.site.register(Products, ProductsAdmin)
admin.site.register(Category, CategoryAdmin)
