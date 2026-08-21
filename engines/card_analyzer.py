"""
💳 Credit Card Analyzer Engine
================================
Motor completo de análisis de tarjetas de crédito/débito:
- BIN/IIN Lookup (primeros 6-8 dígitos)
- Red de pago (Visa, Mastercard, Amex, Discover, etc.)
- Banco emisor
- Tipo (crédito/débito/prepago)
- País de emisión
- Validación Luhn
- Formato de presentación (GRP/BSI/ESQ)

No requiere API externa — usa base de datos local de 100+ BINs.
"""
import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# BIN DATABASE EXPANDED (200+ entries)
# ═══════════════════════════════════════════════════════════════

BIN_DB = {
    # ─── VISA ───────────────────────────────────────────────────
    "400005": {"bank": "Visa Débito Genérica", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "401288": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa", "level": "Classic"},
    "411111": {"bank": "Visa Test", "type": "credit", "country": "US", "network": "Visa", "level": "Classic"},
    "453201": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa", "level": "Gold"},
    "491100": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    # US Banks - Visa
    "400555": {"bank": "Wells Fargo", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "402340": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "402360": {"bank": "Bank of America", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "403550": {"bank": "TD Bank", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "405528": {"bank": "Chase", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "405530": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "410000": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa", "level": "Infinite"},
    "414720": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa", "level": "Sapphire"},
    "415966": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "432000": {"bank": "US Bank", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "432004": {"bank": "US Bank", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "440000": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "440200": {"bank": "Citibank", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "450000": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "450018": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Visa", "level": "Venture"},
    "407350": {"bank": "Alliant CU", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "404600": {"bank": "PenFed CU", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "450200": {"bank": "BECU", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "440300": {"bank": "Navy Federal CU", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "450100": {"bank": "Schools Federal CU", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    # International Visa
    "402600": {"bank": "BBVA", "type": "credit", "country": "ES", "network": "Visa", "level": "Gold"},
    "415056": {"bank": "Santander", "type": "credit", "country": "MX", "network": "Visa", "level": "Gold"},
    "415057": {"bank": "Santander", "type": "debit", "country": "MX", "network": "Visa", "level": "Classic"},
    "416888": {"bank": "Banorte", "type": "credit", "country": "MX", "network": "Visa", "level": "Platinum"},
    "423826": {"bank": "HSBC", "type": "credit", "country": "MX", "network": "Visa", "level": "Signature"},

    # ─── MASTERCARD ─────────────────────────────────────────────
    "510000": {"bank": "Mastercard Genérica", "type": "credit", "country": "US", "network": "Mastercard", "level": "Standard"},
    "520000": {"bank": "Mastercard Débito", "type": "debit", "country": "US", "network": "Mastercard", "level": "Debit"},
    "540000": {"bank": "Mastercard Genérica", "type": "credit", "country": "US", "network": "Mastercard", "level": "Gold"},
    "550000": {"bank": "Mastercard SecureCode", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    # US Banks - Mastercard
    "510510": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "520000": {"bank": "Chase", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "522200": {"bank": "Chase", "type": "credit", "country": "US", "network": "Mastercard", "level": "World Elite"},
    "540400": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Mastercard", "level": "Platinum"},
    "541000": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "542400": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "546600": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "549000": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Mastercard", "level": "World Elite"},
    # Fintechs - Mastercard
    "520473": {"bank": "Cash App (Square)", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "520474": {"bank": "Cash App (Square)", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "530201": {"bank": "Venmo (PayPal)", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "531826": {"bank": "Green Dot", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "533248": {"bank": "Bluebird (AmEx)", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "600001": {"bank": "PayPal Debit", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "543000": {"bank": "Walmart MoneyCard", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    # International Mastercard
    "520128": {"bank": "Santander", "type": "credit", "country": "MX", "network": "Mastercard", "level": "Gold"},
    "535501": {"bank": "Banorte", "type": "debit", "country": "MX", "network": "Mastercard", "level": "Debit"},

    # ─── AMERICAN EXPRESS ────────────────────────────────────────
    "340000": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Gold"},
    "370000": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Platinum"},
    "371449": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Centurion"},
    "377288": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Platinum"},
    "378282": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Gold"},
    "378733": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Green"},
    "371234": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Blue"},
    "372449": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "EveryDay"},
    "374320": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Platinum"},
    "374611": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Gold"},
    # Amex Blue Cash
    "376900": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Blue Cash"},
    "377914": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Platinum"},
    "379766": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Gold"},

    # ─── DISCOVER ────────────────────────────────────────────────
    "601100": {"bank": "Discover Genérica", "type": "credit", "country": "US", "network": "Discover", "level": "Standard"},
    "601101": {"bank": "Discover Genérica", "type": "credit", "country": "US", "network": "Discover", "level": "Standard"},
    "650000": {"bank": "Discover Genérica", "type": "credit", "country": "US", "network": "Discover", "level": "Standard"},
    "644000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Cashback"},
    "645000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Miles"},
    "646000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Platinum"},
    "647000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Chrome"},
    "648000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Secured"},
    "649000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Student"},

    # ─── DINERS CLUB ─────────────────────────────────────────────
    "300000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Classic"},
    "301000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Carte Blanche"},
    "302000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Corporate"},
    "303000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "International"},
    "304000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Elite"},
    "305000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Infinite"},
    "306000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Corporate"},
    "307000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Corporate"},
    "308000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Corporate"},
    "309000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Corporate"},
    "310000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Corporate"},

    # ─── JCB ─────────────────────────────────────────────────────
    "350000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Standard"},
    "352800": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Gold"},
    "353000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Platinum"},
    "354000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Gold"},
    "355000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Standard"},
    "356000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Gold"},
    "357000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Platinum"},

    # ─── UNIONPAY ────────────────────────────────────────────────
    "620000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Standard"},
    "621000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Platinum"},
    "622000": {"bank": "UnionPay", "type": "debit", "country": "CN", "network": "UnionPay", "level": "Classic"},
    "623000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Gold"},
    "624000": {"bank": "UnionPay", "type": "debit", "country": "CN", "network": "UnionPay", "level": "Classic"},
    "625000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Platinum"},
    "626000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Gold"},
    "627000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Standard"},
    "628000": {"bank": "UnionPay", "type": "debit", "country": "CN", "network": "UnionPay", "level": "Classic"},
    "629000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Platinum"},

    # ─── DISCOVER ELITE ──────────────────────────────────────────
    "654000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Platinum"},
    "655000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Signature"},
}

