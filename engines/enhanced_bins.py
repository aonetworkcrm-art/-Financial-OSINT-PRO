"""
🏦 Enhanced BIN Database
=========================
Base de datos de BINs mejorada integrando datos de:
- Super CC (410+ BINs verificados de binlist.io)
- Financial OSINT original
- Fuentes públicas ISO/IEC 7812

Carga BINs desde enhanced_bin_db.json y los fusiona con el BIN_DB local.
"""
import os
import json
from typing import Dict, Optional

# Path to enhanced database
_DB_PATH = os.path.join(os.path.dirname(__file__), "enhanced_bin_db.json")

# Load enhanced database
_ENHANCED_DB: Dict[str, Dict] = {}
try:
    with open(_DB_PATH, "r") as f:
        _ENHANCED_DB = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    pass


def get_enhanced_bin(bin6: str) -> Optional[Dict]:
    """
    Look up a 6-digit BIN in the enhanced database.
    Returns dict with bank, type, country, network, level.
    """
    return _ENHANCED_DB.get(bin6)


def get_all_enhanced_bins() -> Dict[str, Dict]:
    """Return the full enhanced BIN database."""
    return _ENHANCED_DB


def get_bins_by_network(network: str) -> Dict[str, Dict]:
    """Get all BINs for a specific network (Visa, Mastercard, etc.)."""
    network_lower = network.lower()
    return {
        bin6: info
        for bin6, info in _ENHANCED_DB.items()
        if info.get("network", "").lower() == network_lower
    }


def get_bins_by_bank(bank_name: str) -> Dict[str, Dict]:
    """Get all BINs for a specific bank."""
    bank_lower = bank_name.lower()
    return {
        bin6: info
        for bin6, info in _ENHANCED_DB.items()
        if bank_lower in info.get("bank", "").lower()
    }


def get_bins_by_country(country: str) -> Dict[str, Dict]:
    """Get all BINs for a specific country code."""
    country_upper = country.upper()
    return {
        bin6: info
        for bin6, info in _ENHANCED_DB.items()
        if info.get("country", "").upper() == country_upper
    }


def get_bins_by_type(card_type: str) -> Dict[str, Dict]:
    """Get all BINs for a specific type (credit/debit/prepaid)."""
    type_lower = card_type.lower()
    return {
        bin6: info
        for bin6, info in _ENHANCED_DB.items()
        if info.get("type", "").lower() == type_lower
    }


# Enhanced COUNTRY_NAMES
ENHANCED_COUNTRIES = {
    "US": "Estados Unidos", "MX": "México", "CA": "Canadá", "GB": "Reino Unido",
    "DE": "Alemania", "FR": "Francia", "ES": "España", "IT": "Italia",
    "JP": "Japón", "CN": "China", "KR": "Corea del Sur", "BR": "Brasil",
    "AR": "Argentina", "CO": "Colombia", "CL": "Chile", "PE": "Perú",
    "AU": "Australia", "IN": "India", "RU": "Rusia", "NL": "Países Bajos",
}

# Card lengths by network
CARD_LENGTHS = {
    "Visa": [13, 16, 19],
    "Mastercard": [16],
    "Amex": [15],
    "Discover": [16, 19],
    "Diners": [14, 16],
    "JCB": [16],
    "UnionPay": [16, 17, 18, 19],
}

# 3D Secure providers
THREE_D_SECURE = {
    "Visa": "Verified by Visa",
    "Mastercard": "Mastercard SecureCode",
    "Amex": "American Express SafeKey",
    "Discover": "Discover ProtectBuy",
    "JCB": "J/Secure",
    "UnionPay": "UnionPay 3D Secure",
    "Diners": "Diners Club ProtectBuy",
}
