from collections import defaultdict
from datetime import timedelta
from .models import Reserva
# from .models import Reserva

def _normalizar_color_cabana(cabana):
    """Traduce el color de la cabaña a hexadecimal válido para CSS."""
    raw_color = getattr(cabana, 'color', None)
    if raw_color:
        color_lower = raw_color.strip().lower()
        if color_lower == 'verde':
            return '#10b981'
        elif color_lower == 'rosa':
            return "#c824c3"
        else:
            return raw_color
    else:
        return '#10b981' if cabana.id == 1 else '#3b82f6'


def obtener_ocupacion_por_rango(fecha_inicio, fecha_fin):
    """
    Devuelve {date: {cabana_id: dict_con_info_cabana_y_reserva}}.
    Evita duplicados por cabaña en un mismo día y cubre reservas que cruzan meses/años.
    """
    reservas = Reserva.objects.filter(
        fecha_inicio__lte=fecha_fin,
        fecha_fin__gte=fecha_inicio
    ).select_related('cabana', 'cliente')

    fechas_cabinas = defaultdict(dict)
    for r in reservas:
        inicio = r.fecha_inicio.date() if hasattr(r.fecha_inicio, 'date') else r.fecha_inicio
        fin = r.fecha_fin.date() if hasattr(r.fecha_fin, 'date') else (r.fecha_fin or inicio)
        
        c = r.cabana
        info = {
            'id': c.id,
            'nombre': str(c),
            'color': _normalizar_color_cabana(c),
            'reserva_id': r.id,
            'cliente_nombre': str(getattr(r, 'cliente', 'Reservado')),
        }

        dia_actual = max(inicio, fecha_inicio)
        ultimo_dia = min(fin, fecha_fin)
        
        while dia_actual <= ultimo_dia:
            # Copiamos info para que 'es_extremo' sea específico de este día y no afecte a los demás
            info_dia = info.copy()
            info_dia['es_extremo'] = (dia_actual == inicio or dia_actual == fin)
                
            fechas_cabinas[dia_actual][c.id] = info_dia
            dia_actual += timedelta(days=1)

    return fechas_cabinas

def mapeo_dias_ocupados(reservas):
    ocupacion_dias = {}
    for r in reservas:
        curr = r.fecha_inicio
        while curr <= r.fecha_fin:
            if curr not in ocupacion_dias:
                ocupacion_dias[curr] = []
            ocupacion_dias[curr].append({'reserva':r, 'nombre':f'{r.cliente.nombre} {r.cliente.apellido}'})
            curr = curr.fromordinal(curr.toordinal() + 1)

    return ocupacion_dias