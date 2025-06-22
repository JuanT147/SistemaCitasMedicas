# citas/models.py
from django.db import models
from django.utils import timezone 
from datetime import timedelta,datetime
from django.core.exceptions import ValidationError

# Importa los modelos de las otras apps
from usuarios.models import Estudiante, PersonalSalud
from servicios.models import EspecialidadMedica


class Cita(models.Model):
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_ATENDIDO = 'Atendido'
    ESTADO_CANCELADO = 'Cancelado' # Aunque no hay reprogramación, puede ser útil para administración
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_ATENDIDO, 'Atendido'),
        (ESTADO_CANCELADO, 'Cancelado'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='citas_solicitadas')
    personal_salud = models.ForeignKey(PersonalSalud, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas_asignadas')
    especialidad = models.ForeignKey(EspecialidadMedica, on_delete=models.CASCADE, related_name='citas_servicio')

    fecha = models.DateField()
    hora_inicio = models.TimeField()
    #hora fin
    #hora_fin = models.TimeField(blank=True, null=True) # Este campo se puede autocompletar si no lo envías
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)

    # Campos para derivación directamente en la cita si se decide simplificar,
    # aunque la tabla Derivacion es más robusta.
    # Por ahora, nos quedaremos con la tabla Derivacion explícita, como en tu ERD.
    # derivacion_laboratorio_requerida = models.BooleanField(default=False)
    # derivacion_farmacia_requerida = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True) # Registra cuándo se creó la cita
    ultima_modificacion = models.DateTimeField(auto_now=True) # Registra la última vez que se modificó

    class Meta:
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        # Restricción para asegurar que no haya dos citas a la misma hora para el mismo personal/especialidad
        # Ojo: esto debe ser validado también en la lógica del formulario de reserva.
        # UNIQUE_TOGETHER no es suficiente para el slot de 20 minutos, pero ayuda con la hora_inicio exacta
        unique_together = ('especialidad', 'fecha', 'hora_inicio') # Una especialidad solo puede tener una cita en un momento dado
        # Si quieres que sea por personal de salud:
        # unique_together = ('personal_salud', 'fecha', 'hora_inicio')


    def __str__(self):
        return f"Cita de {self.estudiante.persona.nombres} {self.estudiante.persona.apellidos} con {self.personal_salud.persona.nombres} ({self.especialidad.nombre}) el {self.fecha} a las {self.hora_inicio}"

    @property
    def hora_fin(self):
        # Calcula la hora de fin sumando 20 minutos a la hora de inicio
        # Esto requiere convertir hora_inicio a datetime para sumar timedelta,
        # y luego extraer solo la hora.
        # Mejor manejar esto en el momento de crear la cita o en la interfaz.
        # Para fines de simplificación de modelo, puede ser una propiedad,
        # pero la validación de slot se hará en la lógica de la vista/form.
        # Ejemplo: return (datetime.combine(self.fecha, self.hora_inicio) + timedelta(minutes=20)).time()
        return (datetime.combine(self.fecha, self.hora_inicio) + timedelta(minutes=20)).time()

    def clean(self):
        # Validación a nivel de modelo para el slot de 20 minutos
        # (Aunque es mejor en el formulario/vista para feedback al usuario)
        #from django.core.exceptions import ValidationError
        # Verificar si ya existe una cita para esta especialidad en el rango de 20 minutos
        start_time = datetime.combine(self.fecha, self.hora_inicio)
        end_time = start_time + timedelta(minutes=20)
        hora_fin_nueva=end_time.time() # Hora de fin de la nueva cita
        # Convertir la hora de inicio a datetime para comparar rangos
        # No podemos usar self.hora_fin directamente si es una @property que depende de datetime.combine
        # Filtramos citas que se solapen
        citas_solapadas = Cita.objects.filter(
            especialidad=self.especialidad,
            personal_salud=self.personal_salud, # Si es necesario filtrar por personal de salud
            fecha=self.fecha,
            # La cita existente termina después de que la nueva empieza
            #hora_fin__gt=self.hora_inicio, 
            # La cita existente empieza antes de que la nueva termine
            #hora_inicio__lt=end_time 
        ).exclude(pk=self.pk if self.pk else None)  # Excluir la propia cita si estamos actualizando
        """
        # Excluir la propia cita si estamos actualizando
        #if self.pk:
        #    citas_solapadas = citas_solapadas.exclude(pk=self.pk)

        #if citas_solapadas.exists():
        #    raise ValidationError("Ya existe una cita que se solapa con este horario para este doctor y especialidad.")

        # Obtén la hora de inicio de la cita que se está guardando como un objeto datetime.time
        hora_inicio_actual_time = self.hora_inicio 

        # Convierte la hora de inicio a un objeto datetime temporal para realizar operaciones de tiempo
        datetime_hora_inicio_actual = datetime.combine(self.fecha, hora_inicio_actual_time)

        # Calcula el límite inferior para el filtro (19 minutos antes de la hora de inicio actual)
        limite_inferior_filtro = (datetime_hora_inicio_actual - timedelta(minutes=19)).time() # <-- SOLUCIÓN

        # Calcula el límite superior para el filtro (la hora de inicio actual)
        # Esto es para encontrar citas que terminen en los 19 minutos previos a la hora de inicio actual.
        limite_superior_filtro = hora_inicio_actual_time # <-- SOLUCIÓN
        citas_que_solapan = Cita.objects.filter(
            especialidad=self.especialidad,
            personal_salud=self.personal_salud,
            fecha=self.fecha,
            # La cita existente debe terminar después de que la nueva cita comience
            hora_fin__gt=self.hora_inicio,
            # Y la cita existente debe comenzar antes de que la nueva cita termine
            hora_inicio__lt=self.hora_fin # self.hora_fin es una propiedad calculada correctamente
        )

        if self.pk:
            citas_que_solapan = citas_que_solapan.exclude(pk=self.pk)

        if citas_que_solapan.exists():
            raise ValidationError("Ya existe una cita que se solapa con este horario para este profesional de la salud y especialidad.")
        """
        for cita in citas_solapadas:
            # Calcula el rango de la cita existente
            cita_start = datetime.combine(cita.fecha, cita.hora_inicio)
            cita_end = cita_start + timedelta(minutes=20)
            # Si los rangos se solapan, lanza error
            if (start_time < cita_end and end_time > cita_start):
                raise ValidationError("Ya existe una cita que se solapa con este horario para este profesional de la salud y especialidad.")

class Derivacion(models.Model):
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_ATENDIDO = 'Atendido'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_ATENDIDO, 'Atendido'),
    ]
    cita_origen = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='derivaciones')
    # Apunta a la EspecialidadMedica que es de tipo 'secundario' (Laboratorio, Farmacia)
    servicio_destino = models.ForeignKey(EspecialidadMedica, on_delete=models.CASCADE, related_name='derivaciones_recibidas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    observaciones = models.TextField(blank=True, null=True)
    fecha_derivacion = models.DateTimeField(auto_now_add=True) # Cuando se realizó la derivación

    class Meta:
        verbose_name = 'Derivación Médica'
        verbose_name_plural = 'Derivaciones Médicas'
        # Una cita no debería generar la misma derivación múltiple veces
        unique_together = ('cita_origen', 'servicio_destino')

    def __str__(self):
        return f"Derivación de Cita {self.cita_origen.id} a {self.servicio_destino.nombre}"