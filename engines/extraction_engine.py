"""
⚡ Extraction Engine — Motor principal
"""
import re
import time
import logging
from typing import List, Dict, Optional
from core.models import (
    BreachRecord, Profile, ExtractionResult,
    InstitutionMatch, SearchResult, SearchRequest
)
from engines.leakcheck_engine import LeakCheckEngine
from engines.institution_matcher import InstitutionMatcher, INSTITUTIONS
from engines.credit_score_engine import CreditScoreEngine
from engines.address_engine import AddressEngine

logger = logging.getLogger("extraction_engine")


class ExtractionEngine:

    def __init__(self, leakcheck_key=None, dehashed_key=None, intelx_key=None):
        self.leakcheck = LeakCheckEngine(api_key=leakcheck_key)
        self.matcher = InstitutionMatcher()
        self.credit = CreditScoreEngine()
        self.address = AddressEngine(leakcheck_key=leakcheck_key)
        # Store extra keys for future use
        self._dehashed_key = dehashed_key
        self._intelx_key = intelx_key

    def full_search(self, query, query_type="auto", institutions=None):
        request = SearchRequest(query=query, query_type=query_type, institutions=institutions or [])

        if query_type == "auto" and self._is_address(query):
            query_type = "address"

        if query_type == "address":
            ap = self.address.full_address_search(query)
            profile = self._addr_to_profile(ap)
            profiles = [profile] if profile else []
        else:
            records = self.leakcheck.search(query, query_type)
            profiles = self._build_profiles(records)
            if institutions:
                profiles = self._filter_inst(profiles, institutions)

        total_breaches = sum(len(p.breach_sources) for p in profiles)
        total_exposures = sum(len(p.emails) + len(p.phones) + len(p.passwords) + len(p.credit_cards) for p in profiles)
        avg_score = sum(p.risk_score for p in profiles) // len(profiles) if profiles else 0

        return SearchResult(request=request, profiles=profiles, total_breaches=total_breaches,
                           total_exposures=total_exposures, exposure_score=avg_score)

    def _is_address(self, q):
        return bool(re.search(r'\d{5}', q)) and bool(re.search(r'[A-Za-z]{3,}', q))

    def _addr_to_profile(self, ap):
        if not ap or (not ap.emails and not ap.phones and not ap.passwords):
            return None
        p = Profile(name=ap.name, ssn=ap.ssn, dob=ap.dob, emails=ap.emails, phones=ap.phones,
                    addresses=[ap.address], passwords=ap.passwords, credit_cards=ap.credit_cards,
                    breach_sources=ap.breach_sources, risk_score=ap.risk_score)
        for inst in ap.institutions:
            p.institutions.append(InstitutionMatch(institution=inst["name"], institution_type=inst["type"],
                                                   confidence=0.8, evidence=inst["source"]))
        if ap.credit_score:
            p.raw_data = {"credit_score": ap.credit_score.score, "credit_grade": ap.credit_score.grade}
        return p

    def _build_profiles(self, records):
        groups = {}
        for r in records:
            key = r.email or r.phone or r.name or "unknown"
            groups.setdefault(key, []).append(r)
        return [p for g in groups.values() if (p := self._merge(g))]

    def _merge(self, records):
        if not records:
            return None
        p = Profile()
        emails, phones, passwords, cards, breaches = set(), set(), set(), set(), set()
        for r in records:
            if r.email: emails.add(r.email)
            if r.phone: phones.add(self._np(r.phone))
            if r.first_name: p.first_name = p.first_name or r.first_name
            if r.last_name: p.last_name = p.last_name or r.last_name
            if r.ssn: p.ssn = p.ssn or r.ssn
            if r.dob: p.dob = p.dob or r.dob
            if r.password: passwords.add(r.password)
            if r.credit_card: cards.add(r.credit_card)
            if r.breach_name: breaches.add(r.breach_name)
        p.emails, p.phones, p.passwords, p.credit_cards, p.breach_sources = list(emails), list(phones), list(passwords), list(cards), list(breaches)
        if p.first_name and p.last_name:
            p.name = f"{p.first_name} {p.last_name}"
        for e in p.emails: p.institutions.extend(self.matcher.match_email(e))
        for ph in p.phones: p.institutions.extend(self.matcher.match_phone(ph))
        for b in p.breach_sources: p.institutions.extend(self.matcher.match_breach(b))
        cs = self.credit.estimate_score_from_profile({"institutions": [{"institution": i.institution} for i in p.institutions], "accounts": p.credit_cards})
        p.raw_data = {"credit_score": cs.score, "credit_grade": cs.grade}
        p.risk_score = self._risk(p)
        return p

    def _np(self, phone):
        d = re.sub(r'\D', '', phone)
        if d.startswith('1') and len(d) == 11: d = d[1:]
        return f"+1-{d[:3]}-{d[3:6]}-{d[6:]}" if len(d) == 10 else phone

    def _risk(self, p):
        s = 0
        if p.ssn: s += 25
        if p.passwords: s += 20
        if p.credit_cards: s += 15
        if p.emails: s += 5
        if p.phones: s += 5
        if p.institutions: s += min(len(p.institutions) * 5, 20)
        return min(s, 100)

    def _filter_inst(self, profiles, institutions):
        f = [p for p in profiles if any(i.institution.lower() in [x.lower() for x in institutions] for i in p.institutions)]
        return f if f else profiles

    def search_by_address(self, addr, institutions=None): return self.full_search(addr, "address", institutions)
    def search_by_email(self, email): return self.full_search(email, "email")
    def search_by_phone(self, phone): return self.full_search(phone, "phone")
    def search_by_ssn(self, ssn): return self.full_search(ssn, "ssn")
    def search_by_name(self, name): return self.full_search(name, "name")
    def get_portals(self): return EXTRACTION_PORTALS
    def get_institutions(self): return self.matcher.get_all_institutions()


EXTRACTION_PORTALS = {
    "leakcheck": {"name": "LeakCheck", "type": "breach", "status": "active"},
    "xposedornot": {"name": "XposedOrNot", "type": "breach", "status": "active"},
    "credit_score": {"name": "Credit Score Estimator", "type": "financial", "status": "active"},
    "institution_matcher": {"name": "Institution Matcher", "type": "financial", "status": "active"},
}
