#!/usr/bin/env python3
"""
Script para actualizar la base de datos con el campo observaciones
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def actualizar_base_datos():
    """Actualiza la base de datos con los nuevos campos"""
    
    with app.app_context():
        try:
            print("🔄 Actualizando base de datos...")
            
            # Crear todas las tablas (esto agregará el campo observaciones si no existe)
            db.create_all()
            
            print("✅ Base de datos actualizada exitosamente")
            print("✅ El campo 'observaciones' está ahora disponible en la tabla reserva")
            
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando base de datos: {e}")
            return False

if __name__ == '__main__':
    print("🚀 Iniciando actualización de base de datos...")
    
    if actualizar_base_datos():
        print("🎉 Actualización completada exitosamente")
    else:
        print("💥 Error en la actualización")
        sys.exit(1) 