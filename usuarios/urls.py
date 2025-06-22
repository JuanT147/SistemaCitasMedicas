# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios' # Nombre del namespace para esta app

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro-estudiante/', views.registro_estudiante_view, name='registro_estudiante'),
    path('estudiante/dashboard/', views.dashboard_estudiante, name='dashboard_estudiante'),
    path('personal-salud/dashboard/', views.dashboard_personal_salud, name='dashboard_personal_salud'),
]