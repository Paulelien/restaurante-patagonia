# Configuración de Email para el Restaurante Patagonia
# IMPORTANTE: Cambia estas credenciales por las tuyas

import os

# Configuración de Gmail
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'ricardo.delannoy@gmail.com',  # ⚠️ CAMBIA ESTO por tu email de Gmail real
    'password': 'negn zkeg weze cgut'        # ⚠️ CAMBIA ESTO por tu contraseña de aplicación
}

# Email del administrador
ADMIN_EMAIL = 'admin@patagonia-arica.cl'

# Configuración de WhatsApp (opcional)
WHATSAPP_CONFIG = {
    'account_sid': '',  # Tu Account SID de Twilio
    'auth_token': '',   # Tu Auth Token de Twilio
    'from_number': 'whatsapp:+14155238886'  # Tu número de WhatsApp de Twilio
}

def get_email_config():
    """Obtiene la configuración de email desde variables de entorno o valores por defecto"""
    return {
        'smtp_server': os.getenv('EMAIL_SMTP_SERVER', EMAIL_CONFIG['smtp_server']),
        'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', EMAIL_CONFIG['smtp_port'])),
        'email': os.getenv('EMAIL_USER', EMAIL_CONFIG['email']),
        'password': os.getenv('EMAIL_PASSWORD', EMAIL_CONFIG['password'])
    }

def get_admin_email():
    """Obtiene el email del administrador"""
    return os.getenv('ADMIN_EMAIL', ADMIN_EMAIL)

def get_whatsapp_config():
    """Obtiene la configuración de WhatsApp"""
    return {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID', WHATSAPP_CONFIG['account_sid']),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN', WHATSAPP_CONFIG['auth_token']),
        'from_number': os.getenv('TWILIO_FROM_NUMBER', WHATSAPP_CONFIG['from_number'])
    } 