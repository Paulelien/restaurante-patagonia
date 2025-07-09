#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la configuración de email
"""

import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email_config():
    """Prueba la configuración de email"""
    print("🔧 Probando configuración de email...")
    print("=" * 50)
    
    try:
        # Importar configuración
        from config_email import get_email_config
        config = get_email_config()
        
        print(f"📧 Email configurado: {config['email']}")
        print(f"🔑 Contraseña: {'*' * len(config['password'])} ({len(config['password'])} caracteres)")
        print(f"🌐 Servidor SMTP: {config['smtp_server']}:{config['smtp_port']}")
        
        # Verificar si las credenciales son las por defecto
        if 'TU-EMAIL-REAL@gmail.com' in config['email'] or 'tu-email@gmail.com' in config['email']:
            print("\n❌ ERROR: Las credenciales no han sido configuradas")
            print("   Por favor, edita el archivo 'config_email.py' con tus credenciales reales")
            return False
            
        if 'TU-PASSWORD-APP' in config['password'] or 'tu-password-app' in config['password']:
            print("\n❌ ERROR: La contraseña no ha sido configurada")
            print("   Por favor, edita el archivo 'config_email.py' con tu contraseña de aplicación")
            return False
        
        print("\n✅ Configuración de email válida")
        
        # Probar conexión SMTP
        print("\n🔌 Probando conexión SMTP...")
        import smtplib
        from email.mime.text import MIMEText
        
        try:
            # Crear conexión
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            
            # Intentar login
            server.login(config['email'], config['password'])
            print("✅ Conexión SMTP exitosa")
            
            # Cerrar conexión
            server.quit()
            
            print("\n🎉 ¡Todo está configurado correctamente!")
            print("   Los emails se enviarán desde:", config['email'])
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Error de autenticación")
            print("   Verifica que:")
            print("   1. La autenticación de 2 factores esté activada")
            print("   2. Estés usando una contraseña de aplicación")
            print("   3. Las credenciales estén correctas")
            return False
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando configuración: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_email_send():
    """Prueba enviar un email de prueba"""
    print("\n📤 Probando envío de email...")
    print("=" * 50)
    
    try:
        from notificaciones import Notificaciones
        
        # Crear una reserva de prueba
        class ReservaPrueba:
            def __init__(self):
                self.nombre = "Cliente de Prueba"
                self.email = "test@example.com"
                self.fecha = "01/01/2025"
                self.hora = "19:00"
                self.personas = 2
                self.telefono = "+56912345678"
                self.fecha_creacion = "2025-01-01 18:00:00"
        
        reserva_prueba = ReservaPrueba()
        
        # Crear instancia de notificaciones
        notif = Notificaciones()
        
        # Intentar enviar email
        resultado = notif.enviar_email_reserva_cliente(reserva_prueba)
        
        if resultado:
            print("✅ Email de prueba enviado correctamente")
            print("   (Nota: El email se envió a test@example.com)")
        else:
            print("❌ Error enviando email de prueba")
            
        return resultado
        
    except Exception as e:
        print(f"❌ Error en prueba de envío: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PRUEBA DE CONFIGURACIÓN DE EMAIL")
    print("=" * 50)
    
    # Probar configuración
    config_ok = test_email_config()
    
    if config_ok:
        # Probar envío
        send_ok = test_email_send()
        
        if send_ok:
            print("\n🎉 ¡Todo funciona perfectamente!")
            print("   Tu sistema de email está listo para usar")
        else:
            print("\n⚠️  La configuración parece correcta pero hay problemas al enviar")
    else:
        print("\n❌ Hay problemas con la configuración")
        print("   Revisa el archivo CONFIGURAR_EMAIL.md para instrucciones")
    
    print("\n" + "=" * 50) 