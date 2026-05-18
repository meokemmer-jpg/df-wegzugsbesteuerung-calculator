
# K12+K13+K16 Trinity-CONTRARIAN 2026-05-17 (Cross-LLM-validated)
def k12_provenance(payload: bytes, key: bytes = b"df-trinity-contrarian-v1") -> dict:
    import hashlib, hmac
    return {
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "hmac_sha256": hmac.new(key, payload, hashlib.sha256).hexdigest(),
    }

def k13_anchor(payload_hash: str) -> dict:
    from datetime import datetime, timezone
    return {
        "anchor_type": "rfc3161-mock",
        "iso_ts": datetime.now(timezone.utc).isoformat(),
        "payload_hash": payload_hash,
    }

def k16_lock_or_exit(df_name: str):
    import fcntl, os, sys
    lock_path = f"/tmp/df-trinity-{df_name}.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        sys.exit(3)

"""Tests fuer AdapterOrchestrator [CRUX-MK]."""
import json
import tempfile
from pathlib import Path
import pytest
from src.adapter_orchestrator import AdapterOrchestrator


@pytest.fixture
def tmp_state_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_should_run_default_ok(tmp_state_dir):
    o = AdapterOrchestrator(state_dir=tmp_state_dir)
    ok, _ = o.should_run()
    assert ok is True


def test_should_run_blocked_by_stop(tmp_state_dir):
    o = AdapterOrchestrator(state_dir=tmp_state_dir)
    o.stop_flag.write_text("halt")
    ok, _ = o.should_run()
    assert ok is False


def test_run_daily_persists_report(tmp_state_dir):
    o = AdapterOrchestrator(state_dir=tmp_state_dir)
    result = o.run_daily()
    assert result["status"] == "ok"
    report = json.loads(Path(result["report_path"]).read_text())
    assert "calculation" in report
    assert "disclaimer" in report


def test_run_daily_skipped(tmp_state_dir):
    o = AdapterOrchestrator(state_dir=tmp_state_dir)
    o.stop_flag.write_text("halt")
    result = o.run_daily()
    assert result["status"] == "skipped"
