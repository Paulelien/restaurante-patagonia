import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from flask import current_app

class Notificaciones:
    def __init__(self):
        # Importar configuración
        try:
            from config_email import get_email_config, get_whatsapp_config
            self.email_config = get_email_config()
            self.whatsapp_config = get_whatsapp_config()
        except ImportError:
            # Configuración por defecto si no existe el archivo
            self.email_config = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'email': os.getenv('EMAIL_USER', 'tu-email@gmail.com'),
                'password': os.getenv('EMAIL_PASSWORD', 'tu-password-app')
            }
            
            self.whatsapp_config = {
                'account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
                'auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
                'from_number': os.getenv('TWILIO_FROM_NUMBER', 'whatsapp:+14155238886')
            }
    
    def enviar_email_reserva_cliente(self, reserva):
        """Envía email de confirmación al cliente"""
        try:
            subject = f"Reserva Confirmada - Restaurante Patagonia"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2d3e50, #34495e); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .reserva-info {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🍽️ Restaurante Patagonia</h1>
                        <p>Tu reserva ha sido confirmada</p>
                    </div>
                    <div class="content">
                        <h2>¡Hola {reserva.nombre}!</h2>
                        <p>Tu reserva ha sido confirmada exitosamente. Aquí están los detalles:</p>
                        
                        <div class="reserva-info">
                            <h3>📅 Detalles de la Reserva</h3>
                            <p><strong>Fecha:</strong> {reserva.fecha}</p>
                            <p><strong>Hora:</strong> {reserva.hora}</p>
                            <p><strong>Personas:</strong> {reserva.personas}</p>
                            <p><strong>Estado:</strong> <span style="color: #28a745; font-weight: bold;">Confirmada</span></p>
                        </div>
                        
                        <p><strong>📍 Dirección:</strong> Av. Principal 123, Arica, Chile</p>
                        <p><strong>📞 Teléfono:</strong> +56 58 123 4567</p>
                        
                        <p style="margin-top: 20px;">
                            <a href="https://maps.google.com" class="btn">📍 Ver en Google Maps</a>
                        </p>
                        
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>💡 Consejos para tu visita:</h4>
                            <ul>
                                <li>Llega 10 minutos antes de tu hora de reserva</li>
                                <li>Si necesitas cancelar, hazlo con al menos 2 horas de anticipación</li>
                                <li>¡No olvides tu documento de identidad!</li>
                            </ul>
                        </div>
                        
                        <p>¡Esperamos verte pronto en Patagonia!</p>
                        
                        <div class="footer">
                            <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                            <p>© 2024 Restaurante Patagonia - Arica, Chile</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._enviar_email(reserva.email, subject, html_content)
            
        except Exception as e:
            print(f"Error enviando email al cliente: {e}")
            return False
    
    def enviar_email_reserva_admin(self, reserva):
        """Envía notificación al administrador sobre nueva reserva"""
        try:
            subject = f"Nueva Reserva - {reserva.nombre} - {reserva.fecha}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .reserva-info {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🆕 Nueva Reserva Recibida</h1>
                        <p>Restaurante Patagonia - Panel de Administración</p>
                    </div>
                    <div class="content">
                        <h2>Se ha recibido una nueva reserva</h2>
                        
                        <div class="reserva-info">
                            <h3>👤 Información del Cliente</h3>
                            <p><strong>Nombre:</strong> {reserva.nombre}</p>
                            <p><strong>Teléfono:</strong> {reserva.telefono}</p>
                            <p><strong>Email:</strong> {reserva.email or 'No proporcionado'}</p>
                            <p><strong>Usuario registrado:</strong> {'Sí' if reserva.usuario else 'No'}</p>
                        </div>
                        
                        <div class="reserva-info">
                            <h3>📅 Detalles de la Reserva</h3>
                            <p><strong>Fecha:</strong> {reserva.fecha}</p>
                            <p><strong>Hora:</strong> {reserva.hora}</p>
                            <p><strong>Personas:</strong> {reserva.personas}</p>
                            <p><strong>Estado:</strong> <span style="color: #ffc107; font-weight: bold;">Pendiente de confirmación</span></p>
                            <p><strong>Fecha de creación:</strong> {reserva.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                        </div>
                        
                        <p style="margin-top: 20px;">
                            <a href="http://127.0.0.1:5000/admin" class="btn">🔧 Ir al Panel de Administración</a>
                        </p>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>⚠️ Acción Requerida:</h4>
                            <p>Por favor, revisa y confirma esta reserva desde el panel de administración.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@patagonia-arica.cl')
            return self._enviar_email(admin_email, subject, html_content)
            
        except Exception as e:
            print(f"Error enviando email al admin: {e}")
            return False

    def enviar_email_confirmacion_cliente(self, reserva):
        """Envía email de confirmación al cliente cuando se confirma la reserva"""
        try:
            subject = f"✅ Reserva Confirmada - Restaurante Patagonia"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .reserva-info {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #28a745; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .success-badge {{ background: #28a745; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🍽️ Restaurante Patagonia</h1>
                        <p>¡Tu reserva ha sido confirmada!</p>
                    </div>
                    <div class="content">
                        <h2>¡Hola {reserva.nombre}! 👋</h2>
                        <p>Nos complace informarte que tu reserva ha sido <strong>confirmada exitosamente</strong>.</p>
                        
                        <div class="reserva-info">
                            <h3>📅 Detalles de tu Reserva</h3>
                            <p><strong>Fecha:</strong> {reserva.fecha}</p>
                            <p><strong>Hora:</strong> {reserva.hora}</p>
                            <p><strong>Personas:</strong> {reserva.personas}</p>
                            <p><strong>Estado:</strong> <span class="success-badge">✅ CONFIRMADA</span></p>
                            <p><strong>Confirmada el:</strong> {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                        </div>
                        
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>📍 Información del Restaurante</h4>
                            <p><strong>Dirección:</strong> Av. Principal 123, Arica, Chile</p>
                            <p><strong>Teléfono:</strong> +56 58 123 4567</p>
                            <p><strong>Horario:</strong> Lunes a Domingo: 12:00 - 23:00</p>
                        </div>
                        
                        <p style="margin-top: 20px;">
                            <a href="https://maps.google.com" class="btn">📍 Ver en Google Maps</a>
                        </p>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>💡 Información Importante</h4>
                            <ul>
                                <li><strong>Llega 10 minutos antes</strong> de tu hora de reserva</li>
                                <li>Si necesitas <strong>cancelar o modificar</strong>, hazlo con al menos 2 horas de anticipación</li>
                                <li>Trae tu <strong>documento de identidad</strong></li>
                                <li>¡Disfruta de nuestra gastronomía patagónica!</li>
                            </ul>
                        </div>
                        
                        <p style="text-align: center; font-size: 18px; color: #28a745;">
                            <strong>¡Esperamos verte pronto en Patagonia! 🎉</strong>
                        </p>
                        
                        <div class="footer">
                            <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                            <p>© 2024 Restaurante Patagonia - Arica, Chile</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._enviar_email(reserva.email, subject, html_content)
            
        except Exception as e:
            print(f"Error enviando email de confirmación al cliente: {e}")
            return False
    
    def enviar_whatsapp_reserva_cliente(self, reserva):
        """Envía mensaje de WhatsApp al cliente"""
        try:
            if not self.whatsapp_config['account_sid']:
                print("Configuración de WhatsApp no disponible")
                return False
            
            mensaje = f"""
🍽️ *Restaurante Patagonia - Reserva Confirmada*

¡Hola {reserva.nombre}! Tu reserva ha sido confirmada.

📅 *Detalles:*
• Fecha: {reserva.fecha}
• Hora: {reserva.hora}
• Personas: {reserva.personas}
• Estado: ✅ Confirmada

📍 *Ubicación:* Av. Principal 123, Arica, Chile
📞 *Teléfono:* +56 58 123 4567

💡 *Consejos:*
• Llega 10 minutos antes
• Si necesitas cancelar, hazlo con 2 horas de anticipación

¡Esperamos verte pronto! 🎉

---
*Mensaje automático - No responder*
            """
            
            return self._enviar_whatsapp(reserva.telefono, mensaje)
            
        except Exception as e:
            print(f"Error enviando WhatsApp al cliente: {e}")
            return False
    
    def enviar_whatsapp_reserva_admin(self, reserva):
        """Envía notificación WhatsApp al administrador"""
        try:
            if not self.whatsapp_config['account_sid']:
                print("Configuración de WhatsApp no disponible")
                return False
            
            mensaje = f"""
🆕 *Nueva Reserva - Patagonia*

Se ha recibido una nueva reserva:

👤 *Cliente:* {reserva.nombre}
📞 *Teléfono:* {reserva.telefono}
📅 *Fecha:* {reserva.fecha}
🕐 *Hora:* {reserva.hora}
👥 *Personas:* {reserva.personas}
📧 *Email:* {reserva.email or 'No proporcionado'}

⚠️ *Estado:* Pendiente de confirmación

🔧 Revisa el panel de administración para confirmar.

---
*Notificación automática*
            """
            
            admin_phone = os.getenv('ADMIN_PHONE', '+56912345678')
            return self._enviar_whatsapp(admin_phone, mensaje)
            
        except Exception as e:
            print(f"Error enviando WhatsApp al admin: {e}")
            return False
    
    def _enviar_email(self, to_email, subject, html_content):
        """Función interna para enviar emails"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config['email']
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['email'], to_email, text)
            server.quit()
            
            print(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
    
    def _enviar_whatsapp(self, to_phone, mensaje):
        """Función interna para enviar WhatsApp"""
        try:
            from twilio.rest import Client
            
            client = Client(self.whatsapp_config['account_sid'], self.whatsapp_config['auth_token'])
            
            # Formatear número de teléfono
            if not to_phone.startswith('+'):
                to_phone = '+56' + to_phone.lstrip('0')
            
            message = client.messages.create(
                from_=self.whatsapp_config['from_number'],
                body=mensaje,
                to=f'whatsapp:{to_phone}'
            )
            
            print(f"WhatsApp enviado exitosamente a {to_phone}")
            return True
            
        except Exception as e:
            print(f"Error enviando WhatsApp: {e}")
            return False

# Función de conveniencia para usar desde la aplicación
def notificar_reserva(reserva, notificar_cliente=True, notificar_admin=True):
    """Función principal para enviar notificaciones de reserva"""
    notif = Notificaciones()
    resultados = {}
    
    if notificar_cliente and reserva.email:
        resultados['email_cliente'] = notif.enviar_email_reserva_cliente(reserva)
    
    if notificar_cliente and reserva.telefono:
        resultados['whatsapp_cliente'] = notif.enviar_whatsapp_reserva_cliente(reserva)
    
    if notificar_admin:
        resultados['email_admin'] = notif.enviar_email_reserva_admin(reserva)
        resultados['whatsapp_admin'] = notif.enviar_whatsapp_reserva_admin(reserva)
    
    return resultados 