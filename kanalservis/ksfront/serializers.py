from rest_framework import serializers
from .models import SheetData


class SheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheetData
        fields = ('id', 'order_no', 'usd_price', 'delivery_time', 'rub_price')
