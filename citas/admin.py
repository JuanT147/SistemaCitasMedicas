# citas/admin.py
from django.contrib import admin
from .models import Cita, Derivacion

admin.site.register(Cita)
admin.site.register(Derivacion)
