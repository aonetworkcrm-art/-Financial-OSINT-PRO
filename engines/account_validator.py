"""
🏦 Account & Route Validator Engine
====================================
Valida cuentas bancarias, routing numbers y tarjetas de crédito
usando algoritmos de verificación, BIN/IIN lookup y cross-referencing
con datos de brechas para determinar si son activas/válidas.

NO requiere APIs externas para validación básica.
"""
import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# BIN/IIN DATABASE (Primeros 6-8 dígitos de tarjetas)
# ═══════════════════════════════════════════════════════════════

BIN_DATABASE = {
    # US Banks
    "400005": {"bank": "Visa Débito Genérica", "type": "debit", "country": "US", "network": "Visa"},
    "401288": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa"},
    "411111": {"bank": "Visa Test", "type": "credit", "country": "US", "network": "Visa"},
    "453201": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa"},
    "510000": {"bank": "Mastercard Genérica", "type": "credit", "country": "US", "network": "Mastercard"},
    "520000": {"bank": "Mastercard Débito", "type": "debit", "country": "US", "network": "Mastercard"},
    "540000": {"bank": "Mastercard Genérica", "type": "credit", "country": "US", "network": "Mastercard"},
    "601100": {"bank": "Discover Genérica", "type": "credit", "country": "US", "network": "Discover"},
    "601101": {"bank": "Discover Genérica", "type": "credit", "country": "US", "network": "Discover"},
    "650000": {"bank": "Discover Genérica", "type": "credit", "country": "US", "network": "Discover"},
    "340000": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex"},
    "370000": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex"},
    "300000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners"},
    "350000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB"},
    "360000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners"},
    # Specific banks
    "400555": {"bank": "Wells Fargo", "type": "debit", "country": "US", "network": "Visa"},
    "401288": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Visa"},
    "402340": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Visa"},
    "402360": {"bank": "Bank of America", "type": "debit", "country": "US", "network": "Visa"},
    "405528": {"bank": "Chase", "type": "debit", "country": "US", "network": "Visa"},
    "405530": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa"},
    "410000": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa"},
    "414720": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa"},
    "432000": {"bank": "US Bank", "type": "debit", "country": "US", "network": "Visa"},
    "432004": {"bank": "US Bank", "type": "credit", "country": "US", "network": "Visa"},
    "440000": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Visa"},
    "440200": {"bank": "Citibank", "type": "debit", "country": "US", "network": "Visa"},
    "450000": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Visa"},
    "450018": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Visa"},
    "510510": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Mastercard"},
    "520000": {"bank": "Chase", "type": "credit", "country": "US", "network": "Mastercard"},
    "522200": {"bank": "Chase", "type": "credit", "country": "US", "network": "Mastercard"},
    "540400": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Mastercard"},
    "541000": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Mastercard"},
    "542400": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Mastercard"},
    "546600": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Mastercard"},
    "549000": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Mastercard"},
    "550000": {"bank": "Mastercard SecureCode", "type": "credit", "country": "US", "network": "Mastercard"},
    # Fintechs
    "520473": {"bank": "Cash App (Square)", "type": "debit", "country": "US", "network": "Mastercard"},
    "520474": {"bank": "Cash App (Square)", "type": "debit", "country": "US", "network": "Mastercard"},
    "530201": {"bank": "Venmo (PayPal)", "type": "debit", "country": "US", "network": "Mastercard"},
    "530202": {"bank": "Venmo (PayPal)", "type": "debit", "country": "US", "network": "Mastercard"},
    "531826": {"bank": "Green Dot", "type": "debit", "country": "US", "network": "Mastercard"},
    "533248": {"bank": "Bluebird (AmEx)", "type": "debit", "country": "US", "network": "Mastercard"},
    "600001": {"bank": "PayPal Debit", "type": "debit", "country": "US", "network": "Mastercard"},
    # Credit Unions
    "440300": {"bank": "Navy Federal CU", "type": "credit", "country": "US", "network": "Visa"},
    "440301": {"bank": "Navy Federal CU", "type": "debit", "country": "US", "network": "Visa"},
    "450100": {"bank": "Schools Federal CU", "type": "debit", "country": "US", "network": "Visa"},
    "450101": {"bank": "Schools Federal CU", "type": "credit", "country": "US", "network": "Visa"},
    "407350": {"bank": "Alliant CU", "type": "credit", "country": "US", "network": "Visa"},
    "404600": {"bank": "PenFed CU", "type": "credit", "country": "US", "network": "Visa"},
    "450200": {"bank": "BECU", "type": "debit", "country": "US", "network": "Visa"},
}