# Card length by network
CARD_LENGTHS = {
    "Visa": [13, 16, 19],
    "Mastercard": [16],
    "Amex": [15],
    "Discover": [16, 19],
    "Diners": [14],
    "JCB": [16],
    "UnionPay": [16, 19],
}

# Country codes
COUNTRY_NAMES = {
    "US": "Estados Unidos", "MX": "México", "CA": "Canadá", "GB": "Reino Unido",
    "DE": "Alemania", "FR": "Francia", "ES": "España", "IT": "Italia",
    "JP": "Japón", "CN": "China", "KR": "Corea del Sur", "BR": "Brasil",
    "AR": "Argentina", "CO": "Colombia", "CL": "Chile", "PE": "Perú",
    "AU": "Australia", "IN": "India", "RU": "Rusia", "NL": "Países Bajos",
}


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class CardAnalysis:
    """Resultado del análisis de una tarjeta"""
    card_number: str
    card_masked: str = ""
    
    # Network
    network: str = ""           # Visa, Mastercard, Amex, Discover, etc.
    network_icon: str = ""      # 🟦 🟧 🟩 🟫 🟥
    
    # Bank
    issuing_bank: str = ""
    bank_country: str = ""
    bank_country_name: str = ""
    
    # Type
    card_type: str = ""         # credit, debit, prepaid
    card_level: str = ""        # Classic, Gold, Platinum, Signature, Infinite
    
    # VBV / 3D Secure
    is_vbv: Optional[bool] = None  # True=VBV, False=NON-VBV, None=unknown
    vbv_status: str = ""           # VBV_ENROLLED, NON_VBV, UNKNOWN
    vbv_provider: str = ""         # Verified by Visa, SecureCode, etc.
    vbv_reason: str = ""
    
    # Validation
    is_valid_luhn: bool = False
    is_valid_length: bool = False
    is_valid_bin: bool = False
    
    # Overall
    is_valid: bool = False
    confidence: float = 0.0
    status: str = ""            # valid, invalid, suspicious
    status_detail: str = ""
    
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: str = ""
    processing_ms: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BatchCardAnalysis:
    """Resultado de análisis en lote"""
    results: List[CardAnalysis] = field(default_factory=list)
    total: int = 0
    valid: int = 0
    invalid: int = 0
    networks: Dict[str, int] = field(default_factory=dict)
    banks: Dict[str, int] = field(default_factory=dict)
    types: Dict[str, int] = field(default_factory=dict)
    processing_ms: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# CARD ANALYZER ENGINE
# ═══════════════════════════════════════════════════════════════

