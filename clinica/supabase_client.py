# clinica/supabase_client.py
import os
from supabase import create_client
from django.conf import settings

class SupabaseClient:
    _instance = None
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.client = None
        self.conectar()
    
    def conectar(self):
        try:
            if not self.url or not self.key:
                raise ValueError("Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")
            
            self.client = create_client(self.url, self.key)
            print("✅ Conectado a Supabase exitosamente")
            
        except Exception as e:
            print(f"❌ Error conectando a Supabase: {e}")
            self.client = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SupabaseClient()
        return cls._instance

# Instancia global
supabase_client = SupabaseClient.get_instance()