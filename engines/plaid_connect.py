"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🔗 PLAID CONNECT — Mi Perfil Financiero                                    ║
║                                                                              ║
║  Permite al usuario conectar SU propio banco y ver:                          ║
║    - Todas sus cuentas (débito + crédito)                                    ║
║    - Balances actuales                                                       ║
║    - Tarjetas de crédito con límites                                         ║
║    - Historial de transacciones                                              ║
║    - Routing y account numbers                                               ║
║    - Credit score (opcional)                                                 ║
║                                                                              ║
║  100% Legal: el usuario autoriza explícitamente.                             ║
║  Plaid maneja toda la seguridad (nunca vemos credenciales).                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

# ── Plaid API Configuration ──────────────────────────────────────────────────

PLAID_ENVS = {
    "sandbox": {
        "base_url": "https://sandbox.plaid.com",
        "client_id_env": "PLAID_CLIENT_ID",
        "secret_env": "PLAID_SECRET_SANDBOX",
    },
    "development": {
        "base_url": "https://development.plaid.com",
        "client_id_env": "PLAID_CLIENT_ID",
        "secret_env": "PLAID_SECRET_DEVELOPMENT",
    },
    "production": {
        "base_url": "https://production.plaid.com",
        "client_id_env": "PLAID_CLIENT_ID",
        "secret_env": "PLAID_SECRET_PRODUCTION",
    },
}

# Bancos populares para el selector
POPULAR_BANKS = [
    {"name": "Chase", "id": "ins_3", "logo": "🏦"},
    {"name": "Bank of America", "id": "ins_4", "logo": "🏦"},
    {"name": "Wells Fargo", "id": "ins_5", "logo": "🏦"},
    {"name": "Citi", "id": "ins_6", "logo": "🏦"},
    {"name": "Capital One", "id": "ins_11", "logo": "🏦"},
    {"name": "US Bank", "id": "ins_10", "logo": "🏦"},
    {"name": "PNC Bank", "id": "ins_9", "logo": "🏦"},
    {"name": "TD Bank", "id": "ins_12", "logo": "🏦"},
    {"name": "Navy Federal", "id": "ins_15", "logo": "🏦"},
    {"name": "Charles Schwab", "id": "ins_14", "logo": "🏦"},
    {"name": "Fidelity", "id": "ins_16", "logo": "🏦"},
    {"name": "Robinhood", "id": "ins_17", "logo": "📈"},
    {"name": "Venmo", "id": "ins_18", "logo": "💳"},
    {"name": "Cash App", "id": "ins_19", "logo": "💰"},
    {"name": "PayPal", "id": "ins_20", "logo": "💳"},
]


@dataclass
class PlaidAccount:
    account_id: str
    name: str
    official_name: str
    mask: str
    account_type: str  # depository, credit, investment, loan
    subtype: str  # checking, savings, credit card, cd, etc.
    balance_available: float
    balance_current: float
    balance_limit: Optional[float]
    iso_currency_code: str
    # Enriched data
    bin_number: str = ""
    network: str = ""
    bank_name: str = ""
    is_vbv: bool = True
    vbv_type: str = ""  # VBV, SecureCode, SafeKey
    card_level: str = ""  # Classic, Gold, Platinum, Signature
    country: str = ""


@dataclass
class PlaidTransaction:
    transaction_id: str
    account_id: str
    date: str
    name: str
    amount: float
    category: List[str]
    merchant_name: str
    pending: bool
    iso_currency_code: str


@dataclass
class PlaidProfile:
    user_id: str
    connected_at: str
    last_sync: str
    institution_name: str
    institution_id: str
    accounts: List[PlaidAccount]
    transactions: List[PlaidTransaction]
    total_balance: float
    total_credit_limit: float
    total_credit_balance: float
    total_debit_balance: float
    credit_utilization: float
    accounts_count: int
    cards_count: int
    access_token: str  # Encrypted in production


