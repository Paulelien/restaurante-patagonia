# 🔗 Conectar con GitHub - Instrucciones

## Paso 1: Crear repositorio en GitHub

1. Ve a [github.com](https://github.com)
2. Haz clic en "New" o "+" → "New repository"
3. Configuración:
   - **Repository name:** `restaurante-patagonia`
   - **Description:** `Sistema de reservas para Restaurante Patagonia - Arica, Chile`
   - **Visibility:** ✅ **Public** (IMPORTANTE para Render)
   - **NO** marques "Add a README file"
   - **NO** marques "Add .gitignore"
   - **NO** marques "Choose a license"

4. Haz clic en "Create repository"

## Paso 2: Conectar repositorio local

Después de crear el repositorio, GitHub te mostrará comandos. Ejecuta estos en tu terminal:

```bash
git remote add origin https://github.com/TU_USUARIO/restaurante-patagonia.git
git branch -M main
git push -u origin main
```

**Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub**

## Paso 3: Verificar conexión

```bash
git remote -v
```

Deberías ver algo como:
```
origin  https://github.com/TU_USUARIO/restaurante-patagonia.git (fetch)
origin  https://github.com/TU_USUARIO/restaurante-patagonia.git (push)
```

## ✅ Listo para Render

Una vez que hayas subido el código a GitHub, podrás continuar con el despliegue en Render. 