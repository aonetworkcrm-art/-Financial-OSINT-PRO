# 🚀 Guía de Deploy — URLs Reales en Render

## ¿Qué es Render?
Plataforma GRATUITA que te da una URL real (ej: `https://nexus-intel.onrender.com`) para tu app Flask.

---

## PASO 1: Crear cuenta en Render

1. Ve a **https://render.com**
2. Click "Get Started for Free"
3. Regístrate con tu email o GitHub

---

## PASO 2: Subir el código a GitHub

Necesitas una cuenta de GitHub (gratis):

1. Ve a **https://github.com** → crea cuenta
2. Click "+" → "New repository"
3. Nombre: `nexus-intel-landing`
4. Click "Create repository"
5. Sigue los comandos que te muestra:

```bash
cd C:\financial-osint
git init
git add .
git commit -m "NEXUS INTEL Landing Page"
git remote add origin https://github.com/TU_USUARIO/nexus-intel-landing.git
git push -u origin main
```

---

## PASO 3: Deploy en Render

1. En Render → Click **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configura así:
   - **Name:** `nexus-intel-landing`
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn web.server:app --bind 0.0.0.0:$PORT`
   - **Plan:** Free
4. Click **"Create Web Service"**
5. Espera 2-3 minutos
6. **¡Tu URL real aparece!** Algo como: `https://nexus-intel-landing.onrender.com`

---

## PASO 4: Configurar variables de entorno

En Render → tu servicio → **Environment**:

| Variable | Valor |
|----------|-------|
| `SECRET_KEY` | (genera una random) |
| `FLASK_ENV` | `production` |

---

## ¡LISTO! URL Real Funcionando

Tu landing page ahora está en: `https://nexus-intel-landing.onrender.com`

Los clientes pueden:
- Ver la página
- Registrarse
- Elegir plan
- Pagar
- Recibir su API Key

---

## Repetir para Proxy Commander

Mismos pasos pero con `C:\proxy-filter-tool`:
- Repo: `proxy-commander-landing`
- Start: `gunicorn web.server:app --bind 0.0.0.0:$PORT`

---

## Para actualizar después

```bash
git add .
git commit -m "Actualización"
git push
```

Render actualiza solo en 1-2 minutos.

---

## ⚠️ Notas Importantes

- **Free tier** de Render se duerme después de 15 min sin tráfico → se despierta solo (tarda ~30s)
- **Dominio propio** puedes conectar después (ej: nexusintel.com)
- **SSL/HTTPS** incluido gratis
- **Base de datos** SQLite funciona pero en producción sería mejor usar PostgreSQL de Render (gratis también)
