# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Para mostrar mensajes al usuario
from .forms import LoginForm, EstudianteSignUpForm, PasswordResetCorreoInstitucionalForm
from .models import Usuario # Asegúrate de importar tu modelo Usuario
from citas.models import Cita ,Derivacion


def login_view(request):
    if request.user.is_authenticated:
        # Si el usuario ya está autenticado, redirigir a su dashboard
        if request.user.es_estudiante:
            return redirect('usuarios:dashboard_estudiante')
        elif request.user.es_personal_salud:
            return redirect('usuarios:dashboard_personal_salud')
        else: # Admin u otros usuarios sin rol específico
            return redirect('/admin/') # O a una página genérica

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            correo_institucional = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, correo_institucional=correo_institucional, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.correo_institucional}!')
                # Redirigir según el rol
                if user.es_estudiante:
                    return redirect('usuarios:dashboard_estudiante')
                elif user.es_personal_salud:
                    return redirect('usuarios:dashboard_personal_salud')
                else:
                    # Si no es estudiante ni personal de salud (ej. superusuario creado),
                    # puedes redirigirlo a /admin/ o a una página genérica
                    return redirect('/admin/')
            else:
                messages.error(request, 'Correo institucional o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:login') # Redirigir a la página de login

class PasswordResetCorreoInstitucionalView(PasswordResetView):
    form_class = PasswordResetCorreoInstitucionalForm
    template_name = 'registration/password_reset_form.html'  # Puedes personalizar esta plantilla
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

def registro_estudiante_view(request):
    if request.method == 'POST':
        form = EstudianteSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Tu cuenta de estudiante ha sido creada exitosamente! Por favor, inicia sesión.')
            return redirect('usuarios:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        form = EstudianteSignUpForm()
    return render(request, 'usuarios/registro_estudiante.html', {'form': form})

@login_required # Decorador para asegurar que solo usuarios logueados accedan
def dashboard_estudiante(request):
    if not request.user.es_estudiante:
        messages.warning(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:login') # O a un dashboard genérico

    # Aquí podríamos cargar datos específicos del estudiante
    estudiante = None
    try:
        estudiante = request.user.persona.estudiante
    except Usuario.persona.RelatedObjectDoesNotExist: # Usar la excepción correcta
        messages.error(request, 'No se encontró el perfil de estudiante asociado a tu cuenta.')
        return redirect('usuarios:login') # Redirigir si no hay perfil de estudiante

    context = {
        'estudiante': estudiante,
        'user': request.user,
    }
    return render(request, 'usuarios/dashboard_estudiante.html', context)

@login_required
def dashboard_personal_salud(request):
    if not request.user.es_personal_salud:
        messages.warning(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:login') # O a un dashboard genérico

    personal_salud = request.user.persona.personalsalud
    especialidad = personal_salud.especialidad 
    
    
    try:
        personal_salud = request.user.persona.personalsalud
    except Usuario.persona.RelatedObjectDoesNotExist: # Usar la excepción correcta
        messages.error(request, 'No se encontró el perfil de personal de salud asociado a tu cuenta.')
        return redirect('usuarios:login') # Redirigir si no hay perfil de personal de salud
    
    
    # Citas directas (asignadas a este personal de salud)
    citas_directas = Cita.objects.filter(personal_salud=personal_salud)

    # Citas derivadas (donde la especialidad destino es la del usuario)
    derivaciones = Derivacion.objects.filter(servicio_destino=especialidad)
    citas_derivadas = [d.cita_origen for d in derivaciones]

    # Unir ambas listas y eliminar duplicados
    todas_citas = list(set(list(citas_directas) + citas_derivadas))
    
    context = {
        # new
        'citas': todas_citas,  # Unir citas directas y derivadas
        # end new
        'personal_salud': personal_salud,
        'user': request.user,
    }
    return render(request, 'usuarios/dashboard_personal_salud.html', context)