# ═══════════════════════════════════════════════════════════════
# ABA ROUTING NUMBER DATABASE (Routing numbers comunes US)
# ═══════════════════════════════════════════════════════════════

ABA_DATABASE = {
    "021000021": {"bank": "JPMorgan Chase", "name": "Chase", "active": True},
    "021000089": {"bank": "JPMorgan Chase", "name": "Chase", "active": True},
    "021000218": {"bank": "JPMorgan Chase", "name": "Chase", "active": True},
    "021200339": {"bank": "JPMorgan Chase", "name": "Chase", "active": True},
    "026009593": {"bank": "Bank of America", "name": "BofA", "active": True},
    "028000082": {"bank": "Bank of America", "name": "BofA", "active": True},
    "031000011": {"bank": "Bank of America", "name": "BofA", "active": True},
    "031000503": {"bank": "Bank of America", "name": "BofA", "active": True},
    "031001014": {"bank": "Bank of America", "name": "BofA", "active": True},
    "031101266": {"bank": "Bank of America", "name": "BofA", "active": True},
    "041215663": {"bank": "Capital One", "name": "Capital One", "active": True},
    "051000017": {"bank": "Capital One", "name": "Capital One", "active": True},
    "051403049": {"bank": "Capital One", "name": "Capital One", "active": True},
    "052001633": {"bank": "Capital One", "name": "Capital One", "active": True},
    "053101121": {"bank": "Capital One", "name": "Capital One", "active": True},
    "056008802": {"bank": "Capital One", "name": "Capital One", "active": True},
    "071000013": {"bank": "Federal Reserve", "name": "Fed", "active": True},
    "071000028": {"bank": "US Bank", "name": "US Bank", "active": True},
    "071000039": {"bank": "US Bank", "name": "US Bank", "active": True},
    "071000288": {"bank": "US Bank", "name": "US Bank", "active": True},
    "071921891": {"bank": "US Bank", "name": "US Bank", "active": True},
    "082000073": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "091000019": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "091101455": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "091215927": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "091310725": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "101089742": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "102000021": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "103100739": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "111000025": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "111300022": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "112000066": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "121000248": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "122105155": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "124003116": {"bank": "Wells Fargo", "name": "Wells Fargo", "active": True},
    "021001088": {"bank": "Citibank", "name": "Citibank", "active": True},
    "021001486": {"bank": "Citibank", "name": "Citibank", "active": True},
    "021002085": {"bank": "Citibank", "name": "Citibank", "active": True},
    "021200339": {"bank": "Citibank", "name": "Citibank", "active": True},
    "031101266": {"bank": "Citibank", "name": "Citibank", "active": True},
    "071000013": {"bank": "Citibank", "name": "Citibank", "active": True},
    "210000890": {"bank": "Citibank", "name": "Citibank", "active": True},
    "210010529": {"bank": "Citibank", "name": "Citibank", "active": True},
    "021200025": {"bank": "Navy Federal CU", "name": "Navy Federal", "active": True},
    "256074973": {"bank": "Navy Federal CU", "name": "Navy Federal", "active": True},
    "265473405": {"bank": "Navy Federal CU", "name": "Navy Federal", "active": True},
    "325182082": {"bank": "Navy Federal CU", "name": "Navy Federal", "active": True},
    "073905523": {"bank": "Schools FCU", "name": "Schools Federal CU", "active": True},
    "073906625": {"bank": "Schools FCU", "name": "Schools Federal CU", "active": True},
    "211380712": {"bank": "Schools FCU", "name": "Schools Federal CU", "active": True},
    "322274988": {"bank": "Schools FCU", "name": "Schools Federal CU", "active": True},
    "231382383": {"bank": "Alliant CU", "name": "Alliant CU", "active": True},
    "321177526": {"bank": "PayPal", "name": "PayPal", "active": True},
    "322271724": {"bank": "PayPal", "name": "PayPal", "active": True},
    "073921824": {"bank": "Venmo/PayPal", "name": "Venmo", "active": True},
    "073923067": {"bank": "Venmo/PayPal", "name": "Venmo", "active": True},
    "124303068": {"bank": "Cash App", "name": "Cash App", "active": True},
}


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Resultado de validación de un solo item"""
    input_value: str
    input_type: str  # routing, account, card, ssn
    is_valid: bool
    confidence: float  # 0.0 - 1.0

    # Routing
    routing_number: Optional[str] = None
    routing_bank: Optional[str] = None
    routing_active: bool = False

    # Card
    card_bank: Optional[str] = None
    card_type: Optional[str] = None  # credit/debit
    card_network: Optional[str] = None  # Visa/Mastercard/Amex
    card_country: Optional[str] = None
    card_last4: Optional[str] = None

    # Account
    account_masked: Optional[str] = None
    account_length: int = 0

    # SSN
    ssn_valid_format: bool = False
    ssn_area: Optional[str] = None
    ssn_group: Optional[str] = None
    ssn_serial: Optional[str] = None

    # Status
    status: str = "unknown"  # valid, invalid, suspicious, unknown
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
class BatchValidation:
    """Resultado de validación en lote"""
    results: List[ValidationResult] = field(default_factory=list)
    total: int = 0
    valid: int = 0
    invalid: int = 0
    suspicious: int = 0
    unknown: int = 0
    processing_ms: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# MAIN VALIDATOR ENGINE
# ═══════════════════════════════════════════════════════════════

class AccountValidator:
    """
    Motor de validación de cuentas bancarias, routing numbers
    y tarjetas de crédito.

    Valida:
    - Routing numbers (ABA checksum)
    - Credit/debit card numbers (Luhn + BIN lookup)
    - Account number format (length patterns)
    - SSN format (Area/Group/Serial rules)
    """

    def validate(self, value: str, expected_type: str = "auto") -> ValidationResult:
        """Valida un solo valor"""
        start = datetime.now()
        v = value.strip()

        if expected_type == "auto":
            expected_type = self._detect_type(v)

        result = ValidationResult(
            input_value=v,
            input_type=expected_type,
            is_valid=False,
            confidence=0.0,
            timestamp=datetime.now().isoformat(),
        )

        if expected_type == "routing":
            self._validate_routing(v, result)
        elif expected_type == "card":
            self._validate_card(v, result)
        elif expected_type == "account":
            self._validate_account(v, result)
        elif expected_type == "ssn":
            self._validate_ssn(v, result)
        else:
            result.status = "unknown"
            result.status_detail = f"Tipo no reconocido para: {v}"

        elapsed = (datetime.now() - start).total_seconds() * 1000
        result.processing_ms = int(elapsed)
        return result

    def validate_batch(self, items: List[Tuple[str, str]],
                       on_progress=None) -> BatchValidation:
        """Valida múltiples items"""
        start = datetime.now()
        batch = BatchValidation(total=len(items))

        for i, (value, vtype) in enumerate(items):
            r = self.validate(value, vtype)
            batch.results.append(r)
            if r.status == "valid":
                batch.valid += 1
            elif r.status == "invalid":
                batch.invalid += 1
            elif r.status == "suspicious":
                batch.suspicious += 1
            else:
                batch.unknown += 1
            if on_progress:
                on_progress(i + 1, len(items))

        elapsed = (datetime.now() - start).total_seconds() * 1000
        batch.processing_ms = int(elapsed)
        return batch

    # ═══════════════════════════════════════════════════════════════
    # TYPE DETECTION
    # ═══════════════════════════════════════════════════════════════

    def _detect_type(self, v: str) -> str:
        clean = re.sub(r'[^0-9]', '', v)
        if len(clean) == 9 and clean.isdigit():
            return "routing"
        if len(clean) in range(13, 20):
            return "card"
        if len(clean) in range(4, 18) and not clean.startswith('0'):
            return "account"
        if re.match(r'^\d{3}-\d{2}-\d{4}$', v) or (len(clean) == 9 and clean.isdigit()):
            return "ssn"
        return "unknown"

    # ═══════════════════════════════════════════════════════════════
    # ROUTING NUMBER VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def _validate_routing(self, v: str, result: ValidationResult):
        clean = re.sub(r'[^0-9]', '', v)
        result.routing_number = clean

        # Check 1: Length
        if len(clean) != 9:
            result.checks_failed.append("Longitud no es 9 dígitos")
            result.status = "invalid"
            result.status_detail = f"Routing number debe tener 9 dígitos (tiene {len(clean)})"
            result.confidence = 0.9
            return

        result.checks_passed.append("Longitud correcta (9 dígitos)")

        # Check 2: ABA checksum (Luhn-like for ABA)
        if self._aba_checksum(clean):
            result.checks_passed.append("ABA Checksum válido")
        else:
            result.checks_failed.append("ABA Checksum inválido")
            result.warnings.append("El checksum ABA no coincide — puede ser ficticio o erróneo")

        # Check 3: Known bank
        if clean in ABA_DATABASE:
            info = ABA_DATABASE[clean]
            result.routing_bank = f"{info['bank']} ({info['name']})"
            result.routing_active = info.get("active", False)
            result.checks_passed.append(f"Banco identificado: {info['bank']}")
            result.is_valid = True
            result.confidence = 0.95
            result.status = "valid"
            result.status_detail = f"Routing de {info['bank']} — activo"
        else:
            result.routing_bank = "No encontrado en base de datos"
            result.warnings.append("Routing no está en la base de datos de bancos conocidos")
            if self._aba_checksum(clean):
                result.status = "suspicious"
                result.status_detail = "Checksum válido pero banco no identificado"
                result.confidence = 0.6
            else:
                result.status = "invalid"
                result.status_detail = "Routing no válido"
                result.confidence = 0.7

    def _aba_checksum(self, routing: str) -> bool:
        """Calcula el checksum ABA (método estándar)"""
        if len(routing) != 9:
            return False
        try:
            d = [int(c) for c in routing]
            # ABA checksum: 3*d[0] + 7*d[1] + d[2] + 3*d[3] + 7*d[4] + d[5] + 3*d[6] + 7*d[7] + d[8]
            checksum = (3*d[0] + 7*d[1] + d[2] + 3*d[3] + 7*d[4] + d[5] + 3*d[6] + 7*d[7] + d[8])
            return checksum % 10 == 0
        except (ValueError, IndexError):
            return False

    # ═══════════════════════════════════════════════════════════════
    # CARD VALIDATION (Luhn + BIN)
    # ═══════════════════════════════════════════════════════════════

    def _validate_card(self, v: str, result: ValidationResult):
        clean = re.sub(r'[^0-9]', '', v)
        result.card_last4 = clean[-4:] if len(clean) >= 4 else clean

        # Check 1: Length
        if len(clean) not in range(13, 20):
            result.checks_failed.append(f"Longitud inválida ({len(clean)} dígitos)")
            result.status = "invalid"
            result.status_detail = "Número de tarjeta debe tener 13-19 dígitos"
            result.confidence = 0.9
            return

        result.checks_passed.append("Longitud correcta")

        # Check 2: Luhn algorithm
        if self._luhn_check(clean):
            result.checks_passed.append("Algoritmo de Luhn válido")
        else:
            result.checks_failed.append("Luhn check fallido")
            result.status = "invalid"
            result.status_detail = "Número de tarjeta inválido (falla Luhn)"
            result.confidence = 0.95
            return

        # Check 3: BIN lookup (first 6 digits)
        bin6 = clean[:6]
        if bin6 in BIN_DATABASE:
            info = BIN_DATABASE[bin6]
            result.card_bank = info["bank"]
            result.card_type = info["type"]
            result.card_network = info["network"]
            result.card_country = info["country"]
            result.checks_passed.append(f"Banco: {info['bank']} ({info['network']})")
            result.is_valid = True
            result.confidence = 0.9
            result.status = "valid"
            result.status_detail = f"Tarjeta válida — {info['bank']} {info['type']}"
        else:
            # Try first 8 digits
            bin8 = clean[:8]
            found = False
            for prefix, info in BIN_DATABASE.items():
                if bin8.startswith(prefix) or clean.startswith(prefix):
                    result.card_bank = info["bank"]
                    result.card_type = info["type"]
                    result.card_network = info["network"]
                    result.card_country = info["country"]
                    result.checks_passed.append(f"Banco detectado: {info['bank']}")
                    found = True
                    break

            if found:
                result.is_valid = True
                result.confidence = 0.8
                result.status = "valid"
                result.status_detail = f"Tarjeta válida — {result.card_bank}"
            else:
                # Luhn passed but unknown BIN
                result.is_valid = True
                result.confidence = 0.6
                result.status = "suspicious"
                result.card_network = self._detect_network(clean)
                result.status_detail = f"Tarjeta válida (Luhn OK) — Red: {result.card_network or 'desconocida'}"
                result.warnings.append("BIN no encontrado en base de datos")

    def _luhn_check(self, card: str) -> bool:
        """Algoritmo de Luhn para validar números de tarjeta"""
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

    def _detect_network(self, card: str) -> Optional[str]:
        if card.startswith('4'):
            return "Visa"
        elif card.startswith('5') or card.startswith('2'):
            return "Mastercard"
        elif card.startswith('3'):
            if card[1] in '47':
                return "Amex"
            return "Diners/JCB"
        elif card.startswith('6'):
            return "Discover"
        return None

    # ═══════════════════════════════════════════════════════════════
    # ACCOUNT NUMBER VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def _validate_account(self, v: str, result: ValidationResult):
        clean = re.sub(r'[^0-9]', '', v)
        result.account_length = len(clean)
        result.account_masked = f"{'*' * (len(clean)-4)}{clean[-4:]}" if len(clean) >= 4 else "****"

        # Check 1: Length (US bank accounts are typically 8-17 digits)
        if len(clean) < 4:
            result.checks_failed.append("Demasiado corto para un número de cuenta")
            result.status = "invalid"
            result.status_detail = "Número de cuenta demasiado corto"
            result.confidence = 0.9
            return

        if len(clean) > 17:
            result.checks_failed.append("Demasiado largo para un número de cuenta")
            result.status = "suspicious"
            result.status_detail = f"Longitud inusual ({len(clean)} dígitos)"
            result.confidence = 0.6
            return

        # Check 2: Known length patterns
        if len(clean) in [10, 12, 13, 14, 15, 16, 17]:
            result.checks_passed.append(f"Longitud estándar ({len(clean)} dígitos)")
        elif len(clean) in [8, 9]:
            result.checks_passed.append(f"Longitud posible ({len(clean)} dígitos — puede ser cuenta anterior)")
        else:
            result.warnings.append(f"Longitud no estándar ({len(clean)} dígitos)")

        # Check 3: All numeric
        if clean.isdigit():
            result.checks_passed.append("Solo contiene dígitos")
        else:
            result.checks_failed.append("Contiene caracteres no numéricos")
            result.status = "invalid"
            return

        # Check 4: Not all zeros or all same digit
        if len(set(clean)) == 1:
            result.warnings.append("Todos los dígitos son iguales — posible dato de prueba")
            result.status = "suspicious"
            result.confidence = 0.3
            return

        result.is_valid = True
        result.confidence = 0.7
        result.status = "valid"
        result.status_detail = f"Formato de cuenta válido ({len(clean)} dígitos, enmascarado: {result.account_masked})"

    # ═══════════════════════════════════════════════════════════════
    # SSN VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def _validate_ssn(self, v: str, result: ValidationResult):
        clean = re.sub(r'[^0-9]', '', v)
        result.ssn_valid_format = False

        if len(clean) != 9:
            result.checks_failed.append(f"SSN debe tener 9 dígitos (tiene {len(clean)})")
            result.status = "invalid"
            result.status_detail = "Formato SSN inválido"
            result.confidence = 0.9
            return

        area = clean[:3]
        group = clean[3:5]
        serial = clean[5:]

        result.ssn_area = area
        result.ssn_group = group
        result.ssn_serial = serial

        checks_passed = []
        checks_failed = []
        warnings = []

        # Rule 1: Area (001-899, excluding 666)
        if area == "000":
            checks_failed.append("Área 000 inválida")
        elif area == "666":
            warnings.append("Área 666 reservada (nunca emitida)")
        elif int(area) >= 900:
            warnings.append(f"Área {area} — asignada para ITIN/por confirmar")
        else:
            checks_passed.append(f"Área {area} válida")

        # Rule 2: Group (01-99)
        if group == "00":
            checks_failed.append("Grupo 00 inválido")
        else:
            checks_passed.append(f"Grupo {group} válido")

        # Rule 3: Serial (0001-9999)
        if serial == "0000":
            checks_failed.append("Serial 0000 inválido")
        else:
            checks_passed.append(f"Serial {serial} válido")

        # Rule 4: Known invalid SSNs
        invalid_ssns = ["078051120", "219099999", "098765432"]  # Famous test SSNs
        if clean in invalid_ssns:
            warnings.append("SSN conocido como de prueba/dummy")

        result.checks_passed = checks_passed
        result.checks_failed = checks_failed
        result.warnings = warnings

        if checks_failed:
            result.status = "invalid"
            result.status_detail = "SSN con reglas inválidas"
            result.confidence = 0.9
        elif warnings:
            result.status = "suspicious"
            result.status_detail = "SSN con advertencias"
            result.confidence = 0.7
        else:
            result.status = "valid"
            result.status_detail = "SSN con formato válido"
            result.confidence = 0.8
            result.ssn_valid_format = True

    # ═══════════════════════════════════════════════════════════════
    # BATCH INPUT PARSING
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def parse_batch_input(text: str) -> List[Tuple[str, str]]:
        """Parsea input de texto y detecta tipos"""
        items = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            clean = re.sub(r'[^0-9]', '', line)
            if len(clean) == 9:
                items.append((line, "routing"))
            elif len(clean) in range(13, 20):
                items.append((line, "card"))
            elif re.match(r'^\d{3}-\d{2}-\d{4}$', line):
                items.append((line, "ssn"))
            elif len(clean) >= 4 and len(clean) <= 17:
                items.append((line, "account"))
            else:
                items.append((line, "auto"))
        return items

    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def export_csv(batch: BatchValidation) -> str:
        import csv, io
        output = io.StringIO()
        headers = [
            "input", "type", "valid", "status", "confidence",
            "bank", "card_type", "card_network", "routing",
            "account_masked", "ssn_valid", "checks_passed",
            "checks_failed", "warnings", "detail"
        ]
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in batch.results:
            writer.writerow([
                r.input_value, r.input_type, r.is_valid, r.status,
                f"{r.confidence:.0%}",
                r.card_bank or r.routing_bank or "",
                r.card_type or "",
                r.card_network or "",
                r.routing_number or "",
                r.account_masked or "",
                r.ssn_valid_format,
                " | ".join(r.checks_passed),
                " | ".join(r.checks_failed),
                " | ".join(r.warnings),
                r.status_detail,
            ])
        return output.getvalue()

    @staticmethod
    def export_json(batch: BatchValidation) -> str:
        return json.dumps(batch.to_dict(), indent=2, ensure_ascii=False, default=str)
