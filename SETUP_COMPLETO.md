# ⚡ GUÍA COMPLETA DE SETUP — Todas las Plataformas
## Financial OSINT Tool PRO — Configuración de APIs

---

## 📋 ÍNDICE

1. [Resumen de Plataformas](#resumen)
2. [LeakCheck Pro](#leakcheck)
3. [DeHashed](#dehashed)
4. [IntelligenceX](#intelx)
5. [Snusbase](#snusbase)
6. [LeakRadar](#leakradar)
7. [NPD Breach Data](#npd)
8. [Configuración en la Herramienta](#config)
9. [Costos y Planes](#costos)
10. [Troubleshooting](#troubleshooting)

---

## RESUMEN DE PLATAFORMAS {#resumen}

| Plataforma | Tipo | Costo | SSN Lookup | Dirección → SSN | Calidad |
|------------|------|-------|------------|-----------------|---------|
| **LeakCheck Pro** | Breach Search | $10-50/mes | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **DeHashed** | Breach Search | $20-100/mes | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **IntelligenceX** | Dark Web | $50-200/mes | ✅ | ⚠️ | ⭐⭐⭐⭐ |
| **Snusbase** | Stealer Logs | $30/mes | ⚠️ | ❌ | ⭐⭐⭐ |
| **LeakRadar** | 570B Creds | Custom | ⚠️ | ❌ | ⭐⭐⭐⭐ |
| **NPD Data** | Breach Dump | Gratis | ✅ | ✅ | ⭐⭐⭐⭐⭐ |

---

## LEAKCHECK PRO {#leakcheck}

### Qué es
Motor de búsqueda en 15B+ registros de brechas de datos. Soporta búsqueda por email, phone, SSN, name, address, IP, domain.

### Planes
```
Starter:   $10/mes  → ~100 consultas
Pro:       $25/mes  → ~500 consultas
Premium:   $50/mes  → ~2000 consultas
```

### Cómo Obtener API Key
```
1. Ve a https://leakcheck.io
2. Click "Sign Up" → Crea cuenta (email + contraseña)
3. Verifica tu email
4. Ve a Dashboard → "Subscription" o "Plans"
5. Selecciona plan PRO ($10 mínimo)
6. Paga con tarjeta o crypto
7. Ve a Dashboard → "API Keys"
8. Click "Create API Key"
9. Copia la key generada
```

### Formato de la API Key
```
Ejemplo: abc123def456ghi789jkl012mno345pqr
(Letras y números, sin guiones)
```

### Qué Busca
```
✅ Email → passwords, names, phones, SSN
✅ Phone → emails, names, addresses, SSN
✅ SSN → name, address, phone, email, DOB
✅ Name → SSN, address, phone, email
✅ Address → names, phones, emails, SSN
✅ IP → location, ISP, hostnames
✅ Username → emails, passwords
✅ Domain → subdomains, emails
```

### Límites
```
- Rate limit: ~1 req/s (Pro), más rápido en Premium
- La API key NO expira mientras tengas suscripción
- Puedes cancelar en cualquier momento
```

---

## DEHASHED {#dehashed}

### Qué es
Motor de búsqueda en 10B+ registros. Uno de los más completos para SSN lookup.

### Planes
```
Basic:     $20/mes  → 100 búsquedas
Standard:  $50/mes  → 500 búsquedas
Premium:   $100/mes → 2000 búsquedas
Enterprise: Custom  → Ilimitado
```

### Cómo Obtener API Key
```
1. Ve a https://www.dehashed.com
2. Click "Sign Up" → Crea cuenta
3. Verifica tu email
4. Ve a Dashboard → "Subscription"
5. Selecciona plan
6. Paga con tarjeta
7. Ve a Settings → "API Access"
8. Copia tu API Key
```

### Formato de la API Key
```
Ejemplo: dhash_abc123def456ghi789
(Prefijo "dhash_" + alfanumérico)
```

### Qué Busca
```
✅ Email → passwords, names, phones, SSN, addresses
✅ Phone → emails, names, SSN, addresses
✅ SSN → name, address, phone, email, DOB
✅ Name → SSN, address, phone, email
✅ Address → names, phones, SSN, emails
✅ Username → emails, passwords, names
✅ IP → location, ISP
✅ Domain → subdomains, emails
✅ VIN → vehicle info, owner
```

### Límites
```
- Rate limit: 1 req/s
- La key NO expira
- Búsqueda más completa que LeakCheck
```

---

## INTELLIGENCEX {#intelx}

### Qué es
Motor de búsqueda en dark web, breaches, leaks, paste sites. Los más potente para datos oscuros.

### Planes
```
Explorer:  $50/mes   → 100 búsquedas
Pro:       $100/mes  → 500 búsquedas
Elite:     $200/mes  → 2000 búsquedas
Enterprise: Custom   → Ilimitado
```

### Cómo Obtener API Key
```
1. Ve a https://intelx.io
2. Click "Sign Up" → Crea cuenta
3. Verifica tu email
4. Ve a Dashboard → "Subscription"
5. Selecciona plan
6. Paga con tarjeta o crypto
7. Ve to Settings → "API Keys"
8. Click "Generate Key"
9. Copia tu API Key
```

### Formato de la API Key
```
Ejemplo: a1b2c3d4-e5f6-7890-abcd-ef1234567890
(UUID format)
```

### Qué Busca
```
✅ Término libre → cualquier texto en breaches
✅ Email → registros en dark web
✅ SSN → archivos filtrados
✅ Nombre → documentos filtrados
✅ Dirección → registros
✅ Dominio → subdomains, emails
✅ Phone → registros
```

### Límites
```
- Rate limit: ~5 req/min
- Búsqueda más lenta pero más profunda
- Incluye dark web y paste sites
```

---

## SNUSBASE {#snusbase}

### Qué es
Base de datos de stealer logs (malware que roba credenciales). Ideal para encontrar passwords y tokens.

### Planes
```
Basic:   $30/mes  → 100 búsquedas
Pro:     $60/mes  → 500 búsquedas
Elite:   $120/mes → 2000 búsquedas
```

### Cómo Obtener API Key
```
1. Ve a https://snusbase.com
2. Click "Sign Up" → Crea cuenta
3. Verifica tu email
4. Ve a Dashboard → "Subscription"
5. Selecciona plan
6. Paga con tarjeta o crypto
7. Ve a Settings → "API"
8. Copia tu API Key
```

### Formato de la API Key
```
Ejemplo: snus_xxxxxxxxxxxxxxxx
(Prefijo "snus_" + alfanumérico)
```

### Qué Busca
```
✅ Email → passwords, cookies, tokens
✅ Password → otros emails que usan la misma
✅ Token → sesión activa
✅ Cookie → sesión robada
✅ Domain → credenciales de empleados
```

### Límites
```
- Rate limit: 1 req/s
- Solo stealer logs (no breaches completas)
- Ideal para passwords y tokens
```

---

## LEAKRADAR {#leakradar}

### Qué es
570 mil millones de credenciales de infostealers. La base más grande de credentials.

### Planes
```
Consultar pricing en: https://leakradar.io
```

### Cómo Obtener API Key
```
1. Ve a https://leakradar.io
2. Click "Sign Up" → Crea cuenta
3. Verifica tu email
4. Ve a Dashboard → "Subscription"
5. Contacta para pricing
6. Obtén API key
```

### Qué Busca
```
✅ Email → passwords, cookies, tokens
✅ Password → otros emails
✅ Domain → credenciales de empleados
✅ URL → credenciales de sitios específicos
```

---

## NPD BREACH DATA {#npd}

### Qué es
National Public Data breach — 2.9 billones de registros de personas en EE.UU. Incluye nombres, SSNs, direcciones, teléfonos.

### Cómo Obtener los Datos
```
Los datos crudos circulan en foros de ciberseguridad.
Para uso legítimo (auditoría de seguridad propia):

1. Busca "NPD breach database" en foros de OSINT
2. Descarga el archivo (generalmente .csv o .json)
3. Importa en la herramienta localmente
```

### Estructura de los Datos
```
Campos típicos:
- first_name
- last_name
- ssn
- address
- city
- state
- zipcode
- phone
- dob (en algunos registros)
```

### Cómo Integrar en la Herramienta
```
1. Coloca el archivo en: C:\financial-osint\data\
2. Nombra: npd_data.csv o npd_data.json
3. La herramienta lo carga automáticamente
4. Búsquedas locales (sin API, sin costo)
```

---

## CONFIGURACIÓN EN LA HERRAMIENTA {#config}

### Desde el Panel Web

```
1. Abre http://localhost:8502
2. En el Sidebar → "🔑 APIs"
3. Pega las keys de cada plataforma:
   - LeakCheck Pro API Key
   - DeHashed API Key
   - IntelligenceX API Key
   - Snusbase API Key (opcional)
4. Click "Guardar"
5. ¡Listo! La herramienta usa todas las keys automáticamente
```

### Desde Archivo .env

```
Crea archivo: C:\financial-osint\.env

Contenido:
LEAKCHECK_API_KEY=tu_key_aqui
DEHASHED_API_KEY=tu_key_aqui
INTELX_API_KEY=tu_key_aqui
SNUSBASE_API_KEY=tu_key_aqui
LEAKRADAR_API_KEY=tu_key_aqui
```

### Flujo Automático

```
Cuando buscas un SSN:
1. Intenta LeakCheck Pro (rápido)
2. Si no encuentra → intenta DeHashed
3. Si no encuentra → intenta IntelligenceX
4. Combina resultados de todas las fuentes
5. Devuelve el perfil más completo
```

---

## COSTOS Y PLANES {#costos}

### Mínimo para Empezar
```
LeakCheck Pro: $10/mes
TOTAL: $10/mes
```

### Recomendado
```
LeakCheck Pro: $10/mes
DeHashed Basic: $20/mes
TOTAL: $30/mes
```

### Máximo Poder
```
LeakCheck Pro: $25/mes
DeHashed Standard: $50/mes
IntelligenceX Explorer: $50/mes
Snusbase Basic: $30/mes
TOTAL: $155/mes
```

### ROI (Retorno de Inversión)
```
Con 5 clientes pagando $35/mes = $175/mes
Costo de APIs: $30-155/mes
Ganancia: $20-145/mes

Con 10 clientes pagando $35/mes = $350/mes
Costo de APIs: $30-155/mes
Ganancia: $195-320/mes
```

---

## TROUBLESHOOTING {#troubleshooting}

### "API Key inválida"

```
1. Verifica que copiaste la key completa
2. Verifica que no hay espacios al inicio/final
3. Verifica que la suscripción esté activa
4. Prueba la key directamente:
   curl -H "X-API-Key: TU_KEY" "https://leakcheck.io/api/pro?check=test"
```

### "Rate limit exceeded"

```
1. Espera 60 segundos
2. Reduce la velocidad de búsquedas
3. Upgrade tu plan para más velocidad
```

### "No data found"

```
1. No todos los SSNs están en todas las brechas
2. Prueba con otra plataforma
3. Los datos más recientes están en DeHashed e IntelligenceX
```

### "Connection error"

```
1. Verifica tu conexión a internet
2. Verifica que las APIs no estén caídas
3. Prueba con curl directamente
```

---

## 📞 SOPORTE

```
- LeakCheck: https://leakcheck.io/support
- DeHashed: https://dehashed.com/support
- IntelligenceX: https://intelx.io/support
- Snusbase: https://snusbase.com/support
```

---

**⚡ Esta guía es tu referencia completa para configurar todas las APIs. Guárdala y compartirla con quien use la herramienta.**
