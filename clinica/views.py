# clinica/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Dueno, Mascota, Veterinario, Consulta, Pago
from .forms import DuenoForm

# NO importar supabase aquí - causará importación circular
# from .supabase_client import supabase

def get_supabase_client():
    """Obtener cliente Supabase solo cuando sea necesario"""
    from .supabase_client import supabase
    return supabase

# VISTAS DE AUTENTICACIÓN (NUEVAS)
def login_view(request):
    """Vista para el login de usuarios"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            
            # Redirigir a la página que intentaban acceder o al home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')
    
    return render(request, 'clinica/login.html')

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, '✅ Has cerrado sesión exitosamente')
    return redirect('login')

def register_view(request):
    """Vista para registro de nuevos usuarios (solo staff)"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'✅ Usuario {user.username} creado exitosamente')
            return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    
    return render(request, 'clinica/register.html', {'form': form})

# VISTAS EXISTENTES CON LOGIN REQUERIDO
@login_required
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

# VISTAS PARA DUEÑOS
@login_required
def lista_duenos(request):
    duenos = Dueno.objects.filter(activo=True).order_by('nombre')
    
    # Calcular estadísticas
    duenos_con_telefono = Dueno.objects.filter(activo=True).exclude(telefono__isnull=True).exclude(telefono='').count()
    duenos_con_email = Dueno.objects.filter(activo=True).exclude(email__isnull=True).exclude(email='').count()
    duenos_inactivos = Dueno.objects.filter(activo=False).count()
    
    return render(request, 'clinica/lista_duenos.html', {
        'duenos': duenos,
        'duenos_con_telefono': duenos_con_telefono,
        'duenos_con_email': duenos_con_email,
        'duenos_inactivos': duenos_inactivos
    })

@login_required
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

@login_required
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

@login_required
def eliminar_dueno_logico(request, dueno_id):
    """Eliminación lógica CORREGIDA"""
    try:
        dueno = Dueno.objects.get(id=dueno_id, activo=True)
        
        # Verificar si tiene mascotas activas antes de eliminar
        mascotas_count = Mascota.objects.filter(dueno=dueno, activo=True).count()
        if mascotas_count > 0:
            messages.error(request, f'❌ No se puede eliminar al dueño "{dueno.nombre}" porque tiene {mascotas_count} mascota(s) activa(s)')
            return redirect('lista_duenos')
        
        # ELIMINACIÓN LÓGICA (no física)
        dueno.eliminar_logicamente()
        messages.success(request, f'✅ Dueño "{dueno.nombre}" eliminado lógicamente')
        
    except Dueno.DoesNotExist:
        messages.error(request, '❌ Dueño no encontrado o ya está inactivo')
    
    return redirect('lista_duenos')

@login_required
def lista_duenos_inactivos(request):
    """Lista de dueños eliminados lógicamente"""
    duenos_inactivos = Dueno.objects.filter(activo=False).order_by('-fecha_eliminacion')
    
    return render(request, 'clinica/lista_duenos_inactivos.html', {
        'duenos_inactivos': duenos_inactivos
    })

@login_required
def restaurar_dueno(request, dueno_id):
    """Restaurar un dueño eliminado lógicamente"""
    try:
        dueno = Dueno.objects.get(id=dueno_id, activo=False)
        dueno.restaurar()
        messages.success(request, f'✅ Dueño "{dueno.nombre}" restaurado exitosamente')
    except Dueno.DoesNotExist:
        messages.error(request, '❌ Dueño no encontrado o ya está activo')
    
    return redirect('lista_duenos_inactivos')

@login_required
def mascotas_dueno(request, dueno_id):
    """Ver todas las mascotas de un dueño específico"""
    try:
        dueno = Dueno.objects.get(id=dueno_id)
        mascotas = Mascota.objects.filter(dueno=dueno, activo=True)
        
        return render(request, 'clinica/mascotas_dueno.html', {
            'dueno': dueno,
            'mascotas': mascotas
        })
        
    except Dueno.DoesNotExist:
        messages.error(request, '❌ Dueño no encontrado')
        return redirect('lista_duenos')

