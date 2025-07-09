#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""

import os
from app import app, db, Configuracion

def init_database():
    """Inicializa la base de datos y crea configuración inicial"""
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear configuración inicial si no existe
        if not Configuracion.query.first():
            print("📝 Creando configuración inicial...")
            configs_iniciales = [
                ('titulo_sitio', 'Restaurante Patagonia - Arica'),
                ('descripcion_hero', 'Ubicado en Arica, ofrecemos lo mejor de la gastronomía patagónica en el norte de Chile.'),
                ('facebook_url', 'https://facebook.com/patagoniaarica'),
                ('instagram_url', 'https://instagram.com/patagoniaarica'),
                ('telefono', '+56 58 123 4567'),
                ('direccion', 'Av. Principal 123, Arica, Chile'),
                ('horario', 'Lunes a Domingo: 12:00 - 23:00')
            ]
            
            for clave, valor in configs_iniciales:
                config = Configuracion()
                config.clave = clave
                config.valor = valor
                config.descripcion = f'Configuración automática para {clave}'
                db.session.add(config)
            
            db.session.commit()
            print("✅ Configuración inicial creada exitosamente")
        else:
            print("✅ Base de datos ya inicializada")

if __name__ == "__main__":
    print("🚀 Inicializando base de datos...")
    init_database()
    print("✅ Base de datos lista para usar") 