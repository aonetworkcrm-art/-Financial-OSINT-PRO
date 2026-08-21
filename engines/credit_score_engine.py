"""
📊 Credit Score Engine — Motor de Credit Score
Extrae scores de credito desde brechas y fuentes publicas
Basado en los patrones de clarity-automator y fusion-engine
"""
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("credit_score_engine")


@dataclass
class CreditScoreResult:
    """Resultado de una consulta de credit score"""
    score: int = 0
    model: str = ""  # FICO, VantageScore, etc.
    range_min: int = 300
    range_max: int = 850
    grade: str = ""  # Excellent, Good, Fair, Poor
    source: str = ""  # De donde se obtuvo
    trade_lines: int = 0
    inquiries: int = 0
    collections: int = 0
    public_records: int = 0
    utilization: float = 0.0
    age_years: float = 0.0
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.score and not self.grade:
            self.grade = self._calculate_grade()

    def _calculate_grade(self) -> str:
        if self.score >= 800:
            return "Exceptional"
        elif self.score >= 740:
            return "Very Good"
        elif self.score >= 670:
            return "Good"
        elif self.score >= 580:
            return "Fair"
        else:
            return "Poor"

    def to_dict(self):
        return {
            "score": self.score,
            "model": self.model,
            "grade": self.grade,
            "range": f"{self.range_min}-{self.range_max}",
            "source": self.source,
            "trade_lines": self.trade_lines,
            "inquiries": self.inquiries,
            "collections": self.collections,
            "public_records": self.public_records,
            "details": self.details,
        }


class CreditScoreEngine:
    """
    Motor de Credit Score
    Extrae scores desde:
    1. Datos de brechas (LeakCheck Pro)
    2. Regex patterns de reportes de credito
    3. Fuentes publicas (estimaciones)
    """

    # Patrones regex para extraer credit scores (de clarity-automator)
    SCORE_PATTERNS = [
        # "Credit Score: 742" / "Score: 742" / "FICO Score: 742"
        r'(?:score|fico|credit\s*score|vantage)[:\s]*(\d{3})',
        # "742 FICO" / "742 Score" / "742 VantageScore"
        r'(\d{3})\s*(?:fico|score|vantage)',
        # "Score Range: 742/850"
        r'(\d{3})\s*/\s*\d{3}',
        # Standalone 3-digit number in score context
        r'(?:your|the|current)\s+(?:score|credit)\s+(?:is|:)\s*(\d{3})',
    ]

    # Rangos de score por nivel
    SCORE_RANGES = {
        "exceptional": (800, 850),
        "very_good": (740, 799),
        "good": (670, 739),
        "fair": (580, 669),
        "poor": (300, 579),
    }

    # Bancos y sus rangos típicos de score
    BANK_SCORE_INDICATORS = {
        "usbank": {"min": 670, "typical": 720},
        "chase": {"min": 670, "typical": 740},
        "wells_fargo": {"min": 660, "typical": 710},
        "bank_of_america": {"min": 670, "typical": 730},
        "capital_one": {"min": 580, "typical": 680},
        "discover": {"min": 670, "typical": 720},
        "citi": {"min": 680, "typical": 740},
        "navy_federal": {"min": 650, "typical": 700},
    }

    def extract_score_from_text(self, text: str) -> Optional[CreditScoreResult]:
        """Extraer credit score de texto (reporte de credito, breach, etc.)"""
        if not text:
            return None

        for pattern in self.SCORE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    score = int(match)
                    if 300 <= score <= 850:
                        result = CreditScoreResult(
                            score=score,
                            model=self._detect_model(text),
                            source="text_extraction",
                        )
                        return result
                except ValueError:
                    continue

        return None

    def estimate_score_from_breach(self, breach_data: Dict) -> Optional[CreditScoreResult]:
        """
        Estimar credit score desde datos de brechas.
        Si el perfil tiene SSN, puede tener score en la brecha.
        """
        # Buscar score en los campos de la brecha
        for field in ["credit_score", "score", "fico", "vantage"]:
            value = breach_data.get(field, "")
            if value:
                try:
                    score = int(re.sub(r'\D', '', str(value)))
                    if 300 <= score <= 850:
                        return CreditScoreResult(
                            score=score,
                            model="FICO" if "fico" in field.lower() else "Unknown",
                            source="breach_data",
                        )
                except (ValueError, TypeError):
                    continue

        return None

    def estimate_score_from_profile(self, profile_data: Dict) -> CreditScoreResult:
        """
        Estimar credit score basado en el perfil completo.
        Usa indicadores indirectos cuando no hay score directo.
        """
        score = 650  # Base score
        factors = []

        # Factor 1: Instituciones financieras conocidas
        institutions = profile_data.get("institutions", [])
        for inst in institutions:
            inst_name = inst.get("institution", "").lower().replace(" ", "_")
            if inst_name in self.BANK_SCORE_INDICATORS:
                indicator = self.BANK_SCORE_INDICATORS[inst_name]
                score = max(score, indicator["typical"])
                factors.append(f"{inst['institution']}: typical {indicator['typical']}")

        # Factor 2: Cuentas bancarias (más cuentas = mejor historial)
        accounts = profile_data.get("accounts", [])
        if len(accounts) > 5:
            score += 20
            factors.append(f"{len(accounts)} accounts")
        elif len(accounts) > 2:
            score += 10

        # Factor 3: Ausencia de red flags
        if not profile_data.get("collections"):
            score += 10
        if not profile_data.get("public_records"):
            score += 10

        # Factor 4: Edad del historial
        oldest_account = profile_data.get("oldest_account_year")
        if oldest_account:
            try:
                age = 2025 - int(oldest_account)
                if age > 10:
                    score += 15
                elif age > 5:
                    score += 10
            except (ValueError, TypeError):
                pass

        # Cap at 850
        score = min(score, 850)

        return CreditScoreResult(
            score=score,
            model="Estimated",
            source="profile_estimation",
            details={"factors": factors},
        )

    def _detect_model(self, text: str) -> str:
        """Detectar modelo de score usado"""
        text_lower = text.lower()
        if "fico" in text_lower:
            return "FICO"
        elif "vantage" in text_lower:
            return "VantageScore"
        elif "transunion" in text_lower:
            return "TransUnion"
        elif "experian" in text_lower:
            return "Experian"
        elif "equifax" in text_lower:
            return "Equifax"
        return "Unknown"

    def get_grade(self, score: int) -> str:
        """Obtener calificación del score"""
        if score >= 800:
            return "Exceptional"
        elif score >= 740:
            return "Very Good"
        elif score >= 670:
            return "Good"
        elif score >= 580:
            return "Fair"
        else:
            return "Poor"

    def get_grade_color(self, score: int) -> str:
        """Color para el score"""
        if score >= 800:
            return "#00c853"  # Green
        elif score >= 740:
            return "#64dd17"  # Light green
        elif score >= 670:
            return "#ffd600"  # Yellow
        elif score >= 580:
            return "#ff9100"  # Orange
        else:
            return "#e94560"  # Red
