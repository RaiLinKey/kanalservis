from django.db import models


# Create your models here.
class SheetData(models.Model):
    order_no = models.IntegerField()
    usd_price = models.IntegerField()
    delivery_time = models.DateField()
    rub_price = models.IntegerField()
