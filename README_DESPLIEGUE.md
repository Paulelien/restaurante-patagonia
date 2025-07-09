# 🚀 Guía de Despliegue - Restaurante Patagonia

## 📋 Preparación para Producción

### 1. Configuración de Variables de Entorno

Antes de desplegar, configura estas variables de entorno:

```bash
# Configuración básica
SECRET_KEY=tu_clave_secreta_muy_segura
BASE_URL=https://tu-dominio.com

# Base de datos (para PostgreSQL en producción)
DATABASE_URL=postgresql://usuario:password@host:puerto/database

# Email (Gmail)
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicación

# WhatsApp (Twilio) - Opcional
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_FROM_NUMBER=whatsapp:+14155238886
```

## 🌐 Opciones de Despliegue

### **Opción 1: Render.com (Recomendado - Gratis)**

1. **Crear cuenta en [Render.com](https://render.com)**
2. **Conectar tu repositorio de GitHub**
3. **Crear nuevo Web Service**
4. **Configurar:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Environment Variables:** Agregar todas las variables de entorno

### **Opción 2: Railway.app (Gratis y Rápido)**

1. **Crear cuenta en [Railway.app](https://railway.app)**
2. **Conectar repositorio de GitHub**
3. **Railway detectará automáticamente que es una app Python**
4. **Configurar variables de entorno en la pestaña Variables**

### **Opción 3: Heroku (Pago pero Confiable)**

1. **Instalar Heroku CLI**
2. **Crear cuenta en [Heroku.com](https://heroku.com)**
3. **Ejecutar comandos:**
```bash
heroku create tu-app-patagonia
heroku config:set SECRET_KEY=tu-clave-secreta
heroku config:set DATABASE_URL=postgresql://...
heroku config:set MAIL_USERNAME=tu-email@gmail.com
heroku config:set MAIL_PASSWORD=tu-contraseña
git push heroku main
```

### **Opción 4: DigitalOcean App Platform**

1. **Crear cuenta en [DigitalOcean.com](https://digitalocean.com)**
2. **Ir a App Platform**
3. **Conectar repositorio de GitHub**
4. **Configurar como aplicación Python**
5. **Agregar variables de entorno**

## 🔧 Configuración de Base de Datos

### Para Producción (PostgreSQL):

## 💻 Desarrollo en Windows

### Nota importante sobre Gunicorn:
Gunicorn no funciona en Windows porque depende del módulo `fcntl` que solo está disponible en sistemas Unix/Linux. Para desarrollo en Windows, usa:

```bash
# Opción 1: Servidor universal (recomendado)
python start_server.py

# Opción 2: Waitress (servidor WSGI para Windows)
python test_waitress.py

# Opción 3: Servidor de desarrollo Flask
python app.py
```

### Para Producción (PostgreSQL):

1. **Crear base de datos PostgreSQL**
2. **Instalar psycopg2:**
```bash
pip install psycopg2-binary
```

3. **Agregar a requirements.txt:**
```
psycopg2-binary==2.9.7
```

## 📧 Configuración de Email

### Gmail:
1. **Activar verificación en 2 pasos**
2. **Generar contraseña de aplicación**
3. **Usar esa contraseña en MAIL_PASSWORD**

### Otros proveedores:
- **SendGrid:** Usar SMTP de SendGrid
- **Mailgun:** Usar SMTP de Mailgun
- **AWS SES:** Usar SMTP de Amazon SES

## 📱 Configuración de WhatsApp (Opcional)

### Twilio:
1. **Crear cuenta en [Twilio.com](https://twilio.com)**
2. **Obtener Account SID y Auth Token**
3. **Configurar número de WhatsApp**
4. **Agregar variables de entorno**

## 🔒 Seguridad en Producción

### Cambios necesarios:
1. **Cambiar SECRET_KEY por una clave segura**
2. **Usar HTTPS en producción**
3. **Configurar dominio personalizado**
4. **Habilitar logs de seguridad**

## 📊 Monitoreo

### Recomendado:
- **Uptime Robot:** Para monitoreo de disponibilidad
- **Sentry:** Para monitoreo de errores
- **Google Analytics:** Para estadísticas de visitantes

## 🚀 Comandos Útiles

### Verificar aplicación local:
```bash
python app.py
```

### Probar con servidor universal (recomendado):
```bash
python start_server.py
```

### Probar con Gunicorn (Linux/Mac):
```bash
gunicorn wsgi:app
```

### Probar con Waitress (Windows):
```bash
python test_waitress.py
```

### Migrar base de datos:
```bash
python migrate_db.py
```

## 📞 Soporte

Si tienes problemas con el despliegue:
1. **Revisar logs del servidor**
2. **Verificar variables de entorno**
3. **Comprobar conectividad de base de datos**
4. **Revisar configuración de email**

---

**¡Tu restaurante estará online en minutos! 🎉** 