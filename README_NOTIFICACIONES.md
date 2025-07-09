# 📧📱 Sistema de Notificaciones - Restaurante Patagonia

## 🎯 Funcionalidades Implementadas

### ✅ **Notificaciones Automáticas por Reserva:**

1. **📧 Email al Cliente:**
   - Confirmación de reserva con detalles
   - Diseño profesional con HTML
   - Información de ubicación y consejos

2. **📱 WhatsApp al Cliente:**
   - Mensaje de confirmación
   - Detalles de la reserva
   - Consejos para la visita

3. **📧 Email al Administrador:**
   - Notificación de nueva reserva
   - Información completa del cliente
   - Enlace directo al panel de administración

4. **📱 WhatsApp al Administrador:**
   - Alerta inmediata de nueva reserva
   - Resumen de información clave
   - Recordatorio de acción requerida

## ⚙️ Configuración Requerida

### **1. Configuración de Email (Gmail)**

#### **Paso 1: Habilitar Autenticación de 2 Factores**
1. Ve a tu cuenta de Google
2. Seguridad → Verificación en 2 pasos → Activar

#### **Paso 2: Generar Contraseña de Aplicación**
1. Seguridad → Contraseñas de aplicación
2. Selecciona "Correo" y "Windows"
3. Copia la contraseña generada (16 caracteres)

#### **Paso 3: Configurar Variables de Entorno**
```bash
# En config.env
EMAIL_USER=tu-email@gmail.com
EMAIL_PASSWORD=tu-contraseña-de-aplicación
```

### **2. Configuración de WhatsApp (Twilio)**

#### **Paso 1: Crear Cuenta en Twilio**
1. Ve a [twilio.com](https://twilio.com)
2. Crea una cuenta gratuita
3. Obtén tu Account SID y Auth Token

#### **Paso 2: Configurar WhatsApp Sandbox**
1. En Twilio Console → Messaging → Try it out
2. Sigue las instrucciones para conectar WhatsApp
3. Anota el número de WhatsApp proporcionado

#### **Paso 3: Configurar Variables de Entorno**
```bash
# En config.env
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_FROM_NUMBER=whatsapp:+14155238886
```

### **3. Configuración del Administrador**

```bash
# En config.env
ADMIN_EMAIL=admin@patagonia-arica.cl
ADMIN_PHONE=+56912345678
```

## 🚀 Instalación y Uso

### **1. Instalar Dependencias**
```bash
pip install Flask-Mail==0.9.1 twilio==8.10.0 python-dotenv==1.0.0
```

### **2. Configurar Variables de Entorno**
1. Copia `config.env` a `.env`
2. Actualiza con tus credenciales reales
3. Nunca subas `.env` a Git

### **3. Probar el Sistema**
1. Ejecuta la aplicación: `python app.py`
2. Haz una reserva de prueba
3. Verifica que lleguen las notificaciones

## 📋 Flujo de Notificaciones

### **Cuando se hace una reserva:**

1. **Cliente hace reserva** → Sistema procesa
2. **Email al cliente** → Confirmación inmediata
3. **WhatsApp al cliente** → Notificación móvil
4. **Email al admin** → Alerta de nueva reserva
5. **WhatsApp al admin** → Notificación urgente

### **Templates de Mensajes:**

#### **Email Cliente:**
- Diseño profesional con logo
- Detalles completos de la reserva
- Información de ubicación
- Consejos para la visita
- Enlaces útiles

#### **WhatsApp Cliente:**
- Mensaje conciso y claro
- Emojis para mejor UX
- Información esencial
- Recordatorios importantes

#### **Email Admin:**
- Diseño de alerta
- Información completa del cliente
- Estado de la reserva
- Enlace directo al panel

#### **WhatsApp Admin:**
- Mensaje de alerta urgente
- Resumen de información clave
- Recordatorio de acción

## 🔧 Personalización

### **Modificar Templates:**
- Edita `notificaciones.py`
- Cambia el contenido HTML de los emails
- Modifica los mensajes de WhatsApp

### **Agregar Nuevas Notificaciones:**
- Crear nuevas funciones en `Notificaciones`
- Integrar en el flujo de la aplicación
- Configurar triggers automáticos

## 🛡️ Seguridad

### **Buenas Prácticas:**
- ✅ Usar contraseñas de aplicación (no contraseñas normales)
- ✅ Variables de entorno en `.env`
- ✅ Nunca subir credenciales a Git
- ✅ Validar números de teléfono
- ✅ Manejar errores de envío

### **Limitaciones:**
- ⚠️ WhatsApp Sandbox solo funciona con números verificados
- ⚠️ Gmail tiene límites de envío diario
- ⚠️ Twilio tiene límites en cuenta gratuita

## 📊 Monitoreo

### **Logs de Actividad:**
- Los envíos exitosos se registran en consola
- Los errores se capturan y muestran
- Recomendado implementar logging a archivo

### **Métricas Sugeridas:**
- Tasa de envío exitoso
- Tiempo de entrega
- Tasa de apertura de emails
- Respuestas a WhatsApp

## 🆘 Solución de Problemas

### **Email no se envía:**
1. Verificar credenciales de Gmail
2. Confirmar contraseña de aplicación
3. Revisar configuración SMTP

### **WhatsApp no funciona:**
1. Verificar credenciales de Twilio
2. Confirmar número en sandbox
3. Revisar formato del número de teléfono

### **Errores comunes:**
- `SMTPAuthenticationError`: Credenciales incorrectas
- `TwilioRestException`: Configuración de Twilio incorrecta
- `ValueError`: Formato de teléfono inválido

## 🎯 Próximos Pasos

### **Mejoras Sugeridas:**
1. **Plantillas personalizables** desde el panel admin
2. **Notificaciones de recordatorio** 24h antes
3. **Notificaciones de cancelación**
4. **Integración con SMS** como respaldo
5. **Dashboard de notificaciones** para el admin

### **Integración Avanzada:**
1. **Webhooks** para confirmaciones automáticas
2. **API de WhatsApp Business** (cuenta pagada)
3. **Sistema de plantillas** dinámicas
4. **Analytics** de engagement

---

**¿Necesitas ayuda con la configuración?** Revisa los pasos detallados arriba o contacta al equipo de desarrollo. 