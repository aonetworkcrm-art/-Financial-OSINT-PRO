# 🌐 ECOSISTEMA COMPLETO — Documentación Final

## 📍 Mapa del Ecosistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ECOSISTEMA COMPLETO                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🌐 LANDING PAGES (Vercel - URLs Reales)                           │
│  ├── Proxy Commander: https://proxy-commander-vercel.vercel.app    │
│  └── Financial OSINT:  https://financial-osint-vercel.vercel.app   │
│          │                                                          │
│          │  Registro → Login → Checkout → Pago                      │
│          ▼                                                          │
│  🗄️ BASE DE DATOS (Neon PostgreSQL - GRATIS)                       │
│  ├── Tabla: users (registro, créditos, API keys)                    │
│  ├── Tabla: orders (compras, pagos, licencias)                      │
│  └── Tabla: activity_log (tracking de actividad)                    │
│          │                                                          │
│          ▼                                                          │
│  🛠️ HERRAMIENTAS (Streamlit Cloud - URLs Reales)                   │
│  ├── Proxy Commander: https://proxy-commander-lrqj8bcuye7cbzxfxblpzd.streamlit.app  │
│  └── Financial OSINT:  https://mvu68iewaaebks96q4e3pg.streamlit.app                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 TODAS LAS URLs

### 📢 Landing Pages (Ventas)

| Herramienta | URL | Función |
|------------|-----|---------|
| **Proxy Commander Landing** | https://proxy-commander-vercel.vercel.app | Página de ventas + registro + checkout + admin |
| **Financial OSINT Landing** | https://financial-osint-vercel.vercel.app | Página de ventas + registro + checkout + admin |

### 🛠️ Herramientas (Uso)

| Herramienta | URL | Función |
|------------|-----|---------|
| **Proxy Commander Tool** | https://proxy-commander-lrqj8bcuye7cbzxfxblpzd.streamlit.app | Búsqueda y filtrado de proxies |
| **Financial OSINT Tool** | https://mvu68iewaaebks96q4e3pg.streamlit.app | OSINT financiero, SSN, Credit Score |

### 🗄️ Base de Datos

| Servicio | URL | Función |
|----------|-----|---------|
| **Neon Console** | https://console.neon.tech | Administrar la base de datos |
| **GitHub Repos** | https://github.com/aonetworkcrm-art | Código fuente |

---

## 🔑 Credenciales

### Admin Panel (Ambas Landings)

| Landing | Usuario | Contraseña |
|---------|---------|------------|
| Proxy Commander | `admin` | `admin123` |
| Financial OSINT | `admin` | `admin123` |

### Base de Datos Neon

| Campo | Valor |
|-------|-------|
| **Host** | ep-still-snow-axveeqvq-pooler.c-4.us-east-2.aws.neon.tech |
| **Database** | neondb |
| **User** | neondb_owner |
| **URL** | `postgresql://neondb_owner:npg_7sqaTJDi9GPg@ep-still-snow-axveeqvq-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require` |

### Repos GitHub

| Proyecto | URL |
|----------|-----|
| Proxy Commander | https://github.com/aonetworkcrm-art/proxy-commander |
| Financial OSINT | https://github.com/aonetworkcrm-art/-Financial-OSINT-PRO |

---

## 📊 Paquetes de Precios

### Proxy Commander

| Plan | Proxies | Precio | $/proxy |
|------|---------|--------|---------|
| Starter | 50 | $15 | $0.30 |
| Professional ⭐ | 150 | $35 | $0.23 |
| Enterprise | 200 | $50 | $0.25 |
| Business | 500 | $100 | $0.20 |
| Unlimited | 2,000/mes | $150 | $0.075 |

### Financial OSINT

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

## 🔄 Flujo del Usuario

### 1. Encuentra la Landing
```
Usuario ve anuncio/publicación
→ Hace clic en la landing
→ Ve planes, precios, beneficios
```

### 2. Se Registra
```
Click "Empezar Ahora"
→ Formulario: nombre, email, contraseña
→ Cuenta creada en Neon DB
→ Redirige a checkout
```

### 3. Paga
```
Elige método: Crypto (MetaMask) / WhatsApp / Transferencia
→ Crea orden en DB
→ Envía crypto a tu wallet
→ Tú apruebas en Admin panel
→ Se genera API Key
```

### 4. Usa la Herramienta
```
Copia su API Key del panel
→ Ve a la URL de la herramienta (Streamlit)
→ Hace login con su API Key
→ ¡Listo! Puede usar la herramienta
```

### 5. Tracking
```
Todo se registra en Neon DB:
- Login → timestamp
- Búsqueda → tipo, cantidad
- Checker → resultados
- Export → formato
- Pago → monto, método
```

---

## 🏗️ Arquitectura Técnica

### Landing Pages (Vercel)

