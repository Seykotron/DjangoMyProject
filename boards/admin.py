from django.contrib import admin
from .models import Board

# Register your models here.

# Registro el modelo para poder administrarlo desde el admin site
admin.site.register(Board)
