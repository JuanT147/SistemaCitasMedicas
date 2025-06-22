# servicios/models.py
from django.db import models

class EspecialidadMedica(models.Model):
    SERVICIO_PRINCIPAL = 'principal'
    SERVICIO_SECUNDARIO = 'secundario'
    TIPO_SERVICIO_CHOICES = [
        (SERVICIO_PRINCIPAL, 'Servicio Médico Principal'),
        (SERVICIO_SECUNDARIO, 'Servicio Médico Secundario (Derivación)'),
    ]

    nombre = models.CharField(max_length=100, unique=True, help_text='Nombre de la especialidad o servicio (ej. Medicina, Laboratorio)')
    descripcion = models.TextField(blank=True, null=True)
    # Para distinguir entre servicios que agendan citas directamente y los de derivación
    tipo_servicio = models.CharField(
        max_length=10,
        choices=TIPO_SERVICIO_CHOICES,
        default=SERVICIO_PRINCIPAL,
        help_text='Indica si el servicio es principal (se puede agendar cita) o secundario (solo por derivación).'
    )

    class Meta:
        verbose_name = 'Especialidad Médica o Servicio'
        verbose_name_plural = 'Especialidades Médicas y Servicios'

    def __str__(self):
        return self.nombre