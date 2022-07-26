from django.shortcuts import render
from .models import SheetData
from .serializers import SheetSerializer
from rest_framework import generics


# Create your views here.
class SheetListCreate(generics.ListCreateAPIView):
    queryset = SheetData.objects.all()
    serializer_class = SheetSerializer

