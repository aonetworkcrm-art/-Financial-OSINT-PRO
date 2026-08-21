"""
🔒 VBV / 3D Secure Detection Engine
=====================================
Detecta el estado VBV (Verified by Visa) / 3D Secure de tarjetas.

VBV = Verified by Visa → Sistema de autenticación 3D Secure de Visa
Mastercard SecureCode → Equivalente de Mastercard
Amex SafeKey → Equivalente de Amex

NON-VBV = Tarjeta SIN autenticación 3D Secure requerida.

Uso en auditoría de seguridad:
- Identificar tarjetas sin protección 3D Secure
- Filtrar por nivel de seguridad
- Clasificar exposición de datos

Base de datos de BIN ranges conocidos como NON-VBV.
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


# ═══════════════════════════════════════════════════════════════
# VBV STATUS DATABASE
# ═══════════════════════════════════════════════════════════════
# 
# NOTA: El estado VBV/NON-VBV NO es determinístico solo con el BIN.
# Depende del banco emisor, tipo de tarjeta y configuración individual.
# Esta base de datos refleja patrones COMUNES basados en:
# - BIN ranges de bancos conocidos
# - Tipo de tarjeta (débito vs crédito)
# - Nivel de tarjeta (prepaid vs premium)
# - País de emisión
#
# Referencias:
# - Visa: https://www.visa.com/en_us/support/consumer/card-security.html
# - Mastercard: https://www.mastercard.us/en-us/personal/find-support/secure-code.html
# - Amex: https://www.americanexpress.com/us/security/3d-secure/
# ═══════════════════════════════════════════════════════════════

# BINs que generalmente son NON-VBV (débito, prepaid, ciertos bancos)
NON_VBV_BINS = {
    # ─── DEBIT CARDS (generalmente NON-VBV) ─────────────────────
    # La mayoría de tarjetas de débito NO tienen 3D Secure obligatorio
    "400005": {"vbv": False, "reason": "Débito genérica"},
    "400555": {"vbv": False, "reason": "Wells Fargo Débito"},
    "402360": {"vbv": False, "reason": "Bank of America Débito"},
    "405528": {"vbv": False, "reason": "Chase Débito"},
    "432000": {"vbv": False, "reason": "US Bank Débito"},
    "440200": {"vbv": False, "reason": "Citibank Débito"},
    "450200": {"vbv": False, "reason": "BECU Débito"},
    "450100": {"vbv": False, "reason": "Schools FCU Débito"},
    "520000": {"vbv": False, "reason": "Mastercard Débito"},
    "520473": {"vbv": False, "reason": "Cash App Débito"},
    "520474": {"vbv": False, "reason": "Cash App Débito"},
    "530201": {"vbv": False, "reason": "Venmo Débito"},
    "531826": {"vbv": False, "reason": "Green Dot Prepago"},
    "533248": {"vbv": False, "reason": "Bluebird Prepago"},
    "543000": {"vbv": False, "reason": "Walmart MoneyCard"},
    "600001": {"vbv": False, "reason": "PayPal Débito"},
    "622000": {"vbv": False, "reason": "UnionPay Débito"},
    "624000": {"vbv": False, "reason": "UnionPay Débito"},
    "628000": {"vbv": False, "reason": "UnionPay Débito"},
    "535501": {"vbv": False, "reason": "Banorte Débito"},
    "415057": {"vbv": False, "reason": "Santander Débito"},

    # ─── PREPAID CARDS (generalmente NON-VBV) ───────────────────
    "400005": {"vbv": False, "reason": "Visa Prepago"},
    "510000": {"vbv": False, "reason": "Mastercard Prepago"},
    "540000": {"vbv": False, "reason": "Mastercard Prepago"},

    # ─── CREDIT CARDS (generalmente VBV) ────────────────────────
    # La mayoría de tarjetas de crédito US tienen 3D Secure
    "402340": {"vbv": True, "reason": "BofA Crédito (SecureCode)"},
    "405530": {"vbv": True, "reason": "Chase Crédito (Verified)"},
    "410000": {"vbv": True, "reason": "Chase Crédito (Verified)"},
    "414720": {"vbv": True, "reason": "Chase Sapphire (Verified)"},
    "415966": {"vbv": True, "reason": "Citibank Crédito (Verified)"},
    "432004": {"vbv": True, "reason": "US Bank Crédito (Verified)"},
    "440000": {"vbv": True, "reason": "Citibank Crédito (Verified)"},
    "450000": {"vbv": True, "reason": "Capital One Crédito (Verified)"},
    "450018": {"vbv": True, "reason": "Capital One Venture (Verified)"},
    "407350": {"vbv": True, "reason": "Alliant CU Crédito"},
    "404600": {"vbv": True, "reason": "PenFed CU Crédito"},
    "440300": {"vbv": True, "reason": "Navy Federal CU Crédito"},
    "510510": {"vbv": True, "reason": "BofA MC (SecureCode)"},
    "522200": {"vbv": True, "reason": "Chase MC (SecureCode)"},
    "540400": {"vbv": True, "reason": "BofA MC (SecureCode)"},
    "541000": {"vbv": True, "reason": "Capital One MC (SecureCode)"},
    "542400": {"vbv": True, "reason": "Citibank MC (SecureCode)"},
    "546600": {"vbv": True, "reason": "Wells Fargo MC (SecureCode)"},
    "549000": {"vbv": True, "reason": "Wells Fargo MC (SecureCode)"},
    "340000": {"vbv": True, "reason": "Amex (SafeKey)"},
    "370000": {"vbv": True, "reason": "Amex Platinum (SafeKey)"},
    "371449": {"vbv": True, "reason": "Amex Centurion (SafeKey)"},
    "378282": {"vbv": True, "reason": "Amex Gold (SafeKey)"},
    "601100": {"vbv": True, "reason": "Discover (ProtectBuy)"},
    "601101": {"vbv": True, "reason": "Discover (ProtectBuy)"},
    "650000": {"vbv": True, "reason": "Discover (ProtectBuy)"},

    # ─── INTERNATIONAL (varía por banco) ────────────────────────
    "402600": {"vbv": True, "reason": "BBVA (Verified)"},
    "415056": {"vbv": True, "reason": "Santander Crédito (Verified)"},
    "416888": {"vbv": True, "reason": "Banorte Crédito (Verified)"},
    "423826": {"vbv": True, "reason": "HSBC Crédito (Verified)"},
    "520128": {"vbv": True, "reason": "Santander MC (SecureCode)"},

    # ─── UNCERTAIN (puede ser VBV o no) ─────────────────────────
    "400100": {"vbv": None, "reason": "BIN no determinado"},
    "400200": {"vbv": None, "reason": "BIN no determinado"},
}

# Patrones de VBV por tipo de tarjeta
VBV_BY_TYPE = {
    "debit": False,      # Débito generalmente NON-VBV
    "credit": True,      # Crédito generalmente VBV
    "prepaid": False,    # Prepago generalmente NON-VBV
}

# 3D Secure providers por red
THREE_D_SECURE_PROVIDERS = {
    "Visa": "Verified by Visa (VBV)",
    "Mastercard": "Mastercard SecureCode",
    "Amex": "American Express SafeKey",
    "Discover": "Discover ProtectBuy",
    "JCB": "J/Secure",
    "UnionPay": "UnionPay 3D Secure",
    "Diners": "Diners Club ProtectBuy",
}


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class VBVResult:
    """Resultado de detección VBV para una tarjeta"""
    card_masked: str = ""
    network: str = ""
    
    # VBV Status
    is_vbv: Optional[bool] = None  # True=VBV, False=NON-VBV, None=desconocido
    vbv_status: str = ""           # "VBV_ENROLLED", "NON_VBV", "UNKNOWN"
    vbv_provider: str = ""         # "Verified by Visa", "SecureCode", etc.
    
    # Reason
    detection_method: str = ""     # "bin_database", "card_type", "unknown"
    reason: str = ""
    confidence: float = 0.0
    
    # Details
    card_type: str = ""            # credit/debit/prepaid
    issuing_bank: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BatchVBVResult:
    """Resultado de detección VBV en lote"""
    results: List[VBVResult] = field(default_factory=list)
    total: int = 0
    vbv_enrolled: int = 0
    non_vbv: int = 0
    unknown: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# VBV DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════

class VBVEngine:
    """
    Motor de detección VBV / 3D Secure.
    
    Detecta si una tarjeta está inscrita en 3D Secure (VBV) o no.
    
    Métodos de detección:
    1. BIN Database Lookup → Mayor confianza
    2. Card Type Heuristic → Débito/Prepaid = probablemente NON-VBV
    3. Network Defaults → Cada red tiene su protocolo
    """

    def detect(self, card_number: str, network: str = "",
               card_type: str = "", issuing_bank: str = "") -> VBVResult:
        """Detecta el estado VBV de una tarjeta"""
        clean = re.sub(r'[^0-9]', '', card_number)
        
        # Mask
        if len(clean) >= 8:
            masked = f"{clean[:4]}{'*' * (len(clean)-8)}{clean[-4:]}"
        elif len(clean) >= 4:
            masked = f"{'*' * (len(clean)-4)}{clean[-4:]}"
        else:
            masked = clean
        
        result = VBVResult(
            card_masked=masked,
            network=network,
            card_type=card_type,
            issuing_bank=issuing_bank,
        )
        
        # Method 1: BIN Database Lookup
        if len(clean) >= 6:
            bin6 = clean[:6]
            if bin6 in NON_VBV_BINS:
                info = NON_VBV_BINS[bin6]
                result.is_vbv = info["vbv"]
                result.reason = info["reason"]
                result.detection_method = "bin_database"
                result.confidence = 0.85
                
                if info["vbv"] is True:
                    result.vbv_status = "VBV_ENROLLED"
                elif info["vbv"] is False:
                    result.vbv_status = "NON_VBV"
                else:
                    result.vbv_status = "UNKNOWN"
                    result.confidence = 0.4
        
        # Method 2: Card Type Heuristic
        if result.vbv_status == "" and card_type:
            if card_type in VBV_BY_TYPE:
                result.is_vbv = VBV_BY_TYPE[card_type]
                result.detection_method = "card_type_heuristic"
                result.confidence = 0.6
                
                if card_type == "debit":
                    result.reason = "Débito — generalmente NON-VBV"
                    result.vbv_status = "NON_VBV"
                elif card_type == "prepaid":
                    result.reason = "Prepago — generalmente NON-VBV"
                    result.vbv_status = "NON_VBV"
                elif card_type == "credit":
                    result.reason = "Crédito — generalmente VBV"
                    result.vbv_status = "VBV_ENROLLED"
        
        # Method 3: Network Defaults
        if result.vbv_status == "" and network:
            if network in ["Visa", "Mastercard", "Amex", "Discover"]:
                result.is_vbv = True  # Default: assume VBV for major networks
                result.vbv_status = "VBV_ENROLLED"
                result.reason = f"{network} — 3D Secure disponible"
                result.vbv_provider = THREE_D_SECURE_PROVIDERS.get(network, "")
                result.detection_method = "network_default"
                result.confidence = 0.5
            elif network == "UnionPay":
                result.is_vbv = False
                result.vbv_status = "NON_VBV"
                result.reason = "UnionPay — 3D Secure no estándar"
                result.detection_method = "network_default"
                result.confidence = 0.5
        
        # Method 4: Unknown
        if result.vbv_status == "":
            result.vbv_status = "UNKNOWN"
            result.reason = "BIN no encontrado — estado VBV indeterminado"
            result.confidence = 0.3
        
        # Set provider
        if not result.vbv_provider and network:
            result.vbv_provider = THREE_D_SECURE_PROVIDERS.get(network, "")
        
        return result

    def detect_batch(self, cards: List[Dict]) -> BatchVBVResult:
        """
        Detecta VBV para múltiples tarjetas.
        Cada item es un dict con: card_number, network, card_type, issuing_bank
        """
        batch = BatchVBVResult(total=len(cards))
        
        for card in cards:
            r = self.detect(
                card_number=card.get("card_number", ""),
                network=card.get("network", ""),
                card_type=card.get("card_type", ""),
                issuing_bank=card.get("issuing_bank", ""),
            )
            batch.results.append(r)
            
            if r.vbv_status == "VBV_ENROLLED":
                batch.vbv_enrolled += 1
            elif r.vbv_status == "NON_VBV":
                batch.non_vbv += 1
            else:
                batch.unknown += 1
        
        return batch

    def filter_non_vbv(self, cards: List[Dict]) -> List[Dict]:
        """
        Filtra tarjetas para retornar solo NON-VBV.
        Útil para el Route & Account Finder y Card Extractor.
        """
        filtered = []
        for card in cards:
            r = self.detect(
                card_number=card.get("card_number", ""),
                network=card.get("network", ""),
                card_type=card.get("card_type", ""),
                issuing_bank=card.get("issuing_bank", ""),
            )
            if r.vbv_status == "NON_VBV":
                card["vbv_status"] = "NON_VBV"
                card["vbv_reason"] = r.reason
                filtered.append(card)
        
        return filtered

    @staticmethod
    def get_vbv_status_text(status: str) -> str:
        """Retorna texto descriptivo del estado VBV"""
        texts = {
            "VBV_ENROLLED": "🔒 VBV — Requiere 3D Secure",
            "NON_VBV": "🔓 NON-VBV — Sin 3D Secure",
            "UNKNOWN": "❓ Desconocido",
        }
        return texts.get(status, "❓ Desconocido")

    @staticmethod
    def get_vbv_color(status: str) -> str:
        """Retorna color para el estado VBV"""
        colors = {
            "VBV_ENROLLED": "#00c853",
            "NON_VBV": "#e94560",
            "UNKNOWN": "#ffd700",
        }
        return colors.get(status, "#888")
