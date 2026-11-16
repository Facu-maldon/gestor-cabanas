import calendar
from datetime import date
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Reserva
from .forms import *
from django.db.models import Q, Count
from . import utils

def agenda_principal(request):
    reservas = Reserva.objects.select_related('cabana').all()
    
    context = {
        'reservas': reservas,
    }

    return render(request, '../templates/index.html', context)

def calendario_anual(request, year=None):

    current_year = int(year) if year else date.today().year

    fechas_cabinas = utils.obtener_ocupacion_por_rango(
        date(current_year, 1, 1),
        date(current_year, 12, 31)
    )

    # Armado del calendario por meses y semanas
    cal = calendar.Calendar(firstweekday=6) # 6 = Domingo como primer día de la semana
    
    meses = []
    for m in range(1, 13):
        semanas_raw = cal.monthdayscalendar(current_year, m)
        semanas = []
        for semana in semanas_raw:
            dias_semana = []
            for day in semana:
                if day == 0:
                    dias_semana.append({'day': '', 'is_empty': True})
                else:
                    d = date(current_year, m, day)
                    cabanas_dict = fechas_cabinas.get(d, {})
                    cabanas_del_dia = list(cabanas_dict.values())
                    num_reservas = len(cabanas_del_dia)
                    
                    # 2. Si hay una sola reserva, pasamos su color a nivel de día
                    color_dia = cabanas_del_dia[0]['color'] if num_reservas == 1 else None

                    es_extremo = cabanas_del_dia[0]['es_extremo'] if num_reservas == 1 else False

                    dias_semana.append({
                        'day': day,
                        'is_empty': False,
                        'cabanas': cabanas_del_dia,
                        'num_reservas': num_reservas,
                        'color': color_dia,
                        'es_extremo': es_extremo,
                    })
            semanas.append(dias_semana)

        meses.append({
            'numero': m,
            'nombre': calendar.month_name[m].capitalize(),
            'semanas': semanas,
        })
    
    context = {
        'year': current_year,
        'prev_year': current_year - 1,
        'next_year': current_year + 1,
        'meses': meses,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, '../templates/calendario/calendario_anual.html', context)
        
    return render(request, '../templates/calendario/calendario_anual.html', context)

def calendario_mensual_detallado(request, year, month):
    year = int(year)
    month = int(month)
    
    cal = calendar.Calendar(firstweekday=6) # 6 = Domingo
    semanas_raw = cal.monthdatescalendar(year, month)
    
    # Llamamos a la MISMA función compartida usando el primer y último día visible de la cuadrícula
    fechas_cabinas = utils.obtener_ocupacion_por_rango(
        semanas_raw[0][0], 
        semanas_raw[-1][-1]
    )

    dias_del_mes = []
    for semana in semanas_raw:
        semana_procesada = []
        for d in semana:
            cabanas_dict = fechas_cabinas.get(d, {})
            cabanas_del_dia = list(cabanas_dict.values())
            num_reservas = len(cabanas_del_dia)
            
            # Color directo si hay una sola reserva (igual que en el anual)
            color_dia = cabanas_del_dia[0]['color'] if num_reservas == 1 else None
            es_extremo = cabanas_del_dia[0]['es_extremo'] if num_reservas == 1 else False
            
            semana_procesada.append({
                'fecha': d,
                'day': d.day,
                'month': d.month,
                'es_mes_actual': (d.month == month),
                'cabanas': cabanas_del_dia,      # Contiene id, nombre, color, reserva_id y cliente_nombre
                'num_reservas': num_reservas,
                'color': color_dia,
                'es_extremo': es_extremo,
            })
        dias_del_mes.append(semana_procesada)

    # Calcular mes anterior y siguiente para las FLECHAS de navegación
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
        
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month].capitalize(),
        'dias_del_mes': dias_del_mes,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, '../templates/calendario/calendario_mensual_detallado.html', context)
        
    return render(request, '../templates/calendario/calendario_anual_cuadricula.html', context)

def actualizar_lista_reservas(request):
    reservas = Reserva.objects.select_related('cabana').all()
    
    context = {
        'reservas': reservas,
    }

    return render(request, '../templates/mostrar_reservas/lista_reservas.html', context)

def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            # Retorna respuesta para refrescar componentes via HTMX
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'reservaActualizada'
            return response
        return render(request, '../templates/crear_reserva/form_modal.html', {'form': form})
    
    form = ReservaForm()
    context={'form': form, 'operacion': "Modificar reserva"}

    return render(request, '../templates/crear_reserva/form_modal.html', context)

def crear_cliente(request):
    if request.method=='POST':
        formCliente=ClienteForm(request.POST)
        if formCliente.is_valid():
            formCliente.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'clienteActualizado'
            return response
        return render(request, '../templates/crear_reserva/form_modal_cliente.html', {'form': formCliente})

    formCliente = ClienteForm()
    
    return render(request, '../templates/crear_reserva/form_modal_cliente.html', {'form': formCliente})

def actualizar_lista_clientes(request):
    form = ReservaForm()
    return render(request, '../templates/crear_reserva/lista_clientes.html', {'form': form})

def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        reserva.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = 'reservaActualizada'
        return response

    return render(request, 'eliminar_reserva/confirmar_eliminacion.html', {'reserva': reserva})

def modificar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method=='POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
                form.save()
                response=HttpResponse(status=204)
                response['HX-Trigger'] = 'reservaActualizada'
                return response
        return render(request, '../templates/modificar_reserva/form_modal_modificar.html', {'form': form, 'pk':pk})

    form = ReservaForm(instance=reserva)
    
    return render(request, '../templates/modificar_reserva/form_modal_modificar.html', {'form': form, 'pk':pk})


def lista_clientes(request):
    query = request.GET.get('q', '').strip()
    
    # Anotamos cuántas reservas tiene cada cliente para mostrarlo en la tabla
    clientes = Cliente.objects.annotate(
        total_reservas=Count('reserva') # Ajusta si tu related_name es distinto (ej: 'reservas')
    ).order_by('nombre')

    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) | 
            Q(telefono__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'clientes': clientes,
        'query': query,
    }

    # Si viene desde el buscador o desde el trigger HTMX, devolvemos solo la tabla
    if request.headers.get('HX-Request'):
        return render(request, 'clientes/tabla_clientes.html', context)

    return render(request, 'clientes/lista_clientes.html', context)


def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'clienteActualizado'
            return response
        return render(request, 'clientes/form_modal_cliente.html', {
            'form': form,
            'operacion': 'Nuevo Cliente'
        })

    form = ClienteForm()
    return render(request, 'clientes/form_modal_cliente.html', {
        'form': form,
        'operacion': 'Nuevo Cliente'
    })


def modificar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'clienteActualizado'
            return response
        return render(request, 'clientes/form_modal_cliente.html', {
            'form': form,
            'pk': pk,
            'operacion': 'Modificar Cliente'
        })

    form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form_modal_cliente.html', {
        'form': form,
        'pk': pk,
        'operacion': 'Modificar Cliente'
    })


def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        cliente.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = 'clienteActualizado'
        return response

    return render(request, 'clientes/modal_confirmar_eliminar_cliente.html', {
        'cliente': cliente
    })