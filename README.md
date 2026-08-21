# ⚡ Financial OSINT Tool PRO

**Motor de inteligencia financiera multi-fuente con SSN lookup, Credit Score y detección de instituciones.**

## 🌐 URLs

| Cosa | URL |
|------|-----|
| **Landing Page** | https://financial-osint-vercel.vercel.app |
| **Herramienta** | https://mvu68iewaaebks96q4e3pg.streamlit.app |
| **Admin Panel** | https://financial-osint-vercel.vercel.app/admin |

## 🔑 Login Admin

- **Usuario:** `admin`
- **Contraseña:** `admin123`

---

## 🚀 Qué es Financial OSINT

Financial OSINT es una herramienta que te permite:

1. **Buscar por dirección** → Emails, passwords, SSN, tarjetas asociadas
2. **SSN Lookup** → SSN → Identidad / Nombre → SSN
3. **Credit Score** → Estima el score crediticio de un perfil
4. **Detectar instituciones** → Bancos, fintechs, credit unions
5. **Exportar** → CSV, JSON, TXT con todos los datos

---

## 📋 Cómo Usar la Herramienta

### Búsqueda por Dirección
1. Abre https://mvu68iewaaebks96q4e3pg.streamlit.app
2. Pestaña **🔍 Búsqueda Universal**
3. Ingresa una dirección completa:
   ```
   1206 Laurel Ln Richardson, TX 75080
   ```
4. Tipo: `auto` o `address`
5. Click **⚡ BUSCAR**
6. Ve: emails, passwords, SSN, tarjetas, credit score, instituciones

### SSN Lookup
1. Pestaña **🔐 SSN Lookup**
2. Sub-pestaña **SSN → Identidad**
3. Ingresa un SSN: `123-45-6789`
4. Click **⚡ Buscar por SSN**
5. Ve: nombre, DOB, dirección, teléfono, email, brechas

### Reverse Lookup (Nombre → SSN)
1. Pestaña **🔐 SSN Lookup**
2. Sub-pestaña **Nombre/Dirección → SSN**
3. Ingresa: `John Smith` o una dirección
4. Click **⚡ Buscar SSN**
5. Ve: SSN asociado (si existe en brechas)

### Credit Score
1. Pestaña **📊 Credit Score**
2. Ingresa email o nombre
3. Click **📊 Calcular Score**
4. Ve: score estimado (300-850) + grade

---

## 🔧 APIs Requeridas

Para usar la herramienta al máximo, necesitas al menos una API:

### LeakCheck Pro ($10/mes) — MÍNIMO RECOMENDADO
1. Ve a https://leakcheck.io
2. Crea cuenta → Suscríbete a Pro ($10)
3. Copia tu API Key
4. En la herramienta → Sidebar → Pega la key

**Qué puedes hacer con LeakCheck:**
- SSN → Nombre, DOB, Dirección, Teléfono, Email
- Email → Passwords, instituciones
- Dirección → SSN + residentes

### DeHashed ($20/mes) — EL MÁS COMPLETO
1. Ve a https://www.dehashed.com
2. Crea cuenta → Suscríbete a Basic ($20)
3. Copia tu API Key (formato: `dhash_xxx`)

**Qué puedes hacer con DeHashed:**
- SSN → Todos los campos asociados
- Nombre + Estado → SSN
- Phone → SSN + email
- VIN → vehicle info + owner

### IntelligenceX ($50/mes) — DARK WEB
1. Ve a https://intelx.io
2. Crea cuenta → Suscríbete a Explorer ($50)
3. Copia tu API Key

### Snusbase ($30/mes) — STEALER LOGS
1. Ve a https://snusbase.com
2. Crea cuenta → Suscríbete a Basic ($30)
3. Copia tu API Key (formato: `snus_xxx`)

---

## 💰 Planes y Precios

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

## 🏦 Instituciones Detectadas (15+)

### Bancos
- US Bank, Chase, Wells Fargo, Bank of America, Citi
- Capital One, TD Bank, PNC Bank, Truist

### Fintechs
- Venmo, PayPal, Cash App, Zelle, Stripe

### Credit Unions
- Schools Federal Credit Union, Navy Federal, Alliant

---

## 🏗️ Para Desarrolladores

### Ejecutar Localmente
```bash
cd C:\financial-osint
pip install -r requirements.txt
streamlit run app.py
# Abrir http://localhost:8502
```

### Estructura de Motores
```
engines/
├── extraction_engine.py      ← Motor principal
├── ssn_lookup_engine.py      ← SSN lookup
├── credit_score_engine.py    ← Credit score
├── address_engine.py         ← Búsqueda por dirección
├── institution_matcher.py    ← Detección de instituciones
├── leakcheck_engine.py       ← Motor LeakCheck
└── export_engine.py          ← Exportación
```

### Variables de Entorno
```bash
DATABASE_URL=postgresql://...    # Neon DB
LEAKCHECK_API_KEY=tu-key
DEHASHED_API_KEY=tu-key
```

---

## 📊 Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **Frontend** | Streamlit (Python) |
| **Backend** | Python 3.12 |
| **Base de datos** | Neon PostgreSQL |
| **APIs** | LeakCheck, DeHashed, IntelX, Snusbase |
| **Hosting** | Streamlit Cloud (gratis) |
| **Landing** | Flask + Vercel |

---

## 📄 Documentación

| Archivo | Qué contiene |
|---------|-------------|
| `ECOSISTEMA_FINAL.md` | Documentación completa |
| `ESTADO_PROYECTO.md` | Estado del proyecto |
| `SETUP_COMPLETO.md` | Setup de todas las APIs |
| `SSN_LOOKUP_ANALISIS.md` | Análisis de SSN lookup |
| `LEAKCHECK_PRO_SETUP.md` | Guía LeakCheck Pro |
| `DEPLOY_GUIA.md` | Guía de deploy |

---

## 🤝 Soporte

- **WhatsApp:** +57 300 123 4567
- **Email:** admin@financialosint.com
- **GitHub:** https://github.com/aonetworkcrm-art/-Financial-OSINT-PRO

---

## 📝 Licencia

Uso exclusivo para auditoría de seguridad con autorización.
