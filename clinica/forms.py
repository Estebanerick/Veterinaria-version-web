# clinica/forms.py
from django import forms
from .models import Dueno, Mascota, Consulta, Veterinario

class DuenoForm(forms.ModelForm):
    class Meta:
        model = Dueno
        fields = ['nombre', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del dueño'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa',
                'rows': 3
            }),
        }
        labels = {
            'nombre': 'Nombre completo *',
            'telefono': 'Teléfono',
            'email': 'Correo electrónico',
            'direccion': 'Dirección',
        }

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'fecha_nacimiento', 'dueno']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la mascota'
            }),
            'especie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Perro, Gato, etc.'
            }),
            'raza': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Raza de la mascota'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'dueno': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nombre': 'Nombre de la mascota *',
            'especie': 'Especie',
            'raza': 'Raza',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'dueno': 'Dueño *',
        }

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['mascota', 'veterinario', 'motivo', 'diagnostico', 'tratamiento', 'observaciones', 'costo']
        widgets = {
            'mascota': forms.Select(attrs={'class': 'form-control'}),
            'veterinario': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Motivo de la consulta',
                'rows': 3
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Diagnóstico médico',
                'rows': 3
            }),
            'tratamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tratamiento recetado',
                'rows': 3
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones adicionales',
                'rows': 2
            }),
            'costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        labels = {
            'mascota': 'Mascota *',
            'veterinario': 'Veterinario',
            'motivo': 'Motivo de consulta *',
            'diagnostico': 'Diagnóstico',
            'tratamiento': 'Tratamiento',
            'observaciones': 'Observaciones',
            'costo': 'Costo ($)',
        }

class VeterinarioForm(forms.ModelForm):
    class Meta:
        model = Veterinario
        fields = ['nombre', 'especialidad', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del veterinario'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialidad médica'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
        }