"""
📊 Data Models — Financial OSINT Tool
Modelos de datos para todo el sistema
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class BreachRecord:
    """Un registro encontrado en una brecha"""
    email: str = ""
    password: str = ""
    password_hash: str = ""
    phone: str = ""
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    ssn: str = ""
    dob: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zipcode: str = ""
    credit_card: str = ""
    card_type: str = ""
    bank_name: str = ""
    routing_number: str = ""
    account_number: str = ""
    username: str = ""
    source: str = ""
    breach_name: str = ""
    breach_date: str = ""
    fields_exposed: List[str] = field(default_factory=list)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v and v != []}


@dataclass
class InstitutionMatch:
    """Coincidencia con una institución financiera"""
    institution: str
    institution_type: str  # bank, credit_union, fintech
    confidence: float  # 0-1
    evidence: str  # Por qué se detectó
    data_exposed: List[str] = field(default_factory=list)


@dataclass
class Profile:
    """Perfil completo de una persona (construido desde brechas)"""
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    ssn: str = ""
    dob: str = ""
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    credit_cards: List[str] = field(default_factory=list)
    passwords: List[str] = field(default_factory=list)
    institutions: List[InstitutionMatch] = field(default_factory=list)
    breach_sources: List[str] = field(default_factory=list)
    risk_score: int = 0

    def has_bank_data(self):
        return bool(self.ssn or self.credit_cards or self.institutions)

    def summary(self):
        return {
            "name": self.name,
            "emails": len(self.emails),
            "phones": len(self.phones),
            "addresses": len(self.addresses),
            "ssn": bool(self.ssn),
            "credit_cards": len(self.credit_cards),
            "passwords": len(self.passwords),
            "institutions": len(self.institutions),
            "risk_score": self.risk_score,
        }


@dataclass
class ExtractionResult:
    """Resultado de una extracción automatizada"""
    profile_name: str
    portal: str
    status: str  # success, failed, blocked, no_data
    routing_numbers: List[str] = field(default_factory=list)
    account_numbers: List[str] = field(default_factory=list)
    bank_names: List[str] = field(default_factory=list)
    credit_cards: List[str] = field(default_factory=list)
    addresses_found: List[str] = field(default_factory=list)
    phones_found: List[str] = field(default_factory=list)
    emails_found: List[str] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)
    error: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v and v != []}


@dataclass
class SearchRequest:
    """Request de búsqueda"""
    query: str
    query_type: str  # address, email, phone, name, ssn
    institutions: List[str] = field(default_factory=list)
    search_breaches: bool = True
    search_extraction: bool = True
    export_format: str = "csv"


@dataclass
class SearchResult:
    """Resultado completo de una búsqueda"""
    request: SearchRequest
    profiles: List[Profile] = field(default_factory=list)
    extractions: List[ExtractionResult] = field(default_factory=list)
    total_breaches: int = 0
    total_exposures: int = 0
    exposure_score: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
