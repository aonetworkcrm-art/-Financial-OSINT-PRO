"""
🏦 Institution Matcher — Detecta instituciones financieras
Cruza emails/teléfonos con bases de datos de instituciones
"""
import re
import json
from typing import List, Dict, Optional
from core.models import InstitutionMatch

# Base de datos de instituciones financieras
INSTITUTIONS = {
    "usbank": {
        "name": "US Bank",
        "type": "bank",
        "email_domains": ["usbank.com", "usbankaccess.com"],
        "phone_patterns": ["8008722657", "8003657787", "5036443434"],
        "breach_keywords": ["usbank", "us bank", "usbank.com", "usbankaccess"],
        "services": ["checking", "savings", "credit_cards", "mortgage", "loans"],
    },
    "venmo": {
        "name": "Venmo",
        "type": "fintech",
        "email_domains": ["venmo.com"],
        "phone_patterns": ["8558124430"],
        "breach_keywords": ["venmo"],
        "services": ["p2p_payments", "debit_card", "crypto"],
    },
    "schools_fcu": {
        "name": "Schools Federal Credit Union",
        "type": "credit_union",
        "email_domains": ["schoolsfederal.org", "schoolsfcu.org"],
        "phone_patterns": ["8006324600", "3105383393"],
        "breach_keywords": ["schools federal", "schoolsfcu", "schools federal credit"],
        "services": ["checking", "savings", "credit_cards", "auto_loans"],
    },
    "chase": {
        "name": "Chase",
        "type": "bank",
        "email_domains": ["chase.com"],
        "phone_patterns": ["8009359935"],
        "breach_keywords": ["chase", "jpmorgan", "jpmorgan chase"],
        "services": ["checking", "savings", "credit_cards", "mortgage"],
    },
    "wells_fargo": {
        "name": "Wells Fargo",
        "type": "bank",
        "email_domains": ["wellsfargo.com"],
        "phone_patterns": ["8008693557"],
        "breach_keywords": ["wells fargo", "wellsfargo"],
        "services": ["checking", "savings", "credit_cards", "mortgage"],
    },
    "bank_of_america": {
        "name": "Bank of America",
        "type": "bank",
        "email_domains": ["bankofamerica.com", "bofa.com"],
        "phone_patterns": ["8004321000"],
        "breach_keywords": ["bank of america", "bofa", "bankofamerica"],
        "services": ["checking", "savings", "credit_cards", "mortgage"],
    },
    "citi": {
        "name": "Citibank",
        "type": "bank",
        "email_domains": ["citi.com", "citibank.com"],
        "phone_patterns": ["8003749827"],
        "breach_keywords": ["citibank", "citi bank", "citi.com"],
        "services": ["checking", "savings", "credit_cards"],
    },
    "capital_one": {
        "name": "Capital One",
        "type": "bank",
        "email_domains": ["capitalone.com"],
        "phone_patterns": ["8009334674"],
        "breach_keywords": ["capital one", "capitalone"],
        "services": ["checking", "savings", "credit_cards", "auto_loans"],
    },
    "discover": {
        "name": "Discover",
        "type": "bank",
        "email_domains": ["discover.com"],
        "phone_patterns": ["8003472683"],
        "breach_keywords": ["discover", "discover card"],
        "services": ["credit_cards", "banking", "loans"],
    },
    "american_express": {
        "name": "American Express",
        "type": "bank",
        "email_domains": ["americanexpress.com", "amex.com"],
        "phone_patterns": ["8005284800"],
        "breach_keywords": ["american express", "amex"],
        "services": ["credit_cards", "banking", "loans"],
    },
    "paypal": {
        "name": "PayPal",
        "type": "fintech",
        "email_domains": ["paypal.com"],
        "phone_patterns": ["8882211161"],
        "breach_keywords": ["paypal"],
        "services": ["payments", "credit_cards", "crypto"],
    },
    "cash_app": {
        "name": "Cash App",
        "type": "fintech",
        "email_domains": ["square.com", "cash.app"],
        "phone_patterns": ["8553512274"],
        "breach_keywords": ["cash app", "cashapp", "square"],
        "services": ["p2p_payments", "debit_card", "bitcoin"],
    },
    "zelle": {
        "name": "Zelle",
        "type": "fintech",
        "email_domains": ["zellepay.com"],
        "phone_patterns": ["8444288542"],
        "breach_keywords": ["zelle"],
        "services": ["p2p_payments"],
    },
    "navy_federal": {
        "name": "Navy Federal Credit Union",
        "type": "credit_union",
        "email_domains": ["navyfederal.org"],
        "phone_patterns": ["8888426328"],
        "breach_keywords": ["navy federal", "navyfederal"],
        "services": ["checking", "savings", "credit_cards", "mortgage", "auto_loans"],
    },
    "alliant": {
        "name": "Alliant Credit Union",
        "type": "credit_union",
        "email_domains": ["alliantcreditunion.org"],
        "phone_patterns": ["8003288797"],
        "breach_keywords": ["alliant", "alliant credit"],
        "services": ["checking", "savings", "auto_loans"],
    },
}


class InstitutionMatcher:
    def __init__(self):
        self.institutions = INSTITUTIONS

    def match_email(self, email: str) -> List[InstitutionMatch]:
        """Detectar instituciones por email"""
        matches = []
        domain = email.split("@")[-1].lower() if "@" in email else ""

        for key, inst in self.institutions.items():
            # Match por dominio del email
            if domain in inst["email_domains"]:
                matches.append(InstitutionMatch(
                    institution=inst["name"],
                    institution_type=inst["type"],
                    confidence=1.0,
                    evidence=f"Email domain: {domain}",
                    data_exposed=inst["services"],
                ))

        return matches

    def match_phone(self, phone: str) -> List[InstitutionMatch]:
        """Detectar instituciones por teléfono"""
        matches = []
        digits = re.sub(r'\D', '', phone)

        for key, inst in self.institutions.items():
            if digits in inst["phone_patterns"]:
                matches.append(InstitutionMatch(
                    institution=inst["name"],
                    institution_type=inst["type"],
                    confidence=1.0,
                    evidence=f"Phone match: {phone}",
                    data_exposed=inst["services"],
                ))

        return matches

    def match_breach(self, breach_name: str) -> List[InstitutionMatch]:
        """Detectar instituciones por nombre de brecha"""
        matches = []
        breach_lower = breach_name.lower()

        for key, inst in self.institutions.items():
            for keyword in inst["breach_keywords"]:
                if keyword.lower() in breach_lower:
                    matches.append(InstitutionMatch(
                        institution=inst["name"],
                        institution_type=inst["type"],
                        confidence=0.8,
                        evidence=f"Breach: {breach_name}",
                        data_exposed=inst["services"],
                    ))
                    break

        return matches

    def match_all(self, email: str = "", phone: str = "",
                  breach_names: List[str] = None) -> List[InstitutionMatch]:
        """Match completo: email + phone + breach names"""
        all_matches = []

        if email:
            all_matches.extend(self.match_email(email))
        if phone:
            all_matches.extend(self.match_phone(phone))
        if breach_names:
            for bn in breach_names:
                all_matches.extend(self.match_breach(bn))

        # Deduplicate by institution name
        seen = set()
        unique = []
        for m in all_matches:
            if m.institution not in seen:
                seen.add(m.institution)
                unique.append(m)

        return unique

    def get_all_institutions(self) -> Dict:
        """Retornar todas las instituciones"""
        return self.institutions
