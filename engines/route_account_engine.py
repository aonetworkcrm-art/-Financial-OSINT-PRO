"""
🗺️ Route & Account Finder Engine
==================================
Motor unificado para encontrar rutas, cuentas y datos financieros
a partir de CUALQUIER campo: email, phone, SSN, address, name, DOB.

Combina:
- LeakCheck Pro (brechas)
- XposedOrNot (brechas gratuitas)
- SSN Lookup (identidad bidireccional)
- Address Intelligence (direcciones)
- Institution Matcher (bancos)
- Credit Score (score crediticio)
- Clarity Automator (rutas y cuentas de reportes de crédito)
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

logger = logging.getLogger("route_account_engine")


@dataclass
class SearchField:
    """Campo de búsqueda individual"""
    field_type: str  # email, phone, ssn, address, name, dob, username, domain
    value: str
    label: str = ""

    def __post_init__(self):
        if not self.label:
            self.label = f"{self.field_type}: {self.value[:30]}..."


@dataclass
class RouteResult:
    """Resultado de búsqueda de ruta/cuenta"""
    input_field: str
    input_value: str
    
    # Datos encontrados
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    ssns: List[str] = field(default_factory=list)
    dobs: List[str] = field(default_factory=list)
    
    # Datos financieros
    banks: List[str] = field(default_factory=list)
    accounts: List[str] = field(default_factory=list)
    credit_cards: List[str] = field(default_factory=list)
    credit_score: Optional[int] = None
    credit_grade: Optional[str] = None
    
    # Datos de seguridad
    passwords: List[str] = field(default_factory=list)
    breach_sources: List[str] = field(default_factory=list)
    risk_score: int = 0
    
    # Instituciones detectadas
    institutions: List[Dict] = field(default_factory=list)
    
    # Meta
    sources_checked: List[str] = field(default_factory=list)
    search_time_ms: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def total_data(self) -> int:
        return (len(self.emails) + len(self.phones) + len(self.names) +
                len(self.addresses) + len(self.ssns) + len(self.banks) +
                len(self.accounts) + len(self.credit_cards) + len(self.passwords))

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BatchResult:
    """Resultado de búsqueda en lote"""
    results: List[RouteResult] = field(default_factory=list)
    total_queries: int = 0
    total_results: int = 0
    total_time_ms: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class RouteAccountEngine:
    """
    Motor de búsqueda unificado para rutas y cuentas.
    
    Acepta CUALQUIER campo como entrada y cruza múltiples fuentes
    para entregar el máximo de datos posible.
    """

    def __init__(self, leakcheck_key=None, dehashed_key=None, intelx_key=None):
        self.leakcheck_key = leakcheck_key
        self.dehashed_key = dehashed_key
        self.intelx_key = intelx_key
        
        # Import engines lazily
        self._leakcheck = None
        self._matcher = None
        self._credit = None
        self._ssn_lookup = None
        
    def _get_leakcheck(self):
        if self._leakcheck is None:
            from engines.leakcheck_engine import LeakCheckEngine
            self._leakcheck = LeakCheckEngine(api_key=self.leakcheck_key)
        return self._leakcheck

    def _get_matcher(self):
        if self._matcher is None:
            from engines.institution_matcher import InstitutionMatcher
            self._matcher = InstitutionMatcher()
        return self._matcher

    def _get_credit(self):
        if self._credit is None:
            from engines.credit_score_engine import CreditScoreEngine
            self._credit = CreditScoreEngine()
        return self._credit

    def _get_ssn_lookup(self):
        if self._ssn_lookup is None:
            from engines.ssn_lookup_engine import SSNLookupEngine
            self._ssn_lookup = SSNLookupEngine(leakcheck_key=self.leakcheck_key)
        return self._ssn_lookup

    # ═══════════════════════════════════════════════════════════════
    # SINGLE SEARCH
    # ═══════════════════════════════════════════════════════════════

    def search_single(self, field: SearchField) -> RouteResult:
        """Busca un solo campo y retorna resultados combinados"""
        start = datetime.now()
        
        result = RouteResult(
            input_field=field.field_type,
            input_value=field.value,
        )
        
        try:
            # 1. LeakCheck search
            self._search_leakcheck(field, result)
            
            # 2. SSN-specific search
            if field.field_type == "ssn":
                self._search_ssn(field, result)
            
            # 3. Address-specific search
            if field.field_type == "address":
                self._search_address(field, result)
            
            # 4. Institution matching
            self._match_institutions(field, result)
            
            # 5. Credit score estimation
            self._estimate_credit(result)
            
            # 6. Calculate risk score
            self._calculate_risk(result)
            
        except Exception as e:
            logger.error(f"Error searching {field.field_type}: {e}")
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        result.search_time_ms = int(elapsed)
        
        return result

    def _search_leakcheck(self, field: SearchField, result: RouteResult):
        """Busca en LeakCheck"""
        try:
            lc = self._get_leakcheck()
            records = lc.search(field.value, field.field_type)
            result.sources_checked.append("LeakCheck")
            
            for r in records:
                if r.email and r.email not in result.emails:
                    result.emails.append(r.email)
                if r.phone and r.phone not in result.phones:
                    result.phones.append(r.phone)
                if r.first_name:
                    name = f"{r.first_name} {r.last_name}".strip()
                    if name not in result.names:
                        result.names.append(name)
                if r.ssn and r.ssn not in result.ssns:
                    result.ssns.append(r.ssn)
                if r.dob and r.dob not in result.dobs:
                    result.dobs.append(r.dob)
                if r.password and r.password not in result.passwords:
                    result.passwords.append(r.password)
                if r.credit_card and r.credit_card not in result.credit_cards:
                    result.credit_cards.append(r.credit_card)
                if r.breach_name and r.breach_name not in result.breach_sources:
                    result.breach_sources.append(r.breach_name)
        except Exception as e:
            logger.warning(f"LeakCheck error: {e}")

    def _search_ssn(self, field: SearchField, result: RouteResult):
        """Búsqueda específica por SSN"""
        try:
            ssn_eng = self._get_ssn_lookup()
            identity = ssn_eng.reverse_lookup(ssn=field.value)
            result.sources_checked.append("SSN Lookup")
            
            if identity.name and identity.name not in result.names:
                result.names.append(identity.name)
            if identity.dob and identity.dob not in result.dobs:
                result.dobs.append(identity.dob)
            for email in identity.emails:
                if email not in result.emails:
                    result.emails.append(email)
            for phone in identity.phones:
                if phone not in result.phones:
                    result.phones.append(phone)
            for addr in identity.addresses:
                if addr not in result.addresses:
                    result.addresses.append(addr)
        except Exception as e:
            logger.warning(f"SSN Lookup error: {e}")

    def _search_address(self, field: SearchField, result: RouteResult):
        """Búsqueda específica por dirección"""
        try:
            from engines.address_engine import AddressEngine
            addr_eng = AddressEngine(leakcheck_key=self.leakcheck_key)
            profile = addr_eng.full_address_search(field.value)
            result.sources_checked.append("Address Engine")
            
            if profile:
                if profile.name and profile.name not in result.names:
                    result.names.append(profile.name)
                if profile.ssn and profile.ssn not in result.ssns:
                    result.ssns.append(profile.ssn)
                for email in profile.emails:
                    if email not in result.emails:
                        result.emails.append(email)
                for phone in profile.phones:
                    if phone not in result.phones:
                        result.phones.append(phone)
                for pw in profile.passwords:
                    if pw not in result.passwords:
                        result.passwords.append(pw)
                for cc in profile.credit_cards:
                    if cc not in result.credit_cards:
                        result.credit_cards.append(cc)
        except Exception as e:
            logger.warning(f"Address Engine error: {e}")

    def _match_institutions(self, field: SearchField, result: RouteResult):
        """Detecta instituciones financieras"""
        try:
            matcher = self._get_matcher()
            for email in result.emails:
                matches = matcher.match_email(email)
                for m in matches:
                    inst = {"name": m.institution, "type": m.institution_type, "evidence": m.evidence}
                    if inst not in result.institutions:
                        result.institutions.append(inst)
                        if m.institution not in result.banks:
                            result.banks.append(m.institution)
            
            for phone in result.phones:
                matches = matcher.match_phone(phone)
                for m in matches:
                    inst = {"name": m.institution, "type": m.institution_type, "evidence": m.evidence}
                    if inst not in result.institutions:
                        result.institutions.append(inst)
                        if m.institution not in result.banks:
                            result.banks.append(m.institution)
            
            for breach in result.breach_sources:
                matches = matcher.match_breach(breach)
                for m in matches:
                    inst = {"name": m.institution, "type": m.institution_type, "evidence": m.evidence}
                    if inst not in result.institutions:
                        result.institutions.append(inst)
                        if m.institution not in result.banks:
                            result.banks.append(m.institution)
        except Exception as e:
            logger.warning(f"Institution matching error: {e}")

    def _estimate_credit(self, result: RouteResult):
        """Estima credit score"""
        try:
            credit = self._get_credit()
            profile_data = {
                "institutions": [{"institution": i["name"]} for i in result.institutions],
                "accounts": result.credit_cards,
            }
            cs = credit.estimate_score_from_profile(profile_data)
            result.credit_score = cs.score
            result.credit_grade = cs.grade
        except Exception as e:
            logger.warning(f"Credit score error: {e}")

    def _calculate_risk(self, result: RouteResult):
        """Calcula risk score"""
        score = 0
        if result.ssns: score += 25
        if result.passwords: score += 20
        if result.credit_cards: score += 15
        if result.emails: score += min(len(result.emails) * 2, 10)
        if result.phones: score += min(len(result.phones) * 2, 10)
        if result.institutions: score += min(len(result.institutions) * 3, 15)
        if result.breach_sources: score += min(len(result.breach_sources) * 2, 10)
        result.risk_score = min(score, 100)

    # ═══════════════════════════════════════════════════════════════
    # BATCH SEARCH
    # ═══════════════════════════════════════════════════════════════

    def search_batch(self, fields: List[SearchField], max_workers: int = 5,
                     on_progress=None) -> BatchResult:
        """Busca múltiples campos en paralelo"""
        start = datetime.now()
        batch = BatchResult(total_queries=len(fields))
        
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
                    batch.total_results += result.total_data()
                except Exception as e:
                    logger.error(f"Batch error: {e}")
                
                if on_progress:
                    on_progress(completed, len(fields))
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        batch.total_time_ms = int(elapsed)
        
        return batch

    # ═══════════════════════════════════════════════════════════════
    # CSV/EXCEL PARSING
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def parse_batch_input(text: str) -> List[SearchField]:
        """
        Parsea input de texto (una entrada por línea) en SearchFields.
        Detecta automáticamente el tipo de campo.
        """
        fields = []
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        
        for line in lines:
            ft = RouteAccountEngine._detect_field_type(line)
            fields.append(SearchField(field_type=ft, value=line))
        
        return fields

    @staticmethod
    def parse_csv(file_content: str) -> List[SearchField]:
        """Parsea CSV con múltiples columnas"""
        fields = []
        reader = csv.DictReader(io.StringIO(file_content))
        
        for row in reader:
            # Buscar cada columna relevante
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
                elif any(x in key_lower for x in ["address", "direccion", "street", "street"]):
                    fields.append(SearchField(field_type="address", value=val))
                elif any(x in key_lower for x in ["name", "nombre", "first"]):
                    fields.append(SearchField(field_type="name", value=val))
                elif any(x in key_lower for x in ["dob", "birth", "nacimiento"]):
                    fields.append(SearchField(field_type="dob", value=val))
                elif any(x in key_lower for x in ["username", "user", "usuario"]):
                    fields.append(SearchField(field_type="username", value=val))
                elif any(x in key_lower for x in ["domain", "dominio"]):
                    fields.append(SearchField(field_type="domain", value=val))
        
        return fields

    @staticmethod
    def _detect_field_type(value: str) -> str:
        """Detecta automáticamente el tipo de campo"""
        v = value.strip()
        
        # Email
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            return "email"
        
        # SSN (9 digits or XXX-XX-XXXX)
        clean = re.sub(r'[^0-9]', '', v)
        if len(clean) == 9 and clean.isdigit():
            return "ssn"
        
        # Phone
        if re.match(r'^[\+]?[0-9\-\(\)\s]{7,15}$', v) and not re.match(r'^\d{5}$', v):
            return "phone"
        
        # DOB
        if re.match(r'^\d{2}/\d{2}/\d{4}$', v):
            return "dob"
        
        # Zipcode
        if re.match(r'^\d{5}(-\d{4})?$', v):
            return "address"
        
        # Address (has numbers and letters, street-like)
        if re.search(r'\d{1,5}\s+\w+', v) and re.search(r'[A-Za-z]{3,}', v):
            return "address"
        
        # Username (no spaces, short)
        if re.match(r'^[a-zA-Z0-9._-]{3,30}$', v) and ' ' not in v:
            return "username"
        
        # Default to name
        return "name"

    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def export_csv(batch: BatchResult) -> str:
        """Exporta resultados a CSV"""
        output = io.StringIO()
        
        headers = [
            "input_type", "input_value", "emails", "phones", "names",
            "addresses", "ssns", "dobs", "banks", "accounts",
            "credit_cards", "credit_score", "credit_grade", "passwords",
            "breach_sources", "institutions", "risk_score", "sources", "time_ms"
        ]
        
        writer = csv.writer(output)
        writer.writerow(headers)
        
        for r in batch.results:
            writer.writerow([
                r.input_field, r.input_value,
                " | ".join(r.emails),
                " | ".join(r.phones),
                " | ".join(r.names),
                " | ".join(r.addresses),
                " | ".join(r.ssns),
                " | ".join(r.dobs),
                " | ".join(r.banks),
                " | ".join(r.accounts),
                " | ".join(r.credit_cards),
                r.credit_score or "",
                r.credit_grade or "",
                " | ".join(r.passwords[:5]),  # Limit passwords
                " | ".join(r.breach_sources),
                " | ".join([f"{i['name']}({i['type']})" for i in r.institutions]),
                r.risk_score,
                " | ".join(r.sources_checked),
                r.search_time_ms,
            ])
        
        return output.getvalue()

    @staticmethod
    def export_json(batch: BatchResult) -> str:
        """Exporta resultados a JSON"""
        data = {
            "total_queries": batch.total_queries,
            "total_results": batch.total_results,
            "total_time_ms": batch.total_time_ms,
            "timestamp": batch.timestamp,
            "results": [r.to_dict() for r in batch.results],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def export_txt(batch: BatchResult) -> str:
        """Exporta resultados a TXT legible"""
        lines = []
        lines.append("=" * 80)
        lines.append("  ROUTE & ACCOUNT FINDER — RESULTADOS")
        lines.append(f"  Total consultas: {batch.total_queries}")
        lines.append(f"  Total datos encontrados: {batch.total_results}")
        lines.append(f"  Tiempo total: {batch.total_time_ms}ms")
        lines.append("=" * 80)
        
        for i, r in enumerate(batch.results, 1):
            lines.append(f"\n{'#' * 80}")
            lines.append(f"  RESULTADO #{i} — {r.input_field.upper()}")
            lines.append(f"{'#' * 80}")
            lines.append(f"  Input: {r.input_value}")
            lines.append(f"  Risk Score: {r.risk_score}/100")
            
            if r.emails:
                lines.append(f"\n  📧 EMAILS ({len(r.emails)}):")
                for e in r.emails[:20]:
                    lines.append(f"     • {e}")
            if r.phones:
                lines.append(f"\n  📞 TELÉFONOS ({len(r.phones)}):")
                for p in r.phones[:20]:
                    lines.append(f"     • {p}")
            if r.names:
                lines.append(f"\n  👤 NOMBRES ({len(r.names)}):")
                for n in r.names[:20]:
                    lines.append(f"     • {n}")
            if r.addresses:
                lines.append(f"\n  🏠 DIRECCIONES ({len(r.addresses)}):")
                for a in r.addresses[:20]:
                    lines.append(f"     • {a}")
            if r.ssns:
                lines.append(f"\n  🔑 SSN ({len(r.ssns)}):")
                for s in r.ssns:
                    masked = f"***-**-{s[-4:]}" if len(s) >= 4 else "***-**-****"
                    lines.append(f"     • {masked}")
            if r.banks:
                lines.append(f"\n  🏦 BANCOS ({len(r.banks)}):")
                for b in r.banks[:20]:
                    lines.append(f"     • {b}")
            if r.credit_cards:
                lines.append(f"\n  💳 TARJETAS ({len(r.credit_cards)}):")
                for cc in r.credit_cards[:10]:
                    lines.append(f"     • {cc}")
            if r.credit_score:
                lines.append(f"\n  📊 CREDIT SCORE: {r.credit_score} ({r.credit_grade})")
            if r.passwords:
                lines.append(f"\n  🔐 PASSWORDS ({len(r.passwords)}):")
                for pw in r.passwords[:5]:
                    lines.append(f"     • {pw}")
            if r.breach_sources:
                lines.append(f"\n  📋 BRECHAS ({len(r.breach_sources)}):")
                for b in r.breach_sources[:20]:
                    lines.append(f"     • {b}")
            if r.institutions:
                lines.append(f"\n  🏛️ INSTITUCIONES ({len(r.institutions)}):")
                for inst in r.institutions[:20]:
                    lines.append(f"     • {inst['name']} ({inst['type']})")
            
            lines.append(f"\n  Fuentes: {', '.join(r.sources_checked)}")
            lines.append(f"  Tiempo: {r.search_time_ms}ms")
            lines.append(f"\n{'-' * 80}")
        
        return "\n".join(lines)
