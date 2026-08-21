"""
🏦 Plaid Integration Engine
============================
Integra con Plaid API para verificar cuentas bancarias:
- Balance checking
- Account status (active/inactive)
- Account type verification
- Transaction history

Requiere:
1. Cuenta en plaid.com (sandbox gratuito para desarrollo)
2. PLAID_CLIENT_ID y PLAID_SECRET en secrets

Setup:
1. Ve a https://dashboard.plaid.com/signup
2. Crea cuenta gratuita (sandbox = gratis, 100 requests/mes)
3. Ve a Team Settings → Keys
4. Copia Client ID y Secret
5. Agrega a Streamlit secrets:
   PLAID_CLIENT_ID = "tu_client_id"
   PLAID_SECRET = "tu_secret"
   PLAID_ENV = "sandbox"  # sandbox, development, o production
"""
import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger("plaid_engine")


@dataclass
class PlaidAccountInfo:
    """Información de cuenta obtenida de Plaid"""
    account_id: str = ""
    account_name: str = ""
    account_type: str = ""       # depository, credit, loan, investment
    account_subtype: str = ""    # checking, savings, cd, money market, credit card
    official_name: str = ""
    
    # Balance
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    limit: Optional[float] = None  # For credit cards
    
    # Currency
    iso_currency_code: str = "USD"
    
    # Status
    is_active: bool = False
    status_detail: str = ""
    
    # Mask
    mask: str = ""  # Last 4 digits
    
    # Institution
    institution_name: str = ""
    institution_id: str = ""
    
    # Metadata
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PlaidConnection:
    """Resultado de conexión con Plaid"""
    access_token: str = ""
    item_id: str = ""
    institution_name: str = ""
    institution_id: str = ""
    accounts: List[PlaidAccountInfo] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d["accounts"] = [a.to_dict() for a in self.accounts]
        return d