# VISTAS PARA VETERINARIOS
@login_required
def lista_veterinarios(request):
    veterinarios = Veterinario.objects.filter(activo=True).order_by('nombre')
    veterinarios_activos = Veterinario.objects.filter(activo=True).count()
    especialidades_unicas = Veterinario.objects.filter(activo=True).exclude(especialidad__isnull=True).exclude(especialidad='').values_list('especialidad', flat=True).distinct().count()
    
    return render(request, 'clinica/lista_veterinarios.html', {
        'veterinarios': veterinarios,
        'veterinarios_activos': veterinarios_activos,
        'especialidades_unicas': especialidades_unicas
    })

@login_required
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

@login_required
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

@login_required
def eliminar_veterinario_logico(request, veterinario_id):
    """Eliminación lógica de veterinario"""
    try:
        veterinario = Veterinario.objects.get(id=veterinario_id, activo=True)
        veterinario.eliminar_logicamente()
        messages.success(request, f'✅ Veterinario "{veterinario.nombre}" eliminado lógicamente')
        
    except Veterinario.DoesNotExist:
        messages.error(request, '❌ Veterinario no encontrado o ya está inactivo')
    
    return redirect('lista_veterinarios')

@login_required
def lista_veterinarios_inactivos(request):
    """Lista de veterinarios eliminados lógicamente"""
    veterinarios_inactivos = Veterinario.objects.filter(activo=False).order_by('-fecha_eliminacion')
    
    return render(request, 'clinica/lista_veterinarios_inactivos.html', {
        'veterinarios_inactivos': veterinarios_inactivos
    })

@login_required
def restaurar_veterinario(request, veterinario_id):
    """Restaurar un veterinario eliminado lógicamente"""
    try:
        veterinario = Veterinario.objects.get(id=veterinario_id, activo=False)
        veterinario.restaurar()
        messages.success(request, f'✅ Veterinario "{veterinario.nombre}" restaurado exitosamente')
    except Veterinario.DoesNotExist:
        messages.error(request, '❌ Veterinario no encontrado o ya está activo')
    
    return redirect('lista_veterinarios_inactivos')

# VISTAS PARA MASCOTAS
@login_required
def lista_mascotas(request):
    mascotas = Mascota.objects.filter(activo=True).select_related('dueno').all()
    duenos_count = Dueno.objects.filter(activo=True).count()
    especies_unicas = Mascota.objects.filter(activo=True).exclude(especie__isnull=True).exclude(especie='').values_list('especie', flat=True).distinct().count()
    
    return render(request, 'clinica/lista_mascotas.html', {
        'mascotas': mascotas,
        'duenos_count': duenos_count,
        'especies_unicas': especies_unicas
    })

