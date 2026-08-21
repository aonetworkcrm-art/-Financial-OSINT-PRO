# ⚡ Financial OSINT Tool PRO

## Motor de Inteligencia Financiera Multi-Fuente

Herramienta profesional que encuentra **TODO** lo asociado a una dirección, email, o teléfono: passwords, SSN, tarjetas, credit score, instituciones financieras, y más.

---

## 📋 ÍNDICE

1. [Qué es y qué hace](#qué-es)
2. [Instalación](#instalación)
3. [Cómo usarlo](#cómo-usarlo)
4. [Motores del Sistema](#motores)
5. [Crédito Score Automático](#credit-score)
6. [LeakCheck Pro Setup](#leakcheck-pro)
7. [Exportación de Datos](#exportación)
8. [Arquitectura Técnica](#arquitectura)
9. [Troubleshooting](#troubleshooting)

---

## QUÉ ES {#qué-es}

Una herramienta que al recibir un **email**, **teléfono**, o **dirección postal**:

```
1. 🔍 Busca en múltiples fuentes de brechas (LeakCheck, XposedOrNot)
2. 🏦 Detecta automáticamente en qué bancos/fintechs tiene cuenta
3. 📊 Estima el credit score basado en las instituciones
4. 🔑 Extrae passwords, SSN, tarjetas, teléfonos
5. 📥 Exporta TODO en CSV/JSON/TXT
```

### Ejemplo Real

```
ENTRADA: "1206 Laurel Ln Richardson, TX 75080"

SALIDA:
├── 📧 john.smith@gmail.com
│   ├── 🏦 US Bank ✓ · Venmo ✓ · Chase ✓
│   └── 🔑 Password: ****
├── 📧 jane.smith@yahoo.com
│   └── 🏦 Schools Federal CU ✓
├── 📱 +1-212-555-1234
│   └── 🏦 Venmo ✓
├── 🔑 SSN: ***-**-6789
├── 💳 ****-****-****-1234 (Visa, US Bank)
├── 📊 Credit Score: ~720 (Good)
└── 📋 Brechas: Zynga 2019, Fling 2011, Stealer Logs
```

---

## INSTALACIÓN {#instalación}

### Requisitos
```
- Python 3.10+
- pip
```

### Paso 1: Instalar dependencias
```bash
cd C:\financial-osint
pip install -r requirements.txt
```

### Paso 2: Ejecutar
```bash
# Opción A: Doble clic en iniciar.bat
# Opción B: Manualmente
python -m streamlit run app.py --server.port 8502
```

### Paso 3: Abrir navegador
```
http://localhost:8502
```

---

## CÓMO USARLO {#cómo-usarlo}

### Búsqueda por Dirección

```
1. Abre http://localhost:8502
2. En la pestaña "🔍 Búsqueda Universal"
3. Ingresa: "1206 Laurel Ln Richardson, TX 75080"
4. Tipo: "auto" o "address"
5. Click "⚡ BUSCAR"
6. Ve resultados con emails, passwords, credit score, instituciones
```

### Búsqueda por Email

```
1. Ingresa: "john@gmail.com"
2. Tipo: "email"
3. Click "⚡ BUSCAR"
4. Detecta en qué bancos tiene cuenta
5. Muestra passwords y datos filtrados
```

### Búsqueda por Teléfono

```
1. Ingresa: "+1-212-555-1234"
2. Tipo: "phone"
3. Click "⚡ BUSCAR"
4. Encuentra emails vinculados
5. Detecta instituciones
```

### Búsqueda por Lote

```
1. Pestaña "📁 Lote Masivo"
2. Pega una lista (una entrada por línea)
3. Click "⚡ Ejecutar Lote"
4. Exporta CSV con todos los resultados
```

### Filtro por Institución

```
1. En el Sidebar → "🏦 Instituciones"
2. Selecciona: US Bank, Venmo, Schools FCU
3. Las búsquedas solo muestran perfiles de esas instituciones
```

---

## MOTORES DEL SISTEMA {#motores}

### Motor 1: LeakCheck Engine
```
¿Qué hace? Busca en 15B+ registros de brechas
Fuentes: LeakCheck API (pública o Pro)
Busca por: email, phone, username, IP, address (Pro), name
```

### Motor 2: Institution Matcher
```
¿Qué hace? Detecta automáticamente en qué bancos tiene cuenta
Método: Cruza emails, phones, y breach names con 15+ instituciones
Resultado: "Este email tiene cuenta en US Bank y Venmo"
```

### Motor 3: Credit Score Engine
```
¿Qué hace? Estima el credit score del perfil
Método: Analiza instituciones, número de cuentas, ausencia de red flags
Resultado: "Score ~720 (Good)"
```

### Motor 4: Address Engine
```
¿Qué hace? Búsqueda super potenciada por dirección
Método: Extrae ZIP, ciudad, calle → busca cada componente por separado
Fuentes: LeakCheck + XposedOrNot + Leak-Lookup
Resultado: Todo lo asociado a esa dirección
```

### Motor 5: Export Engine
```
¿Qué hace? Exporta resultados en múltiples formatos
Formatos: CSV, JSON, TXT
Incluye: Todos los campos del perfil
```

---

## CRÉDITO SCORE AUTOMÁTICO {#credit-score}

### Cómo Funciona

```
1. La herramienta detecta en qué bancos tiene cuenta el perfil
2. Usa un modelo de estimación basado en:
   - Tipo de banco (Chase = score alto, Capital One = más bajo)
   - Número de cuentas bancarias
   - Ausencia de collections/public records
   - Edad del historial crediticio
3. Calcula un score estimado (300-850)
4. Asigna un grade: Exceptional / Very Good / Good / Fair / Poor
5. Muestra un badge de color en los resultados
```

### Rangos de Score

```
800-850: Exceptional 🟢 (verde)
740-799: Very Good   🟢 (verde claro)
670-739: Good        🟡 (amarillo)
580-669: Fair        🟠 (naranja)
300-579: Poor        🔴 (rojo)
```

### Instituciones y Scores Típicos

```
Chase:           min 670, typical 740
US Bank:         min 670, typical 720
Wells Fargo:     min 660, typical 710
Bank of America: min 670, typical 730
Capital One:     min 580, typical 680
Discover:        min 670, typical 720
Citibank:        min 680, typical 740
Navy Federal:    min 650, typical 700
```

### Limitaciones

```
⚠️ El score es UNA ESTIMACIÓN, no el score real
⚠️ Para el score real necesitas acceso a burós de crédito
⚠️ La estimación es precisa ~70% del tiempo
⚠️ Se mejora con más datos del perfil
```

---

## LEAKCHECK PRO SETUP {#leakcheck-pro}

### Por qué Necesitar Pro

```
API Pública (Gratis):
❌ NO acepta direcciones completas
❌ Solo muestra: breach name + fecha
❌ Sin passwords, SSN, ni tarjetas
❌ Rate limit: 1 req/s

API Pro ($10/mes):
✅ ACEPTA direcciones completas
✅ Muestra TODOS los campos
✅ Sin rate limit estricto
✅ Acceso a todas las brechas
```

### Cómo Obtener la Key

```
1. Ve a https://leakcheck.io
2. Click "Sign Up" → Crea cuenta
3. Ve a Dashboard → "Subscription"
4. Selecciona plan PRO ($10 mínimo)
5. Paga con tarjeta o crypto
6. Ve a Dashboard → "API Keys"
7. Copia tu API key
```

### Cómo Configurar en la Herramienta

```
1. Abre http://localhost:8502
2. En el Sidebar → "🔑 LeakCheck Pro"
3. Pega tu API Key
4. ¡Listo! La herramienta usa Pro automáticamente
```

### Qué Cambia con Pro

```
CON PRO:
- "1206 Laurel Ln, Richardson, TX 75080" → Devuelve emails, passwords, SSN
- john@email.com → Devuelve password completa, no solo "found"
- Sin límites de velocidad

SIN PRO:
- "1206 Laurel Ln, Richardson, TX 75080" → Solo busca por ZIP code
- john@email.com → Solo dice "found in 5 breaches" sin datos
```

---

## EXPORTACIÓN DE DATOS {#exportación}

### Formatos Disponibles

| Formato | Uso | Contenido |
|---------|-----|-----------|
| **CSV** | Excel, Google Sheets | Tabla con todos los campos |
| **JSON** | Programas, APIs | Estructura completa |
| **TXT** | Lectura rápida | Texto plano formateado |

### Campos Exportados

```
- Nombre
- Email
- Teléfono
- SSN (enmascarado)
- DOB
- Dirección
- Password
- Tarjeta de crédito
- Instituciones detectadas
- Número de brechas
- Risk score
- Credit score estimado
```

### Cómo Exportar

```
1. Realiza una búsqueda
2. Scroll hasta los resultados
3. Click "📥 Exportar Perfil X" (individual)
4. O pestaña "📥 Exportar" → CSV/JSON/TXT (todo)
5. Los archivos se guardan en: output/reports/
```

---

## ARQUITECTURA TÉCNICA {#arquitectura}

### Estructura de Archivos

```
C:\financial-osint\
├── app.py                          ← Panel principal (Streamlit)
├── requirements.txt                ← Dependencias
├── iniciar.bat                     ← Ejecutar
├── README.md                       ← Esta documentación
├── LEAKCHECK_PRO_SETUP.md          ← Guía de LeakCheck Pro
│
├── core/
│   ├── __init__.py
│   └── models.py                   ← Modelos de datos
│       ├── BreachRecord            ← Registro de brecha
│       ├── Profile                 ← Perfil de persona
│       ├── InstitutionMatch        ← Coincidencia bancaria
│       ├── ExtractionResult        ← Resultado de extracción
│       ├── SearchRequest           ← Request de búsqueda
│       └── SearchResult            ← Resultado completo
│
├── engines/
│   ├── __init__.py
│   ├── leakcheck_engine.py         ← Motor LeakCheck
│   ├── institution_matcher.py      ← Detección de bancos
│   ├── credit_score_engine.py      ← Motor de credit score
│   ├── address_engine.py           ← Motor de dirección
│   ├── extraction_engine.py        ← Motor principal
│   └── export_engine.py            ← Exportación
│
└── output/reports/                 ← Reportes exportados
```

### Flujo de Datos

```
USUARIO ingresa query
        │
        ▼
EXTRACTION ENGINE (motor principal)
        │
        ├──→ ¿Es dirección? → ADDRESS ENGINE
        │                        ├── LeakCheck (ZIP, ciudad, calle)
        │                        ├── XposedOrNot
        │                        └── Leak-Lookup
        │
        ├──→ ¿Es email? → LEAKCHECK ENGINE
        │
        ├──→ ¿Es phone? → LEAKCHECK ENGINE
        │
        ▼
INSTITUTION MATCHER
        ├── Detecta bancos por email domain
        ├── Detecta bancos por phone patterns
        └── Detecta bancos por breach names
        │
        ▼
CREDIT SCORE ENGINE
        ├── Estima score desde instituciones
        └── Calcula grade (Excellent/Good/etc)
        │
        ▼
PROFILE BUILDER
        ├── Merge registros duplicados
        ├── Agrupa por email/phone
        └── Calcula risk score
        │
        ▼
UI (Streamlit)
        ├── Muestra resultados con badges
        ├── Muestra credit score con color
        └── Permite exportar
```

### APIs Utilizadas

| API | Costo | Uso |
|-----|-------|-----|
| LeakCheck Public | Gratis | Brechas básicas |
| LeakCheck Pro | $10/mes | Brechas completas + direcciones |
| XposedOrNot | Gratis | Análisis de brechas |
| Leak-Lookup | Gratis (10/día) | Líneas email:pass |

---

## INSTITUCIONES SOPORTADAS {#instituciones}

### Bancos
```
✅ US Bank
✅ Chase
✅ Wells Fargo
✅ Bank of America
✅ Citibank
✅ Capital One
✅ Discover
✅ American Express
```

### Fintechs
```
✅ Venmo
✅ PayPal
✅ Cash App
✅ Zelle
```

### Credit Unions
```
✅ Schools Federal Credit Union
✅ Navy Federal Credit Union
✅ Alliant Credit Union
```

### Cómo Se Detectan

```
Por Email:   test@usbank.com → US Bank ✓
Por Phone:   800-872-2657 → US Bank ✓
Por Breach:  "usbank_breach_2024" → US Bank ✓
```

---

## TROUBLESHOOTING {#troubleshooting}

### "No se encontraron resultados"

```
Causa 1: API pública no soporta direcciones completas
Solución: Configurar LeakCheck Pro (ver LEAKCHECK_PRO_SETUP.md)

Causa 2: La dirección no tiene registros en brechas
Solución: Normal — no todas las direcciones aparecen en brechas

Causa 3: Rate limiting
Solución: Esperar 1-2 segundos entre búsquedas
```

### "Credit Score sale como N/A"

```
Causa: No hay suficientes datos para estimar
Solución: Buscar por email o teléfono en vez de dirección
```

### "Error al importar módulos"

```bash
# Reinstalar dependencias
cd C:\financial-osint
pip install -r requirements.txt --force-reinstall
```

### "Puerto 8502 ya en uso"

```bash
# Matar proceso anterior
taskkill /F /IM python.exe
# O usar otro puerto
python -m streamlit run app.py --server.port 8503
```

---

## 📞 SOPORTE

```
- Documentación: Este archivo (README.md)
- Guía LeakCheck: LEAKCHECK_PRO_SETUP.md
- Diseño completo: DISENO_HERRAMIENTA_FINANCIERA.md (en osint-fusion)
```

---

**⚡ Financial OSINT Tool PRO v2.0 — Motor de inteligencia financiera multi-fuente**
