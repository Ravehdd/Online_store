from django.db import models
from django.contrib.auth.models import User


class Products(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField(null=False)
    description = models.TextField(null=True)
    # in_stock = models.IntegerField()
    photo = models.ImageField(upload_to="photos/", null=True)
    is_published = models.BooleanField(default=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, null=True)
    country = models.ForeignKey("Country", on_delete=models.PROTECT, null=True)
    war = models.ManyToManyField("War", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["id"]


class Cart(models.Model):
    product = models.ForeignKey("Products", on_delete=models.PROTECT)
    user_id = models.IntegerField()
    amount = models.IntegerField()


class Category(models.Model):
    cat_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cat_name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["id"]


class OrderData(models.Model):
    product_id = models.ForeignKey("Products", on_delete=models.PROTECT)
    user_id = models.IntegerField()


class Verify(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    verify = models.BooleanField(default=False)


class Country(models.Model):
    country_name = models.CharField(max_length=255)

    def __str__(self):
        return self.country_name


class War(models.Model):
    war_name = models.CharField(max_length=255)

    def __str__(self):
        return self.war_name

#
# class WarModelConnection(models.Model):
#     model = models.ForeignKey("Products", on_delete=models.PROTECT)
#     war = models.ForeignKey("War", on_delete=models.PROTECT)


class EmailVerifyCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    verify_code = models.IntegerField()