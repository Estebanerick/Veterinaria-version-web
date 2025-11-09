# clinica/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Dueno, Mascota, Veterinario, Consulta
from .forms import DuenoForm

# NO importar supabase aquí - causará importación circular
# from .supabase_client import supabase

def get_supabase_client():
    """Obtener cliente Supabase solo cuando sea necesario"""
    from .supabase_client import supabase
    return supabase

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

# En clinica/views.py - actualizar la función lista_duenos
def lista_duenos(request):
    duenos = Dueno.objects.all().order_by('nombre')
    
    # Calcular estadísticas
    duenos_con_telefono = Dueno.objects.exclude(telefono__isnull=True).exclude(telefono='').count()
    duenos_con_email = Dueno.objects.exclude(email__isnull=True).exclude(email='').count()
    
    return render(request, 'clinica/lista_duenos.html', {
        'duenos': duenos,
        'duenos_con_telefono': duenos_con_telefono,
        'duenos_con_email': duenos_con_email
    })

def agregar_dueno(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            direccion = request.POST.get('direccion')
            
            if nombre:
                # 1. Guardar en SQLite (Django)
                dueno_local = Dueno.objects.create(
                    nombre=nombre,
                    telefono=telefono or None,
                    email=email or None,
                    direccion=direccion or None
                )
                
                # 2. Guardar en Supabase (en silencio)
                supabase = get_supabase_client()
                if supabase:
                    datos_supabase = {
                        "nombre": nombre,
                        "telefono": telefono or "",
                        "email": email or "",
                        "direccion": direccion or ""
                    }
                    supabase.table("dueno").insert(datos_supabase).execute()
                    print(f"✅ Dueño sincronizado con Supabase: {nombre}")
                
                messages.success(request, f'✅ Dueño "{dueno_local.nombre}" registrado exitosamente')
                return redirect('lista_duenos')
            else:
                messages.error(request, '❌ El nombre es obligatorio')
                
        except Exception as e:
            messages.error(request, f'❌ Error al guardar: {e}')
    
    return render(request, 'clinica/agregar_dueno.html')

# clinica/views.py - agregar estas funciones después de las existentes

def editar_dueno(request, dueno_id):
    try:
        dueno = Dueno.objects.get(id=dueno_id)
        
        if request.method == 'POST':
            # Actualizar datos
            dueno.nombre = request.POST.get('nombre', dueno.nombre)
            dueno.telefono = request.POST.get('telefono', dueno.telefono)
            dueno.email = request.POST.get('email', dueno.email)
            dueno.direccion = request.POST.get('direccion', dueno.direccion)
            dueno.save()
            
            # Actualizar en Supabase también
            supabase = get_supabase_client()
            if supabase:
                datos_supabase = {
                    "nombre": dueno.nombre,
                    "telefono": dueno.telefono or "",
                    "email": dueno.email or "",
                    "direccion": dueno.direccion or ""
                }
                supabase.table("dueno").update(datos_supabase).eq("nombre", dueno.nombre).execute()
                print(f"✅ Dueño actualizado en Supabase: {dueno.nombre}")
            
            messages.success(request, f'✅ Dueño "{dueno.nombre}" actualizado exitosamente')
            return redirect('lista_duenos')
        
        return render(request, 'clinica/editar_dueno.html', {'dueno': dueno})
        
    except Dueno.DoesNotExist:
        messages.error(request, '❌ Dueño no encontrado')
        return redirect('lista_duenos')

def eliminar_dueno(request, dueno_id):
    try:
        dueno = Dueno.objects.get(id=dueno_id)
        nombre_dueno = dueno.nombre
        
        # Verificar si tiene mascotas antes de eliminar
        mascotas_count = Mascota.objects.filter(dueno=dueno).count()
        if mascotas_count > 0:
            messages.error(request, f'❌ No se puede eliminar al dueño "{nombre_dueno}" porque tiene {mascotas_count} mascota(s) registrada(s)')
            return redirect('lista_duenos')
        
        dueno.delete()
        
        # Eliminar de Supabase también
        supabase = get_supabase_client()
        if supabase:
            supabase.table("dueno").delete().eq("nombre", nombre_dueno).execute()
            print(f"✅ Dueño eliminado de Supabase: {nombre_dueno}")
        
        messages.success(request, f'✅ Dueño "{nombre_dueno}" eliminado exitosamente')
        
    except Dueno.DoesNotExist:
        messages.error(request, '❌ Dueño no encontrado')
    
    return redirect('lista_duenos')

def mascotas_dueno(request, dueno_id):
    """Ver todas las mascotas de un dueño específico"""
    try:
        dueno = Dueno.objects.get(id=dueno_id)
        mascotas = Mascota.objects.filter(dueno=dueno)
        
        return render(request, 'clinica/mascotas_dueno.html', {
            'dueno': dueno,
            'mascotas': mascotas
        })
        
    except Dueno.DoesNotExist:
        messages.error(request, '❌ Dueño no encontrado')
        return redirect('lista_duenos')

def lista_veterinarios(request):
    veterinarios = Veterinario.objects.all().order_by('nombre')
    veterinarios_activos = Veterinario.objects.filter(activo=True).count()
    especialidades_unicas = Veterinario.objects.exclude(especialidad__isnull=True).exclude(especialidad='').values_list('especialidad', flat=True).distinct().count()
    
    return render(request, 'clinica/lista_veterinarios.html', {
        'veterinarios': veterinarios,
        'veterinarios_activos': veterinarios_activos,
        'especialidades_unicas': especialidades_unicas
    })

def agregar_veterinario(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            especialidad = request.POST.get('especialidad')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            
            if nombre:
                # 1. Guardar en SQLite (Django)
                veterinario_local = Veterinario.objects.create(
                    nombre=nombre,
                    especialidad=especialidad or None,
                    telefono=telefono or None,
                    email=email or None
                )
                
                # 2. Guardar en Supabase (en silencio)
                supabase = get_supabase_client()
                if supabase:
                    datos_supabase = {
                        "nombre": nombre,
                        "especialidad": especialidad or "",
                        "telefono": telefono or "",
                        "email": email or "",
                        "activo": True
                    }
                    supabase.table("veterinario").insert(datos_supabase).execute()
                    print(f"✅ Veterinario sincronizado con Supabase: {nombre}")
                
                messages.success(request, f'✅ Veterinario "{veterinario_local.nombre}" registrado exitosamente')
                return redirect('lista_veterinarios')
            else:
                messages.error(request, '❌ El nombre es obligatorio')
                
        except Exception as e:
            messages.error(request, f'❌ Error al guardar veterinario: {e}')
    
    return render(request, 'clinica/agregar_veterinario.html')

def lista_mascotas(request):
    mascotas = Mascota.objects.select_related('dueno').all()
    duenos_count = Dueno.objects.count()
    especies_unicas = Mascota.objects.exclude(especie__isnull=True).exclude(especie='').values_list('especie', flat=True).distinct().count()
    
    return render(request, 'clinica/lista_mascotas.html', {
        'mascotas': mascotas,
        'duenos_count': duenos_count,
        'especies_unicas': especies_unicas
    })

def agregar_mascota(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            especie = request.POST.get('especie')
            raza = request.POST.get('raza')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            id_dueno = request.POST.get('dueno')
            
            if nombre and id_dueno:
                # Verificar que el dueño existe en SQLite
                dueno_local = Dueno.objects.get(id=id_dueno)
                
                # 1. Guardar en SQLite (Django)
                mascota_local = Mascota.objects.create(
                    nombre=nombre,
                    especie=especie or None,
                    raza=raza or None,
                    fecha_nacimiento=fecha_nacimiento or None,
                    dueno=dueno_local
                )
                
                # 2. Guardar en Supabase (en silencio)
                supabase = get_supabase_client()
                if supabase:
                    # Buscar ID del dueño en Supabase
                    resultado_dueno = supabase.table("dueno").select("id").eq("nombre", dueno_local.nombre).execute()
                    if resultado_dueno.data:
                        id_dueno_supabase = resultado_dueno.data[0]['id']
                        
                        datos_supabase = {
                            "nombre": nombre,
                            "especie": especie or "",
                            "raza": raza or "",
                            "fecha_nacimiento": fecha_nacimiento or None,
                            "id_dueno": id_dueno_supabase
                        }
                        supabase.table("mascota").insert(datos_supabase).execute()
                        print(f"✅ Mascota sincronizada con Supabase: {nombre}")
                    else:
                        print(f"⚠️ Dueño no encontrado en Supabase: {dueno_local.nombre}")
                
                messages.success(request, f'✅ Mascota "{mascota_local.nombre}" registrada exitosamente')
                return redirect('lista_mascotas')
            else:
                messages.error(request, '❌ El nombre y dueño son obligatorios')
                
        except Dueno.DoesNotExist:
            messages.error(request, '❌ El dueño seleccionado no existe')
        except Exception as e:
            messages.error(request, f'❌ Error al guardar mascota: {e}')
    
    # Obtener dueños para el dropdown
    duenos = Dueno.objects.all()
    return render(request, 'clinica/agregar_mascota.html', {'duenos': duenos})

def lista_consultas(request):
    consultas = Consulta.objects.select_related('mascota', 'veterinario').all().order_by('-fecha_consulta')
    mascotas_con_consultas = Mascota.objects.filter(consulta__isnull=False).distinct().count()
    
    return render(request, 'clinica/lista_consultas.html', {
        'consultas': consultas,
        'mascotas_con_consultas': mascotas_con_consultas
    })

def agregar_consulta(request):
    if request.method == 'POST':
        try:
            id_mascota = request.POST.get('mascota')
            id_veterinario = request.POST.get('veterinario')
            motivo = request.POST.get('motivo')
            diagnostico = request.POST.get('diagnostico')
            tratamiento = request.POST.get('tratamiento')
            observaciones = request.POST.get('observaciones')
            costo = request.POST.get('costo')
            
            if id_mascota and motivo:
                # Verificar que la mascota existe en SQLite
                mascota_local = Mascota.objects.get(id=id_mascota)
                
                veterinario_local = None
                if id_veterinario:
                    veterinario_local = Veterinario.objects.get(id=id_veterinario)
                
                # 1. Guardar en SQLite (Django)
                consulta_data = {
                    'mascota': mascota_local,
                    'motivo': motivo,
                    'diagnostico': diagnostico or None,
                    'tratamiento': tratamiento or None,
                    'observaciones': observaciones or None,
                }
                
                if veterinario_local:
                    consulta_data['veterinario'] = veterinario_local
                
                if costo:
                    consulta_data['costo'] = float(costo)
                
                consulta_local = Consulta.objects.create(**consulta_data)
                
                # 2. Guardar en Supabase (en silencio)
                supabase = get_supabase_client()
                if supabase:
                    # Buscar IDs en Supabase
                    resultado_mascota = supabase.table("mascota").select("id").eq("nombre", mascota_local.nombre).execute()
                    id_mascota_supabase = resultado_mascota.data[0]['id'] if resultado_mascota.data else None
                    
                    id_veterinario_supabase = None
                    if veterinario_local:
                        resultado_veterinario = supabase.table("veterinario").select("id").eq("nombre", veterinario_local.nombre).execute()
                        id_veterinario_supabase = resultado_veterinario.data[0]['id'] if resultado_veterinario.data else None
                    
                    if id_mascota_supabase:
                        datos_supabase = {
                            "motivo": motivo,
                            "diagnostico": diagnostico or "",
                            "tratamiento": tratamiento or "",
                            "observaciones": observaciones or "",
                            "costo": float(costo) if costo else 0.0,
                            "id_mascota": id_mascota_supabase,
                            "id_veterinario": id_veterinario_supabase
                        }
                        supabase.table("consulta").insert(datos_supabase).execute()
                        print(f"✅ Consulta sincronizada con Supabase: {mascota_local.nombre}")
                    else:
                        print(f"⚠️ Mascota no encontrada en Supabase: {mascota_local.nombre}")
                
                messages.success(request, f'✅ Consulta registrada exitosamente para {mascota_local.nombre}')
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

def editar_veterinario(request, veterinario_id):
    try:
        veterinario = Veterinario.objects.get(id=veterinario_id)
        
        if request.method == 'POST':
            # Actualizar datos
            veterinario.nombre = request.POST.get('nombre', veterinario.nombre)
            veterinario.especialidad = request.POST.get('especialidad', veterinario.especialidad)
            veterinario.telefono = request.POST.get('telefono', veterinario.telefono)
            veterinario.email = request.POST.get('email', veterinario.email)
            veterinario.save()
            
            messages.success(request, f'✅ Veterinario "{veterinario.nombre}" actualizado exitosamente')
            return redirect('lista_veterinarios')
        
        return render(request, 'clinica/editar_veterinario.html', {'veterinario': veterinario})
        
    except Veterinario.DoesNotExist:
        messages.error(request, '❌ Veterinario no encontrado')
        return redirect('lista_veterinarios')

def eliminar_veterinario(request, veterinario_id):
    try:
        veterinario = Veterinario.objects.get(id=veterinario_id)
        nombre_veterinario = veterinario.nombre
        veterinario.delete()
        
        messages.success(request, f'✅ Veterinario "{nombre_veterinario}" eliminado exitosamente')
        
    except Veterinario.DoesNotExist:
        messages.error(request, '❌ Veterinario no encontrado')
    
    return redirect('lista_veterinarios')