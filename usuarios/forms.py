# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm,UserChangeForm
from .models import Usuario, Persona, Estudiante
from django.forms.widgets import DateInput # Para el calendario en fecha_nacimiento
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives

class LoginForm(AuthenticationForm):
    # Sobreescribe el campo username para usar correo_institucional
    username = forms.EmailField(label="Correo Institucional", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['correo_institucional', 'password']

class PasswordResetCorreoInstitucionalForm(forms.Form):
    correo_institucional = forms.EmailField(label="Correo institucional", max_length=254)

    def get_users(self, correo_institucional):
        UserModel = get_user_model()
        active_users = UserModel._default_manager.filter(
            correo_institucional__iexact=correo_institucional, is_active=True
        )
        return (u for u in active_users if u.has_usable_password())

    def clean(self):
        correo = self.cleaned_data.get('correo_institucional')
        if not list(self.get_users(correo)):
            raise forms.ValidationError("No existe un usuario con ese correo institucional.")
        return self.cleaned_data

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        correo = self.cleaned_data["correo_institucional"]
        for user in self.get_users(correo):
            context = {
                'email': correo,
                'domain': domain_override or request.get_host(),
                'site_name': 'Sistema de Citas Médicas',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            subject = render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())
            body = render_to_string(email_template_name, context)
            user_email = correo
            email_message = EmailMultiAlternatives(subject, body, from_email, [user_email])
            email_message.send()

class EstudianteSignUpForm(forms.ModelForm):
    # Campos del Usuario
    correo_institucional = forms.EmailField(
        label="Correo Institucional",
        max_length=254,
        help_text='Debe terminar con @unsch.edu.pe',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Campos de Persona
    dni = forms.CharField(
        label="DNI (8 dígitos)",
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nombres = forms.CharField(
        label="Nombres",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    apellidos = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento",
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False # Puedes hacerlo requerido si deseas
    )
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    sexo = forms.ChoiceField(
        label="Sexo",
        choices=SEXO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    # Campos de Estudiante
    codigo_estudiante = forms.CharField(
        label="Código de Estudiante (8 dígitos)",
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ESCUELA_PROFESIONAL_CHOICES = [
        ('ADMINISTRACION_EMPRESAS', 'Administración de Empresas'),
        ('AGRONOMIA', 'Agronomía'),
        ('ANTROPOLOGIA', 'Antropología'),
        ('ARQUEOLOGIA_HISTORIA', 'Arqueología e Historia'),
        ('BIOLOGIA', 'Biología'),
        ('CIENCIAS_COMUNICACION', 'Ciencias de la Comunicación'),
        ('CIENCIAS_FISICOMATEMATICAS', 'Ciencias Físico-Matemáticas'),
        ('CONTABILIDAD_AUDITORIA', 'Contabilidad y Auditoría'),
        ('DERECHO', 'Derecho'),
        ('ECONOMIA', 'Economía'),
        ('EDUCACION FISICA','Educación Física'),
        ('EDUCACION_INICIAL', 'Educación Inicial'),
        ('EDUCACION_PRIMARIA', 'Educación Primaria'),
        ('EDUCACION_SECUNDARIA', 'Educación Secundaria'),
        ('ENFERMERIA', 'Enfermería'),
        ('FARMACIA_BIOQUIMICA', 'Farmacia y Bioquímica'),
        ('ING_AGROFORESTAL', 'Ingeniería Agroforestal'),
        ('ING_AGROINDUSTRIAL', 'Ingeniería Agroindustrial'),
        ('ING_AGRICOLA', 'Ingeniería Agrícola'),
        ('ING_CIVIL', 'Ingeniería Civil'),
        ('ING_MINAS', 'Ingeniería de Minas'),
        ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
        ('ING_ALIMENTARIAS','Ingeniería en Industrias Alimentarias'),
        ('ING_QUIMICA', 'Ingeniería Química'),
        ('MEDICINA_HUMANA', 'Medicina Humana'),
        ('MEDICINA_VETERINARIA', 'Medicina Veterinaria'),
        ('OBSTETRICIA', 'Obstetricia'),
        ('TRABAJO_SOCIAL', 'Trabajo Social'),
        
    ]
    escuela_profesional = forms.ChoiceField(
        label="Escuela Profesional",
        choices=ESCUELA_PROFESIONAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    semestre_academico = forms.CharField(
        label="Semestre Académico (ej. 2025-I)",
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario # El formulario se basa en Usuario, pero añadiremos datos de Persona y Estudiante
        fields = ['correo_institucional', 'password'] # Solo los campos de Usuario que se manejan directamente

    def clean_correo_institucional(self):
        # Aquí aplicamos la validación de dominio de UNSCH
        correo = self.cleaned_data['correo_institucional']
        if not correo.endswith('@unsch.edu.pe'):
            raise forms.ValidationError('El correo institucional debe terminar con @unsch.edu.pe')
        if Usuario.objects.filter(correo_institucional=correo).exists():
            raise forms.ValidationError('Este correo institucional ya está registrado.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")

        # Validar DNI y Código de Estudiante usando los validadores del modelo
        dni = cleaned_data.get('dni')
        codigo_estudiante = cleaned_data.get('codigo_estudiante')

        if dni:
            if not dni.isdigit() or len(dni) != 8:
                self.add_error('dni', 'El DNI debe contener 8 dígitos numéricos.')
            elif Persona.objects.filter(dni=dni).exists():
                self.add_error('dni', 'Ya existe una persona registrada con este DNI.')

        if codigo_estudiante:
            if not codigo_estudiante.isdigit() or len(codigo_estudiante) != 8:
                self.add_error('codigo_estudiante', 'El código de estudiante debe contener 8 dígitos numéricos.')
            elif Estudiante.objects.filter(codigo_estudiante=codigo_estudiante).exists():
                self.add_error('codigo_estudiante', 'Ya existe un estudiante registrado con este código.')

        return cleaned_data

    def save(self, commit=True):
        # Crea el objeto Usuario
        user = Usuario.objects.create_user(
            correo_institucional=self.cleaned_data['correo_institucional'],
            password=self.cleaned_data['password'],
            es_estudiante=True, # Asegúrate de que este usuario es un estudiante
            es_personal_salud=False
        )

        # Crea el objeto Persona asociado
        persona = Persona.objects.create(
            usuario=user,
            dni=self.cleaned_data['dni'],
            nombres=self.cleaned_data['nombres'],
            apellidos=self.cleaned_data['apellidos'],
            fecha_nacimiento=self.cleaned_data.get('fecha_nacimiento'),
            sexo=self.cleaned_data.get('sexo')
        )

        # Crea el objeto Estudiante asociado
        estudiante = Estudiante.objects.create(
            persona=persona,
            codigo_estudiante=self.cleaned_data['codigo_estudiante'],
            escuela_profesional=self.cleaned_data['escuela_profesional'],
            semestre_academico=self.cleaned_data['semestre_academico']
        )
        return user # Devuelve el usuario creado
    
class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        # Define los campos que aparecerán al CREAR un nuevo usuario en el admin
        fields = ('correo_institucional', 'es_estudiante', 'es_personal_salud') # Campos adicionales para roles
        
    
class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        # Define los campos que aparecerán al EDITAR un usuario existente en el admin
        fields = ('correo_institucional', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'es_estudiante', 'es_personal_salud')

