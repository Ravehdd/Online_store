from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField(null=False)
    description = models.TextField(null=True)
    in_stock = models.IntegerField()
    photo = models.ImageField(upload_to="photos/", null=True)
    is_published = models.BooleanField(default=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, null=True)

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
