from django.urls import path
from . import views

urlpatterns = [
    path('', views.agenda_principal, name='agenda_principal'),
    path('reserva/crear/', views.crear_reserva, name='crear_reserva'),
    path('reserva/<int:pk>/eliminar/', views.eliminar_reserva, name='eliminar_reserva'),
    path('reserva/crear/crear_cliente/', views.crear_cliente, name='crear_cliente'),
    path('reserva/crear/crear_cliente/actualizar_lista_clientes', views.actualizar_lista_clientes, name='actualizar_lista_clientes'),
    path('reserva/<int:pk>/modificar', views.modificar_reserva, name='modificar_reserva'),
    path('calendario/<int:year>/', views.calendario_anual, name='calendario_anual'),
    path('calendario/', views.calendario_anual, name='calendario_anual_actual'),
    path('calendario/<int:year>/<int:month>/', views.calendario_mensual_detallado, name='calendario_mensual_detallado'),
    path('reserva/actualizar', views.actualizar_lista_reservas, name="actualizar_lista_reservas"),
    
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:pk>/editar/', views.modificar_cliente, name='modificar_cliente'),
    path('clientes/<int:pk>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
]