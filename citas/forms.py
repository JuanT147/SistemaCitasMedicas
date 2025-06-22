# citas/forms.py
from django import forms
from .models import Cita
from servicios.models import EspecialidadMedica
from django.forms.widgets import DateInput
from datetime import time, datetime, timedelta
from django.utils import timezone

class CitaForm(forms.ModelForm):
    # Sobrescribimos el campo especialidad para filtrar solo servicios principales
    especialidad = forms.ModelChoiceField(
        queryset=EspecialidadMedica.objects.filter(tipo_servicio=EspecialidadMedica.SERVICIO_PRINCIPAL),
        label="Especialidad Médica",
        empty_label="Seleccione una especialidad",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    fecha = forms.DateField(
        label="Fecha de la Cita",
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Seleccione una fecha futura."
    )

    # Campo para la hora de inicio, que luego se validará por slots
    # Opciones de hora (ej: cada 20 minutos de 8 AM a 5 PM)
    HORA_CHOICES = []
    start_time = datetime.strptime('08:00', '%H:%M').time()
    end_time = datetime.strptime('17:00', '%H:%M').time()
    current_time = datetime.combine(datetime.min, start_time)
    while current_time.time() <= end_time:
        HORA_CHOICES.append((current_time.strftime('%H:%M'), current_time.strftime('%I:%M %p'))) # 24h y 12h formato
        current_time += timedelta(minutes=20)

    hora_inicio = forms.ChoiceField(
        label="Hora de Inicio (slots de 20 minutos)",
        choices=HORA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Los slots se habilitarán según la disponibilidad."
    )

    class Meta:
        model = Cita
        fields = ['especialidad', 'fecha', 'hora_inicio']

    def clean(self):
        cleaned_data = super().clean()
        especialidad = cleaned_data.get('especialidad')
        fecha = cleaned_data.get('fecha')
        hora_inicio_str = cleaned_data.get('hora_inicio')

        if not especialidad or not fecha or not hora_inicio_str:
            # La validación básica de campos requeridos ya la hace ModelForm
            # pero es bueno asegurarse si vas a usar estos campos en validaciones cruzadas.
            return cleaned_data

        try:
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        except ValueError:
            raise forms.ValidationError("Formato de hora inválido.")

        # Validación: Fecha no puede ser pasada
        if fecha < timezone.now().date():
            raise forms.ValidationError("No puedes reservar citas en una fecha pasada.")

        # Validación: Hora de inicio no puede ser pasada si la fecha es hoy
        if fecha == timezone.now().date() and hora_inicio <= timezone.now().time():
             raise forms.ValidationError("No puedes reservar citas en una hora pasada para el día de hoy.")


        # Validación de Disponibilidad de Slot (esto es clave)
        # El flujo de atención es un estudiante por cada 20 minutos por servicio.
        # Verificamos si hay alguna cita que se solape con el slot de 20 minutos propuesto.

        # Convertir hora_inicio a un objeto datetime para manejar rangos de tiempo
        proposed_start_dt = datetime.combine(fecha, hora_inicio)
        proposed_end_dt = proposed_start_dt + timedelta(minutes=20)

        # Citas existentes para la misma especialidad y fecha
        existing_citas = Cita.objects.filter(
            especialidad=especialidad,
            fecha=fecha,
            estado=Cita.ESTADO_PENDIENTE # Considerar solo citas pendientes
        )

        for cita in existing_citas:
            cita_start_dt = datetime.combine(cita.fecha, cita.hora_inicio)
            cita_end_dt = cita_start_dt + timedelta(minutes=20)

            # Comprobar solapamiento:
            # Una cita se solapa si (proposed_start_dt < cita_end_dt) Y (proposed_end_dt > cita_start_dt)
            if (proposed_start_dt < cita_end_dt) and (proposed_end_dt > cita_start_dt):
                raise forms.ValidationError(
                    f"El slot de tiempo para la especialidad '{especialidad.nombre}' en {fecha} a las {hora_inicio_str} ya está ocupado."
                )

        # Puedes añadir aquí validación de que el PersonalSalud esté disponible,
        # pero para simplificar, por ahora asumimos que la especialidad tiene capacidad.
        # La asignación de PersonalSalud se podría hacer después o en el dashboard del admin.

        # Si todo está bien, asignamos la hora_inicio como un objeto time (Django lo espera así)
        cleaned_data['hora_inicio'] = hora_inicio

        return cleaned_data