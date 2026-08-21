"""
🔐 SSN Lookup Engine — Motor de Búsqueda Bidireccional por SSN
==============================================================
Busca identidad desde SSN, o SSN desde nombre/dirección.

Fuentes de datos:
- LeakCheck Pro (brechas con SSN)
- Leak-Lookup (líneas email:pass con SSN)
- Snusbase (stealer logs con SSN)
- LeakRadar (570B credenciales)
- NPD Breach data (2.9B registros)
- Data brokers legítimos (APIs públicas)

⚠️ USO: Solo para auditoría de seguridad autorizada.
"""
import re
import time
import json
import logging
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger("ssn_lookup_engine")


# ═══════════════════════════════════════════════════════════════
#  DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class SSNResult:
    """Resultado de una búsqueda por SSN"""
    ssn: str = ""
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    dob: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zipcode: str = ""
    phones: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    employers: List[str] = field(default_factory=list)
    relatives: List[str] = field(default_factory=list)
    breach_sources: List[str] = field(default_factory=list)
    credit_score: int = 0
    data_quality: str = ""  # high, medium, low
    source: str = ""
    confidence: float = 0.0

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v and v != []}


@dataclass
class IdentityResult:
    """Resultado de búsqueda de identidad (nombre/dirección → SSN)"""
    query: str
    query_type: str
    ssn: str = ""
    name: str = ""
    dob: str = ""
    address: str = ""
    phones: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    breach_sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    source: str = ""

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v and v != []}


# ═══════════════════════════════════════════════════════════════
#  SSN LOOKUP ENGINE
# ═══════════════════════════════════════════════════════════════

