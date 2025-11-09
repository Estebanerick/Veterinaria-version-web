# clinica/models.py
from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.nombre

# clinica/models.py - modificar el modelo Dueno
class Dueno(Persona):
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)  # ← Agregar este campo
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)  # ← Agregar este campo

    def __str__(self):
        return f"{self.nombre} {'(Inactivo)' if not self.activo else ''}"
    
    def eliminar_logicamente(self):
        """Eliminación lógica en lugar de física"""
        self.activo = False
        self.fecha_eliminacion = timezone.now()
        self.save()
        
        # También marcar como inactivo en Supabase
        from .supabase_client import supabase
        if supabase:
            try:
                supabase.table("dueno").update({"activo": False}).eq("nombre", self.nombre).execute()
                print(f"✅ Dueño marcado como inactivo en Supabase: {self.nombre}")
            except Exception as e:
                print(f"❌ Error actualizando Supabase: {e}")
    
    def restaurar(self):
        """Restaurar un dueño eliminado lógicamente"""
        self.activo = True
        self.fecha_eliminacion = None
        self.save()
        
        # Restaurar en Supabase también
        from .supabase_client import supabase
        if supabase:
            try:
                supabase.table("dueno").update({"activo": True}).eq("nombre", self.nombre).execute()
                print(f"✅ Dueño restaurado en Supabase: {self.nombre}")
            except Exception as e:
                print(f"❌ Error actualizando Supabase: {e}")

    class Meta:
        verbose_name_plural = "Dueños"

class Veterinario(Persona):
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50, blank=True, null=True)
    raza = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.especie})"

# clinica/models.py - modelo Consulta
class Consulta(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField()
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Consulta {self.mascota.nombre} - {self.fecha_consulta}"

# clinica/models.py - agregar al final
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
    
    def __str__(self):
        return f"Pago {self.consulta.id} - ${self.monto}"