# clinica/admin.py
from django.contrib import admin
from .models import Dueno, Veterinario, Mascota, Consulta, Pago

@admin.register(Dueno)
class DuenoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'fecha_registro', 'activo', 'fecha_eliminacion']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'email']
    actions = ['restaurar_duenos']
    
    def get_queryset(self, request):
        # Mostrar todos los dueños (activos e inactivos)
        return Dueno.objects.incluir_eliminados()
    
    def restaurar_duenos(self, request, queryset):
        for dueno in queryset:
            if not dueno.activo:
                dueno.restaurar()
        self.message_user(request, f"{queryset.count()} dueños restaurados exitosamente.")
    restaurar_duenos.short_description = "Restaurar dueños seleccionados"

@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especialidad', 'activo', 'fecha_eliminacion']
    list_filter = ['activo', 'especialidad']
    search_fields = ['nombre']
    actions = ['restaurar_veterinarios']
    
    def get_queryset(self, request):
        return Veterinario.objects.incluir_eliminados()
    
    def restaurar_veterinarios(self, request, queryset):
        for vet in queryset:
            if not vet.activo:
                vet.restaurar()
        self.message_user(request, f"{queryset.count()} veterinarios restaurados exitosamente.")
    restaurar_veterinarios.short_description = "Restaurar veterinarios seleccionados"

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie', 'raza', 'dueno', 'activo', 'fecha_eliminacion']
    list_filter = ['activo', 'especie', 'fecha_registro']
    search_fields = ['nombre', 'dueno__nombre']
    actions = ['restaurar_mascotas']
    
    def get_queryset(self, request):
        return Mascota.objects.incluir_eliminados()
    
    def restaurar_mascotas(self, request, queryset):
        for mascota in queryset:
            if not mascota.activo:
                mascota.restaurar()
        self.message_user(request, f"{queryset.count()} mascotas restauradas exitosamente.")
    restaurar_mascotas.short_description = "Restaurar mascotas seleccionadas"

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'veterinario', 'fecha_consulta', 'costo', 'activo', 'fecha_eliminacion']
    list_filter = ['activo', 'fecha_consulta', 'veterinario']
    search_fields = ['mascota__nombre', 'veterinario__nombre']
    actions = ['restaurar_consultas']
    
    def get_queryset(self, request):
        return Consulta.objects.incluir_eliminados()
    
    def restaurar_consultas(self, request, queryset):
        for consulta in queryset:
            if not consulta.activo:
                consulta.restaurar()
        self.message_user(request, f"{queryset.count()} consultas restauradas exitosamente.")
    restaurar_consultas.short_description = "Restaurar consultas seleccionadas"

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['consulta', 'monto', 'metodo_pago', 'estado', 'fecha_pago', 'activo']
    list_filter = ['activo', 'metodo_pago', 'estado', 'fecha_pago']
    search_fields = ['consulta__mascota__nombre']
    actions = ['restaurar_pagos']
    
    def get_queryset(self, request):
        return Pago.objects.incluir_eliminados()
    
    def restaurar_pagos(self, request, queryset):
        for pago in queryset:
            if not pago.activo:
                pago.restaurar()
        self.message_user(request, f"{queryset.count()} pagos restaurados exitosamente.")
    restaurar_pagos.short_description = "Restaurar pagos seleccionados"