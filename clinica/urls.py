# clinica/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('duenos/', views.lista_duenos, name='lista_duenos'),
    path('duenos/agregar/', views.agregar_dueno, name='agregar_dueno'),
    path('mascotas/', views.lista_mascotas, name='lista_mascotas'),
    path('mascotas/agregar/', views.agregar_mascota, name='agregar_mascota'),
    path('veterinarios/', views.lista_veterinarios, name='lista_veterinarios'),
    path('consultas/', views.lista_consultas, name='lista_consultas'),
]