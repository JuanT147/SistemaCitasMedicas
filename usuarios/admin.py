# SistemaCitasMedicas/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Importa el UserAdmin base de Django
from .models import Usuario, Persona, Estudiante, PersonalSalud
# Importa los formularios específicos para el admin que acabamos de definir/modificar
from .forms import UsuarioCreationForm, UsuarioChangeForm 

# Clase Admin personalizada para tu modelo Usuario
@admin.register(Usuario) # Este decorador registra tu modelo Usuario con esta clase Admin
class CustomUserAdmin(BaseUserAdmin): # Hereda de BaseUserAdmin para mantener la funcionalidad base

    # Asigna los formularios que el admin usará para la creación y edición de usuarios.
    form = UsuarioChangeForm  # Formulario para editar usuarios existentes
    add_form = UsuarioCreationForm # Formulario para CREAR nuevos usuarios
  
    def save_model(self, request, obj, form, change):
        print("ERRORES DEL FORMULARIO:", form.errors)  # <-- Agrega esto
        super().save_model(request, obj, form, change)
    # --- Configuraciones para la lista de usuarios en el panel admin ---
    list_display = (
        'correo_institucional',
        'es_estudiante',
        'es_personal_salud',
        'is_staff',      # ¿Es parte del staff de admin?
        'is_active'      # ¿Está activo?
    )
    list_filter = ('is_staff', 'is_active', 'es_estudiante', 'es_personal_salud')
    search_fields = ('correo_institucional',)

    # Le dice a Django que ordene los usuarios por 'correo_institucional'
    ordering = ('correo_institucional',) 

    # --- Configuraciones para la vista de EDICIÓN de un usuario existente ---
    # Este es para la página de "cambiar usuario"
    fieldsets = (
        # Sección de información básica y contraseña
        (None, {'fields': ('correo_institucional', 'password')}),
        # Sección de permisos de Django
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # Sección para tus roles personalizados
        ('Roles Personalizados', {'fields': ('es_estudiante', 'es_personal_salud')}),
        # Sección de fechas de login y unión
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # --- Configuraciones para la vista de CREACIÓN de un nuevo usuario ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # Hace que los campos de esta sección ocupen todo el ancho
            # Los campos que se mostrarán al crear un usuario.
            # UserCreationForm espera 'password' y 'password2' para la confirmación.
            'fields': ('correo_institucional', 'password1', 'password2'), 
        }),
        ('Roles', {'fields': ('es_estudiante', 'es_personal_salud')}),
    )

    # Usar filtros horizontales para los campos ManyToMany (grupos y permisos)
    filter_horizontal = ('groups', 'user_permissions')

# Registra tus otros modelos relacionados en el panel de administración
admin.site.register(Persona)
admin.site.register(Estudiante)
admin.site.register(PersonalSalud)