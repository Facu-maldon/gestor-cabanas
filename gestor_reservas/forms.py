from django import forms
from .models import *
from django.core.exceptions import ValidationError

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cabana', 'cliente', 'fecha_inicio', 'fecha_fin', 'notas']
        widgets = {
            'cabana': forms.Select(attrs={'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),
            'cliente': forms.Select(attrs={'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej. Maria Garcia'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),
            'notas': forms.Textarea(attrs={'rows': 2, 'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cabana = cleaned_data.get('cabana')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Si faltan datos básicos, dejamos que las validaciones propias de cada campo actúen primero
        if not (cabana and fecha_inicio and fecha_fin):
            return cleaned_data

        # 1. Validar que el rango de fechas tenga sentido lógico
        if fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        # 2. Buscar reservas existentes de la MISMA cabaña que se solapen con estas fechas
        # Fórmula matemática de solapamiento de rangos: (InicioA <= FinB) y (FinA >= InicioB)
        reservas_superpuestas = Reserva.objects.filter(
            cabana=cabana,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        )

        # 3. Si estamos MODIFICANDO una reserva existente, la excluimos de la búsqueda
        # para que no choque contra sí misma
        if self.instance and self.instance.pk:
            reservas_superpuestas = reservas_superpuestas.exclude(pk=self.instance.pk)

        if reservas_superpuestas.exists():
            # Opcional: tomamos la primera reserva en conflicto para dar un mensaje más claro
            conflicto = reservas_superpuestas.first()
            raise ValidationError(
                f"La cabaña '{cabana}' ya tiene una reserva en esas fechas "
                f"(del {conflicto.fecha_inicio.strftime('%d/%m/%Y')} al {conflicto.fecha_fin.strftime('%d/%m/%Y')})."
            )

        return cleaned_data

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),
            'apellido': forms.TextInput(attrs={'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej. Maria Garcia'}),
            'email': forms.TextInput(attrs={'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full p-2 border border-stone-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500'}),            
        }

