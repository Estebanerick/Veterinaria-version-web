# clinica/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)
    
    def incluir_eliminados(self):
        return super().get_queryset()
    
    def solo_eliminados(self):
        return super().get_queryset().filter(activo=False)

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.nombre

class Dueno(Persona):
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)
    
    objects = SoftDeleteManager()
    
    def __str__(self):
        return f"{self.nombre} {'(Inactivo)' if not self.activo else ''}"
    
    def eliminar_logicamente(self):
        self.activo = False
        self.fecha_eliminacion = timezone.now()
        self.save()
        
        from .supabase_client import supabase
        if supabase:
            try:
                supabase.table("dueno").update({"activo": False}).eq("nombre", self.nombre).execute()
                print(f"Dueño marcado como inactivo en Supabase: {self.nombre}")
            except Exception as e:
                print(f"Error actualizando Supabase: {e}")
    
    def restaurar(self):
        self.activo = True
        self.fecha_eliminacion = None
        self.save()
        
        from .supabase_client import supabase
        if supabase:
            try:
                supabase.table("dueno").update({"activo": True}).eq("nombre", self.nombre).execute()
                print(f"Dueño restaurado en Supabase: {self.nombre}")
            except Exception as e:
                print(f"Error actualizando Supabase: {e}")

    class Meta:
        verbose_name_plural = "Dueños"

class Veterinario(Persona):
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)
    
    objects = SoftDeleteManager()
    
    def eliminar_logicamente(self):
        self.activo = False
        self.fecha_eliminacion = timezone.now()
        self.save()
    
    def restaurar(self):
        self.activo = True
        self.fecha_eliminacion = None
        self.save()

class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50, blank=True, null=True)
    raza = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)
    
    objects = SoftDeleteManager()
    
    def clean(self):
        """Validar que la fecha de nacimiento no sea en el futuro"""
        if self.fecha_nacimiento and self.fecha_nacimiento > date.today():
            raise ValidationError({'fecha_nacimiento': 'La fecha de nacimiento no puede ser en el futuro.'})
    
    def __str__(self):
        status = " (Inactiva)" if not self.activo else ""
        return f"{self.nombre} ({self.especie}){status}"
    
    def eliminar_logicamente(self):
        self.activo = False
        self.fecha_eliminacion = timezone.now()
        self.save()
    
    def restaurar(self):
        self.activo = True
        self.fecha_eliminacion = None
        self.save()

class Consulta(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField()
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)
    
    objects = SoftDeleteManager()
    
    def __str__(self):
        status = " (Eliminada)" if not self.activo else ""
        return f"Consulta {self.mascota.nombre} - {self.fecha_consulta}{status}"
    
    def eliminar_logicamente(self):
        self.activo = False
        self.fecha_eliminacion = timezone.now()
        self.save()
    
    def restaurar(self):
        self.activo = True
        self.fecha_eliminacion = None
        self.save()

class Pago(models.Model):
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    estado = models.CharField(max_length=20, default='PAGADO')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)
    
    objects = SoftDeleteManager()
    
    def __str__(self):
        status = " (Eliminado)" if not self.activo else ""
        return f"Pago {self.consulta.id} - ${self.monto}{status}"
    
    def eliminar_logicamente(self):
        self.activo = False
        self.fecha_eliminacion = timezone.now()
        self.save()
    
    def restaurar(self):
        self.activo = True
        self.fecha_eliminacion = None
        self.save()