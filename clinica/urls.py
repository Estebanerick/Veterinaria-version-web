from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Dueños
    path('duenos/', views.lista_duenos, name='lista_duenos'),
    path('duenos/agregar/', views.agregar_dueno, name='agregar_dueno'),
    path('duenos/editar/<int:dueno_id>/', views.editar_dueno, name='editar_dueno'),
    path('duenos/eliminar/<int:dueno_id>/', views.eliminar_dueno_logico, name='eliminar_dueno_logico'),
    path('duenos/inactivos/', views.lista_duenos_inactivos, name='lista_duenos_inactivos'),
    path('duenos/restaurar/<int:dueno_id>/', views.restaurar_dueno, name='restaurar_dueno'),
    path('duenos/<int:dueno_id>/mascotas/', views.mascotas_dueno, name='mascotas_dueno'),
    
    # Veterinarios
    path('veterinarios/', views.lista_veterinarios, name='lista_veterinarios'),
    path('veterinarios/agregar/', views.agregar_veterinario, name='agregar_veterinario'),
    path('veterinarios/editar/<int:veterinario_id>/', views.editar_veterinario, name='editar_veterinario'),
    path('veterinarios/eliminar/<int:veterinario_id>/', views.eliminar_veterinario_logico, name='eliminar_veterinario'),
    path('veterinarios/inactivos/', views.lista_veterinarios_inactivos, name='lista_veterinarios_inactivos'),
    path('veterinarios/restaurar/<int:veterinario_id>/', views.restaurar_veterinario, name='restaurar_veterinario'),
    
    # Mascotas
    path('mascotas/', views.lista_mascotas, name='lista_mascotas'),
    path('mascotas/agregar/', views.agregar_mascota, name='agregar_mascota'),
    path('mascotas/eliminar/<int:mascota_id>/', views.eliminar_mascota_logico, name='eliminar_mascota_logico'),
    path('mascotas/inactivas/', views.lista_mascotas_inactivas, name='lista_mascotas_inactivas'),
    path('mascotas/restaurar/<int:mascota_id>/', views.restaurar_mascota, name='restaurar_mascota'),
    path('mascotas/<int:mascota_id>/historial/', views.historial_mascota, name='historial_mascota'),
    
    # Consultas
    path('consultas/', views.lista_consultas, name='lista_consultas'),
    path('consultas/agregar/', views.agregar_consulta, name='agregar_consulta'),
    path('consultas/eliminar/<int:consulta_id>/', views.eliminar_consulta_logico, name='eliminar_consulta_logico'),
    path('consultas/inactivas/', views.lista_consultas_inactivas, name='lista_consultas_inactivas'),
    path('consultas/restaurar/<int:consulta_id>/', views.restaurar_consulta, name='restaurar_consulta'),
    
    # Pagos
    path('pagos/eliminar/<int:pago_id>/', views.eliminar_pago_logico, name='eliminar_pago_logico'),
    path('pagos/inactivos/', views.lista_pagos_inactivos, name='lista_pagos_inactivos'),
    path('pagos/restaurar/<int:pago_id>/', views.restaurar_pago, name='restaurar_pago'),
]