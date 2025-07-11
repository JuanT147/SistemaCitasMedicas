"""
URL configuration for SistemaCitasMedicas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView # Importa RedirectView
from usuarios.views import PasswordResetCorreoInstitucionalView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Redirige la raíz '/' a la página de login de la app 'usuarios'
    path('', RedirectView.as_view(pattern_name='usuarios:login', permanent=True)),
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='admin_logout'),
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')), # Incluye las URLs de la app usuarios
    path('citas/', include('citas.urls')), # <-- Incluye las URLs de la app citas bajo el prefijo 'citas/'
    path('password_reset/', PasswordResetCorreoInstitucionalView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