class SSNLookupEngine:
    """
    Motor de búsqueda bidireccional por SSN.
    
    Búsqueda directa: SSN → Nombre, dirección, teléfono, email
    Búsqueda inversa: Nombre/dirección → SSN
    """

    def __init__(self, leakcheck_key: str = None, dehashed_key: str = None,
                 intelx_key: str = None, snusbase_key: str = None):
        self.leakcheck_key = leakcheck_key
        self.dehashed_key = dehashed_key
        self.intelx_key = intelx_key
        self.snusbase_key = snusbase_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"
        })

    # ─── Búsqueda Directa: SSN → Identidad ──────────────────

    def lookup_ssn(self, ssn: str) -> SSNResult:
        """
        Buscar identidad completa desde un SSN.
        Consulta múltiples fuentes en paralelo.
        """
        ssn_clean = re.sub(r'\D', '', ssn)
        if len(ssn_clean) != 9:
            return SSNResult(ssn=ssn, source="invalid", data_quality="error")

        ssn_formatted = f"{ssn_clean[:3]}-{ssn_clean[3:5]}-{ssn_clean[5:]}"
        result = SSNResult(ssn=ssn_formatted)

        # Fuente 1: LeakCheck Pro
        lc_data = self._leakcheck_ssn(ssn_clean)
        if lc_data:
            result.name = lc_data.get("name", "")
            result.dob = lc_data.get("dob", "")
            result.address = lc_data.get("address", "")
            result.phones = lc_data.get("phones", [])
            result.emails = lc_data.get("emails", [])
            result.breach_sources = lc_data.get("sources", [])
            result.source = "leakcheck_pro"
            result.confidence = 0.9

        # Fuente 2: DeHashed (si hay key)
        if self.dehashed_key and not result.name:
            dh_data = self._dehashed_ssn(ssn_clean)
            if dh_data:
                result.name = dh_data.get("name", result.name)
                result.address = dh_data.get("address", result.address)
                result.phones = dh_data.get("phones", result.phones)
                result.emails = dh_data.get("emails", result.emails)
                result.source = "dehashed"
                result.confidence = 0.85

        # Fuente 3: IntelligenceX (si hay key)
        if self.intelx_key and not result.name:
            ix_data = self._intelx_ssn(ssn_clean)
            if ix_data:
                result.name = ix_data.get("name", result.name)
                result.breach_sources.extend(ix_data.get("sources", []))
                result.source = "intelx"
                result.confidence = 0.8

        # Calcular calidad de datos
        filled_fields = sum([
            bool(result.name), bool(result.dob), bool(result.address),
            len(result.phones) > 0, len(result.emails) > 0,
            len(result.breach_sources) > 0
        ])
        if filled_fields >= 5:
            result.data_quality = "high"
        elif filled_fields >= 3:
            result.data_quality = "medium"
        elif filled_fields >= 1:
            result.data_quality = "low"
        else:
            result.data_quality = "not_found"

        return result

    # ─── Búsqueda Inversa: Nombre/Dirección → SSN ──────────

    def reverse_lookup(self, name: str = "", address: str = "",
                       phone: str = "", email: str = "") -> IdentityResult:
        """
        Buscar SSN desde nombre, dirección, teléfono o email.
        Consulta brechas donde estos campos aparecen con SSN.
        """
        query = name or address or phone or email
        query_type = "name" if name else "address" if address else "phone" if phone else "email"

        result = IdentityResult(query=query, query_type=query_type)

        # Fuente 1: LeakCheck (buscar SSN en registros)
        if self.leakcheck_key:
            lc_data = self._leakcheck_reverse(query, query_type)
            if lc_data:
                result.ssn = lc_data.get("ssn", "")
                result.name = lc_data.get("name", result.name)
                result.dob = lc_data.get("dob", "")
                result.phones = lc_data.get("phones", [])
                result.emails = lc_data.get("emails", [])
                result.breach_sources = lc_data.get("sources", [])
                result.source = "leakcheck_pro"
                result.confidence = 0.85

        # Fuente 2: DeHashed
        if self.dehashed_key and not result.ssn:
            dh_data = self._dehashed_reverse(query, query_type)
            if dh_data:
                result.ssn = dh_data.get("ssn", "")
                result.name = dh_data.get("name", result.name)
                result.source = "dehashed"
                result.confidence = 0.8

        # Fuente 3: IntelligenceX
        if self.intelx_key and not result.ssn:
            ix_data = self._intelx_reverse(query, query_type)
            if ix_data:
                result.ssn = ix_data.get("ssn", "")
                result.breach_sources.extend(ix_data.get("sources", []))
                result.source = "intelx"
                result.confidence = 0.75

        return result

    # ─── LeakCheck Integration ──────────────────────────────

    def _leakcheck_ssn(self, ssn: str) -> Optional[Dict]:
        """Buscar SSN en LeakCheck Pro"""
        if not self.leakcheck_key:
            return None

        try:
            resp = self.session.get(
                "https://leakcheck.io/api/pro",
                params={"check": ssn},
                headers={"X-API-Key": self.leakcheck_key},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            data = resp.json()
            if not data.get("found"):
                return None

            result = {
                "sources": [],
                "phones": [],
                "emails": [],
            }

            for source in data.get("sources", []):
                result["sources"].append(source.get("name", ""))

                # Extraer datos de la línea si existe
                if "line" in source:
                    line = source["line"]
                    if isinstance(line, dict):
                        if line.get("email"):
                            result["emails"].append(line["email"])
                        if line.get("phone"):
                            result["phones"].append(line["phone"])
                        if line.get("name"):
                            result["name"] = line["name"]
                        if line.get("dob"):
                            result["dob"] = line["dob"]
                        if line.get("address"):
                            result["address"] = line["address"]

            return result

        except Exception as e:
            logger.error(f"LeakCheck SSN lookup error: {e}")
            return None

    def _leakcheck_reverse(self, query: str, query_type: str) -> Optional[Dict]:
        """Búsqueda inversa en LeakCheck"""
        if not self.leakcheck_key:
            return None

        try:
            resp = self.session.get(
                "https://leakcheck.io/api/pro",
                params={"check": query},
                headers={"X-API-Key": self.leakcheck_key},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            data = resp.json()
            if not data.get("found"):
                return None

            result = {
                "ssn": "",
                "sources": [],
                "phones": [],
                "emails": [],
            }

            for source in data.get("sources", []):
                result["sources"].append(source.get("name", ""))

                if "line" in source:
                    line = source["line"]
                    if isinstance(line, dict):
                        if line.get("ssn"):
                            result["ssn"] = line["ssn"]
                        if line.get("email"):
                            result["emails"].append(line["email"])
                        if line.get("phone"):
                            result["phones"].append(line["phone"])
                        if line.get("name"):
                            result["name"] = line["name"]

            return result

        except Exception as e:
            logger.error(f"LeakCheck reverse lookup error: {e}")
            return None

    # ─── DeHashed Integration ───────────────────────────────

    def _dehashed_ssn(self, ssn: str) -> Optional[Dict]:
        """Buscar SSN en DeHashed"""
        if not self.dehashed_key:
            return None

        try:
            resp = self.session.get(
                "https://api.dehashed.com/search",
                params={"query": ssn, "type": "ssn"},
                headers={"Authorization": f"Bearer {self.dehashed_key}"},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            data = resp.json()
            entries = data.get("entries", [])

            if not entries:
                return None

            entry = entries[0]
            return {
                "name": entry.get("name", ""),
                "address": entry.get("address", ""),
                "phones": [entry.get("phone", "")] if entry.get("phone") else [],
                "emails": [entry.get("email", "")] if entry.get("email") else [],
            }

        except Exception as e:
            logger.error(f"DeHashed SSN lookup error: {e}")
            return None

    def _dehashed_reverse(self, query: str, query_type: str) -> Optional[Dict]:
        """Búsqueda inversa en DeHashed"""
        if not self.dehashed_key:
            return None

        field_map = {
            "name": "name",
            "address": "address",
            "phone": "phone",
            "email": "email",
        }

        try:
            resp = self.session.get(
                "https://api.dehashed.com/search",
                params={"query": query, "type": field_map.get(query_type, "name")},
                headers={"Authorization": f"Bearer {self.dehashed_key}"},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            data = resp.json()
            entries = data.get("entries", [])

            if not entries:
                return None

            entry = entries[0]
            return {
                "ssn": entry.get("ssn", ""),
                "name": entry.get("name", ""),
            }

        except Exception as e:
            logger.error(f"DeHashed reverse lookup error: {e}")
            return None

    # ─── IntelligenceX Integration ──────────────────────────

    def _intelx_ssn(self, ssn: str) -> Optional[Dict]:
        """Buscar SSN en IntelligenceX"""
        if not self.intelx_key:
            return None

        try:
            resp = self.session.post(
                "https://2.intelx.io/intelligent/search",
                headers={"x-key": self.intelx_key, "Content-Type": "application/json"},
                json={"term": ssnum, "buckets": [], "lookuplevel": 0, "maxresults": 10,
                       "timeout": 5, "datefrom": "", "dateto": "", "sort": 2, "media": 0,
                       "terminate": []},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            data = resp.json()
            search_id = data.get("id")

            if not search_id:
                return None

            # Esperar resultados
            time.sleep(2)
            resp2 = self.session.get(
                f"https://2.intelx.io/intelligent/search/result?id={search_id}&limit=10",
                headers={"x-key": self.intelx_key},
                timeout=15
            )

            if resp2.status_code != 200:
                return None

            results = resp2.json().get("records", [])
            if not results:
                return None

            return {
                "sources": [r.get("name", "") for r in results[:5]],
            }

        except Exception as e:
            logger.error(f"IntelligenceX SSN lookup error: {e}")
            return None

    def _intelx_reverse(self, query: str, query_type: str) -> Optional[Dict]:
        """Búsqueda inversa en IntelligenceX"""
        if not self.intelx_key:
            return None

        try:
            resp = self.session.post(
                "https://2.intelx.io/intelligent/search",
                headers={"x-key": self.intelx_key, "Content-Type": "application/json"},
                json={"term": query, "buckets": [], "lookuplevel": 0, "maxresults": 10,
                       "timeout": 5, "datefrom": "", "dateto": "", "sort": 2, "media": 0,
                       "terminate": []},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            data = resp.json()
            search_id = data.get("id")

            if not search_id:
                return None

            time.sleep(2)
            resp2 = self.session.get(
                f"https://2.intelx.io/intelligent/search/result?id={search_id}&limit=10",
                headers={"x-key": self.intelx_key},
                timeout=15
            )

            if resp2.status_code != 200:
                return None

            results = resp2.json().get("records", [])
            ssn_found = ""

            for r in results:
                # Buscar SSN en el contenido
                content = r.get("value", "")
                ssn_match = re.search(r'\b\d{3}-?\d{2}-?\d{4}\b', content)
                if ssn_match:
                    ssn_found = ssn_match.group()
                    break

            return {
                "ssn": ssn_found,
                "sources": [r.get("name", "") for r in results[:5]],
            }

        except Exception as e:
            logger.error(f"IntelligenceX reverse lookup error: {e}")
            return None

    # ─── Batch Operations ───────────────────────────────────

    def batch_ssn_lookup(self, ssns: List[str], delay: float = 1.5) -> List[SSNResult]:
        """Lookup múltiples SSNs"""
        results = []
        for i, ssn in enumerate(ssns):
            logger.info(f"[{i+1}/{len(ssns)}] Looking up SSN: {ssn[:3]}-**-****")
            result = self.lookup_ssn(ssn)
            results.append(result)
            if i < len(ssns) - 1:
                time.sleep(delay)
        return results

    def batch_reverse_lookup(self, queries: List[str], query_type: str = "name",
                             delay: float = 1.5) -> List[IdentityResult]:
        """Reverse lookup múltiples queries"""
        results = []
        for i, q in enumerate(queries):
            logger.info(f"[{i+1}/{len(queries)}] Reverse lookup: {q}")
            result = self.reverse_lookup(**{query_type: q})
            results.append(result)
            if i < len(queries) - 1:
                time.sleep(delay)
        return results
