"""
📥 Export Engine — Exportación de resultados
CSV, JSON, TXT, HTML
"""
import csv
import json
import os
from typing import List, Dict
from datetime import datetime
from core.models import SearchResult, Profile, ExtractionResult


class ExportEngine:
    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_csv(self, result: SearchResult, filename: str = None) -> str:
        """Exportar a CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        rows = []
        for profile in result.profiles:
            for email in profile.emails:
                institutions = ", ".join(i.institution for i in profile.institutions)
                rows.append({
                    "name": profile.name,
                    "email": email,
                    "phone": profile.phones[0] if profile.phones else "",
                    "ssn": profile.ssn,
                    "dob": profile.dob,
                    "address": profile.addresses[0] if profile.addresses else "",
                    "password": profile.passwords[0] if profile.passwords else "",
                    "credit_card": profile.credit_cards[0] if profile.credit_cards else "",
                    "institutions": institutions,
                    "breaches": len(profile.breach_sources),
                    "risk_score": profile.risk_score,
                })

            # Si no hay emails, crear una fila con el perfil
            if not profile.emails:
                institutions = ", ".join(i.institution for i in profile.institutions)
                rows.append({
                    "name": profile.name,
                    "email": "",
                    "phone": profile.phones[0] if profile.phones else "",
                    "ssn": profile.ssn,
                    "dob": profile.dob,
                    "address": profile.addresses[0] if profile.addresses else "",
                    "password": profile.passwords[0] if profile.passwords else "",
                    "credit_card": profile.credit_cards[0] if profile.credit_cards else "",
                    "institutions": institutions,
                    "breaches": len(profile.breach_sources),
                    "risk_score": profile.risk_score,
                })

        if not rows:
            return ""

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        return filepath

    def export_json(self, result: SearchResult, filename: str = None) -> str:
        """Exportar a JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        data = {
            "query": result.request.query,
            "query_type": result.request.query_type,
            "timestamp": result.timestamp,
            "metrics": {
                "total_profiles": len(result.profiles),
                "total_breaches": result.total_breaches,
                "total_exposures": result.total_exposures,
                "exposure_score": result.exposure_score,
            },
            "profiles": []
        }

        for profile in result.profiles:
            data["profiles"].append({
                "name": profile.name,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "ssn": profile.ssn,
                "dob": profile.dob,
                "emails": profile.emails,
                "phones": profile.phones,
                "addresses": profile.addresses,
                "passwords": profile.passwords,
                "credit_cards": profile.credit_cards,
                "institutions": [
                    {"name": i.institution, "type": i.institution_type, "confidence": i.confidence}
                    for i in profile.institutions
                ],
                "breach_sources": profile.breach_sources,
                "risk_score": profile.risk_score,
            })

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def export_txt(self, result: SearchResult, filename: str = None) -> str:
        """Exportar a TXT plano"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_{timestamp}.txt"

        filepath = os.path.join(self.output_dir, filename)

        lines = []
        lines.append("=" * 60)
        lines.append("FINANCIAL OSINT TOOL — RESULTADOS")
        lines.append(f"Query: {result.request.query}")
        lines.append(f"Tipo: {result.request.query_type}")
        lines.append(f"Fecha: {result.timestamp}")
        lines.append(f"Perfiles: {len(result.profiles)}")
        lines.append(f"Score de Exposición: {result.exposure_score}/100")
        lines.append("=" * 60)

        for i, profile in enumerate(result.profiles, 1):
            lines.append(f"\n--- PERFIL {i} ---")
            lines.append(f"Nombre: {profile.name}")
            if profile.ssn:
                lines.append(f"SSN: {profile.ssn}")
            if profile.dob:
                lines.append(f"DOB: {profile.dob}")

            if profile.emails:
                lines.append(f"\nEmails ({len(profile.emails)}):")
                for e in profile.emails:
                    lines.append(f"  📧 {e}")

            if profile.phones:
                lines.append(f"\nTeléfonos ({len(profile.phones)}):")
                for p in profile.phones:
                    lines.append(f"  📱 {p}")

            if profile.addresses:
                lines.append(f"\nDirecciones ({len(profile.addresses)}):")
                for a in profile.addresses:
                    lines.append(f"  📍 {a}")

            if profile.passwords:
                lines.append(f"\n🔑 Passwords ({len(profile.passwords)}):")
                for pw in profile.passwords:
                    lines.append(f"  • {pw}")

            if profile.credit_cards:
                lines.append(f"\n💳 Tarjetas ({len(profile.credit_cards)}):")
                for cc in profile.credit_cards:
                    lines.append(f"  • {cc}")

            if profile.institutions:
                lines.append(f"\n🏦 Instituciones ({len(profile.institutions)}):")
                for inst in profile.institutions:
                    lines.append(f"  • {inst.institution} ({inst.institution_type})")

            if profile.breach_sources:
                lines.append(f"\n📋 Brechas ({len(profile.breach_sources)}):")
                for b in profile.breach_sources:
                    lines.append(f"  • {b}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return filepath

    def export_all(self, result: SearchResult) -> Dict[str, str]:
        """Exportar en todos los formatos"""
        return {
            "csv": self.export_csv(result),
            "json": self.export_json(result),
            "txt": self.export_txt(result),
        }
