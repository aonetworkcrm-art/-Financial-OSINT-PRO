# 🔑 Guía de Configuración — LeakCheck Pro API

## Cómo Obtener tu API Key ($10 mínimo)

### Paso 1: Crear Cuenta
```
1. Ve a https://leakcheck.io
2. Click "Sign Up" o "Register"
3. Crea tu cuenta (email + contraseña)
4. Verifica tu email
```

### Paso 2: Suscribirse a Pro
```
1. Ve a Dashboard → "Subscription" o "Plans"
2. Selecciona el plan PRO ($10 mínimo)
3. Paga con tarjeta o crypto
4. Recibes tu API key inmediatamente
```

### Paso 3: Copiar API Key
```
1. Ve a Dashboard → "API Keys"
2. Copia tu API key
3. PégalA en la herramienta: Sidebar → "LeakCheck Pro" → API Key
```

### Paso 4: ¡Listo!
```
La herramienta automáticamente usa la API Pro:
✅ Búsqueda por dirección completa (no solo ZIP)
✅ Datos completos (email, password, SSN, tarjetas)
✅ Sin límite de rate (más rápido)
✅ Acceso a todas las brechas
```

---

## Qué Cambia con API Pro

### API Pública (Gratis)
```
❌ NO acepta direcciones completas
❌ Solo muestra: breach name + fecha
❌ Sin passwords, SSN, ni tarjetas
❌ Rate limit: 1 req/s
```

### API Pro ($10/mes)
```
✅ ACEPTA direcciones completas: "1206 Laurel Ln, Richardson, TX 75080"
✅ Muestra TODOS los campos: email, password, SSN, tarjeta, phone, DOB
✅ Sin rate limit estricto
✅ Acceso a todas las brechas
✅ Datos de personas (name, address, employer)
```

---

## Formatos de Búsqueda Soportados (Pro)

```
Email:      user@domain.com
Phone:      +12125551234 o 2125551234
Username:   john_doe
IP:         192.168.1.1
Name:       John Smith
Address:    1206 Laurel Ln, Richardson, TX 75080  ← ¡NUEVO en Pro!
Domain:     example.com
Password:   mypassword123
```

---

## Límites del Plan Pro

```
Plan $10:
- ~100 consultas/mes
- Todas las funciones

Plan $25:
- ~500 consultas/mes
- Prioridad en velocidad

Plan $50:
- ~2000 consultas/mes
- Soporte prioritario
```

---

## Configuración en la Herramienta

```
1. Abre http://localhost:8502
2. En el Sidebar → "🔑 LeakCheck Pro"
3. Pega tu API Key
4. ¡Listo! La herramienta usa Pro automáticamente
```

---

## Verificar que Funciona

```bash
# Test rápido desde consola
cd C:\financial-osint
python -c "
import requests
key = 'TU_API_KEY_AQUI'
resp = requests.get(
    'https://leakcheck.io/api/pro',
    params={'check': 'test@email.com'},
    headers={'X-API-Key': key}
)
print(resp.json())
"
```

---

## Notas Importantes

```
1. La API key NO expira (mientras tengas suscripción activa)
2. Puedes cancelar en cualquier momento
3. Los $10 iniciales te dan acceso inmediato
4. Para direcciones: usa el formato completo con ciudad y estado
5. La herramienta maneja el rate limiting automáticamente
```
