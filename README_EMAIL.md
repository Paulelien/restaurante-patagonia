# 📧 Configuración de Email - Restaurante Patagonia

## 🔧 Configurar Email para Confirmaciones de Reservas

### **Paso 1: Configurar Gmail**

1. **Ve a tu cuenta de Gmail**
2. **Habilita la verificación en dos pasos** (obligatorio)
3. **Genera una contraseña de aplicación:**
   - Ve a "Gestionar tu cuenta de Google"
   - Seguridad → Verificación en dos pasos → Contraseñas de aplicación
   - Selecciona "Correo" y "Windows"
   - Copia la contraseña generada (16 caracteres)

### **Paso 2: Configurar el archivo config_email.py**

Edita el archivo `config_email.py` y cambia estas líneas:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'tu-email@gmail.com',  # ← Cambia por tu email
    'password': 'tu-password-app'   # ← Cambia por la contraseña de aplicación
}
```

### **Paso 3: Probar el sistema**

1. **Haz una reserva** con un email válido
2. **Accede al panel de administración** (`/admin/login`)
3. **Confirma la reserva** haciendo clic en "Confirmar"
4. **El cliente recibirá un email** de confirmación

### **Ejemplo de configuración:**

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'patagonia.arica@gmail.com',
    'password': 'abcd efgh ijkl mnop'  # Contraseña de aplicación
}
```

## 📱 Configuración de WhatsApp (Opcional)

Para habilitar notificaciones por WhatsApp:

1. **Crea una cuenta en Twilio**
2. **Obtén las credenciales** (Account SID, Auth Token)
3. **Configura el número de WhatsApp**
4. **Actualiza el archivo config_email.py**

## 🔒 Seguridad

- **NUNCA** subas las credenciales a GitHub
- **Usa contraseñas de aplicación** de Gmail
- **Mantén las credenciales seguras**

## 📧 Tipos de Email

### **1. Email de Nueva Reserva (Admin)**
- Se envía al administrador cuando llega una nueva reserva
- Incluye todos los detalles del cliente y la reserva

### **2. Email de Confirmación (Cliente)**
- Se envía al cliente cuando se confirma su reserva
- Incluye detalles de la reserva, ubicación y consejos

### **3. Email de Reserva Realizada (Cliente)**
- Se envía al cliente cuando hace una reserva
- Incluye confirmación de recepción

## 🚨 Solución de Problemas

### **Error: "Username and Password not accepted"**
- Verifica que la verificación en dos pasos esté habilitada
- Usa la contraseña de aplicación, no tu contraseña normal
- Asegúrate de que el email esté correcto

### **Error: "SMTP Authentication"**
- Verifica que el puerto sea 587
- Asegúrate de usar TLS/SSL

### **No se envían emails**
- Verifica la conexión a internet
- Revisa los logs del servidor
- Confirma que las credenciales sean correctas

## 📞 Soporte

Si tienes problemas con la configuración:
1. Revisa los logs del servidor
2. Verifica las credenciales
3. Prueba con un email de prueba primero

---

**¡Con esta configuración, tu restaurante enviará emails automáticos de confirmación!** 🎉 