class PlaidEngine:
    """
    Motor de integración con Plaid para verificación de cuentas.
    
    En modo sandbox (gratis), usa credenciales de prueba:
    - Public token: test-ins-109512
    - Access token: access-sandbox-xxxxx
    
    En modo development/production, necesita credenciales reales.
    """

    def __init__(self, client_id: str = "", secret: str = "", env: str = "sandbox"):
        self.client_id = client_id or os.environ.get("PLAID_CLIENT_ID", "")
        self.secret = secret or os.environ.get("PLAID_SECRET", "")
        self.env = env or os.environ.get("PLAID_ENV", "sandbox")
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if not self.client_id:
                self.client_id = st.secrets.get("PLAID_CLIENT_ID", "")
            if not self.secret:
                self.secret = st.secrets.get("PLAID_SECRET", "")
            if env == "sandbox":
                self.env = st.secrets.get("PLAID_ENV", "sandbox")
        except Exception:
            pass

        self._base_url = self._get_base_url()
        self._connected = False

    def _get_base_url(self) -> str:
        envs = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        return envs.get(self.env, envs["sandbox"])

    def is_configured(self) -> bool:
        """Check if Plaid credentials are set"""
        return bool(self.client_id and self.secret)

    def _make_request(self, endpoint: str, payload: dict) -> dict:
        """Make a request to Plaid API"""
        import requests
        
        url = f"{self._base_url}/{endpoint}"
        payload["client_id"] = self.client_id
        payload["secret"] = self.secret
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            data = resp.json()
            if "error" in data:
                error_msg = data["error"].get("error_message", str(data["error"]))
                logger.warning(f"Plaid API error: {error_msg}")
                return {"error": error_msg}
            return data
        except requests.exceptions.ConnectionError:
            return {"error": "No se pudo conectar a Plaid API"}
        except Exception as e:
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    # SANDBOX MODE (Free - for testing)
    # ═══════════════════════════════════════════════════════════════

    def get_sandbox_token(self) -> Optional[str]:
        """Get a sandbox public token for testing"""
        if not self.is_configured():
            return None
        
        data = self._make_request("sandbox/public_token/create", {
            "institution_id": "ins_109512",  # First Platypus Bank (test)
            "initial_products": ["transactions", "auth", "identity", "balance"],
        })
        return data.get("public_token")

    def exchange_token(self, public_token: str) -> Optional[PlaidConnection]:
        """Exchange public token for access token"""
        if not self.is_configured():
            return PlaidConnection(errors=["Plaid no configurado. Agrega PLAID_CLIENT_ID y PLAID_SECRET."])
        
        data = self._make_request("item/public_token/exchange", {
            "public_token": public_token,
        })
        
        if "error" in data:
            return PlaidConnection(errors=[data["error"]])
        
        conn = PlaidConnection(
            access_token=data.get("access_token", ""),
            item_id=data.get("item_id", ""),
        )
        self._connected = True
        return conn

    # ═══════════════════════════════════════════════════════════════
    # ACCOUNT OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    def get_accounts(self, access_token: str) -> PlaidConnection:
        """Get all accounts and their balances"""
        if not self.is_configured():
            return PlaidConnection(errors=["Plaid no configurado"])
        
        data = self._make_request("accounts/get", {
            "access_token": access_token,
            "options": {
                "account_ids": [],
            }
        })
        
        if "error" in data:
            return PlaidConnection(errors=[data["error"]])
        
        conn = PlaidConnection(
            access_token=access_token,
            item_id=data.get("item", {}).get("item_id", ""),
            institution_name=data.get("item", {}).get("institution_id", ""),
        )
        
        for acct in data.get("accounts", []):
            balances = acct.get("balances", {})
            info = PlaidAccountInfo(
                account_id=acct.get("account_id", ""),
                account_name=acct.get("name", ""),
                account_type=acct.get("type", ""),
                account_subtype=acct.get("subtype", ""),
                official_name=acct.get("official_name", ""),
                available_balance=balances.get("available"),
                current_balance=balances.get("current"),
                limit=balances.get("limit"),
                iso_currency_code=balances.get("iso_currency_code", "USD"),
                is_active=balances.get("available") is not None or balances.get("current") is not None,
                mask=acct.get("mask", ""),
                status_detail="Activa" if balances.get("current") is not None else "Sin datos",
            )
            conn.accounts.append(info)
        
        return conn

    def get_balances(self, access_token: str) -> List[PlaidAccountInfo]:
        """Get balances for all accounts"""
        conn = self.get_accounts(access_token)
        return conn.accounts

    def get_auth(self, access_token: str) -> Dict:
        """Get routing and account numbers (for US accounts)"""
        if not self.is_configured():
            return {"error": "Plaid no configurado"}
        
        data = self._make_request("auth/get", {
            "access_token": access_token,
        })
        
        if "error" in data:
            return {"error": data["error"]}
        
        result = {
            "numbers": [],
            "accounts": [],
        }
        
        for num in data.get("numbers", {}).get("ach", []):
            result["numbers"].append({
                "account": num.get("account", ""),
                "routing": num.get("routing", ""),
                "wire_routing": num.get("wire_routing", ""),
                "account_id": num.get("account_id", ""),
            })
        
        for acct in data.get("accounts", []):
            result["accounts"].append({
                "name": acct.get("name", ""),
                "mask": acct.get("mask", ""),
                "type": acct.get("type", ""),
                "subtype": acct.get("subtype", ""),
            })
        
        return result

    def get_identity(self, access_token: str) -> Dict:
        """Get identity information (names, emails, phones, addresses)"""
        if not self.is_configured():
            return {"error": "Plaid no configurado"}
        
        data = self._make_request("identity/get", {
            "access_token": access_token,
        })
        
        if "error" in data:
            return {"error": data["error"]}
        
        result = {"owners": []}
        
        for owner in data.get("accounts", [{}])[0].get("owners", []) if data.get("accounts") else []:
            result["owners"].append({
                "names": owner.get("names", []),
                "phone_numbers": [p.get("data", "") for p in owner.get("phone_numbers", [])],
                "emails": [e.get("data", "") for e in owner.get("emails", [])],
                "addresses": [a.get("data", {}) for a in owner.get("addresses", [])],
            })
        
        return result

    # ═══════════════════════════════════════════════════════════════
    # DIRECT ACCOUNT CHECK (Simulated for sandbox)
    # ═══════════════════════════════════════════════════════════════

    def check_account_direct(self, routing: str = "", account: str = "") -> PlaidAccountInfo:
        """
        Check account status directly (without full Plaid link).
        
        In sandbox mode, simulates results based on routing number.
        In production, would need full Plaid Link flow.
        """
        import re
        clean_routing = re.sub(r'[^0-9]', '', routing) if routing else ""
        clean_account = re.sub(r'[^0-9]', '', account) if account else ""
        
        result = PlaidAccountInfo(
            account_name="Cuenta verificada",
            account_type="depository",
            account_subtype="checking",
            mask=clean_account[-4:] if len(clean_account) >= 4 else "****",
        )
        
        # Check if we have Plaid configured
        if not self.is_configured():
            result.warnings.append("Plaid no configurado — usando validación básica")
            result.is_active = bool(clean_routing and clean_account)
            result.status_detail = "Verificación básica (sin Plaid)"
            return result
        
        # Sandbox simulation
        if self.env == "sandbox":
            result.is_active = True
            result.current_balance = 0.00
            result.available_balance = 0.00
            result.institution_name = "Banco (sandbox)"
            result.status_detail = "Sandbox: cuenta simulada activa"
            result.warnings.append("Modo sandbox — datos simulados")
            return result
        
        # Production would need Plaid Link
        result.warnings.append("Verificación completa requiere Plaid Link (usuario debe autenticarse)")
        result.status_detail = "Necesita autenticación Plaid completa"
        return result

    # ═══════════════════════════════════════════════════════════════
    # STATUS
    # ═══════════════════════════════════════════════════════════════

    def get_status(self) -> Dict:
        """Get Plaid connection status"""
        return {
            "configured": self.is_configured(),
            "env": self.env,
            "has_client_id": bool(self.client_id),
            "has_secret": bool(self.secret),
            "connected": self._connected,
        }