@login_required
def agregar_mascota(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            especie = request.POST.get('especie')
            raza = request.POST.get('raza')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            id_dueno = request.POST.get('dueno')
            
            if nombre and id_dueno:
                # Validar que la fecha de nacimiento no sea en el futuro
                if fecha_nacimiento:
                    from datetime import datetime
                    fecha_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                    from datetime import date
                    if fecha_obj > date.today():
                        messages.error(request, '❌ La fecha de nacimiento no puede ser en el futuro')
                        duenos = Dueno.objects.filter(activo=True).order_by('nombre')
                        return render(request, 'clinica/agregar_mascota.html', {'duenos': duenos})
                
                # Verificar que el dueño existe en SQLite
                dueno_local = Dueno.objects.get(id=id_dueno, activo=True)
                
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
            messages.error(request, '❌ El dueño seleccionado no existe o está inactivo')
        except Exception as e:
            messages.error(request, f'❌ Error al guardar mascota: {e}')
    
    # Obtener dueños activos para el dropdown
    duenos = Dueno.objects.filter(activo=True)
    return render(request, 'clinica/agregar_mascota.html', {'duenos': duenos})

@login_required
def eliminar_mascota_logico(request, mascota_id):
    """Eliminación lógica de mascota"""
    try:
        mascota = Mascota.objects.get(id=mascota_id, activo=True)
        mascota.eliminar_logicamente()
        messages.success(request, f'✅ Mascota "{mascota.nombre}" eliminada lógicamente')
        
    except Mascota.DoesNotExist:
        messages.error(request, '❌ Mascota no encontrada o ya está inactiva')
    
    return redirect('lista_mascotas')

@login_required
def lista_mascotas_inactivas(request):
    """Lista de mascotas eliminadas lógicamente"""
    mascotas_inactivas = Mascota.objects.filter(activo=False).select_related('dueno').order_by('-fecha_eliminacion')
    
    return render(request, 'clinica/lista_mascotas_inactivas.html', {
        'mascotas_inactivas': mascotas_inactivas
    })

@login_required
def restaurar_mascota(request, mascota_id):
    """Restaurar una mascota eliminada lógicamente"""
    try:
        mascota = Mascota.objects.get(id=mascota_id, activo=False)
        mascota.restaurar()
        messages.success(request, f'✅ Mascota "{mascota.nombre}" restaurada exitosamente')
    except Mascota.DoesNotExist:
        messages.error(request, '❌ Mascota no encontrada o ya está activa')
    
    return redirect('lista_mascotas_inactivas')

# VISTAS PARA CONSULTAS
@login_required
def lista_consultas(request):
    consultas = Consulta.objects.filter(activo=True).select_related('mascota', 'veterinario').all().order_by('-fecha_consulta')
    mascotas_con_consultas = Mascota.objects.filter(consulta__isnull=False, activo=True).distinct().count()
    
    return render(request, 'clinica/lista_consultas.html', {
        'consultas': consultas,
        'mascotas_con_consultas': mascotas_con_consultas
    })

@login_required
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
                mascota_local = Mascota.objects.get(id=id_mascota, activo=True)
                
                veterinario_local = None
                if id_veterinario:
                    veterinario_local = Veterinario.objects.get(id=id_veterinario, activo=True)
                
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
            messages.error(request, '❌ La mascota seleccionada no existe o está inactiva')
        except Veterinario.DoesNotExist:
            messages.error(request, '❌ El veterinario seleccionado no existe o está inactivo')
        except Exception as e:
            messages.error(request, f'❌ Error al guardar consulta: {e}')
    
    # Obtener datos activos para los dropdowns
    mascotas = Mascota.objects.filter(activo=True).select_related('dueno').all()
    veterinarios = Veterinario.objects.filter(activo=True)
    
    return render(request, 'clinica/agregar_consulta.html', {
        'mascotas': mascotas,
        'veterinarios': veterinarios
    })

@login_required
def eliminar_consulta_logico(request, consulta_id):
    """Eliminación lógica de consulta"""
    try:
        consulta = Consulta.objects.get(id=consulta_id, activo=True)
        consulta.eliminar_logicamente()
        messages.success(request, f'✅ Consulta eliminada lógicamente')
        
    except Consulta.DoesNotExist:
        messages.error(request, '❌ Consulta no encontrada o ya está inactiva')
    
    return redirect('lista_consultas')

@login_required
def lista_consultas_inactivas(request):
    """Lista de consultas eliminadas lógicamente"""
    consultas_inactivas = Consulta.objects.filter(activo=False).select_related('mascota', 'veterinario').order_by('-fecha_eliminacion')
    
    return render(request, 'clinica/lista_consultas_inactivas.html', {
        'consultas_inactivas': consultas_inactivas
    })

@login_required
def restaurar_consulta(request, consulta_id):
    """Restaurar una consulta eliminada lógicamente"""
    try:
        consulta = Consulta.objects.get(id=consulta_id, activo=False)
        consulta.restaurar()
        messages.success(request, f'✅ Consulta restaurada exitosamente')
    except Consulta.DoesNotExist:
        messages.error(request, '❌ Consulta no encontrada o ya está activa')
    
    return redirect('lista_consultas_inactivas')

@login_required
def historial_mascota(request, mascota_id):
    """Ver historial de consultas de una mascota específica"""
    try:
        mascota = Mascota.objects.get(id=mascota_id)
        consultas = Consulta.objects.filter(mascota=mascota, activo=True).select_related('veterinario').order_by('-fecha_consulta')
        
        return render(request, 'clinica/historial_mascota.html', {
            'mascota': mascota,
            'consultas': consultas
        })
        
    except Mascota.DoesNotExist:
        messages.error(request, '❌ Mascota no encontrada')
        return redirect('lista_mascotas')

# VISTAS PARA PAGOS
@login_required
def eliminar_pago_logico(request, pago_id):
    """Eliminación lógica de pago"""
    try:
        pago = Pago.objects.get(id=pago_id, activo=True)
        pago.eliminar_logicamente()
        messages.success(request, f'✅ Pago eliminado lógicamente')
        
    except Pago.DoesNotExist:
        messages.error(request, '❌ Pago no encontrado o ya está inactivo')
    
    return redirect('lista_consultas')  # Ajustar según tu ruta de pagos

@login_required
def lista_pagos_inactivos(request):
    """Lista de pagos eliminados lógicamente"""
    pagos_inactivos = Pago.objects.filter(activo=False).select_related('consulta').order_by('-fecha_eliminacion')
    
    return render(request, 'clinica/lista_pagos_inactivos.html', {
        'pagos_inactivos': pagos_inactivos
    })

@login_required
def restaurar_pago(request, pago_id):
    """Restaurar un pago eliminado lógicamente"""
    try:
        pago = Pago.objects.get(id=pago_id, activo=False)
        pago.restaurar()
        messages.success(request, f'✅ Pago restaurado exitosamente')
    except Pago.DoesNotExist:
        messages.error(request, '❌ Pago no encontrado o ya está activo')
    
    return redirect('lista_pagos_inactivos')

# VETERINARIOS - Eliminación Lógica
@login_required
def eliminar_veterinario_logico(request, veterinario_id):
    """Eliminación lógica de veterinario"""
    try:
        veterinario = Veterinario.objects.get(id=veterinario_id, activo=True)
        veterinario.eliminar_logicamente()
        messages.success(request, f'✅ Veterinario "{veterinario.nombre}" eliminado lógicamente')
        
    except Veterinario.DoesNotExist:
        messages.error(request, '❌ Veterinario no encontrado o ya está inactivo')
    
    return redirect('lista_veterinarios')

@login_required
def lista_veterinarios_inactivos(request):
    """Lista de veterinarios eliminados lógicamente"""
    veterinarios_inactivos = Veterinario.objects.filter(activo=False).order_by('-fecha_eliminacion')
    
    return render(request, 'clinica/lista_veterinarios_inactivos.html', {
        'veterinarios_inactivos': veterinarios_inactivos
    })

@login_required
def restaurar_veterinario(request, veterinario_id):
    """Restaurar un veterinario eliminado lógicamente"""
    if not request.user.is_staff:  # Solo staff/admin pueden restaurar
        messages.error(request, '❌ No tienes permisos para restaurar veterinarios. Contacta al administrador.')
        return redirect('lista_veterinarios_inactivos')
    
    try:
        veterinario = Veterinario.objects.get(id=veterinario_id, activo=False)
        veterinario.restaurar()
        messages.success(request, f'✅ Veterinario "{veterinario.nombre}" restaurado exitosamente')
    except Veterinario.DoesNotExist:
        messages.error(request, '❌ Veterinario no encontrado o ya está activo')
    
    return redirect('lista_veterinarios_inactivos')