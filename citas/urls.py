# citas/urls.py
from django.urls import path
from . import views

app_name = 'citas' # Nombre del namespace para esta app

urlpatterns = [
    path('solicitar/', views.solicitar_cita, name='solicitar_cita'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),
    path('personal-salud/citas/', views.citas_personal_salud, name='citas_personal_salud'),
    path('personal-salud/citas/<int:cita_id>/detalle/', views.detalle_cita_personal_salud, name='detalle_cita_personal_salud'),
]