```
C:\proxy-commander-vercel\
├── api/
│   ├── index.py        ← Flask app principal
│   ├── database.py     ← Neon PostgreSQL + SQLite fallback
│   └── templates/      ← 13 templates HTML
│       ├── index.html
│       ├── register.html
│       ├── login.html
│       ├── checkout.html
│       ├── panel.html
│       ├── admin.html
│       ├── payment_crypto.html
│       ├── payment_whatsapp.html
│       └── ...
├── vercel.json
└── requirements.txt
```

### Herramientas (Streamlit Cloud)

```
C:\proxy-filter-tool\
├── app.py              ← Herramienta principal (Streamlit)
├── user_tracker.py     ← Tracking de usuarios (Neon DB)
├── help_panel.py       ← Panel de ayuda
├── requirements.txt
└── engines/            ← (solo Financial OSINT)
    ├── extraction_engine.py
    ├── ssn_lookup_engine.py
    ├── credit_score_engine.py
    └── ...

C:\financial-osint\
├── app.py              ← Herramienta principal
├── user_tracker.py     ← Tracking de usuarios
├── engines/
│   ├── extraction_engine.py
│   ├── ssn_lookup_engine.py
│   ├── credit_score_engine.py
│   ├── address_engine.py
│   ├── institution_matcher.py
│   └── export_engine.py
└── requirements.txt
```

### Base de Datos (Neon PostgreSQL)

```
users
├── id (SERIAL PRIMARY KEY)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
├── full_name
├── whatsapp
├── role (admin/user)
├── credits
├── plan
├── api_key (UNIQUE)
├── total_searches
├── total_checks
├── login_count
├── created_at
└── last_login

orders
├── id (PRIMARY KEY)
├── user_id → users.id
├── plan
├── credits
├── amount_usd
├── payment_method (crypto/whatsapp/transfer)
├── payment_status (pending/paid)
├── status (pending/approved/rejected)
├── license_key
├── tx_hash
└── created_at

activity_log
├── id (SERIAL PRIMARY KEY)
├── user_id → users.id
├── action (register/login/search/check/export)
├── details (JSONB)
└── created_at
```

---

## 💰 Pagos Crypto (MetaMask)

### Flujo Actual
```
1. Usuario ve wallet address en checkout
2. Envía ETH/USDC/USDT desde MetaMask
3. Pega tx hash en formulario
4. Tú verificas en blockchain
5. Apruebas en admin panel
6. Se activa la cuenta
```

### Para Implementar (Web3.py)
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/TU_KEY'))

def verify_payment(tx_hash, expected_usd, wallet):
    tx = w3.eth.get_transaction(tx_hash)
    if tx['to'].lower() == wallet.lower():
        return {"valid": True, "from": tx['from'], "amount": w3.from_wei(tx['value'], 'ether')}
    return {"valid": False}
```

---

## 📋 Para Activar Neon DB en Streamlit Cloud

1. Ve a **https://share.streamlit.io**
2. Tu app → ⋮ → Settings → Secrets
3. Pega:
```toml
DATABASE_URL = "postgresql://neondb_owner:npg_7sqaTJDi9GPg@ep-still-snow-axveeqvq-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
```
4. Save

---

## 🚀 Cómo Actualizar

### Landings (Vercel)
```bash
cd C:\proxy-commander-vercel
# Editar api/index.py o templates
vercel --yes --prod
```

### Herramientas (Streamlit Cloud)
```bash
cd C:\proxy-filter-tool
# Editar app.py
git add . && git commit -m "update" && git push
# Streamlit Cloud detecta el push y redespliega
```

### Código en GitHub
```bash
cd C:\proxy-filter-tool
git add . && git commit -m "descripción" && git push
```

---

## 📊 Resumen de Inversión

| Componente | Costo | Estado |
|-----------|-------|--------|
| **Vercel** (Landings) | $0 (gratis) | ✅ Desplegado |
| **Streamlit Cloud** (Herramientas) | $0 (gratis) | ✅ Desplegado |
| **Neon PostgreSQL** (Base de datos) | $0 (gratis) | ✅ Conectado |
| **GitHub** (Código fuente) | $0 (gratis) | ✅ Subido |
| **Dominio personalizado** | ~$12/año | ⏳ Opcional |
| **TOTAL** | **$0** | ✅ Funcionando |

---

## 📂 Archivos de Documentación

| Archivo | Qué contiene |
|---------|-------------|
| `ECOSISTEMA_FINAL.md` | Este documento |
| `NEON_SETUP.md` | Setup de Neon DB |
| `WEB3_PAGOS_ANALISIS.md` | Análisis de pagos crypto |
| `DEPLOY_STREAMLIT_CLOUD.md` | Deploy a Streamlit Cloud |
| `ESTADO_PROYECTO.md` | Estado del proyecto |
| `SETUP_COMPLETO.md` | Setup de todas las APIs |
| `SSN_LOOKUP_ANALISIS.md` | Análisis de SSN lookup |
| `README.md` | Manual de uso |
