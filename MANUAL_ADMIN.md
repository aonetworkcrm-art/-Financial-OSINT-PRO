# 👑 Manual de Admin — Panel de Administración

## 🌐 Acceso al Admin

**URL:** https://proxy-commander-vercel.vercel.app/admin

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 📊 Dashboard

Al entrar al admin, ves el dashboard con:

| Métrica | Qué significa |
|---------|--------------|
| **Usuarios** | Total de usuarios registrados |
| **Órdenes Totales** | Compras realizadas |
| **Pendientes** | Pagos esperando aprobación |
| **Ingresos** | Dinero total ganado |

---

## 📋 Gestionar Órdenes

### Aprobar una Orden
1. Ve a la pestaña **📋 Órdenes**
2. Busca la orden **pendiente**
3. Click **✅ Aprobar**
4. Se genera automáticamente una **API Key**
5. Copia la key y envíasela al usuario

### Rechazar una Orden
1. Busca la orden
2. Click **✕ Rechazar**
3. La orden se marca como rechazada

---

## 👤 Gestionar Usuarios

### Ver Todos los Usuarios
1. Ve a la pestaña **👤 Usuarios**
2. Ves: username, email, créditos, plan, fecha de registro

### Agregar Créditos Manualmente
1. Encuentra al usuario
2. Click **+ Créditos**
3. Ingresa la cantidad
4. Click confirmar

---

## 🔑 Generar API Keys

### Generar Key Manual
1. Ve a la pestaña **🔑 Generar Key**
2. Selecciona el plan
3. Agrega notas (opcional)
4. Click **🔑 Generar Key**
5. Copia la key generada

### Formato de Keys
```
PCMD-PRO-XXXXXXXX-XXXXXXXX
PCMD-STD-XXXXXXXX-XXXXXXXX
PCMD-ENT-XXXXXXXX-XXXXXXXX
```

---

## 💰 Métodos de Pago Aceptados

### Crypto (MetaMask)
```
1. Usuario envía ETH/USDC/USDT a tu wallet
2. Peg tx hash en el formulario
3. Tú verificas en blockchain
4. Aprobas en admin
```

### WhatsApp
```
1. Usuario te contacta por WhatsApp
2. Tú acuerdas el pago
3. Una vez confirmado, apruebas en admin
```

### Transferencia Bancaria
```
1. Usuario hace transferencia
2. Tú verificas en tu banco
3. Apruebas en admin
```

---

## 📊 Monitoreo

### Ver Actividad de Usuarios
- Login count
- Último login
- Búsquedas realizadas
- Proxies verificados
- Exportaciones

### Ver Ingresos
- Órdenes aprobadas
- Total ganado
- Créditos en circulación

---

## ⚠️ Notas Importantes

1. **Siempre verifica el pago** antes de aprobar
2. **Guarda los tx hashes** de crypto para referencia
3. **Responde rápido** a los usuarios (menos de 24h)
4. **Monitorea** el dashboard diariamente
5. **Respalda** la base de datos regularmente

---

## 🔄 Flujo de Trabajo Diario

```
Mañana:
1. Entrar al admin
2. Revisar órdenes pendientes
3. Aprobar pagos verificados
4. Responder mensajes de WhatsApp

Tarde:
1. Verificar nuevos registros
2. Revisar actividad de usuarios
3. Actualizar precios si es necesario

Noche:
1. Revisar métricas del día
2. Planificar mejoras
```
