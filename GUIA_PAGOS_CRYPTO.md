# 💰 Guía de Pagos Crypto con MetaMask

## 🦊 Cómo Recibir Pagos con MetaMask

### Paso 1: Crear Wallet Dedicada
1. Abre MetaMask
2. Click **Create Account** → Nombre: "Proxy Commander Payments"
3. Copia la dirección de la wallet
4. **NUNCA uses tu wallet personal**

### Paso 2: Configurar en la Landing
1. Abre `api/index.py`
2. Busca `CONFIG["wallet_address"]`
3. Cambia `0xYOUR_WALLET_ADDRESS` por tu wallet
4. Redespliega: `vercel --yes --prod`

### Paso 3: Mostrar en Checkout
El checkout muestra automáticamente:
- Tu dirección de wallet
- Red: Ethereum Mainnet
- Tokens aceptados: ETH, USDC, USDT

---

## 🔄 Flujo de Pago

### Para el Usuario:
```
1. Ve al checkout
2. Selecciona "Crypto (MetaMask)"
3. Copia la dirección de la wallet
4. Abre MetaMask
5. Envía el monto exacto
6. Copia el tx hash
7. Pega el tx hash en el formulario
8. Click "Ya Envié el Crypto"
```

### Para Tú (Admin):
```
1. Usuario te envía el tx hash
2. Tú verificas en Etherscan:
   - https://etherscan.io/tx/TX_HASH
3. Verificas:
   - Destino correcto (tu wallet)
   - Monto correcto
   - Confirmaciones >= 3
4. Apruebas en admin panel
5. Se genera la API Key
6. Se la envías al usuario
```

---

## 🔍 Cómo Verificar un Pago

### Opción 1: Etherscan (Recomendado)
1. Ve a https://etherscan.io
2. Busca el tx hash
3. Verifica:
   - **To:** Tu wallet address
   - **Value:** Monto correcto
   - **Status:** Success
   - **Confirmations:** >= 3

### Opción 2: MetaMask
1. Abre MetaMask
2. Ve a **Activity**
3. Busca la transacción
4. Verifica los detalles

### Opción 3: Web3.py (Automático)
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/TU_KEY'))

def verify_payment(tx_hash, expected_usd, your_wallet):
    tx = w3.eth.get_transaction(tx_hash)
    
    if tx['to'].lower() != your_wallet.lower():
        return {"valid": False, "error": "Wallet destino incorrecta"}
    
    amount_eth = w3.from_wei(tx['value'], 'ether')
    return {
        "valid": True,
        "from": tx['from'],
        "amount_eth": float(amount_eth),
        "block": tx['blockNumber']
    }
```

---

## 💵 Conversión de Precios

### Precios en ETH (aproximados)
| Plan | USD | ETH (aprox) |
|------|-----|-------------|
| Starter | $15 | 0.004 ETH |
| Professional | $35 | 0.009 ETH |
| Enterprise | $50 | 0.013 ETH |
| Business | $100 | 0.026 ETH |
| Unlimited | $150 | 0.039 ETH |

### Precios en USDC/USDT
| Plan | USD | USDC/USDT |
|------|-----|-----------|
| Starter | $15 | 15 USDC |
| Professional | $35 | 35 USDC |
| Enterprise | $50 | 50 USDC |
| Business | $100 | 100 USDC |
| Unlimited | $150 | 150 USDC |

**Recomendación:** Pide USDC/USDT para evitar volatilidad de ETH.

---

## ⚠️ Notas Importantes

### Seguridad
1. **NUNCA** compartas tu private key
2. **NUNCA** uses tu wallet personal para negocios
3. **SIEMPRE** verifica pagos antes de aprobar
4. **GUARDA** todos los tx hashes

### Gas Fees
- El usuario paga el gas fee, no tú
- Gas fee típico: $2-20 dependiendo de congestión
- Recomienda enviar en horarios de baja congestión

### Confirmaciones
- Espera al menos **3 confirmaciones** antes de aprobar
- Para montos grandes, espera **6 confirmaciones**
- Tiempo promedio: 15-30 minutos

---

## 🚀 Futuro: Smart Contracts

Cuando tengas 50+ clientes, considera implementar smart contracts para:
- Pagos automáticos
- Sin verificación manual
- Transparencia total

Ver `WEB3_PAGOS_ANALISIS.md` para más detalles.
