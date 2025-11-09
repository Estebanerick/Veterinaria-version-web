# clinica/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('duenos/', views.lista_duenos, name='lista_duenos'),
    path('duenos/agregar/', views.agregar_dueno, name='agregar_dueno'),
    path('mascotas/', views.lista_mascotas, name='lista_mascotas'),
    path('mascotas/agregar/', views.agregar_mascota, name='agregar_mascota'),
    path('mascotas/<int:mascota_id>/historial/', views.historial_mascota, name='historial_mascota'),
    path('consultas/', views.lista_consultas, name='lista_consultas'),
    path('consultas/agregar/', views.agregar_consulta, name='agregar_consulta'),
    path('veterinarios/', views.lista_veterinarios, name='lista_veterinarios'),
    path('veterinarios/agregar/', views.agregar_veterinario, name='agregar_veterinario'),
    path('veterinarios/<int:veterinario_id>/editar/', views.editar_veterinario, name='editar_veterinario'),
    path('veterinarios/<int:veterinario_id>/eliminar/', views.eliminar_veterinario, name='eliminar_veterinario'),
]