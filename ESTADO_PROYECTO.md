# 📊 Estado del Proyecto — Financial OSINT Tool PRO

## 🌐 URLs Activas

| Componente | URL | Estado |
|------------|-----|--------|
| **Landing Page** | https://financial-osint-vercel.vercel.app | ✅ 200 OK |
| **Herramienta** | https://mvu68iewaaebks96q4e3pg.streamlit.app | ✅ Funcionando |
| **GitHub** | https://github.com/aonetworkcrm-art/-Financial-OSINT-PRO | ✅ Código subido |
| **Neon DB** | https://console.neon.tech | ✅ Compartida con Proxy Commander |

---

## 📂 Estructura del Proyecto

```
C:\financial-osint\
├── 📄 CÓDIGO PRINCIPAL
│   ├── app.py                    ← Herramienta Streamlit (800+ líneas)
│   ├── user_tracker.py           ← Tracking de usuarios
│   ├── database.py               ← Base de datos SQLite
│   ├── database_shared.py        ← Base de datos PostgreSQL
│   ├── reiniciar.bat             ← Reiniciar servidor
│   └── iniciar.bat               ← Iniciar herramienta
│
├── 📁 engines/                   ← Motores de búsqueda
│   ├── __init__.py
│   ├── extraction_engine.py      ← Motor principal de extracción
│   ├── ssn_lookup_engine.py      ← Motor de SSN lookup
│   ├── credit_score_engine.py    ← Motor de Credit Score
│   ├── address_engine.py         ← Motor de búsqueda por dirección
│   ├── institution_matcher.py    ← Detección de 15+ instituciones
│   ├── leakcheck_engine.py       ← Motor LeakCheck API
│   └── export_engine.py          ← Exportación CSV/JSON/TXT
│
├── 📁 core/
│   ├── __init__.py
│   └── models.py                 ← Modelos de datos
│
├── 🌐 LANDING PAGE (Vercel)
│   └── web/
│       ├── server.py
│       └── templates/            ← 13 templates HTML
│
├── 📖 DOCUMENTACIÓN
│   ├── ECOSISTEMA_FINAL.md       ← Documentación completa
│   ├── ESTADO_PROYECTO.md        ← Este documento
│   ├── README.md                 ← Manual de uso
│   ├── SETUP_COMPLETO.md         ← Setup de todas las APIs
│   ├── SSN_LOOKUP_ANALISIS.md    ← Análisis de SSN lookup
│   ├── LEAKCHECK_PRO_SETUP.md    ← Guía LeakCheck Pro
│   ├── DEPLOY_GUIA.md            ← Guía de deploy
│   └── RESUMEN_SESION.md         ← Resumen de sesiones
│
└── 📊 output/reports/            ← Reportes exportados
```

---

## 🔑 Credenciales

### Admin Panel
- **URL:** https://financial-osint-vercel.vercel.app/admin
- **Usuario:** `admin`
- **Contraseña:** `admin123`

---

## 🔧 Motores de Búsqueda

| Motor | Qué hace | APIs Necesarias |
|-------|----------|----------------|
| **Extraction Engine** | Búsqueda multi-fuente | LeakCheck, DeHashed |
| **SSN Lookup** | SSN → Identidad / Nombre → SSN | LeakCheck Pro |
| **Credit Score** | Estima score crediticio | Datos de brechas |
| **Address Engine** | Dirección → Emails, Phones, SSN | LeakCheck Pro |
| **Institution Matcher** | Detecta bancos/fintechs | Automático |
| **Export Engine** | CSV, JSON, TXT | Ninguna |

---

## 📊 Instituciones Detectadas (15+)

### Bancos
- US Bank, Chase, Wells Fargo, Bank of America, Citi
- Capital One, TD Bank, PNC Bank, Truist

### Fintechs
- Venmo, PayPal, Cash App, Zelle, Stripe

### Credit Unions
- Schools Federal Credit Union, Navy Federal, Alliant

---

## 💰 Paquetes de Precios

| Plan | Búsquedas | Precio | Período |
|------|-----------|--------|---------|
| Scout | 50 | $39 | Mensual |
| Hunter ⭐ | 200 | $99 | Mensual |
| Titan | 1,000 | $249 | Mensual |
| Scout 3M | 150 | $99 | 3 meses |
| Hunter 3M | 600 | $249 | 3 meses |
| Titan 3M | 3,000 | $599 | 3 meses |
| Scout Annual | 600 | $349 | Anual |
| Hunter Annual | 2,400 | $899 | Anual |
| Titan Annual | 12,000 | $2,199 | Anual |
| Lifetime 🏆 | Ilimitado | $3,999 | Para siempre |

---

## 🛠️ APIs Disponibles

| API | Precio | Qué Hace | Link |
|-----|--------|----------|------|
| **LeakCheck Pro** | $10/mes | SSN → Identidad | leakcheck.io |
| **DeHashed** | $20/mes | SSN → Datos completos | dehashed.com |
| **IntelligenceX** | $50/mes | Dark web search | intelx.io |
| **Snusbase** | $30/mes | Stealer logs | snusbase.com |

**Para empezar:** Solo necesitas LeakCheck Pro ($10/mes)

---

## 🔄 Flujo de Uso

### Búsqueda por Dirección
```
1. Pestaña "🔍 Búsqueda Universal"
2. Ingresa: "1206 Laurel Ln Richardson, TX 75080"
3. Tipo: "auto" o "address"
4. Click "⚡ BUSCAR"
5. Ve: emails, passwords, SSN, tarjetas, credit score
```

### SSN Lookup
```
1. Pestaña "🔐 SSN Lookup"
2. Sub-pestaña "SSN → Identidad"
3. Ingresa SSN: "123-45-6789"
4. Click "⚡ Buscar por SSN"
5. Ve: nombre, DOB, dirección, teléfono, email
```

### Credit Score
```
1. Pestaña "📊 Credit Score"
2. Ingresa email o nombre
3. Click "📊 Calcular Score"
4. Ve: score estimado (300-850) + grade
```

---

## 📊 Checklist de Completado

- [x] Herramienta Streamlit funcionando
- [x] Landing page desplegada en Vercel
- [x] 7 motores de búsqueda
- [x] SSN lookup bidireccional
- [x] Credit score automático
- [x] Detección de 15+ instituciones
- [x] Exportación CSV/JSON/TXT
- [x] Tracking de usuarios
- [x] Panel de admin
- [x] 10 planes de precios
- [x] Código en GitHub
- [x] Documentación completa

---

## ⏳ Próximos Pasos

- [ ] Configurar APIs (LeakCheck, DeHashed)
- [ ] Integrar pagos crypto
- [ ] Smart contracts
- [ ] Dominio personalizado
- [ ] Monitoreo de uptime
