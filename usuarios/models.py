# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator, validate_email
from django.core.exceptions import ValidationError 
from servicios.models import EspecialidadMedica 


# Validador para DNI (8 dígitos numéricos)
dni_validator = RegexValidator(r'^\d{8}$', 'El DNI debe contener 8 dígitos numéricos.')

# Validador para Código de Estudiante (8 dígitos numéricos)
codigo_estudiante_validator = RegexValidator(r'^\d{8}$', 'El código de estudiante debe contener 8 dígitos numéricos.')

# ----- NUEVA FUNCIÓN DE VALIDACIÓN PARA CORREO INSTITUCIONAL -----
def validate_unsch_email(value):
    if not value.endswith('@unsch.edu.pe'):
        raise ValidationError(
            'El correo institucional debe terminar con @unsch.edu.pe',
            code='invalid_unsch_email'
        )

class CustomUserManager(BaseUserManager):
    def create_user(self, correo_institucional, password=None, **extra_fields):
        if not correo_institucional:
            raise ValueError('El correo institucional es obligatorio.')

        user = self.model(correo_institucional=correo_institucional, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo_institucional, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('es_estudiante', False)
        extra_fields.setdefault('es_personal_salud', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(correo_institucional, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    # Aplica el validador directamente al campo
    correo_institucional = models.EmailField(
        unique=True,
        help_text='Correo institucional de la universidad',
        validators=[validate_unsch_email] # <-- Añade el validador aquí
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    es_estudiante = models.BooleanField(default=False)
    es_personal_salud = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'correo_institucional'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'

    def __str__(self):
        return self.correo_institucional

    def get_full_name(self):
        return self.correo_institucional

    def get_short_name(self):
        return self.correo_institucional

    # Métodos para permisos (Django los espera si usas PermissionsMixin)
    # Aunque PermissionsMixin ya los provee, a veces se redefinen para claridad.
    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser # O lógica de permisos más compleja

    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser # O lógica de permisos más compleja


class Persona(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    # Un campo para el DNI con validador y único
    dni = models.CharField(max_length=8, unique=True, validators=[dni_validator], help_text='DNI de 8 dígitos')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100) # Django soporta CharField para apellidos con espacios
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)

    # Relación One-to-One con el Usuario personalizado
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=False) # primary_key=False para no hacer de Persona.id el PK del Usuario

    class Meta:
        verbose_name = 'Datos Personales'
        verbose_name_plural = 'Datos Personales'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Estudiante(models.Model):
    # Relación One-to-One con Persona para heredar los datos comunes
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, primary_key=True)
    codigo_estudiante = models.CharField(max_length=8, unique=True, validators=[codigo_estudiante_validator], help_text='Código único de estudiante de 8 dígitos')

    ESCUELA_PROFESIONAL_CHOICES = [
        #  28 escuelas profesionales. 
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
    escuela_profesional = models.CharField(max_length=100, choices=ESCUELA_PROFESIONAL_CHOICES)

    # Semestre Académico (ejemplo: 2025-I)
    semestre_academico = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f"{self.persona.nombres} {self.persona.apellidos} ({self.codigo_estudiante})"


class PersonalSalud(models.Model):
    # Relación One-to-One con Persona
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, primary_key=True)

    # La especialidad se definirá en la app 'servicios', así que la FK va aquí
    # Por ahora, un CharField, luego será una ForeignKey a EspecialidadMedica
    especialidad = models.ForeignKey(EspecialidadMedica, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_asignado')


    # Esta FK la añadiremos en la app 'servicios' para evitar dependencias circulares
    # especialidad = models.ForeignKey('servicios.EspecialidadMedica', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Personal de Salud'
        verbose_name_plural = 'Personal de Salud'

    def __str__(self):
        especialidad_nombre = self.especialidad.nombre if self.especialidad else 'Sin Especialidad'
        return f"{self.persona.nombres} {self.persona.apellidos} ({self.especialidad.nombre})" # Cuando la FK esté definida