# 🚀 Guía Completa - Despliegue en Render.com

## 📋 Prerequisitos

✅ Código subido a GitHub (repositorio público)  
✅ Cuenta en Render.com  

## 🌐 Paso 1: Crear cuenta en Render

1. Ve a [render.com](https://render.com)
2. Haz clic en "Get Started for Free"
3. Regístrate con tu cuenta de GitHub (recomendado)

## 🔗 Paso 2: Conectar repositorio

1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu cuenta de GitHub si no lo has hecho
4. Busca y selecciona tu repositorio: `restaurante-patagonia`

## ⚙️ Paso 3: Configurar el servicio

### Configuración básica:
- **Name:** `restaurante-patagonia`
- **Environment:** `Python 3`
- **Region:** `Oregon (US West)` (más rápido para Chile)
- **Branch:** `main`
- **Root Directory:** (dejar vacío)

### Configuración de build:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:app`

### Plan:
- **Plan:** `Free` (para prototipo)

## 🔐 Paso 4: Configurar variables de entorno

En la sección "Environment Variables", agrega:

### Variables obligatorias:
```
SECRET_KEY = (Render lo genera automáticamente)
BASE_URL = https://tu-app.onrender.com
```

### Variables para email (opcional):
```
MAIL_USERNAME = tu-email@gmail.com
MAIL_PASSWORD = tu-contraseña-de-aplicación
```

### Variables para WhatsApp (opcional):
```
TWILIO_ACCOUNT_SID = tu-account-sid
TWILIO_AUTH_TOKEN = tu-auth-token
TWILIO_FROM_NUMBER = whatsapp:+14155238886
```

## 🚀 Paso 5: Desplegar

1. Haz clic en "Create Web Service"
2. Render comenzará a construir tu aplicación
3. El proceso toma 2-5 minutos
4. Verás logs en tiempo real

## ✅ Paso 6: Verificar despliegue

Una vez completado:
- Tu aplicación estará disponible en: `https://tu-app.onrender.com`
- El primer acceso puede tardar 30 segundos (Render "despierta" la app)

## 🔧 Paso 7: Configurar dominio personalizado (opcional)

1. Ve a la pestaña "Settings"
2. Sección "Custom Domains"
3. Agrega tu dominio: `www.turestaurante.com`
4. Configura DNS según las instrucciones de Render

## 📊 Paso 8: Monitoreo

### En Render:
- **Logs:** Ve a la pestaña "Logs" para ver errores
- **Metrics:** Ve a "Metrics" para estadísticas
- **Events:** Ve a "Events" para ver despliegues

### Herramientas recomendadas:
- **Uptime Robot:** Para monitoreo de disponibilidad
- **Google Analytics:** Para estadísticas de visitantes

## 🛠️ Solución de problemas comunes

### Error: "Build failed"
- Verifica que `requirements.txt` esté en la raíz
- Revisa los logs de build

### Error: "Application error"
- Verifica las variables de entorno
- Revisa los logs de la aplicación

### Error: "Module not found"
- Asegúrate de que todas las dependencias estén en `requirements.txt`

### La app tarda en cargar
- Normal en el plan gratuito
- Considera actualizar a plan pago para mejor rendimiento

## 📞 Soporte

- **Render Docs:** [docs.render.com](https://docs.render.com)
- **Render Support:** [render.com/support](https://render.com/support)
- **Comunidad:** [community.render.com](https://community.render.com)

---

## 🎉 ¡Tu restaurante estará online!

Una vez completado, tu aplicación tendrá:
- ✅ URL pública accesible desde cualquier lugar
- ✅ SSL automático (HTTPS)
- ✅ Despliegue automático al hacer cambios
- ✅ Logs y monitoreo
- ✅ Escalabilidad automática

**URL de tu aplicación:** `https://tu-app.onrender.com` 