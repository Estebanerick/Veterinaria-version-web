# clinica/admin.py
from django.contrib import admin
from .models import Dueno, Mascota, Veterinario, Consulta, Pago

@admin.register(Dueno)
class DuenoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'fecha_registro']
    search_fields = ['nombre', 'email']

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie', 'raza', 'dueno', 'fecha_registro']
    list_filter = ['especie', 'fecha_registro']

@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especialidad', 'telefono', 'activo']
    list_filter = ['especialidad', 'activo']

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'veterinario', 'motivo', 'costo', 'fecha_consulta']
    list_filter = ['fecha_consulta']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['consulta', 'monto', 'metodo_pago', 'estado', 'fecha_pago']
    list_filter = ['metodo_pago', 'estado']