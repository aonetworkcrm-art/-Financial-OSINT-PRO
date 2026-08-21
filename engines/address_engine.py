"""
🏠 Address Engine — Motor de búsqueda por dirección SUPER POTENCIADO
Busca TODO lo asociado a una dirección postal:
- Emails, teléfonos, nombres
- Credit scores
- Datos de brechas
- Instituciones financieras
- Registros públicos
"""
import re
import time
import logging
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.models import BreachRecord, Profile, InstitutionMatch
from engines.leakcheck_engine import LeakCheckEngine
from engines.institution_matcher import InstitutionMatcher
from engines.credit_score_engine import CreditScoreEngine, CreditScoreResult

logger = logging.getLogger("address_engine")


@dataclass
class AddressProfile:
    """Perfil completo construido desde una dirección"""
    address: str
    name: str = ""
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    ssn: str = ""
    dob: str = ""
    passwords: List[str] = field(default_factory=list)
    credit_cards: List[str] = field(default_factory=list)
    credit_score: Optional[CreditScoreResult] = None
    institutions: List[Dict] = field(default_factory=list)
    breach_sources: List[str] = field(default_factory=list)
    risk_score: int = 0
    raw_records: List[Dict] = field(default_factory=list)


class AddressEngine:
    """
    Motor de búsqueda por dirección super potenciado.
    Combina múltiples fuentes para encontrar todo lo asociado.
    """

    def __init__(self, leakcheck_key: str = None):
        self.leakcheck = LeakCheckEngine(api_key=leakcheck_key)
        self.matcher = InstitutionMatcher()
        self.credit_engine = CreditScoreEngine()

    def full_address_search(self, address: str) -> AddressProfile:
        """
        Búsqueda COMPLETA por dirección.
        Combina todas las fuentes disponibles.
        """
        profile = AddressProfile(address=address)

        # Paso 1: Normalizar dirección
        components = self._parse_address(address)

        # Paso 2: Buscar por cada componente
        all_records = []

        # Buscar por ZIP code
        if components.get("zipcode"):
            records = self.leakcheck.search(components["zipcode"], "generic")
            all_records.extend(records)

        # Buscar por ciudad
        if components.get("city"):
            time.sleep(1.5)
            records = self.leakcheck.search(components["city"], "generic")
            all_records.extend(records)

        # Buscar por nombre de calle
        if components.get("street_name"):
            time.sleep(1.5)
            records = self.leakcheck.search(components["street_name"], "generic")
            all_records.extend(records)

        # Paso 3: Buscar en fuentes externas (gratuitas)
        ext_results = self._search_external_sources(address, components)
        all_records.extend(ext_results)

        # Paso 4: Construir perfil desde registros
        self._build_profile_from_records(profile, all_records)

        # Paso 5: Detectar instituciones
        self._detect_institutions(profile)

        # Paso 6: Estimar credit score
        self._estimate_credit_score(profile)

        # Paso 7: Calcular risk score
        profile.risk_score = self._calculate_risk(profile)

        return profile

    def _parse_address(self, address: str) -> Dict:
        """Parsear dirección en componentes"""
        components = {}

        # ZIP code
        zip_match = re.search(r'(\d{5}(?:-\d{4})?)', address)
        if zip_match:
            components["zipcode"] = zip_match.group(1)

        # City, State - find pattern like "Richardson, TX 75080"
        cs_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})?', address)
        if cs_match:
            city = cs_match.group(1).strip()
            # Remove street name artifacts
            city = re.sub(r'^.*?(Ln|St|Ave|Dr|Rd|Blvd|Ct|Pl|Way)\s+', '', city)
            if not city:
                # Fallback: get text between last comma and state
                parts = address.split(',')
                for p in parts:
                    if re.search(r'[A-Z]{2}', p):
                        city = re.sub(r'[A-Z]{2}.*', '', p).strip()
                        break
            if city:
                components["city"] = city
            components["state"] = cs_match.group(2)
            if cs_match.group(3):
                components["zipcode"] = cs_match.group(3)

        # Street
        street_part = address.split(',')[0].strip() if ',' in address else address
        street_match = re.match(r'^(\d+)\s+(.+)', street_part)
        if street_match:
            components["street_number"] = street_match.group(1)
            raw_name = street_match.group(2)
            # Quitar abreviaturas
            components["street_name"] = re.sub(
                r'\b(Ln|St|Ave|Dr|Rd|Blvd|Ct|Pl|Way|Ter)\b', '', raw_name
            ).strip()

        return components

    def _search_external_sources(self, address: str, components: Dict) -> List[BreachRecord]:
        """Buscar en fuentes externas gratuitas"""
        records = []

        # 1. XposedOrNot (gratis, sin key)
        try:
            for term in [components.get("zipcode"), components.get("city")]:
                if term:
                    resp = requests.get(
                        f"https://api.xposedornot.com/v1/check-email/{term}",
                        timeout=10
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "found":
                            records.append(BreachRecord(
                                source="xposedornot",
                                breach_name=f"xposed_{term}",
                                fields_exposed=["email"],
                            ))
        except Exception as e:
            logger.debug(f"XposedOrNot error: {e}")

        # 2. Leak-Lookup (key pública, ~10/día)
        try:
            if components.get("zipcode"):
                resp = requests.get(
                    f"https://api.leak-lookup.com/v1/search?query={components['zipcode']}",
                    timeout=10,
                    headers={"Authorization": "Bearer public_key"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success") and data.get("data"):
                        for entry in data["data"][:5]:
                            records.append(BreachRecord(
                                source="leaklookup",
                                breach_name=entry.get("source", "leaklookup"),
                                email=entry.get("email", ""),
                                password=entry.get("password", ""),
                            ))
        except Exception as e:
            logger.debug(f"Leak-Lookup error: {e}")

        return records

    def _build_profile_from_records(self, profile: AddressProfile, records: List[BreachRecord]):
        """Construir perfil desde registros de brechas"""
        emails = set()
        phones = set()
        names = set()
        passwords = set()
        credit_cards = set()
        breach_sources = set()

        for r in records:
            if r.email:
                emails.add(r.email)
            if r.phone:
                phones.add(self._normalize_phone(r.phone))
            if r.name:
                names.add(r.name)
            if r.password:
                passwords.add(r.password)
            if r.credit_card:
                credit_cards.add(r.credit_card)
            if r.breach_name:
                breach_sources.add(r.breach_name)
            if r.ssn:
                profile.ssn = profile.ssn or r.ssn
            if r.dob:
                profile.dob = profile.dob or r.dob

        profile.emails = list(emails)
        profile.phones = list(phones)
        profile.passwords = list(passwords)
        profile.credit_cards = list(credit_cards)
        profile.breach_sources = list(breach_sources)

        if names:
            profile.name = list(names)[0]

        # Guardar records raw para análisis
        profile.raw_records = [r.to_dict() for r in records if r.to_dict()]

    def _detect_institutions(self, profile: AddressProfile):
        """Detectar instituciones financieras"""
        for email in profile.emails:
            matches = self.matcher.match_email(email)
            for m in matches:
                profile.institutions.append({
                    "name": m.institution,
                    "type": m.institution_type,
                    "source": f"email: {email}",
                })

        for phone in profile.phones:
            matches = self.matcher.match_phone(phone)
            for m in matches:
                profile.institutions.append({
                    "name": m.institution,
                    "type": m.institution_type,
                    "source": f"phone: {phone}",
                })

        for breach in profile.breach_sources:
            matches = self.matcher.match_breach(breach)
            for m in matches:
                profile.institutions.append({
                    "name": m.institution,
                    "type": m.institution_type,
                    "source": f"breach: {breach}",
                })

        # Deduplicate
        seen = set()
        unique = []
        for inst in profile.institutions:
            key = inst["name"]
            if key not in seen:
                seen.add(key)
                unique.append(inst)
        profile.institutions = unique

    def _estimate_credit_score(self, profile: AddressProfile):
        """Estimar credit score desde el perfil"""
        profile_data = {
            "institutions": profile.institutions,
            "accounts": profile.credit_cards,
        }
        profile.credit_score = self.credit_engine.estimate_score_from_profile(profile_data)

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r'\D', '', phone)
        if digits.startswith('1') and len(digits) == 11:
            digits = digits[1:]
        if len(digits) == 10:
            return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return phone

    def _calculate_risk(self, profile: AddressProfile) -> int:
        score = 0
        if profile.ssn:
            score += 25
        if profile.passwords:
            score += 20
        if profile.credit_cards:
            score += 15
        if profile.emails:
            score += 5
        if profile.phones:
            score += 5
        if profile.institutions:
            score += min(len(profile.institutions) * 5, 20)
        if profile.credit_score and profile.credit_score.score < 600:
            score += 10
        return min(score, 100)
