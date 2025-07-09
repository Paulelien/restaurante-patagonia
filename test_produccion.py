#!/usr/bin/env python3
"""
Script para probar la aplicación en modo producción
"""

import subprocess
import sys
import os

def test_gunicorn():
    """Prueba la aplicación con Gunicorn"""
    print("🚀 Probando aplicación con Gunicorn...")
    
    try:
        # Verificar si gunicorn está instalado
        subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
        
        # Ejecutar con gunicorn
        print("✅ Gunicorn instalado. Iniciando servidor...")
        print("🌐 La aplicación estará disponible en: http://127.0.0.1:8000")
        print("⏹️  Presiona Ctrl+C para detener")
        
        subprocess.run([
            sys.executable, "-m", "gunicorn", 
            "wsgi:app", 
            "--bind", "127.0.0.1:8000",
            "--workers", "2",
            "--timeout", "120"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("📦 Verificando dependencias...")
    
    required_packages = [
        'flask', 'flask-sqlalchemy', 'flask-login', 
        'gunicorn', 'werkzeug', 'email-validator'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

if __name__ == "__main__":
    print("🔧 Preparando aplicación para producción...")
    test_dependencies()
    test_gunicorn() 