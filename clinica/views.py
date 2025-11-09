# clinica/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Dueno, Mascota, Veterinario, Consulta
from .forms import DuenoForm

def home(request):
    # Obtener estadísticas básicas
    total_duenos = Dueno.objects.count()
    total_mascotas = Mascota.objects.count()
    total_consultas = Consulta.objects.count()
    total_veterinarios = Veterinario.objects.count()
    
    context = {
        'total_duenos': total_duenos,
        'total_mascotas': total_mascotas,
        'total_consultas': total_consultas,
        'total_veterinarios': total_veterinarios,
        'conexion_supabase': True,
    }
    
    return render(request, 'clinica/home.html', context)

def lista_duenos(request):
    duenos = Dueno.objects.all().order_by('nombre')
    return render(request, 'clinica/lista_duenos.html', {'duenos': duenos})

def agregar_dueno(request):
    if request.method == 'POST':
        try:
            # Crear dueño manualmente
            nombre = request.POST.get('nombre')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            direccion = request.POST.get('direccion')
            
            if nombre:  # Validación básica
                dueno = Dueno.objects.create(
                    nombre=nombre,
                    telefono=telefono or None,
                    email=email or None,
                    direccion=direccion or None
                )
                messages.success(request, f'✅ Dueño "{dueno.nombre}" registrado exitosamente')
                return redirect('lista_duenos')
            else:
                messages.error(request, '❌ El nombre es obligatorio')
                
        except Exception as e:
            messages.error(request, f'❌ Error al guardar: {e}')
    
    return render(request, 'clinica/agregar_dueno.html')

# En clinica/views.py, actualiza la función lista_mascotas:
def lista_mascotas(request):
    mascotas = Mascota.objects.select_related('dueno').all()
    duenos_count = Dueno.objects.count()  # Agregar esta línea
    return render(request, 'clinica/lista_mascotas.html', {
        'mascotas': mascotas,
        'duenos_count': duenos_count  # Pasar el conteo al template
    })

def agregar_mascota(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            especie = request.POST.get('especie')
            raza = request.POST.get('raza')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            id_dueno = request.POST.get('dueno')
            
            print(f"🔍 DEBUG: Datos mascota - Nombre: {nombre}, Dueño ID: {id_dueno}")
            
            if nombre and id_dueno:
                # Verificar que el dueño existe
                try:
                    dueno = Dueno.objects.get(id=id_dueno)
                    
                    mascota = Mascota.objects.create(
                        nombre=nombre,
                        especie=especie or None,
                        raza=raza or None,
                        fecha_nacimiento=fecha_nacimiento or None,
                        dueno=dueno
                    )
                    messages.success(request, f'✅ Mascota "{mascota.nombre}" registrada exitosamente')
                    return redirect('lista_mascotas')
                    
                except Dueno.DoesNotExist:
                    messages.error(request, '❌ El dueño seleccionado no existe')
            else:
                messages.error(request, '❌ El nombre y dueño son obligatorios')
                
        except Exception as e:
            messages.error(request, f'❌ Error al guardar mascota: {e}')
    
    # Obtener dueños para el dropdown
    duenos = Dueno.objects.all()
    return render(request, 'clinica/agregar_mascota.html', {'duenos': duenos})

def lista_veterinarios(request):
    veterinarios = Veterinario.objects.all()
    return render(request, 'clinica/lista_veterinarios.html', {'veterinarios': veterinarios})

def lista_consultas(request):
    consultas = Consulta.objects.all()
    return render(request, 'clinica/lista_consultas.html', {'consultas': consultas})