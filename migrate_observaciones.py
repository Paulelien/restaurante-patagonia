#!/usr/bin/env python3
"""
Script de migración para agregar el campo observaciones a la tabla de reservas
"""

import os
import sys
from sqlalchemy import text

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrar_observaciones():
    """Agrega el campo observaciones a la tabla reserva si no existe"""
    
    with app.app_context():
        try:
            print("🔍 Verificando si existe el campo 'observaciones' en la tabla reserva...")
            
            # Verificar si el campo ya existe
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reserva' 
                AND column_name = 'observaciones'
            """))
            
            if result.fetchone():
                print("✅ El campo 'observaciones' ya existe en la tabla reserva")
                return True
            
            print("📝 Agregando campo 'observaciones' a la tabla reserva...")
            
            # Agregar el campo observaciones
            db.session.execute(text("""
                ALTER TABLE reserva 
                ADD COLUMN observaciones TEXT
            """))
            
            db.session.commit()
            print("✅ Campo 'observaciones' agregado exitosamente")
            
            # Verificar que se agregó correctamente
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reserva' 
                AND column_name = 'observaciones'
            """))
            
            if result.fetchone():
                print("✅ Verificación exitosa: el campo 'observaciones' está disponible")
                return True
            else:
                print("❌ Error: El campo no se agregó correctamente")
                return False
                
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🚀 Iniciando migración para agregar campo observaciones...")
    
    if migrar_observaciones():
        print("🎉 Migración completada exitosamente")
    else:
        print("💥 Error en la migración")
        sys.exit(1) 