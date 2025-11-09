# clinica/management/commands/migrar_a_supabase.py
import os
import sys
from django.core.management.base import BaseCommand
from clinica.models import Dueno, Mascota, Veterinario, Consulta
from clinica.supabase_client import supabase

class Command(BaseCommand):
    help = 'Migrar datos de SQLite a Supabase'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tablas',
            type=str,
            help='Tablas específicas a migrar (ej: dueno,mascota)'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 INICIANDO MIGRACIÓN A SUPABASE')
        self.stdout.write('=' * 50)
        
        if not supabase:
            self.stdout.write(self.style.ERROR('❌ No hay conexión a Supabase'))
            self.stdout.write('💡 Verifica tus variables de entorno SUPABASE_URL y SUPABASE_KEY')
            return

        # Verificar conexión
        try:
            resultado = supabase.table("dueno").select("*").limit(1).execute()
            self.stdout.write(self.style.SUCCESS('✅ Conexión a Supabase verificada'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error conectando a Supabase: {e}'))
            return

        tablas_migrar = options['tablas']
        
        if not tablas_migrar or 'dueno' in tablas_migrar:
            self.migrar_duenos()
        
        if not tablas_migrar or 'veterinario' in tablas_migrar:
            self.migrar_veterinarios()
            
        if not tablas_migrar or 'mascota' in tablas_migrar:
            self.migrar_mascotas()
            
        if not tablas_migrar or 'consulta' in tablas_migrar:
            self.migrar_consultas()
            
        if not tablas_migrar or 'pago' in tablas_migrar:
            self.migrar_pagos()

        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Migración completada!'))

    def migrar_duenos(self):
        self.stdout.write('\n📋 MIGRANDO DUEÑOS...')
        dueños = Dueno.objects.all()
        
        if not dueños:
            self.stdout.write('  ℹ️ No hay dueños para migrar')
            return
            
        migrados = 0
        for dueno in dueños:
            try:
                datos = {
                    "nombre": dueno.nombre or "",
                    "telefono": dueno.telefono or "",
                    "email": dueno.email or "",
                    "direccion": dueno.direccion or ""
                }
                
                # Verificar si ya existe
                existente = supabase.table("dueno").select("id").eq("nombre", dueno.nombre).execute()
                
                if existente.data:
                    self.stdout.write(f'  ⚠️ {dueno.nombre} (ya existe en Supabase)')
                else:
                    resultado = supabase.table("dueno").insert(datos).execute()
                    migrados += 1
                    self.stdout.write(f'  ✅ {dueno.nombre}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {dueno.nombre}: {str(e)[:100]}...'))

        self.stdout.write(f'  📊 Total: {migrados}/{len(dueños)} dueños migrados')

    def migrar_veterinarios(self):
        self.stdout.write('\n👨‍⚕️ MIGRANDO VETERINARIOS...')
        veterinarios = Veterinario.objects.all()
        
        if not veterinarios:
            self.stdout.write('  ℹ️ No hay veterinarios para migrar')
            return
            
        migrados = 0
        for vet in veterinarios:
            try:
                datos = {
                    "nombre": vet.nombre or "",
                    "especialidad": vet.especialidad or "",
                    "telefono": vet.telefono or "",
                    "email": vet.email or "",
                    "activo": vet.activo
                }
                
                # Verificar si ya existe
                existente = supabase.table("veterinario").select("id").eq("nombre", vet.nombre).execute()
                
                if existente.data:
                    self.stdout.write(f'  ⚠️ {vet.nombre} (ya existe en Supabase)')
                else:
                    resultado = supabase.table("veterinario").insert(datos).execute()
                    migrados += 1
                    self.stdout.write(f'  ✅ {vet.nombre}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {vet.nombre}: {str(e)[:100]}...'))

        self.stdout.write(f'  📊 Total: {migrados}/{len(veterinarios)} veterinarios migrados')

    def migrar_mascotas(self):
        self.stdout.write('\n🐕 MIGRANDO MASCOTAS...')
        mascotas = Mascota.objects.select_related('dueno').all()
        
        if not mascotas:
            self.stdout.write('  ℹ️ No hay mascotas para migrar')
            return
            
        # Primero necesitamos mapear IDs locales a IDs de Supabase
        mapeo_duenos = self.obtener_mapeo_duenos()
        
        migrados = 0
        for mascota in mascotas:
            try:
                # Buscar el ID de Supabase del dueño
                id_dueno_supabase = mapeo_duenos.get(mascota.dueno.nombre)
                
                if not id_dueno_supabase:
                    self.stdout.write(f'  ⚠️ {mascota.nombre} (dueño no encontrado en Supabase)')
                    continue
                
                datos = {
                    "nombre": mascota.nombre or "",
                    "especie": mascota.especie or "",
                    "raza": mascota.raza or "",
                    "fecha_nacimiento": mascota.fecha_nacimiento.isoformat() if mascota.fecha_nacimiento else None,
                    "id_dueno": id_dueno_supabase
                }
                
                resultado = supabase.table("mascota").insert(datos).execute()
                migrados += 1
                self.stdout.write(f'  ✅ {mascota.nombre} (Dueño: {mascota.dueno.nombre})')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {mascota.nombre}: {str(e)[:100]}...'))

        self.stdout.write(f'  📊 Total: {migrados}/{len(mascotas)} mascotas migradas')

    def migrar_consultas(self):
        self.stdout.write('\n🏥 MIGRANDO CONSULTAS...')
        consultas = Consulta.objects.select_related('mascota', 'veterinario').all()
        
        if not consultas:
            self.stdout.write('  ℹ️ No hay consultas para migrar')
            return
            
        # Mapeos necesarios
        mapeo_mascotas = self.obtener_mapeo_mascotas()
        mapeo_veterinarios = self.obtener_mapeo_veterinarios()
        
        migrados = 0
        for consulta in consultas:
            try:
                # Buscar IDs en Supabase
                id_mascota_supabase = mapeo_mascotas.get(consulta.mascota.nombre)
                id_veterinario_supabase = mapeo_veterinarios.get(consulta.veterinario.nombre) if consulta.veterinario else None
                
                if not id_mascota_supabase:
                    self.stdout.write(f'  ⚠️ Consulta de {consulta.mascota.nombre} (mascota no encontrada)')
                    continue
                
                datos = {
                    "motivo": consulta.motivo or "",
                    "diagnostico": consulta.diagnostico or "",
                    "tratamiento": consulta.tratamiento or "",
                    "observaciones": consulta.observaciones or "",
                    "costo": float(consulta.costo) if consulta.costo else 0.0,
                    "fecha_consulta": consulta.fecha_consulta.isoformat() if consulta.fecha_consulta else None,
                    "id_mascota": id_mascota_supabase,
                    "id_veterinario": id_veterinario_supabase
                }
                
                resultado = supabase.table("consulta").insert(datos).execute()
                migrados += 1
                self.stdout.write(f'  ✅ Consulta de {consulta.mascota.nombre}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Consulta de {consulta.mascota.nombre}: {str(e)[:100]}...'))

        self.stdout.write(f'  📊 Total: {migrados}/{len(consultas)} consultas migradas')

    def migrar_pagos(self):
        self.stdout.write('\n💰 MIGRANDO PAGOS...')
        # Nota: Necesitarías tener un modelo Pago en Django primero
        self.stdout.write('  ℹ️ No hay modelo Pago en Django para migrar')

    def obtener_mapeo_duenos(self):
        """Obtener mapeo de nombres de dueños a IDs de Supabase"""
        self.stdout.write('  🔍 Obteniendo mapeo de dueños...')
        mapeo = {}
        try:
            resultado = supabase.table("dueno").select("id, nombre").execute()
            for dueno in resultado.data:
                mapeo[dueno['nombre']] = dueno['id']
            self.stdout.write(f'  📋 {len(mapeo)} dueños encontrados en Supabase')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error obteniendo dueños: {e}'))
        return mapeo

    def obtener_mapeo_mascotas(self):
        """Obtener mapeo de nombres de mascotas a IDs de Supabase"""
        self.stdout.write('  🔍 Obteniendo mapeo de mascotas...')
        mapeo = {}
        try:
            resultado = supabase.table("mascota").select("id, nombre").execute()
            for mascota in resultado.data:
                mapeo[mascota['nombre']] = mascota['id']
            self.stdout.write(f'  📋 {len(mapeo)} mascotas encontradas en Supabase')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error obteniendo mascotas: {e}'))
        return mapeo

    def obtener_mapeo_veterinarios(self):
        """Obtener mapeo de nombres de veterinarios a IDs de Supabase"""
        self.stdout.write('  🔍 Obteniendo mapeo de veterinarios...')
        mapeo = {}
        try:
            resultado = supabase.table("veterinario").select("id, nombre").execute()
            for vet in resultado.data:
                mapeo[vet['nombre']] = vet['id']
            self.stdout.write(f'  📋 {len(mapeo)} veterinarios encontrados en Supabase')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error obteniendo veterinarios: {e}'))
        return mapeo