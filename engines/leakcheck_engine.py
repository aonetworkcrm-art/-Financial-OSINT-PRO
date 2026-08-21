"""
🔍 LeakCheck Engine — Búsqueda de brechas
Soporta: email, phone, username, IP, domain, name
Para direcciones: fallback por ZIP code y ciudad
"""
import re
import time
import json
import logging
import requests
from typing import List, Dict, Optional
from core.models import BreachRecord

logger = logging.getLogger("leakcheck_engine")

API_BASE = "https://leakcheck.io/api/public"
API_PRO = "https://leakcheck.io/api/pro"


class LeakCheckEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base = API_PRO if api_key else API_BASE
        self.last_request = 0
        self.min_interval = 1.2

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def search(self, query: str, query_type: str = "auto") -> List[BreachRecord]:
        """Buscar en LeakCheck"""
        self._rate_limit()

        if query_type == "auto":
            query_type = self._detect_type(query)

        # Para direcciones, usar búsqueda inteligente
        if query_type == "address":
            return self._search_address(query)

        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        try:
            resp = requests.get(
                f"{self.base}",
                params={"check": query},
                headers=headers,
                timeout=15
            )

            if resp.status_code == 429:
                logger.warning("Rate limited, waiting 5s...")
                time.sleep(5)
                return self.search(query, query_type)

            if resp.status_code != 200:
                logger.error(f"LeakCheck error: {resp.status_code}")
                return []

            data = resp.json()
            return self._parse_results(data, query, query_type)

        except Exception as e:
            logger.error(f"LeakCheck error: {e}")
            return []

    def _detect_type(self, query: str) -> str:
        """Detectar tipo de query automáticamente"""
        q = query.strip()
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', q):
            return "email"
        digits = re.sub(r'\D', '', q)
        if len(digits) == 10:
            return "phone"
        if re.match(r'^\d{3}-?\d{2}-?\d{4}$', q):
            return "ssn"
        if re.match(r'^\d{1,5}\s+\w+', q):
            return "address"
        if re.match(r'^[\w\.-]+\.\w+$', q):
            return "domain"
        return "generic"

    def _search_address(self, address: str) -> List[BreachRecord]:
        """Buscar por dirección con fallbacks inteligentes"""
        all_records = []

        # La API pública NO soporta dirección completa
        # Solo funciona: email, phone, username, IP
        # Fallback: extraer ZIP code y ciudad para buscar

        variants = self._extract_searchable_variants(address)

        for variant in variants:
            logger.info(f"Trying address variant: {variant}")
            records = self._raw_search(variant, "generic")
            all_records.extend(records)
            if records:
                logger.info(f"Found {len(records)} records for: {variant}")

        # Deduplicate
        seen = set()
        unique = []
        for r in all_records:
            key = (r.breach_name, r.email, r.phone)
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique

    def _extract_searchable_variants(self, address: str) -> list:
        """Extraer variantes que la API pública puede buscar"""
        variants = []

        # Solo ZIP code (la API pública acepta números)
        zip_match = re.search(r'(\d{5}(?:-\d{4})?)', address)
        if zip_match:
            variants.append(zip_match.group(1))

        # Solo nombre de la ciudad (sin espacios extra)
        city_match = re.search(r'([A-Za-z]+(?:\s[A-Za-z]+)*),\s*[A-Z]{2}', address)
        if city_match:
            city = city_match.group(1).strip()
            if len(city) > 2:
                variants.append(city)

        # Nombre de la calle (sin número, sin caracteres raros)
        street_match = re.match(r'^\d+\s+([A-Za-z\s]+?)(?:,|$)', address)
        if street_match:
            street = street_match.group(1).strip()
            # Quitar abreviaturas comunes
            street = re.sub(r'\b(Ln|St|Ave|Dr|Rd|Blvd|Ct|Pl)\b', '', street).strip()
            if len(street) > 3:
                variants.append(street)

        return variants

    def _raw_search(self, query: str, query_type: str) -> List[BreachRecord]:
        """Búsqueda raw"""
        self._rate_limit()

        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        try:
            resp = requests.get(
                f"{self.base}",
                params={"check": query},
                headers=headers,
                timeout=15
            )

            if resp.status_code == 429:
                time.sleep(5)
                return self._raw_search(query, query_type)

            if resp.status_code != 200:
                return []

            data = resp.json()
            return self._parse_results(data, query, query_type)
        except Exception as e:
            logger.error(f"Raw search error: {e}")
            return []

    def search_address(self, address: str) -> List[BreachRecord]:
        """Buscar por dirección"""
        return self._search_address(address)

    def _parse_results(self, data: dict, query: str, query_type: str) -> List[BreachRecord]:
        """Parsear resultados de LeakCheck"""
        records = []

        if not data.get("found"):
            return records

        for source in data.get("sources", []):
            record = BreachRecord(
                source="leakcheck",
                breach_name=source.get("name", "Unknown"),
                breach_date=source.get("date", ""),
                fields_exposed=source.get("fields", []),
            )

            # Asignar el campo de búsqueda
            if query_type == "email":
                record.email = query
            elif query_type == "phone":
                record.phone = query
            elif query_type == "address":
                record.address = query
            elif query_type == "name":
                record.name = query

            # API Pro: datos completos
            if "line" in source:
                line = source["line"]
                if isinstance(line, str):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        record.email = parts[0]
                        record.password = parts[1] if len(parts) > 1 else ""
                elif isinstance(line, dict):
                    record.email = line.get("email", "")
                    record.password = line.get("password", "")
                    record.phone = line.get("phone", "")
                    record.ssn = line.get("ssn", "")
                    record.name = line.get("name", "")

            records.append(record)

        return records

    def search_batch(self, queries: List[str], query_type: str = "auto",
                     delay: float = 1.2) -> Dict[str, List[BreachRecord]]:
        """Búsqueda en lote"""
        results = {}
        for i, q in enumerate(queries):
            logger.info(f"[{i+1}/{len(queries)}] Searching: {q}")
            results[q] = self.search(q, query_type)
            if i < len(queries) - 1:
                time.sleep(delay)
        return results
