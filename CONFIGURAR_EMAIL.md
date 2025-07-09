# 🔧 Configuración de Email para Patagonia Raw Bar

## 📧 Paso a Paso para Configurar Gmail

### 1. Habilitar Autenticación de 2 Factores en Gmail
1. Ve a tu cuenta de Google
2. Seguridad → Verificación en 2 pasos → Activar
3. Sigue los pasos para configurar tu teléfono

### 2. Generar Contraseña de Aplicación
1. Ve a tu cuenta de Google
2. Seguridad → Contraseñas de aplicación
3. Selecciona "Otra" y ponle un nombre como "Patagonia Restaurant"
4. **Copia la contraseña de 16 caracteres** que te genera

### 3. Configurar el Archivo
Edita el archivo `config_email.py` y cambia estas líneas:

```python
'email': 'TU-EMAIL-REAL@gmail.com',  # ⚠️ CAMBIA ESTO por tu email de Gmail real
'password': 'TU-PASSWORD-APP'        # ⚠️ CAMBIA ESTO por tu contraseña de aplicación
```

**Ejemplo:**
```python
'email': 'patagonia.arica@gmail.com',
'password': 'abcd efgh ijkl mnop'  # La contraseña de 16 caracteres
```

### 4. Probar la Configuración
1. Reinicia el servidor Flask
2. Haz una reserva de prueba
3. Verifica que llegue el email

## 🔒 Seguridad
- ✅ Usa siempre contraseñas de aplicación
- ✅ No compartas las credenciales
- ✅ Usa un email dedicado para el restaurante
- ❌ Nunca uses tu contraseña personal de Gmail

## 📱 Email que verán los clientes
Los clientes recibirán emails desde: `TU-EMAIL-REAL@gmail.com`

## 🆘 Si no funciona
1. Verifica que la autenticación de 2 factores esté activada
2. Asegúrate de usar la contraseña de aplicación (no la normal)
3. Revisa que el email esté bien escrito
4. Verifica que no haya espacios extra en la contraseña 