class PlaidConnectEngine:
    """
    Motor de integración con Plaid para ver el perfil financiero propio del usuario.
    
    Flujo:
    1. Usuario hace click "Conectar Banco"
    2. Se genera un Link Token
    3. Plaid abre popup seguro
    4. Usuario autentica en su banco
    5. Plaid entrega un Access Token
    6. Nosotros usamos el token para consultar datos
    """
    
    def __init__(self, env: str = "sandbox"):
        self.env = env
        self.config = PLAID_ENVS.get(env, PLAID_ENVS["sandbox"])
        self.client_id = os.environ.get(self.config["client_id_env"], "")
        self.secret = os.environ.get(self.config["secret_env"], "")
        self.base_url = self.config["base_url"]
        self.profiles: Dict[str, PlaidProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load saved profiles from disk."""
        profiles_dir = os.path.join(os.path.dirname(__file__), "..", "data", "plaid_profiles")
        os.makedirs(profiles_dir, exist_ok=True)
        for f in os.listdir(profiles_dir):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(profiles_dir, f), "r") as fh:
                        data = json.load(fh)
                        # Reconstruct objects
                        accounts = [PlaidAccount(**a) for a in data.get("accounts", [])]
                        transactions = [PlaidTransaction(**t) for t in data.get("transactions", [])]
                        data["accounts"] = accounts
                        data["transactions"] = transactions
                        self.profiles[data["user_id"]] = PlaidProfile(**data)
                except Exception:
                    pass
    
    def _save_profile(self, profile: PlaidProfile):
        """Save profile to disk."""
        profiles_dir = os.path.join(os.path.dirname(__file__), "..", "data", "plaid_profiles")
        os.makedirs(profiles_dir, exist_ok=True)
        path = os.path.join(profiles_dir, f"{profile.user_id}.json")
        data = asdict(profile)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _plaid_request(self, endpoint: str, payload: dict) -> dict:
        """Make a request to Plaid API."""
        url = f"{self.base_url}/{endpoint}"
        payload["client_id"] = self.client_id
        payload["secret"] = self.secret
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "User-Agent": "FinancialOSINT/1.0"
        })
        
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            return {"error": str(e)}
    
    def create_link_token(self, user_id: str) -> dict:
        """
        Create a Link Token for the user to connect their bank.
        This is the FIRST step - the user needs this to open Plaid Link.
        """
        payload = {
            "user": {"client_user_id": user_id},
            "client_name": "Financial OSINT PRO",
            "products": ["auth", "transactions", "balance", "identity"],
            "country_codes": ["US"],
            "language": "en",
        }
        return self._plaid_request("link/token/create", payload)
    
    def exchange_public_token(self, public_token: str, user_id: str) -> dict:
        """
        Exchange the public token (from Plaid Link) for an access token.
        This happens AFTER the user authenticates with their bank.
        """
        payload = {"public_token": public_token}
        result = self._plaid_request("item/public_token/exchange", payload)
        
        if "access_token" in result:
            # Store the access token securely
            self._store_access_token(user_id, result["access_token"], result.get("item_id", ""))
        
        return result
    
    def _store_access_token(self, user_id: str, access_token: str, item_id: str):
        """Store access token securely (encrypted in production)."""
        tokens_dir = os.path.join(os.path.dirname(__file__), "..", "data", "plaid_tokens")
        os.makedirs(tokens_dir, exist_ok=True)
        # In production, encrypt this!
        token_data = {
            "access_token": access_token,
            "item_id": item_id,
            "created_at": datetime.now().isoformat(),
        }
        with open(os.path.join(tokens_dir, f"{user_id}.json"), "w") as f:
            json.dump(token_data, f, indent=2)
    
    def _get_access_token(self, user_id: str) -> Optional[str]:
        """Get stored access token for user."""
        token_path = os.path.join(os.path.dirname(__file__), "..", "data", "plaid_tokens", f"{user_id}.json")
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                data = json.load(f)
                return data.get("access_token")
        return None
    
    def get_accounts(self, user_id: str) -> List[PlaidAccount]:
        """Get all accounts for a connected user."""
        access_token = self._get_access_token(user_id)
        if not access_token:
            return []
        
        payload = {"access_token": access_token}
        result = self._plaid_request("accounts/get", payload)
        
        if "accounts" not in result:
            return []
        
        accounts = []
        for acc in result["accounts"]:
            account = PlaidAccount(
                account_id=acc["account_id"],
                name=acc["name"],
                official_name=acc.get("official_name", ""),
                mask=acc.get("mask", ""),
                account_type=acc["type"],
                subtype=acc.get("subtype", ""),
                balance_available=acc["balances"].get("available", 0) or 0,
                balance_current=acc["balances"].get("current", 0) or 0,
                balance_limit=acc["balances"].get("limit"),
                iso_currency_code=acc["balances"].get("iso_currency_code", "USD"),
            )
            # Enrich with BIN data for credit cards
            if account.account_type == "credit" and len(account.mask) >= 6:
                account.bin_number = account.mask[:6]
            accounts.append(account)
        
        return accounts
    
    def get_transactions(self, user_id: str, count: int = 50) -> List[PlaidTransaction]:
        """Get recent transactions for a connected user."""
        access_token = self._get_access_token(user_id)
        if not access_token:
            return []
        
        payload = {
            "access_token": access_token,
            "options": {"count": count}
        }
        result = self._plaid_request("transactions/get", payload)
        
        if "transactions" not in result:
            return []
        
        transactions = []
        for tx in result["transactions"]:
            transactions.append(PlaidTransaction(
                transaction_id=tx["transaction_id"],
                account_id=tx["account_id"],
                date=tx["date"],
                name=tx["name"],
                amount=tx["amount"],
                category=tx.get("category", []),
                merchant_name=tx.get("merchant_name", tx["name"]),
                pending=tx.get("pending", False),
                iso_currency_code=tx.get("iso_currency_code", "USD"),
            ))
        
        return transactions
    
    def get_balance(self, user_id: str) -> dict:
        """Get real-time balance for all accounts."""
        access_token = self._get_access_token(user_id)
        if not access_token:
            return {"error": "Not connected"}
        
        payload = {"access_token": access_token}
        return self._plaid_request("accounts/balance/get", payload)
    
    def get_identity(self, user_id: str) -> dict:
        """Get identity info (name, email, phone, address) from the bank."""
        access_token = self._get_access_token(user_id)
        if not access_token:
            return {"error": "Not connected"}
        
        payload = {"access_token": access_token}
        return self._plaid_request("identity/get", payload)
    
    def build_profile(self, user_id: str, institution_name: str = "", institution_id: str = "") -> PlaidProfile:
        """Build complete financial profile for a user."""
        accounts = self.get_accounts(user_id)
        transactions = self.get_transactions(user_id)
        
        # Calculate totals
        total_credit_limit = sum(a.balance_limit or 0 for a in accounts if a.account_type == "credit")
        total_credit_balance = sum(a.balance_current for a in accounts if a.account_type == "credit")
        total_debit_balance = sum(a.balance_current for a in accounts if a.account_type == "depository")
        total_balance = total_debit_balance + sum(max(0, a.balance_current) for a in accounts if a.account_type == "credit")
        credit_utilization = (total_credit_balance / total_credit_limit * 100) if total_credit_limit > 0 else 0
        
        profile = PlaidProfile(
            user_id=user_id,
            connected_at=datetime.now().isoformat(),
            last_sync=datetime.now().isoformat(),
            institution_name=institution_name,
            institution_id=institution_id,
            accounts=accounts,
            transactions=transactions,
            total_balance=total_balance,
            total_credit_limit=total_credit_limit,
            total_credit_balance=total_credit_balance,
            total_debit_balance=total_debit_balance,
            credit_utilization=round(credit_utilization, 1),
            accounts_count=len(accounts),
            cards_count=sum(1 for a in accounts if a.account_type == "credit"),
            access_token="",  # Don't store in profile
        )
        
        self.profiles[user_id] = profile
        self._save_profile(profile)
        
        return profile
    
    def disconnect(self, user_id: str) -> bool:
        """Disconnect a user's bank connection."""
        # Remove access token
        token_path = os.path.join(os.path.dirname(__file__), "..", "data", "plaid_tokens", f"{user_id}.json")
        if os.path.exists(token_path):
            os.remove(token_path)
        
        # Remove profile
        if user_id in self.profiles:
            del self.profiles[user_id]
        
        # Remove profile file
        profile_path = os.path.join(os.path.dirname(__file__), "..", "data", "plaid_profiles", f"{user_id}.json")
        if os.path.exists(profile_path):
            os.remove(profile_path)
        
        return True
    
    def get_all_connected_users(self) -> List[Dict]:
        """Admin: Get all connected users."""
        users = []
        for user_id, profile in self.profiles.items():
            users.append({
                "user_id": user_id,
                "institution": profile.institution_name,
                "connected_at": profile.connected_at,
                "last_sync": profile.last_sync,
                "accounts_count": profile.accounts_count,
                "cards_count": profile.cards_count,
                "total_balance": profile.total_balance,
                "total_credit_limit": profile.total_credit_limit,
            })
        return users
    
    def export_profile_csv(self, user_id: str) -> str:
        """Export profile to CSV."""
        profile = self.profiles.get(user_id)
        if not profile:
            return ""
        
        lines = ["type,name,mask,balance,available,limit,currency,institution"]
        for acc in profile.accounts:
            lines.append(
                f'"{acc.account_type}","{acc.name}","{acc.mask}",'
                f'{acc.balance_current},{acc.balance_available},'
                f'{acc.balance_limit or 0},"{acc.iso_currency_code}",'
                f'"{profile.institution_name}"'
            )
        
        lines.append("")
        lines.append("date,name,amount,category,account,pending")
        for tx in profile.transactions:
            cat = " > ".join(tx.category) if tx.category else ""
            lines.append(
                f'"{tx.date}","{tx.name}",{tx.amount},"{cat}",'
                f'"{tx.account_id}","{tx.pending}"'
            )
        
        return "\n".join(lines)
