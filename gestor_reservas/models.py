from django.db import models

class Cliente(models.Model):
    nombre = models.CharField()
    apellido = models.CharField()
    email = models.CharField(blank=True)
    telefono = models.CharField()

    def __str__(self):
        return self.nombre + " " + self.apellido

class Cabana(models.Model):
    COLOR_CHOICES = [
        ('verde', 'Verde'),
        ('rosa', 'Rosa'),
    ]
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='verde')

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    cabana = models.ForeignKey(Cabana, on_delete=models.CASCADE, related_name='reservas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    notas = models.TextField(blank=True)
    creada_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.cliente} - {self.cabana.nombre} ({self.fecha_inicio} al {self.fecha_fin})"
