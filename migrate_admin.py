#!/usr/bin/env python3
"""
Script para migrar el sistema de administración de Patagonia Raw Bar
Este script convierte el sistema de contraseña global a usuarios administradores
"""

import os
import sys
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

def main():
    with app.app_context():
        print("🔧 Migración del Sistema de Administración - Patagonia Raw Bar")
        print("=" * 60)
        
        # Verificar si ya existe algún administrador
        admin_existente = Usuario.query.filter_by(is_admin=True).first()
        if admin_existente:
            print(f"✅ Ya existe un administrador: {admin_existente.nombre} ({admin_existente.email})")
            print("El sistema ya está migrado correctamente.")
            return
        
        print("📋 Configuración del Primer Administrador")
        print("-" * 40)
        
        # Solicitar datos del administrador
        nombre = input("Nombre completo del administrador: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            return
        
        email = input("Email del administrador: ").strip()
        if not email:
            print("❌ El email es obligatorio")
            return
        
        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            print(f"⚠️  El email {email} ya está registrado")
            respuesta = input("¿Convertir este usuario en administrador? (s/n): ").strip().lower()
            if respuesta == 's':
                usuario_existente.is_admin = True
                db.session.commit()
                print(f"✅ Usuario {usuario_existente.nombre} convertido en administrador")
                return
            else:
                print("❌ Operación cancelada")
                return
        
        password = input("Contraseña del administrador: ").strip()
        if not password:
            print("❌ La contraseña es obligatoria")
            return
        
        password_confirmar = input("Confirmar contraseña: ").strip()
        if password != password_confirmar:
            print("❌ Las contraseñas no coinciden")
            return
        
        # Crear el administrador
        try:
            admin = Usuario(
                email=email,
                password_hash=generate_password_hash(password),
                nombre=nombre,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Administrador creado exitosamente!")
            print(f"   Nombre: {nombre}")
            print(f"   Email: {email}")
            print("\n🔐 Ahora puedes acceder al panel de administración con estas credenciales")
            print("   URL: /admin/login")
            
        except Exception as e:
            print(f"❌ Error al crear el administrador: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main() 