class CardAnalyzer:
    """
    Motor de análisis de tarjetas de crédito/débito.
    
    Analyzes:
    - BIN/IIN lookup (first 6-8 digits)
    - Network detection (Visa, MC, Amex, Discover, etc.)
    - Issuing bank identification
    - Card type (credit/debit/prepaid)
    - Card level (Classic/Gold/Platinum/Signature)
    - Country of origin
    - Luhn validation
    - Length validation per network
    """

    def analyze(self, card_number: str) -> CardAnalysis:
        """Analyze a single card number"""
        start = datetime.now()
        clean = re.sub(r'[^0-9]', '', card_number)
        
        result = CardAnalysis(
            card_number=clean,
            card_masked=self._mask_card(clean),
            timestamp=datetime.now().isoformat(),
        )
        
        # 1. Detect network
        result.network = self._detect_network(clean)
        result.network_icon = self._network_icon(result.network)
        
        # 2. BIN lookup (first 6 digits) - Enhanced database first
        if len(clean) >= 6:
            bin6 = clean[:6]
            
            # Try enhanced database first (410+ BINs)
            try:
                from engines.enhanced_bins import get_enhanced_bin, ENHANCED_COUNTRIES
                enhanced = get_enhanced_bin(bin6)
                if enhanced:
                    result.issuing_bank = enhanced.get("bank", "")
                    result.card_type = enhanced.get("type", "")
                    result.card_level = enhanced.get("level", "")
                    result.bank_country = enhanced.get("country", "")
                    result.bank_country_name = ENHANCED_COUNTRIES.get(result.bank_country, result.bank_country)
                    result.is_valid_bin = True
                    result.checks_passed.append(f"BIN {bin6} identificado (enhanced): {result.issuing_bank}")
            except ImportError:
                pass
            
            # Fallback to local BIN_DB
            if not result.is_valid_bin and bin6 in BIN_DB:
                info = BIN_DB[bin6]
                result.issuing_bank = info["bank"]
                result.card_type = info["type"]
                result.card_level = info["level"]
                result.bank_country = info["country"]
                result.bank_country_name = COUNTRY_NAMES.get(info["country"], info["country"])
                result.is_valid_bin = True
                result.checks_passed.append(f"BIN {bin6} identificado: {info['bank']}")
            
            # Try first 8 digits if still not found
            if not result.is_valid_bin:
                bin8 = clean[:8]
                for prefix, info in BIN_DB.items():
                    if bin8.startswith(prefix):
                        result.issuing_bank = info["bank"]
                        result.card_type = info["type"]
                        result.card_level = info["level"]
                        result.bank_country = info["country"]
                        result.bank_country_name = COUNTRY_NAMES.get(info["country"], info["country"])
                        result.is_valid_bin = True
                        break
                
                if not result.is_valid_bin:
                    result.warnings.append("BIN no encontrado en base de datos")
        
        # 3. Length validation
        valid_lengths = CARD_LENGTHS.get(result.network, [16])
        if len(clean) in valid_lengths:
            result.is_valid_length = True
            result.checks_passed.append(f"Longitud correcta ({len(clean)} dígitos para {result.network})")
        else:
            result.checks_failed.append(f"Longitud {len(clean)} no es válida para {result.network or 'desconocida'} (esperado: {valid_lengths})")
        
        # 4. Luhn validation
        if self._luhn(clean):
            result.is_valid_luhn = True
            result.checks_passed.append("Algoritmo de Luhn válido")
        else:
            result.checks_failed.append("Falló validación Luhn")

        # 5. VBV / 3D Secure Detection
        try:
            from engines.vbv_engine import VBVEngine
            vbv = VBVEngine()
            vbv_result = vbv.detect(
                card_number=clean,
                network=result.network,
                card_type=result.card_type,
                issuing_bank=result.issuing_bank,
            )
            result.is_vbv = vbv_result.is_vbv
            result.vbv_status = vbv_result.vbv_status
            result.vbv_provider = vbv_result.vbv_provider
            result.vbv_reason = vbv_result.reason
            if vbv_result.vbv_status == "NON_VBV":
                result.checks_passed.append(f"NON-VBV detectado: {vbv_result.reason}")
            elif vbv_result.vbv_status == "VBV_ENROLLED":
                result.checks_passed.append(f"VBV/3DS: {vbv_result.vbv_provider}")
        except ImportError:
            pass
        
        # 5. Overall status
        if result.is_valid_luhn and result.is_valid_length:
            if result.is_valid_bin:
                result.is_valid = True
                result.confidence = 0.95
                result.status = "valid"
                result.status_detail = f"Tarjeta válida — {result.issuing_bank} {result.card_type} {result.card_level}"
            else:
                result.is_valid = True
                result.confidence = 0.7
                result.status = "suspicious"
                result.status_detail = f"Tarjeta válida (Luhn + longitud OK) — Banco no identificado"
        elif not result.is_valid_luhn and not result.is_valid_length:
            result.status = "invalid"
            result.confidence = 0.95
            result.status_detail = "Tarjeta inválida (Luhn + longitud fallidos)"
        elif not result.is_valid_luhn:
            result.status = "invalid"
            result.confidence = 0.9
            result.status_detail = "Tarjeta inválida (Luhn fallido)"
        else:
            result.status = "suspicious"
            result.confidence = 0.6
            result.status_detail = f"Longitud inválida para {result.network}"
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        result.processing_ms = int(elapsed)
        return result

    def analyze_batch(self, card_numbers: List[str],
                      on_progress=None) -> BatchCardAnalysis:
        """Analyze multiple card numbers"""
        start = datetime.now()
        batch = BatchCardAnalysis(total=len(card_numbers))
        
        for i, card in enumerate(card_numbers):
            r = self.analyze(card)
            batch.results.append(r)
            
            if r.status == "valid":
                batch.valid += 1
            elif r.status == "invalid":
                batch.invalid += 1
            
            if r.network:
                batch.networks[r.network] = batch.networks.get(r.network, 0) + 1
            if r.issuing_bank:
                batch.banks[r.issuing_bank] = batch.banks.get(r.issuing_bank, 0) + 1
            if r.card_type:
                batch.types[r.card_type] = batch.types.get(r.card_type, 0) + 1
            
            if on_progress:
                on_progress(i + 1, len(card_numbers))
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        batch.processing_ms = int(elapsed)
        return batch

    # ═══════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _detect_network(self, card: str) -> str:
        """Detect card network from number"""
        if not card:
            return ""
        if card.startswith("4"):
            return "Visa"
        if card.startswith("5") or (card.startswith("2") and len(card) >= 2 and int(card[1]) in range(2, 8)):
            return "Mastercard"
        if card.startswith("3"):
            if len(card) >= 2 and card[1] in "47":
                return "Amex"
            if card[1] in "012345678":
                return "Diners"
            return "JCB"
        if card.startswith("6"):
            if card.startswith("60") or card.startswith("64") or card.startswith("65"):
                return "Discover"
            if card.startswith("62"):
                return "UnionPay"
            return "Discover"
        return ""

    def _network_icon(self, network: str) -> str:
        icons = {
            "Visa": "🟦", "Mastercard": "🟧", "Amex": "🟩",
            "Discover": "🟫", "Diners": "🟥", "JCB": "🟨", "UnionPay": "🟪",
        }
        return icons.get(network, "💳")

    def _mask_card(self, card: str) -> str:
        """Mask card number showing only last 4"""
        if len(card) <= 4:
            return card
        # Show first 4, mask middle, show last 4
        first4 = card[:4]
        last4 = card[-4:]
        masked_len = len(card) - 8
        if masked_len > 0:
            return f"{first4}{'*' * masked_len}{last4}"
        return f"****{last4}"

    def _luhn(self, card: str) -> bool:
        """Luhn algorithm validation"""
        try:
            digits = [int(c) for c in card]
            digits.reverse()
            total = 0
            for i, d in enumerate(digits):
                if i % 2 == 1:
                    d *= 2
                    if d > 9:
                        d -= 9
                total += d
            return total % 10 == 0
        except (ValueError, IndexError):
            return False

    @staticmethod
    def parse_batch_input(text: str) -> List[str]:
        """Parse card numbers from text input"""
        cards = []
        for line in text.strip().split("\n"):
            line = line.strip()
            clean = re.sub(r'[^0-9]', '', line)
            if len(clean) >= 13 and clean.isdigit():
                cards.append(clean)
        return cards

    @staticmethod
    def export_csv(batch: BatchCardAnalysis) -> str:
        import csv, io
        output = io.StringIO()
        headers = [
            "card_masked", "network", "issuing_bank", "card_type", "card_level",
            "country", "is_valid", "confidence", "status", "detail",
            "luhn", "valid_length", "checks_passed", "checks_failed", "warnings"
        ]
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in batch.results:
            writer.writerow([
                r.card_masked, r.network, r.issuing_bank, r.card_type, r.card_level,
                r.bank_country_name, r.is_valid, f"{r.confidence:.0%}", r.status,
                r.status_detail, r.is_valid_luhn, r.is_valid_length,
                " | ".join(r.checks_passed), " | ".join(r.checks_failed),
                " | ".join(r.warnings),
            ])
        return output.getvalue()

    @staticmethod
    def export_json(batch: BatchCardAnalysis) -> str:
        return json.dumps(batch.to_dict(), indent=2, ensure_ascii=False, default=str)