class MockPlaidEngine(PlaidEngine):
    """Mock engine when Plaid is not configured — returns demo data"""

    def __init__(self):
        super().__init__()
        self._mock = True

    def check_account_direct(self, routing: str = "", account: str = "") -> PlaidAccountInfo:
        import re
        clean_routing = re.sub(r'[^0-9]', '', routing) if routing else ""
        clean_account = re.sub(r'[^0-9]', '', account) if account else ""
        
        # Determine bank from routing
        bank_name = "Banco Desconocido"
        known_routings = {
            "021000021": "JPMorgan Chase",
            "026000082": "Bank of America",
            "021000013": "US Bank",
            "071000013": "Wells Fargo",
            "031000011": "Bank of America",
            "091000019": "Wells Fargo",
            "121000248": "Wells Fargo",
            "041215663": "Capital One",
            "051000017": "Capital One",
            "021200025": "Navy Federal CU",
            "073905523": "Schools Federal CU",
            "321177526": "PayPal",
            "073921824": "Venmo",
        }
        if clean_routing in known_routings:
            bank_name = known_routings[clean_routing]
        
        return PlaidAccountInfo(
            account_name=f"Cuenta {bank_name}",
            account_type="depository",
            account_subtype="checking",
            available_balance=0.0,
            current_balance=0.0,
            is_active=True,
            mask=clean_account[-4:] if len(clean_account) >= 4 else "****",
            institution_name=bank_name,
            status_detail="Verificación básica (sin Plaid — modo demo)",
            warnings=["Sin Plaid configurado — datos de ejemplo"],
            timestamp=datetime.now().isoformat(),
        )
