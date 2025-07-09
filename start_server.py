#!/usr/bin/env python3
"""
Script universal para iniciar el servidor según el sistema operativo
"""

import os
import sys
import platform

def start_gunicorn():
    """Inicia el servidor con Gunicorn (Linux/Mac)"""
    print("🚀 Iniciando servidor con Gunicorn...")
    print("🌐 La aplicación estará disponible en: http://127.0.0.1:8000")
    print("⏹️  Presiona Ctrl+C para detener")
    
    os.system("gunicorn wsgi:app --bind 127.0.0.1:8000 --workers 2")

def start_waitress():
    """Inicia el servidor con Waitress (Windows)"""
    print("🚀 Iniciando servidor con Waitress...")
    print("🌐 La aplicación estará disponible en: http://127.0.0.1:8000")
    print("⏹️  Presiona Ctrl+C para detener")
    
    from waitress import serve
    from app import app
    
    try:
        serve(app, host='127.0.0.1', port=8000)
    except KeyboardInterrupt:
        print("\n⏹️  Servidor detenido por el usuario")

def start_flask_dev():
    """Inicia el servidor de desarrollo de Flask"""
    print("🚀 Iniciando servidor de desarrollo Flask...")
    print("🌐 La aplicación estará disponible en: http://127.0.0.1:5000")
    print("⏹️  Presiona Ctrl+C para detener")
    
    from app import app
    app.run(debug=True, host='127.0.0.1', port=5000)

def main():
    """Función principal que detecta el sistema y elige el servidor"""
    print("🔧 Detectando sistema operativo...")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("✅ Detectado: Windows")
        print("📝 Usando Waitress (compatible con Windows)")
        start_waitress()
    elif system in ["linux", "darwin"]:  # Linux o Mac
        print("✅ Detectado:", system.title())
        print("📝 Usando Gunicorn")
        start_gunicorn()
    else:
        print("⚠️  Sistema no reconocido, usando servidor de desarrollo Flask")
        start_flask_dev()

if __name__ == "__main__":
    main() 