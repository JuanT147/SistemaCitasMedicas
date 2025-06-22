# citas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta,time,date

from .forms import CitaForm
from .models import Cita, Derivacion
from usuarios.models import Estudiante, PersonalSalud, Usuario
from servicios.models import EspecialidadMedica


@login_required
def solicitar_cita(request):
    # Asegurarse de que solo los estudiantes puedan solicitar citas
    if not request.user.is_authenticated or not request.user.es_estudiante:
        messages.warning(request, "Debes iniciar sesión como estudiante para solicitar una cita.")
        return redirect('usuarios:login')

    estudiante = None
    try:
        estudiante = request.user.persona.estudiante
    except Estudiante.DoesNotExist:
        messages.error(request, "Tu perfil de estudiante no está completo. Contacta a administración.")
        return redirect('usuarios:dashboard_estudiante') # O a una página para completar perfil

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            especialidad = form.cleaned_data['especialidad']
            fecha = form.cleaned_data['fecha']
            hora_inicio_val =form.cleaned_data['hora_inicio'] # Objeto time
            # aceptar tanto str como time
            if isinstance(hora_inicio_val, time):
                hora_inicio_obj = hora_inicio_val
            else:
                hora_inicio_obj = datetime.strptime(hora_inicio_val, '%H:%M').time()
            
            # Verificar si hay PersonalSalud disponible para esa especialidad y fecha/hora
            # Por ahora, simplemente intentaremos asignar a CUALQUIER personal de esa especialidad.
            # En un sistema más robusto, se buscaría el personal menos ocupado o específico.
            personal_salud_disponible = PersonalSalud.objects.filter(
                especialidad=especialidad,
                # Aquí podríamos añadir lógica más compleja de disponibilidad del personal
                # Por ejemplo, que no tenga otra cita agendada en ese mismo slot
                # Pero el form.clean ya valida que el slot de la ESPECIALIDAD esté libre.
                # Asumimos que si la especialidad tiene un slot libre, hay un personal capaz de atender.
            ).first() # Tomamos el primero que encontremos

            if not personal_salud_disponible:
                messages.error(request, f"No hay personal de salud disponible para {especialidad.nombre} en la fecha y hora seleccionadas.")
                return render(request, 'citas/solicitar_cita.html', {'form': form})

            # Crear la cita
            cita = form.save(commit=False) # No guardar aún para añadir el estudiante
            cita.estudiante = estudiante
            cita.personal_salud = personal_salud_disponible
            cita.hora_inicio = hora_inicio_obj # Asegurarse de que el objeto time se asigne
            cita.save()

            messages.success(request, f'¡Tu cita para {especialidad.nombre} el {fecha} a las {hora_inicio_obj} ha sido solicitada con éxito!')
            return redirect('citas:mis_citas') # Redirigir a la lista de citas del estudiante
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = CitaForm()

    return render(request, 'citas/solicitar_cita.html', {'form': form})


@login_required
def mis_citas(request):
    # Asegurarse de que solo los estudiantes puedan ver sus citas
    if not request.user.is_authenticated or not request.user.es_estudiante:
        messages.warning(request, "Debes iniciar sesión como estudiante para ver tus citas.")
        return redirect('usuarios:login')

    estudiante = None
    try:
        estudiante = request.user.persona.estudiante
    except Estudiante.DoesNotExist:
        messages.error(request, "Tu perfil de estudiante no está completo. Contacta a administración.")
        return redirect('usuarios:dashboard_estudiante')

    # Obtener todas las citas asociadas a este estudiante, ordenadas por fecha y hora
    citas = Cita.objects.filter(estudiante=estudiante).order_by('fecha', 'hora_inicio')

    context = {
        'citas': citas,
        'estudiante': estudiante,
    }
    return render(request, 'citas/mis_citas.html', context)


@login_required
def citas_personal_salud(request):
    
    personal_salud = request.user.persona.personalsalud
    especialidad = personal_salud.especialidad

    # Citas directas (solo para principales)
    citas_directas = Cita.objects.filter(personal_salud=personal_salud)

    # Citas derivadas (para secundarios)
    derivaciones = Derivacion.objects.filter(servicio_destino=especialidad)
    citas_derivadas = [d.cita_origen for d in derivaciones]

    # ¿Es personal secundario?
    es_secundario = especialidad.nombre.lower() in ['farmacia', 'laboratorio']
    

    if es_secundario:
        # Solo mostrar derivaciones pendientes para esta especialidad
        derivaciones_pendientes = Derivacion.objects.filter(
            servicio_destino=especialidad,
            estado=Derivacion.ESTADO_PENDIENTE,
            cita_origen__fecha__gte=date.today()
        )
        citas_pendientes = [d.cita_origen for d in derivaciones_pendientes]

        # Historial: derivaciones atendidas
        derivaciones_historial = Derivacion.objects.filter(
            servicio_destino=especialidad,
            estado=Derivacion.ESTADO_ATENDIDO
        )
        citas_historial = [d.cita_origen for d in derivaciones_historial]
    else:
        todas_citas = list(set(list(citas_directas) + citas_derivadas))
        citas_pendientes = [
            c for c in todas_citas
            if c.estado == Cita.ESTADO_PENDIENTE and c.fecha >= date.today()
        ]
        citas_historial = [
            c for c in todas_citas
            if c.estado in [Cita.ESTADO_ATENDIDO, Cita.ESTADO_CANCELADO]
        ]
   
    context = {
        'personal_salud': personal_salud,
        'citas_pendientes': citas_pendientes,
        'citas_historial': citas_historial,
    }
    return render(request, 'citas/citas_personal_salud.html', context)

