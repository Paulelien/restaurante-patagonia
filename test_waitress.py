#!/usr/bin/env python3
"""
Script para probar la aplicación con Waitress en Windows
"""

from waitress import serve
from app import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor con Waitress...")
    print("🌐 La aplicación estará disponible en: http://127.0.0.1:8000")
    print("⏹️  Presiona Ctrl+C para detener")
    
    try:
        serve(app, host='127.0.0.1', port=8000)
    except KeyboardInterrupt:
        print("\n⏹️  Servidor detenido por el usuario") 