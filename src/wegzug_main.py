"""
Wegzugsbesteuerung-Calculator [CRUX-MK]
§6 AStG (Aussensteuergesetz) Berechnung mit DBA-DE-USA Comparison.

DISCLAIMER: KEIN Steuer-Rat (StBerG §3). Nur Vorabschaetzung.

K_0 Touch: 6-7-stellige EUR-Belastung moeglich
Q_0 Touch: Familien-Steuer-Class-Optimierung
"""
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


# §6 AStG Wesentlichkeits-Schwelle
ASTG_WESENTLICHE_BETEILIGUNG_PCT = 1.0  # >=1% Beteiligung an Kap-Gesellschaft

# Teileinkuenfteverfahren §3 Nr. 40 EStG
TEILEINKUENFTE_STEUERFREI_PCT = 40.0

# Spitzensteuersatz DE 2026 (Reichensteuer)
DE_SPITZENSTEUERSATZ = 0.45
DE_SOLIDARITAETSZUSCHLAG = 0.055  # 5.5% auf Steuer

# USA Federal LTCG Top-Bracket
USA_LTCG_TOP_BRACKET = 0.20
USA_NET_INVESTMENT_INCOME_TAX = 0.038  # NIIT 3.8% (>$250k MFJ)

# Florida State Income Tax
FLORIDA_STATE_INCOME_TAX = 0.00  # 0%


@dataclass
class WegzugCalculation:
    """Steuerberechnung-Ergebnis."""
    fiktiver_veraeusserungsgewinn_eur: float
    de_steuerschuld_eur: float
    de_effektiver_satz_pct: float
    usa_steuerschuld_usd: float
    usa_effektiver_satz_pct: float
    delta_eur_savings: float  # positive = USA cheaper
    sec883_carve_out_applicable: bool
    timestamp: str


class WegzugCalculator:
    """§6 AStG Wegzugssteuer-Calculator (Vorabschaetzung)."""

    def __init__(self, real_enabled: Optional[bool] = None, eur_usd_rate: float = 1.08):
        if real_enabled is None:
            real_enabled = os.environ.get("DF_WEGZUG_REAL_ENABLED", "false").lower() == "true"
        self.real_enabled = real_enabled
        self.phronesis_ticket = os.environ.get("PHRONESIS_TICKET", "MISSING")
        self.eur_usd_rate = eur_usd_rate

        if self.real_enabled and self.phronesis_ticket == "MISSING":
            raise RuntimeError(
                "K13-PAV-VIOLATION: Wegzug-Real-Mode ohne PHRONESIS_TICKET. "
                "Steuerberater-Coordination Pflicht."
            )

    def is_wesentliche_beteiligung(self, ownership_pct: float) -> bool:
        """§6 AStG: >=1% Beteiligung loest Wegzugssteuer aus."""
        return ownership_pct >= ASTG_WESENTLICHE_BETEILIGUNG_PCT

    def compute_de_steuer(self, fiktiver_gewinn_eur: float) -> tuple[float, float]:
        """DE-Steuer auf fiktiven Veraeusserungsgewinn (Teileinkuenfteverfahren).

        Returns: (steuerschuld_eur, effektiver_satz)
        """
        # Teileinkuenfteverfahren: 60% steuerpflichtig, 40% steuerfrei
        steuerpflichtiger_anteil = fiktiver_gewinn_eur * (1.0 - TEILEINKUENFTE_STEUERFREI_PCT / 100.0)
        einkommensteuer = steuerpflichtiger_anteil * DE_SPITZENSTEUERSATZ
        soli = einkommensteuer * DE_SOLIDARITAETSZUSCHLAG
        gesamt = einkommensteuer + soli
        effektiver_satz = (gesamt / fiktiver_gewinn_eur * 100) if fiktiver_gewinn_eur > 0 else 0.0
        return (round(gesamt, 2), round(effektiver_satz, 2))

    def compute_usa_steuer(self, gewinn_eur: float, niit_applicable: bool = True) -> tuple[float, float]:
        """USA-Steuer auf Capital-Gain (Florida 0% State).

        Returns: (steuerschuld_usd, effektiver_satz)
        """
        gewinn_usd = gewinn_eur * self.eur_usd_rate
        federal_ltcg = gewinn_usd * USA_LTCG_TOP_BRACKET
        niit = gewinn_usd * USA_NET_INVESTMENT_INCOME_TAX if niit_applicable else 0.0
        state = gewinn_usd * FLORIDA_STATE_INCOME_TAX
        gesamt = federal_ltcg + niit + state
        effektiver_satz = (gesamt / gewinn_usd * 100) if gewinn_usd > 0 else 0.0
        return (round(gesamt, 2), round(effektiver_satz, 2))

    def sec883_carve_out_applicable(self, business_type: str, ownership_pct: float) -> bool:
        """Sec-883 Internal Revenue Code: USA-LLC fuer International-Hospitality.

        Vereinfachte Pruefung. Realitaet braucht Steuerberater.
        """
        return business_type.lower() in ("hospitality", "shipping", "aircraft") and ownership_pct >= 50.0

    def compute(
        self,
        fiktiver_gewinn_eur: float,
        ownership_pct: float,
        business_type: str = "hospitality",
        niit_applicable: bool = True,
    ) -> WegzugCalculation:
        """Voll-Berechnung."""
        de_steuer, de_pct = self.compute_de_steuer(fiktiver_gewinn_eur)
        usa_steuer, usa_pct = self.compute_usa_steuer(fiktiver_gewinn_eur, niit_applicable)
        usa_steuer_eur = usa_steuer / self.eur_usd_rate
        delta = de_steuer - usa_steuer_eur  # positive = USA cheaper

        return WegzugCalculation(
            fiktiver_veraeusserungsgewinn_eur=fiktiver_gewinn_eur,
            de_steuerschuld_eur=de_steuer,
            de_effektiver_satz_pct=de_pct,
            usa_steuerschuld_usd=usa_steuer,
            usa_effektiver_satz_pct=usa_pct,
            delta_eur_savings=round(delta, 2),
            sec883_carve_out_applicable=self.sec883_carve_out_applicable(business_type, ownership_pct),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_report(self) -> dict:
        """Mock-Run fuer Sandbox: Annahme HeyLou-Anteil ~5M EUR fiktiver Gewinn."""
        calc = self.compute(
            fiktiver_gewinn_eur=5_000_000.0,
            ownership_pct=51.0,  # Mehrheits-Anteil
            business_type="hospitality",
            niit_applicable=True,
        )
        return {
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_mode": "real" if self.real_enabled else "sandbox-mock",
            "phronesis_ticket": self.phronesis_ticket,
            "disclaimer": "KEIN Steuer-Rat (StBerG §3). Steuerberater-Pflicht vor Real-Decision.",
            "eur_usd_rate": self.eur_usd_rate,
            "calculation": asdict(calc),
        }
