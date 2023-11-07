from django.db import models


class Products(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField(null=False)
    in_stock = models.IntegerField()

    def __str__(self):
        return self.name


class Cart(models.Model):
    product_id = models.ForeignKey("Products", on_delete=models.PROTECT)
    user_id = models.IntegerField()
    amount = models.IntegerField()
