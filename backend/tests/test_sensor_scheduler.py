import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.sensor_scheduler import _get_interval, _is_enabled, run_sensor_ingestion_loop


# --- _is_enabled ---

def test_is_enabled_true_by_default():
    env = {k: v for k, v in os.environ.items() if k != "SENSOR_SYNC_ENABLED"}
    with patch.dict(os.environ, env, clear=True):
        assert _is_enabled() is True


def test_is_enabled_true_when_set_to_true():
    with patch.dict(os.environ, {"SENSOR_SYNC_ENABLED": "true"}):
        assert _is_enabled() is True


def test_is_enabled_false_when_set_to_false():
    with patch.dict(os.environ, {"SENSOR_SYNC_ENABLED": "false"}):
        assert _is_enabled() is False


def test_is_enabled_case_insensitive():
    with patch.dict(os.environ, {"SENSOR_SYNC_ENABLED": "FALSE"}):
        assert _is_enabled() is False


# --- _get_interval ---

def test_get_interval_returns_default_when_env_not_set():
    env = {k: v for k, v in os.environ.items() if k != "SENSOR_SYNC_INTERVAL_SECONDS"}
    with patch.dict(os.environ, env, clear=True):
        assert _get_interval() == 300


def test_get_interval_reads_value_from_env():
    with patch.dict(os.environ, {"SENSOR_SYNC_INTERVAL_SECONDS": "60"}):
        assert _get_interval() == 60


def test_get_interval_returns_default_when_env_is_non_numeric():
    with patch.dict(os.environ, {"SENSOR_SYNC_INTERVAL_SECONDS": "notanumber"}):
        assert _get_interval() == 300


def test_get_interval_clamps_to_15_when_below_minimum():
    with patch.dict(os.environ, {"SENSOR_SYNC_INTERVAL_SECONDS": "5"}):
        assert _get_interval() == 15


def test_get_interval_accepts_minimum_boundary():
    with patch.dict(os.environ, {"SENSOR_SYNC_INTERVAL_SECONDS": "15"}):
        assert _get_interval() == 15


# --- run_sensor_ingestion_loop ---

def test_loop_calls_sync_at_least_once_on_success():
    call_log = []

    def fake_sync():
        n = len(call_log)
        result = {"success": True, "entry_id": str(n), "data": {"timestamp": "2025-01-01T00:00:00Z"}}
        call_log.append(result)
        return result

    async def _run():
        task = asyncio.create_task(run_sensor_ingestion_loop())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    with patch("app.services.sensor_scheduler.sync_latest_sensor_data_to_influx", fake_sync), \
         patch("app.services.sensor_scheduler._get_interval", return_value=0), \
         patch("app.services.sensor_scheduler._is_enabled", return_value=True):
        asyncio.run(_run())

    assert len(call_log) >= 1


def test_loop_continues_after_sync_raises_exception():
    call_log = []

    def fake_sync():
        n = len(call_log)
        call_log.append(n)
        if n == 0:
            raise RuntimeError("simulated ThingSpeak timeout")
        return {"success": True, "entry_id": str(n), "data": {"timestamp": "2025-01-01T00:00:01Z"}}

    async def _run():
        task = asyncio.create_task(run_sensor_ingestion_loop())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    with patch("app.services.sensor_scheduler.sync_latest_sensor_data_to_influx", fake_sync), \
         patch("app.services.sensor_scheduler._get_interval", return_value=0), \
         patch("app.services.sensor_scheduler._is_enabled", return_value=True):
        asyncio.run(_run())

    assert len(call_log) >= 2, "Loop must continue even after an exception"


def test_loop_continues_after_sync_returns_failure_dict():
    call_log = []

    def fake_sync():
        call_log.append(True)
        return {"success": False, "error": "No feed from ThingSpeak"}

    async def _run():
        task = asyncio.create_task(run_sensor_ingestion_loop())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    with patch("app.services.sensor_scheduler.sync_latest_sensor_data_to_influx", fake_sync), \
         patch("app.services.sensor_scheduler._get_interval", return_value=0), \
         patch("app.services.sensor_scheduler._is_enabled", return_value=True):
        asyncio.run(_run())

    assert len(call_log) >= 2, "Loop must continue even when sync reports failure"


def test_loop_exits_immediately_when_disabled():
    call_log = []

    def fake_sync():
        call_log.append(True)
        return {"success": True, "entry_id": "1", "data": {"timestamp": "t"}}

    async def _run():
        await asyncio.wait_for(run_sensor_ingestion_loop(), timeout=0.5)

    with patch("app.services.sensor_scheduler.sync_latest_sensor_data_to_influx", fake_sync), \
         patch("app.services.sensor_scheduler._is_enabled", return_value=False):
        asyncio.run(_run())

    assert len(call_log) == 0, "Sync must not be called when SENSOR_SYNC_ENABLED=false"
