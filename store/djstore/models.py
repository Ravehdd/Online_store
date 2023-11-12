from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField(null=False)
    description = models.TextField(null=True)
    in_stock = models.IntegerField()
    photo = models.ImageField(upload_to="photos/", null=True)

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