@login_required
def detalle_cita_personal_salud(request, cita_id):
    # Asegurarse de que solo el personal de salud pueda acceder
    if not request.user.is_authenticated or not request.user.es_personal_salud:
        messages.warning(request, "Debes iniciar sesión como personal de salud para acceder a los detalles de una cita.")
        return redirect('usuarios:login')
    
    try:
        personal_salud = request.user.persona.personalsalud
    except PersonalSalud.DoesNotExist:
        messages.error(request, "Tu perfil de personal de salud no está completo. Contacta a administración.")
        return redirect('usuarios:dashboard_personal_salud')

    # Obtener la cita o devolver 404
    cita = get_object_or_404(Cita, id=cita_id)

    # Permitir acceso si:
    # - Es el personal_salud asignado (principal)
    # - O la cita fue derivada a la especialidad de este usuario (secundario)
    es_directa = cita.personal_salud == personal_salud
    es_derivada = Derivacion.objects.filter(cita_origen=cita, servicio_destino=personal_salud.especialidad).exists()

    if not (es_directa or es_derivada):
        messages.error(request, "No tienes permiso para ver los detalles de esta cita.")
        return redirect('citas:citas_personal_salud')

    # Lógica para cambiar estado de la cita o crear derivación
    if request.method == 'POST':
        if 'marcar_atendido' in request.POST:
            if es_derivada and not es_directa:
                # El personal secundario atiende la derivación
                derivacion = Derivacion.objects.get(
                    cita_origen=cita,
                    servicio_destino=personal_salud.especialidad,
                    estado=Derivacion.ESTADO_PENDIENTE
                )
                derivacion.estado = Derivacion.ESTADO_ATENDIDO
                derivacion.save()
                messages.success(request, "Cita derivada marcada como atendida para tu especialidad.")
            else:
                # El personal principal atiende la cita
                cita.estado = Cita.ESTADO_ATENDIDO
                cita.save()
                messages.success(request, f"Cita con {cita.estudiante.persona.nombres} {cita.estudiante.persona.apellidos} marcada como ATENDIDA.")
            return redirect('citas:citas_personal_salud')


        elif 'derivar_laboratorio' in request.POST:
            try:
                laboratorio_servicio = EspecialidadMedica.objects.get(
                    nombre='Laboratorio',
                    tipo_servicio=EspecialidadMedica.SERVICIO_SECUNDARIO
                )
                # Validar si ya existe la derivación
                if not Derivacion.objects.filter(cita_origen=cita, servicio_destino=laboratorio_servicio).exists():
                    Derivacion.objects.create(
                        cita_origen=cita,
                        servicio_destino=laboratorio_servicio,
                        observaciones="Derivación a Laboratorio solicitada."
                    )
                    messages.success(request, f"Derivación a Laboratorio creada para la cita con {cita.estudiante.persona.nombres}.")
                else:
                    messages.warning(request, "Esta cita ya fue derivada a Laboratorio.")
            except EspecialidadMedica.DoesNotExist:
                messages.error(request, "La especialidad 'Laboratorio' no está configurada como servicio secundario.")
            return redirect('citas:detalle_cita_personal_salud', cita_id=cita.id)
        
        elif 'derivar_farmacia' in request.POST:
            try:
                farmacia_servicio = EspecialidadMedica.objects.get(
                    nombre='Farmacia',
                    tipo_servicio=EspecialidadMedica.SERVICIO_SECUNDARIO
                )
                if not Derivacion.objects.filter(cita_origen=cita, servicio_destino=farmacia_servicio).exists():
                    Derivacion.objects.create(
                        cita_origen=cita,
                        servicio_destino=farmacia_servicio,
                        observaciones="Derivación a Farmacia solicitada."
                    )
                    messages.success(request, f"Derivación a Farmacia creada para la cita con {cita.estudiante.persona.nombres}.")
                else:
                    messages.warning(request, "Esta cita ya fue derivada a Farmacia.")
            except EspecialidadMedica.DoesNotExist:
                messages.error(request, "La especialidad 'Farmacia' no está configurada como servicio secundario.")
            return redirect('citas:detalle_cita_personal_salud', cita_id=cita.id)

        elif 'cancelar_cita' in request.POST: # Opcional: permitir al personal de salud cancelar
            cita.estado = Cita.ESTADO_CANCELADO
            cita.save()
            messages.success(request, f"Cita con {cita.estudiante.persona.nombres} {cita.estudiante.persona.apellidos} ha sido CANCELADA.")
            return redirect('citas:citas_personal_salud')


    # Obtener las derivaciones existentes para esta cita
    derivaciones = Derivacion.objects.filter(cita_origen=cita)

    context = {
        'cita': cita,
        'derivaciones': derivaciones,
        'personal_salud': personal_salud,
        'es_directa': es_directa,
        'es_derivada': es_derivada,
    }
    return render(request, 'citas/detalle_cita_personal_salud.html', context)