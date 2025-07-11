# 🔧 Migración del Sistema de Administración - Patagonia Raw Bar

## 📋 Resumen de Cambios

Se ha migrado el sistema de administración de una **contraseña global** a un sistema basado en **usuarios administradores** individuales.

### ❌ Sistema Anterior (Inseguro)
- Contraseña global: `admin123`
- Cualquier persona con la contraseña podía acceder
- No había control de usuarios individuales
- La funcionalidad "Hacer Admin" no tenía sentido

### ✅ Sistema Nuevo (Seguro)
- Usuarios individuales con rol de administrador
- Cada administrador tiene su propia cuenta
- Control granular de acceso
- Funcionalidad "Hacer Admin" ahora es útil

## 🚀 Pasos para la Migración

### **Paso 1: Ejecutar el Script de Migración**

```bash
python migrate_admin.py
```

Este script te guiará para crear el primer administrador del sistema.

### **Paso 2: Configurar el Primer Administrador**

El script te pedirá:
- **Nombre completo** del administrador
- **Email** del administrador
- **Contraseña** segura
- **Confirmación** de contraseña

### **Paso 3: Acceder al Panel de Administración**

Una vez creado el administrador:
1. Ve a `/admin/login`
2. Usa el email y contraseña que configuraste
3. Accede al panel de administración

## 🔐 Funcionalidades del Nuevo Sistema

### **Gestión de Administradores**
- ✅ Crear nuevos administradores desde el panel
- ✅ Quitar privilegios de administrador
- ✅ Cada administrador tiene su propia contraseña
- ✅ Control individual de acceso

### **Seguridad Mejorada**
- ✅ No más contraseña global
- ✅ Autenticación por usuario individual
- ✅ Contraseñas hasheadas y seguras
- ✅ Control de sesiones por usuario

### **Panel de Administración**
- ✅ Acceso solo para usuarios con `is_admin = True`
- ✅ Gestión de usuarios y administradores
- ✅ Todas las funcionalidades anteriores mantenidas

## 📁 Archivos Modificados

### **app.py**
- Eliminada variable `ADMIN_PASSWORD`
- Actualizada función `admin_required()`
- Nueva función `setup_admin()`
- Actualizada función `admin_login()`
- Actualizada función `cambiar_password_admin()`

### **Templates**
- `admin_login.html` - Agregado campo email
- `setup_admin.html` - Nuevo template para configuración inicial
- `admin_cambiar_password.html` - Actualizado para usuarios individuales

### **Scripts**
- `migrate_admin.py` - Script de migración

## 🛠️ Comandos Útiles

### **Crear Administrador Manualmente**
```python
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Usuario(
        email='admin@patagonia.com',
        password_hash=generate_password_hash('tu-contraseña'),
        nombre='Tu Nombre',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
```

### **Convertir Usuario Existente en Admin**
```python
from app import app, db, Usuario

with app.app_context():
    usuario = Usuario.query.filter_by(email='usuario@ejemplo.com').first()
    if usuario:
        usuario.is_admin = True
        db.session.commit()
        print(f"Usuario {usuario.nombre} convertido en administrador")
```

## 🔒 Buenas Prácticas de Seguridad

### **Contraseñas**
- ✅ Usa contraseñas fuertes (mínimo 8 caracteres)
- ✅ Combina letras, números y símbolos
- ✅ No uses contraseñas comunes
- ✅ Cambia las contraseñas regularmente

### **Acceso**
- ✅ Limita el número de administradores
- ✅ Revisa regularmente los usuarios con privilegios
- ✅ Usa emails únicos para cada administrador
- ✅ Mantén un registro de cambios

### **Backup**
- ✅ Haz backup de la base de datos antes de migrar
- ✅ Guarda las credenciales de administrador en lugar seguro
- ✅ Documenta los cambios realizados

## 🆘 Solución de Problemas

### **Error: "No hay administradores"**
- Ejecuta `python migrate_admin.py`
- O ve a `/admin/setup` en el navegador

### **Error: "Acceso denegado"**
- Verifica que el usuario tenga `is_admin = True`
- Usa las credenciales correctas
- Asegúrate de estar logueado

### **Error: "Email ya registrado"**
- El script te dará opción de convertir el usuario existente
- O usa un email diferente

## 📞 Soporte

Si tienes problemas con la migración:
1. Revisa este README
2. Ejecuta el script de migración
3. Verifica la configuración de la base de datos
4. Contacta al equipo de desarrollo

---

**¡La migración está completa!** 🎉

El sistema ahora es más seguro y profesional. 