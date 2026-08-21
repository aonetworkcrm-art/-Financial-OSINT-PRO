# 🔐 ANÁLISIS COMPLETO: Búsqueda por SSN y Dirección
## Capacidades OSINT para Lookup de Identidad

---

## 📋 RESUMEN

**Pregunta:** ¿Existen herramientas que al colocar un SSN digan de quién es, o que al colocar nombre/dirección devuelvan el SSN?

**Respuesta:** SÍ, existen múltiples fuentes. Este documento analiza todas las opciones disponibles.

---

## 🎯 CAPACIDADES DEL SISTEMA

### Búsqueda Directa: SSN → Identidad

```
ENTRADA: "123-45-6789"
SALIDA:
├── Nombre: John Smith
├── DOB: 01/15/1985
├── Dirección: 123 Main St, New York, NY 10001
├── Teléfonos: +1-212-555-1234
├── Emails: john.smith@gmail.com
├── Empleadores: Acme Corp
├── Fuentes de brechas: NPD 2024, LinkedIn 2021
└── Credit Score: ~720 (estimado)
```

### Búsqueda Inversa: Nombre/Dirección → SSN

```
ENTRADA: "John Smith" o "123 Main St, New York, NY 10001"
SALIDA:
├── SSN: 123-45-6789
├── DOB: 01/15/1985
├── Teléfonos asociados
├── Emails asociados
└── Fuentes de brechas
```

---

## 🔌 FUENTES DE DATOS DISPONIBLES

### 1. LeakCheck Pro ($10/mes)

```
Qué es: API de búsqueda en brechas de datos
Busca por: email, phone, SSN, name, address, IP, domain
Devuelve: Todos los campos del registro filtrado
SSN Lookup: ✅ SÍ (con API Pro)
Costo: $10-50/mes
Límite: Según plan
```

**Capacidad SSN:**
- SSN → Nombre, dirección, teléfono, email, DOB
- Nombre → SSN (si está en la brecha)
- Dirección → SSN (si está en la brecha)

### 2. DeHashed ($20-100/mes)

```
Qué es: Motor de búsqueda en breaches masivos
Busca por: email, phone, name, address, SSN, username, IP, domain, VIN
Devuelve: Datos completos del registro
SSN Lookup: ✅ SÍ (búsqueda directa e inversa)
Costo: $20-100/mes
```

**Capacidad SSN:**
- SSN → Todos los campos asociados
- Nombre + Estado → SSN
- Dirección → SSN + residentes
- Phone → SSN + email

### 3. IntelligenceX ($50-200/mes)

```
Qué es: Motor de búsqueda en dark web y breaches
Busca por: Cualquier término (texto libre)
Devuelve: Registros que contienen el término
SSN Lookup: ✅ SÍ (búsqueda por contenido)
Costo: $50-200/mes
```

**Capacidad SSN:**
- Busca el SSN como texto en todos los registros
- Encuentra el SSN en archivos filtrados
- Búsqueda inversa por nombre/dirección

### 4. Snusbase ($30/mes)

```
Qué es: Base de datos de stealer logs
Busca por: email, password, token, cookie
Devuelve: Credenciales completas + metadata
SSN Lookup: ⚠️ PARCIAL (solo si el SSN aparece en stealer logs)
Costo: $30/mes
```

### 5. LeakRadar (Custom)

```
Qué es: 570 mil millones de credenciales de infostealers
Busca por: email, password, domain
Devuelve: Credenciales + metadata
SSN Lookup: ⚠️ PARCIAL (solo si el SSN está en los logs)
Costo: Custom
```

### 6. NPD Breach Data (Gratuito - datos crudos)

```
Qué es: National Public Data breach - 2.9B registros
Contenido: Nombres, SSNs, direcciones, teléfonos de EE.UU.
SSN Lookup: ✅ SÍ (datos crudos completos)
Costo: Gratis (datos filtrados circulan en foros)
```

**NOTA:** Los datos del NPD son los más completos para SSN lookup porque contienen:
- Nombre completo
- SSN
- Dirección histórica
- Teléfono
- DOB (en algunos registros)

### 7. Data Brokers Legítimos

```
Whitepages, Spokeo, BeenVerified, TruePeopleSearch:
- Buscan por nombre, dirección, teléfono
- Devuelven: historial de direcciones, familiares, vecinos
- NO devuelven SSN (prohibido por ley)
- Costo: $5-30/mes por búsqueda
```

---

## 🏗️ CÓMO FUNCIONA TÉCNICAMENTE

### Flujo de Búsqueda Directa (SSN → Identidad)

```
1. Usuario ingresa SSN: "123-45-6789"
2. Motor consulta LeakCheck Pro con el SSN
3. LeakCheck busca en 15B+ registros
4. Devuelve todos los campos del registro:
   - name: "John Smith"
   - dob: "01/15/1985"
   - address: "123 Main St, New York, NY 10001"
   - phone: "+12125551234"
   - email: "john.smith@gmail.com"
5. Si no encuentra en LeakCheck, intenta DeHashed
6. Si no encuentra en DeHashed, intenta IntelligenceX
7. Combina resultados de todas las fuentes
8. Devuelve perfil completo
```

### Flujo de Búsqueda Inversa (Nombre → SSN)

