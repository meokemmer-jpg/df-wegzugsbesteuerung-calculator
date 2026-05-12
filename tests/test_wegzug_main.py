"""Tests fuer WegzugCalculator [CRUX-MK]."""
import pytest
from src.wegzug_main import (
    WegzugCalculator, ASTG_WESENTLICHE_BETEILIGUNG_PCT,
    DE_SPITZENSTEUERSATZ, FLORIDA_STATE_INCOME_TAX
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("DF_WEGZUG_REAL_ENABLED", raising=False)
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)


def test_default_sandbox_mode():
    c = WegzugCalculator()
    assert c.real_enabled is False


def test_real_mode_requires_phronesis(monkeypatch):
    monkeypatch.setenv("DF_WEGZUG_REAL_ENABLED", "true")
    with pytest.raises(RuntimeError, match="K13-PAV-VIOLATION"):
        WegzugCalculator()


def test_wesentliche_beteiligung_threshold():
    c = WegzugCalculator()
    assert c.is_wesentliche_beteiligung(1.0) is True
    assert c.is_wesentliche_beteiligung(0.99) is False
    assert c.is_wesentliche_beteiligung(50.0) is True


def test_de_steuer_teileinkuenfteverfahren():
    """1M EUR fiktiver Gewinn: 60% steuerpflichtig × 45% × (1+5.5%)."""
    c = WegzugCalculator()
    steuer, pct = c.compute_de_steuer(1_000_000.0)
    # 1M × 0.6 × 0.45 × 1.055 = 284,850
    assert 280_000 < steuer < 290_000
    assert 28.0 < pct < 29.0


def test_de_steuer_zero_gewinn():
    c = WegzugCalculator()
    steuer, pct = c.compute_de_steuer(0.0)
    assert steuer == 0.0
    assert pct == 0.0


def test_usa_steuer_florida_no_state_tax():
    """USA: 20% Federal LTCG + 3.8% NIIT, 0% Florida."""
    c = WegzugCalculator(eur_usd_rate=1.08)
    steuer_usd, pct = c.compute_usa_steuer(1_000_000.0, niit_applicable=True)
    # 1M EUR × 1.08 = 1.08M USD × (20% + 3.8% + 0%) = 257,040
    assert 250_000 < steuer_usd < 260_000
    assert 23.0 < pct < 24.0


def test_usa_steuer_no_niit():
    c = WegzugCalculator(eur_usd_rate=1.08)
    steuer_usd, pct = c.compute_usa_steuer(1_000_000.0, niit_applicable=False)
    # 1M × 1.08 × 20% = 216,000
    assert 215_000 < steuer_usd < 217_000
    assert pct == 20.0


def test_sec883_carve_out_hospitality():
    c = WegzugCalculator()
    assert c.sec883_carve_out_applicable("hospitality", 51.0) is True
    assert c.sec883_carve_out_applicable("retail", 51.0) is False
    assert c.sec883_carve_out_applicable("hospitality", 30.0) is False


def test_compute_full_calculation():
    c = WegzugCalculator()
    calc = c.compute(
        fiktiver_gewinn_eur=5_000_000.0,
        ownership_pct=51.0,
        business_type="hospitality",
    )
    assert calc.fiktiver_veraeusserungsgewinn_eur == 5_000_000.0
    assert calc.de_steuerschuld_eur > 0
    assert calc.usa_steuerschuld_usd > 0
    assert calc.sec883_carve_out_applicable is True


def test_compute_delta_savings_usa_typically_cheaper():
    """Bei hoher Summe + Hospitality: USA cheaper."""
    c = WegzugCalculator()
    calc = c.compute(5_000_000.0, 51.0, "hospitality")
    # DE ~28% effektiv vs USA ~23% -> USA cheaper -> delta positive
    assert calc.delta_eur_savings > 0


def test_to_report_includes_disclaimer():
    c = WegzugCalculator()
    report = c.to_report()
    assert "disclaimer" in report
    assert "StBerG" in report["disclaimer"]
    assert report["source_mode"] == "sandbox-mock"


def test_florida_state_tax_zero_constant():
    """Florida State-Tax = 0 (Cape-Coral Standortvorteil)."""
    assert FLORIDA_STATE_INCOME_TAX == 0.00


def test_eur_usd_rate_configurable():
    c = WegzugCalculator(eur_usd_rate=1.10)
    assert c.eur_usd_rate == 1.10
