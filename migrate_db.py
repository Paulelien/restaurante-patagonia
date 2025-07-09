#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar la base de datos y agregar campos de recuperación de contraseña
"""

import os
import sqlite3
from datetime import datetime

def migrate_database():
    """Migra la base de datos para agregar campos de recuperación de contraseña"""
    
    db_path = 'patagonia.db'
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos 'patagonia.db'")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Iniciando migración de la base de datos...")
        
        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(usuario)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Agregar campo reset_token si no existe
        if 'reset_token' not in columns:
            print("➕ Agregando campo 'reset_token'...")
            cursor.execute("ALTER TABLE usuario ADD COLUMN reset_token VARCHAR(100)")
        
        # Agregar campo reset_token_expiry si no existe
        if 'reset_token_expiry' not in columns:
            print("➕ Agregando campo 'reset_token_expiry'...")
            cursor.execute("ALTER TABLE usuario ADD COLUMN reset_token_expiry DATETIME")
        
        # Crear índice único para reset_token (SQLite no permite UNIQUE en ALTER TABLE)
        try:
            cursor.execute("CREATE UNIQUE INDEX idx_usuario_reset_token ON usuario(reset_token)")
            print("➕ Creando índice único para reset_token...")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print("ℹ️  Índice único para reset_token ya existe")
            else:
                print(f"⚠️  Advertencia al crear índice: {e}")
        
        # Confirmar cambios
        conn.commit()
        
        print("✅ Migración completada exitosamente")
        print("📋 Campos agregados:")
        print("   - reset_token: Token único para recuperación")
        print("   - reset_token_expiry: Fecha de expiración del token")
        
        # Mostrar estructura actualizada
        cursor.execute("PRAGMA table_info(usuario)")
        columns = cursor.fetchall()
        
        print("\n📊 Estructura actualizada de la tabla 'usuario':")
        for column in columns:
            print(f"   - {column[1]} ({column[2]})")
        
        # Mostrar índices
        cursor.execute("PRAGMA index_list(usuario)")
        indexes = cursor.fetchall()
        
        print("\n🔍 Índices de la tabla 'usuario':")
        for index in indexes:
            print(f"   - {index[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    print("🔄 MIGRACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    # Preguntar confirmación
    response = input("¿Deseas continuar con la migración? (s/n): ").lower()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        success = migrate_database()
        if success:
            print("\n🎉 ¡Migración completada!")
            print("   El sistema de recuperación de contraseña está listo para usar.")
        else:
            print("\n❌ La migración falló. Revisa los errores arriba.")
    else:
        print("❌ Migración cancelada por el usuario.")
    
    print("\n" + "=" * 50) 