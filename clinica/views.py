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

# clinica/views.py - agregar estas funciones
def lista_consultas(request):
    consultas = Consulta.objects.select_related('mascota', 'veterinario').all().order_by('-fecha_consulta')
    return render(request, 'clinica/lista_consultas.html', {'consultas': consultas})

def agregar_consulta(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            id_mascota = request.POST.get('mascota')
            id_veterinario = request.POST.get('veterinario')
            motivo = request.POST.get('motivo')
            diagnostico = request.POST.get('diagnostico')
            tratamiento = request.POST.get('tratamiento')
            observaciones = request.POST.get('observaciones')
            costo = request.POST.get('costo')
            
            print(f"🔍 DEBUG: Datos consulta - Mascota ID: {id_mascota}, Veterinario ID: {id_veterinario}")
            
            if id_mascota and motivo:
                # Verificar que la mascota existe
                mascota = Mascota.objects.get(id=id_mascota)
                
                consulta_data = {
                    'mascota': mascota,
                    'motivo': motivo,
                    'diagnostico': diagnostico or None,
                    'tratamiento': tratamiento or None,
                    'observaciones': observaciones or None,
                }
                
                # Agregar veterinario si se seleccionó uno
                if id_veterinario:
                    veterinario = Veterinario.objects.get(id=id_veterinario)
                    consulta_data['veterinario'] = veterinario
                
                # Agregar costo si se proporcionó
                if costo:
                    consulta_data['costo'] = float(costo)
                
                consulta = Consulta.objects.create(**consulta_data)
                messages.success(request, f'✅ Consulta registrada exitosamente para {mascota.nombre}')
                return redirect('lista_consultas')
                
            else:
                messages.error(request, '❌ La mascota y el motivo son obligatorios')
                
        except Mascota.DoesNotExist:
            messages.error(request, '❌ La mascota seleccionada no existe')
        except Veterinario.DoesNotExist:
            messages.error(request, '❌ El veterinario seleccionado no existe')
        except Exception as e:
            messages.error(request, f'❌ Error al guardar consulta: {e}')
    
    # Obtener datos para los dropdowns
    mascotas = Mascota.objects.select_related('dueno').all()
    veterinarios = Veterinario.objects.filter(activo=True)
    
    return render(request, 'clinica/agregar_consulta.html', {
        'mascotas': mascotas,
        'veterinarios': veterinarios
    })

def historial_mascota(request, mascota_id):
    """Ver historial de consultas de una mascota específica"""
    try:
        mascota = Mascota.objects.get(id=mascota_id)
        consultas = Consulta.objects.filter(mascota=mascota).select_related('veterinario').order_by('-fecha_consulta')
        
        return render(request, 'clinica/historial_mascota.html', {
            'mascota': mascota,
            'consultas': consultas
        })
        
    except Mascota.DoesNotExist:
        messages.error(request, '❌ Mascota no encontrada')
        return redirect('lista_mascotas')