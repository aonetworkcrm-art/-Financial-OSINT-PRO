"""
💳 Credit Card Extractor Engine
================================
Motor que EXTRA credit cards asociadas a cualquier campo:
email, phone, SSN, address, name, username, domain.

Cruza múltiples fuentes de brechas para encontrar TODAS las
tarjetas vinculadas a una identidad o dirección.

Combina:
- LeakCheck Pro (brechas con datos de tarjetas)
- DeHashed (campos adicionales)
- IntelligenceX (dark web)
- Snusbase (stealer logs con tokens/tarjetas)
- BIN Lookup automático para cada tarjeta encontrada
"""
import re
import csv
import io
import json
import logging
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger("card_extractor")


# ═══════════════════════════════════════════════════════════════
# BIN DATABASE (compartida con card_analyzer)
# ═══════════════════════════════════════════════════════════════

BIN_DB = {
    "400005": {"bank": "Visa Débito Genérica", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "401288": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa", "level": "Classic"},
    "411111": {"bank": "Visa Test", "type": "credit", "country": "US", "network": "Visa", "level": "Classic"},
    "453201": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa", "level": "Gold"},
    "491100": {"bank": "Visa Genérica", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "400555": {"bank": "Wells Fargo", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "402340": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "402360": {"bank": "Bank of America", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "405528": {"bank": "Chase", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "405530": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "410000": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa", "level": "Infinite"},
    "414720": {"bank": "Chase", "type": "credit", "country": "US", "network": "Visa", "level": "Sapphire"},
    "432000": {"bank": "US Bank", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "432004": {"bank": "US Bank", "type": "credit", "country": "US", "network": "Visa", "level": "Signature"},
    "440000": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "440200": {"bank": "Citibank", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "450000": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "450018": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Visa", "level": "Venture"},
    "407350": {"bank": "Alliant CU", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "404600": {"bank": "PenFed CU", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "440300": {"bank": "Navy Federal CU", "type": "credit", "country": "US", "network": "Visa", "level": "Platinum"},
    "450100": {"bank": "Schools Federal CU", "type": "debit", "country": "US", "network": "Visa", "level": "Classic"},
    "510000": {"bank": "Mastercard Genérica", "type": "credit", "country": "US", "network": "Mastercard", "level": "Standard"},
    "520000": {"bank": "Mastercard Débito", "type": "debit", "country": "US", "network": "Mastercard", "level": "Debit"},
    "540000": {"bank": "Mastercard Genérica", "type": "credit", "country": "US", "network": "Mastercard", "level": "Gold"},
    "510510": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "522200": {"bank": "Chase", "type": "credit", "country": "US", "network": "Mastercard", "level": "World Elite"},
    "540400": {"bank": "Bank of America", "type": "credit", "country": "US", "network": "Mastercard", "level": "Platinum"},
    "541000": {"bank": "Capital One", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "542400": {"bank": "Citibank", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "546600": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Mastercard", "level": "World"},
    "549000": {"bank": "Wells Fargo", "type": "credit", "country": "US", "network": "Mastercard", "level": "World Elite"},
    "520473": {"bank": "Cash App (Square)", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "530201": {"bank": "Venmo (PayPal)", "type": "debit", "country": "US", "network": "Mastercard", "level": "Prepaid"},
    "340000": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Gold"},
    "370000": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Platinum"},
    "371449": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Centurion"},
    "378282": {"bank": "American Express", "type": "credit", "country": "US", "network": "Amex", "level": "Gold"},
    "601100": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Standard"},
    "601101": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Standard"},
    "650000": {"bank": "Discover", "type": "credit", "country": "US", "network": "Discover", "level": "Standard"},
    "350000": {"bank": "JCB", "type": "credit", "country": "JP", "network": "JCB", "level": "Standard"},
    "300000": {"bank": "Diners Club", "type": "credit", "country": "US", "network": "Diners", "level": "Classic"},
    "620000": {"bank": "UnionPay", "type": "credit", "country": "CN", "network": "UnionPay", "level": "Standard"},
}

COUNTRY_NAMES = {
    "US": "Estados Unidos", "MX": "México", "CA": "Canadá", "GB": "Reino Unido",
    "DE": "Alemania", "FR": "Francia", "ES": "España", "IT": "Italia",
    "JP": "Japón", "CN": "China", "KR": "Corea del Sur", "BR": "Brasil",
    "AR": "Argentina", "CO": "Colombia", "CL": "Chile", "PE": "Perú",
}


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class SearchField:
    field_type: str
    value: str
    label: str = ""

    def __post_init__(self):
        if not self.label:
            self.label = f"{self.field_type}: {self.value[:30]}..."


@dataclass
class ExtractedCard:
    """Una tarjeta encontrada en brechas"""
    card_number: str = ""
    card_masked: str = ""

    # BIN Analysis
    network: str = ""
    network_icon: str = ""
    issuing_bank: str = ""
    bank_country: str = ""
    bank_country_name: str = ""
    card_type: str = ""        # credit/debit/prepaid
    card_level: str = ""       # Classic/Gold/Platinum/Signature

    # VBV / 3D Secure
    is_vbv: Optional[bool] = None
    vbv_status: str = ""       # VBV_ENROLLED, NON_VBV, UNKNOWN
    vbv_provider: str = ""     # Verified by Visa, SecureCode, etc.
    vbv_reason: str = ""

    # Luhn
    is_valid_luhn: bool = False

    # Associated data
    associated_email: str = ""
    associated_phone: str = ""
    associated_name: str = ""
    associated_address: str = ""
    associated_ssn: str = ""

    # Breach info
    breach_source: str = ""
    breach_date: str = ""
    exposure_level: str = ""   # full, partial, masked

    # Confidence
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CardSearchResult:
    """Resultado de búsqueda de tarjetas para un campo"""
    input_field: str = ""
    input_value: str = ""

    cards_found: List[ExtractedCard] = field(default_factory=list)

    # Associated identity data
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    ssns: List[str] = field(default_factory=list)

    # Breach info
    breach_sources: List[str] = field(default_factory=list)

    # Meta
    sources_checked: List[str] = field(default_factory=list)
    search_time_ms: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def total_cards(self) -> int:
        return len(self.cards_found)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BatchCardSearch:
    """Resultado de búsqueda en lote"""
    results: List[CardSearchResult] = field(default_factory=list)
    total_queries: int = 0
    total_cards: int = 0
    unique_cards: int = 0
    total_time_ms: int = 0
    timestamp: str = ""

    # Summary stats
    networks: Dict[str, int] = field(default_factory=dict)
    banks: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# CARD EXTRACTOR ENGINE
# ═══════════════════════════════════════════════════════════════

class CardExtractor:
    """
    Motor de extracción de credit cards desde brechas de datos.

    Dado un campo (email, phone, SSN, address, name), busca en
    múltiples fuentes de brechas TODAS las tarjetas de crédito/débito
    asociadas a esa identidad.

    Cada tarjeta encontrada es analizada con BIN lookup para
    identificar banco emisor, red, tipo y nivel.
    """

    def __init__(self, leakcheck_key=None, dehashed_key=None, intelx_key=None):
        self.leakcheck_key = leakcheck_key or ""
        self.dehashed_key = dehashed_key or ""
        self.intelx_key = intelx_key or ""

    # ═══════════════════════════════════════════════════════════════
    # SINGLE SEARCH
    # ═══════════════════════════════════════════════════════════════

    def search_single(self, field: SearchField) -> CardSearchResult:
        """Busca tarjetas para un solo campo"""
        start = datetime.now()

        result = CardSearchResult(
            input_field=field.field_type,
            input_value=field.value,
        )

        try:
            # 1. Search LeakCheck
            self._search_leakcheck(field, result)

            # 2. Search DeHashed (if key available)
            if self.dehashed_key:
                self._search_dehashed(field, result)

            # 3. Search IntelligenceX (if key available)
            if self.intelx_key:
                self._search_intelx(field, result)

            # 4. Analyze each card with BIN lookup
            for card in result.cards_found:
                self._analyze_card(card)

        except Exception as e:
            logger.error(f"Error in card search: {e}")

        elapsed = (datetime.now() - start).total_seconds() * 1000
        result.search_time_ms = int(elapsed)

        return result

    def _search_leakcheck(self, field: SearchField, result: CardSearchResult):
        """Busca tarjetas en LeakCheck"""
        if not self.leakcheck_key:
            return

        try:
            result.sources_checked.append("LeakCheck Pro")

            # Build query based on field type
            query = field.value
            query_type = field.field_type
            if query_type == "auto":
                query_type = self._detect_type(query)

            # Make API request
            url = "https://leakcheck.io/api/public"
            params = {"key": self.leakcheck_key, "query": query, "type": query_type}

            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()

            if data.get("success") and data.get("result"):
                for record in data["result"]:
                    # Extract credit card if present
                    cc = record.get("credit_card", "") or record.get("cc_number", "")
                    if cc and len(re.sub(r'[^0-9]', '', cc)) >= 13:
                        card = ExtractedCard(
                            card_number=re.sub(r'[^0-9]', '', cc),
                            breach_source=record.get("breach", "LeakCheck"),
                            breach_date=record.get("date", ""),
                            exposure_level="full" if len(re.sub(r'[^0-9]', '', cc)) >= 15 else "partial",
                        )
                        # Associate identity data
                        if record.get("email"):
                            card.associated_email = record["email"]
                            if record["email"] not in result.emails:
                                result.emails.append(record["email"])
                        if record.get("phone"):
                            card.associated_phone = record["phone"]
                            if record["phone"] not in result.phones:
                                result.phones.append(record["phone"])
                        if record.get("first_name") or record.get("last_name"):
                            name = f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
                            card.associated_name = name
                            if name not in result.names:
                                result.names.append(name)
                        if record.get("address"):
                            card.associated_address = record["address"]
                            if record["address"] not in result.addresses:
                                result.addresses.append(record["address"])
                        if record.get("ssn"):
                            card.associated_ssn = record["ssn"]
                            if record["ssn"] not in result.ssns:
                                result.ssns.append(record["ssn"])
                        if record.get("breach") and record["breach"] not in result.breach_sources:
                            result.breach_sources.append(record["breach"])

                        result.cards_found.append(card)

        except Exception as e:
            logger.warning(f"LeakCheck card search error: {e}")

    def _search_dehashed(self, field: SearchField, result: CardSearchResult):
        """Busca tarjetas en DeHashed"""
        try:
            result.sources_checked.append("DeHashed")

            url = "https://api.dehashed.com/search"
            headers = {"Authorization": f"Bearer {self.dehashed_key}"}
            params = {"query": field.value}

            resp = requests.get(url, headers=headers, params=params, timeout=30)
            data = resp.json()

            for record in data.get("entries", []):
                cc = record.get("credit_card", "") or record.get("cc_number", "")
                if cc and len(re.sub(r'[^0-9]', '', cc)) >= 13:
                    card = ExtractedCard(
                        card_number=re.sub(r'[^0-9]', '', cc),
                        breach_source=record.get("database_name", "DeHashed"),
                        breach_date=record.get("pwned_date", ""),
                        exposure_level="full",
                    )
                    if record.get("email_address"):
                        card.associated_email = record["email_address"]
                        if record["email_address"] not in result.emails:
                            result.emails.append(record["email_address"])
                    if record.get("phone_number"):
                        card.associated_phone = record["phone_number"]
                        if record["phone_number"] not in result.phones:
                            result.phones.append(record["phone_number"])
                    if record.get("name"):
                        card.associated_name = record["name"]
                        if record["name"] not in result.names:
                            result.names.append(record["name"])
                    if record.get("password") or record.get("hashed_password"):
                        pass  # Track passwords if needed
                    if record.get("database_name") and record["database_name"] not in result.breach_sources:
                        result.breach_sources.append(record["database_name"])

                    result.cards_found.append(card)

        except Exception as e:
            logger.warning(f"DeHashed card search error: {e}")

    def _search_intelx(self, field: SearchField, result: CardSearchResult):
        """Busca tarjetas en IntelligenceX"""
        try:
            result.sources_checked.append("IntelligenceX")

            url = f"https://2.intelx.io/intelligent/search"
            headers = {"x-api-key": self.intelx_key}
            params = {"term": field.value, "buckets": []}

            resp = requests.post(url, json=params, headers=headers, timeout=30)
            data = resp.json()

            search_id = data.get("id")
            if search_id:
                # Poll for results
                import time
                for _ in range(5):
                    time.sleep(2)
                    results_resp = requests.get(
                        f"https://2.intelx.io/intelligent/search/result?id={search_id}",
                        headers=headers,
                        timeout=30,
                    )
                    results_data = results_resp.json()

                    for record in results_data.get("records", []):
                        # IntelX may contain card data in selector or content
                        content = record.get("selector", "") + " " + record.get("data", "")
                        # Extract card numbers from content
                        cards_found = re.findall(r'\b[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b', content)
                        for cc in cards_found:
                            clean = re.sub(r'[^0-9]', '', cc)
                            if len(clean) >= 13 and self._luhn(clean):
                                card = ExtractedCard(
                                    card_number=clean,
                                    breach_source=record.get("name", "IntelligenceX"),
                                    breach_date=record.get("date", ""),
                                    exposure_level="partial",
                                )
                                result.cards_found.append(card)

                    if results_data.get("status") == 2:  # Done
                        break

        except Exception as e:
            logger.warning(f"IntelligenceX card search error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # BATCH SEARCH
    # ═══════════════════════════════════════════════════════════════

    def search_batch(self, fields: List[SearchField], max_workers: int = 5,
                     on_progress=None) -> BatchCardSearch:
        """Busca tarjetas para múltiples campos en paralelo"""
        start = datetime.now()
        batch = BatchCardSearch(total_queries=len(fields))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.search_single, f): f
                for f in fields
            }

            completed = 0
            for future in as_completed(futures):
                completed += 1
                try:
                    result = future.result()
                    batch.results.append(result)
                    batch.total_cards += result.total_cards()

                    for card in result.cards_found:
                        net = card.network or "Unknown"
                        batch.networks[net] = batch.networks.get(net, 0) + 1
                        bank = card.issuing_bank or "Unknown"
                        batch.banks[bank] = batch.banks.get(bank, 0) + 1

                except Exception as e:
                    logger.error(f"Batch error: {e}")

                if on_progress:
                    on_progress(completed, len(fields))

        # Calculate unique cards
        all_cards = set()
        for r in batch.results:
            for c in r.cards_found:
                all_cards.add(c.card_number)
        batch.unique_cards = len(all_cards)

        elapsed = (datetime.now() - start).total_seconds() * 1000
        batch.total_time_ms = int(elapsed)

        return batch

    # ═══════════════════════════════════════════════════════════════
    # CARD ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    def _analyze_card(self, card: ExtractedCard):
        """Analiza una tarjeta encontrada con BIN lookup"""
        clean = card.card_number

        # Mask
        if len(clean) >= 8:
            card.card_masked = f"{clean[:4]}{'*' * (len(clean)-8)}{clean[-4:]}"
        elif len(clean) >= 4:
            card.card_masked = f"{'*' * (len(clean)-4)}{clean[-4:]}"
        else:
            card.card_masked = clean

        # Network detection
        card.network = self._detect_network(clean)
        card.network_icon = self._network_icon(card.network)

        # BIN lookup - Enhanced database first
        if len(clean) >= 6:
            bin6 = clean[:6]
            
            # Try enhanced database first (410+ BINs)
            try:
                from engines.enhanced_bins import get_enhanced_bin, ENHANCED_COUNTRIES
                enhanced = get_enhanced_bin(bin6)
                if enhanced:
                    card.issuing_bank = enhanced.get("bank", "")
                    card.card_type = enhanced.get("type", "")
                    card.card_level = enhanced.get("level", "")
                    card.bank_country = enhanced.get("country", "")
                    card.bank_country_name = ENHANCED_COUNTRIES.get(card.bank_country, card.bank_country)
                    card.confidence = 0.95
            except ImportError:
                pass
            
            # Fallback to local BIN_DB
            if not card.issuing_bank and bin6 in BIN_DB:
                info = BIN_DB[bin6]
                card.issuing_bank = info["bank"]
                card.card_type = info["type"]
                card.card_level = info["level"]
                card.bank_country = info["country"]
                card.bank_country_name = COUNTRY_NAMES.get(info["country"], info["country"])
                card.confidence = 0.95
            
            if not card.issuing_bank:
                card.confidence = 0.6

        # Luhn
        card.is_valid_luhn = self._luhn(clean)

        # VBV Detection
        try:
            from engines.vbv_engine import VBVEngine
            vbv = VBVEngine()
            vbv_result = vbv.detect(
                card_number=clean,
                network=card.network,
                card_type=card.card_type,
                issuing_bank=card.issuing_bank,
            )
            card.is_vbv = vbv_result.is_vbv
            card.vbv_status = vbv_result.vbv_status
            card.vbv_provider = vbv_result.vbv_provider
            card.vbv_reason = vbv_result.reason
        except ImportError:
            pass

    def _detect_network(self, card: str) -> str:
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
            if card.startswith("62"):
                return "UnionPay"
            return "Discover"
        return ""

    def _network_icon(self, network: str) -> str:
        return {"Visa": "🟦", "Mastercard": "🟧", "Amex": "🟩",
                "Discover": "🟫", "Diners": "🟥", "JCB": "🟨", "UnionPay": "🟪"}.get(network, "💳")

    def _luhn(self, card: str) -> bool:
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
    def _detect_type(value: str) -> str:
        v = value.strip()
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            return "email"
        clean = re.sub(r'[^0-9]', '', v)
        if len(clean) == 9 and clean.isdigit():
            return "ssn"
        if re.match(r'^[\+]?[0-9\-\(\)\s]{7,15}$', v):
            return "phone"
        if re.search(r'\d{1,5}\s+\w+', v) and re.search(r'[A-Za-z]{3,}', v):
            return "address"
        return "name"

    # ═══════════════════════════════════════════════════════════════
    # INPUT PARSING
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def parse_batch_input(text: str) -> List[SearchField]:
        """Parsea input de texto y detecta tipos"""
        fields = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            ft = CardExtractor._detect_type(line)
            fields.append(SearchField(field_type=ft, value=line))
        return fields

    @staticmethod
    def parse_csv(file_content: str) -> List[SearchField]:
        """Parsea CSV con columnas relevantes"""
        fields = []
        reader = csv.DictReader(io.StringIO(file_content))
        for row in reader:
            for key, val in row.items():
                if not val or not str(val).strip():
                    continue
                key_lower = key.lower().strip()
                val = str(val).strip()
                if any(x in key_lower for x in ["email", "mail", "correo"]):
                    fields.append(SearchField(field_type="email", value=val))
                elif any(x in key_lower for x in ["phone", "tel", "telefono", "mobile"]):
                    fields.append(SearchField(field_type="phone", value=val))
                elif any(x in key_lower for x in ["ssn", "social", "security"]):
                    fields.append(SearchField(field_type="ssn", value=re.sub(r'[^0-9]', '', val)))
                elif any(x in key_lower for x in ["address", "direccion", "street"]):
                    fields.append(SearchField(field_type="address", value=val))
                elif any(x in key_lower for x in ["name", "nombre", "first"]):
                    fields.append(SearchField(field_type="name", value=val))
        return fields

    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def export_csv(batch: BatchCardSearch) -> str:
        output = io.StringIO()
        headers = [
            "query_type", "query", "card_masked", "network", "issuing_bank",
            "card_type", "card_level", "country", "luhn_valid",
            "associated_email", "associated_phone", "associated_name",
            "associated_ssn", "breach_source", "confidence", "time_ms"
        ]
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in batch.results:
            for c in r.cards_found:
                writer.writerow([
                    r.input_field, r.input_value, c.card_masked, c.network,
                    c.issuing_bank, c.card_type, c.card_level, c.bank_country_name,
                    c.is_valid_luhn, c.associated_email, c.associated_phone,
                    c.associated_name, c.associated_ssn, c.breach_source,
                    f"{c.confidence:.0%}", r.search_time_ms,
                ])
        return output.getvalue()

    @staticmethod
    def export_json(batch: BatchCardSearch) -> str:
        return json.dumps(batch.to_dict(), indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def export_txt(batch: BatchCardSearch) -> str:
        lines = []
        lines.append("=" * 80)
        lines.append("  CREDIT CARD EXTRACTOR — RESULTADOS")
        lines.append(f"  Total consultas: {batch.total_queries}")
        lines.append(f"  Total tarjetas: {batch.total_cards}")
        lines.append(f"  Tarjetas únicas: {batch.unique_cards}")
        lines.append(f"  Tiempo total: {batch.total_time_ms}ms")
        lines.append("=" * 80)

        if batch.networks:
            lines.append("\n  📡 REDES:")
            for net, cnt in sorted(batch.networks.items(), key=lambda x: -x[1]):
                lines.append(f"     {net}: {cnt} tarjetas")

        if batch.banks:
            lines.append("\n  🏦 BANCOS EMISORES:")
            for bank, cnt in sorted(batch.banks.items(), key=lambda x: -x[1]):
                lines.append(f"     {bank}: {cnt} tarjetas")

        for i, r in enumerate(batch.results, 1):
            lines.append(f"\n{'#' * 80}")
            lines.append(f"  CONSULTA #{i} — {r.input_field.upper()}")
            lines.append(f"{'#' * 80}")
            lines.append(f"  Input: {r.input_value}")
            lines.append(f"  Tarjetas encontradas: {r.total_cards()}")

            if r.cards_found:
                lines.append(f"\n  💳 TARJETAS:")
                for c in r.cards_found:
                    lines.append(f"     {c.card_masked} | {c.network} | {c.issuing_bank} ({c.card_level}) | {c.bank_country_name}")
                    if c.associated_email:
                        lines.append(f"       Email: {c.associated_email}")
                    if c.associated_name:
                        lines.append(f"       Nombre: {c.associated_name}")
                    lines.append(f"       Brecha: {c.breach_source} | Luhn: {'✅' if c.is_valid_luhn else '❌'}")

            if r.emails:
                lines.append(f"\n  📧 EMAILS: {', '.join(r.emails[:5])}")
            if r.phones:
                lines.append(f"\n  📱 TELÉFONOS: {', '.join(r.phones[:5])}")
            if r.names:
                lines.append(f"\n  👤 NOMBRES: {', '.join(r.names[:5])}")
            if r.ssns:
                lines.append(f"\n  🔑 SSNs: {', '.join(r.ssns[:3])}")

            lines.append(f"\n  Fuentes: {', '.join(r.sources_checked)}")
            lines.append(f"  Tiempo: {r.search_time_ms}ms")
            lines.append(f"\n{'-' * 80}")

        return "\n".join(lines)