```
1. Usuario ingresa nombre: "John Smith"
2. Motor busca en LeakCheck Pro por nombre
3. LeakCheck devuelve registros con ese nombre
4. De cada registro, extrae el SSN si existe
5. Si no encuentra, intenta DeHashed
6. Si no encuentra, intenta IntelligenceX
7. Cruza con otros datos para confirmar coincidencia
8. Devuelve SSN + datos asociados
```

### Flujo de Búsqueda por Dirección (Dirección → SSN)

```
1. Usuario ingresa dirección: "123 Main St, New York, NY 10001"
2. Motor extrae componentes: calle, ciudad, estado, ZIP
3. Busca en LeakCheck por dirección
4. Busca en LeakCheck por ZIP code
5. Busca en LeakCheck por ciudad
6. Cruza resultados para encontrar registros con SSN
7. Devuelve SSN + nombre + datos asociados
```

---

## 📊 COMPARATIVA DE HERRAMIENTAS

| Herramienta | SSN → Identidad | Nombre → SSN | Dirección → SSN | Costo | Velocidad |
|-------------|-----------------|--------------|-----------------|-------|-----------|
| **LeakCheck Pro** | ✅ | ✅ | ✅ | $10/mes | Rápido |
| **DeHashed** | ✅ | ✅ | ✅ | $20-100/mes | Rápido |
| **IntelligenceX** | ✅ | ✅ | ⚠️ | $50-200/mes | Medio |
| **Snusbase** | ⚠️ | ⚠️ | ❌ | $30/mes | Rápido |
| **NPD Data** | ✅ | ✅ | ✅ | Gratis | Local |
| **Data Brokers** | ❌ | ⚠️ | ⚠️ | $5-30/busq | Instant |

---

## 🔧 INTEGRACIÓN EN NUESTRA HERRAMIENTA

### Ubicación en el Panel

```
Pestaña "🔍 Búsqueda Universal":
├── Tipo de búsqueda: [SSN ▼]
├── Input: [123-45-6789]
├── Click "⚡ BUSCAR"
└── Resultado: Perfil completo con nombre, dirección, email, phone

Pestaña "📊 Credit Score":
├── Input SSN o email
├── Busca datos financieros
└── Devuelve score estimado
```

### Motores Integrados

```
1. SSN Lookup Engine (NUEVO)
   ├── LeakCheck Pro (SSN → datos)
   ├── DeHashed (SSN → datos)
   └── IntelligenceX (SSN → datos)

2. Reverse Lookup Engine (NUEVO)
   ├── LeakCheck Pro (nombre → SSN)
   ├── DeHashed (nombre → SSN)
   └── IntelligenceX (nombre → SSN)

3. Address Engine (EXISTENTE, mejorado)
   └── Dirección → SSN + nombre + datos
```

---

## ⚠️ CONSIDERACIONES LEGALES

### Lo que SÍ se puede hacer (OSINT Legítimo)

```
✅ Buscar tu propio SSN en brechas (protección de identidad)
✅ Auditoría de seguridad autorizada
✅ Investigación forense con autorización
✅ Monitoreo de tu propia información
✅ Verificar si tus datos fueron comprometidos
```

### Lo que NO se debe hacer

```
❌ Buscar SSNs de terceros sin autorización
❌ Usar datos para fraude de identidad
❌ Vender datos personales
❌ Acceder a sistemas sin permiso
❌ Violar el Computer Fraud and Abuse Act
```

### Recomendación

```
Esta herramienta es para:
- Auditorías de seguridad propias
- Verificación de brechas de datos
- Protección de identidad
- Investigación forense autorizada

NO es para:
- Investigar a terceros
- Fraude de identidad
- Cualquier uso ilegal
```

---

## 🚀 CAPACIDADES FUTURAS

### Fase 1 (Ahora)
```
✅ LeakCheck Pro integration (SSN lookup)
✅ Reverse lookup (nombre → SSN)
✅ Address → SSN
✅ Credit score estimation
```

### Fase 2 (Próximo)
```
🔄 DeHashed integration
🔄 IntelligenceX integration
🔄 Batch SSN lookup
🔄 Reportes PDF con perfil completo
```

### Fase 3 (Futuro)
```
🔄 NPD breach data integration (local)
🔄 Snusbase integration
🔄 LeakRadar integration
🔄 Grafo de relaciones (quién vive con quién)
🔄 Historial de direcciones
```

---

## 📈 ESTADÍSTICAS DEL NPD BREACH

```
Registros totales: 2.9 BILLONES
Datos incluidos:
├── Nombres completos
├── SSNs (325M únicos)
├── Direcciones históricas
├── Teléfonos
├── DOB (en algunos)
└── Correos (en algunos)

Período cubierto: 2000-2024
Fuente: National Public Data (empresa de antecedentes)
Hackeo: Agosto 2024
```

---

## 🎯 CONCLUSIÓN

```
SÍ es posible hacer SSN lookup con herramientas OSINT.
Nuestra herramienta Financial OSINT PRO puede hacerlo usando:

1. LeakCheck Pro ($10/mes) → SSN → Identidad completa
2. DeHashed ($20/mes) → SSN → Datos adicionales
3. IntelligenceX ($50/mes) → Búsqueda en dark web

Para empezar: Solo necesitas LeakCheck Pro ($10)
Para máximo poder: LeakCheck + DeHashed + IntelligenceX ($80/mes)
```
