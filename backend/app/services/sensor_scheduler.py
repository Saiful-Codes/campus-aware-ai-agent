import asyncio
import logging
import os

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    return os.getenv("SENSOR_SYNC_ENABLED", "true").lower() == "true"


def _get_interval() -> int:
    raw = os.getenv("SENSOR_SYNC_INTERVAL_SECONDS", "300")
    try:
        value = int(raw)
    except ValueError:
        logger.warning(
            "[Scheduler] Invalid SENSOR_SYNC_INTERVAL_SECONDS=%r — using default 300s",
            raw,
        )
        return 300
    if value < 15:
        logger.warning(
            "[Scheduler] SENSOR_SYNC_INTERVAL_SECONDS=%d is below minimum 15 — clamping to 15s",
            value,
        )
        return 15
    return value


async def run_sensor_ingestion_loop() -> None:
    if not _is_enabled():
        logger.info("[Scheduler] Disabled via SENSOR_SYNC_ENABLED — skipping ingestion loop.")
        return

    interval = _get_interval()
    logger.info("[Scheduler] Starting sensor ingestion loop (interval=%ds).", interval)

    try:
        from app.services.influx_sensor_service import sync_latest_sensor_data_to_influx
    except Exception as exc:
        logger.warning(
            "[Scheduler] Influx sensor sync dependency unavailable — scheduler disabled: %s",
            exc,
        )
        return

    while True:
        try:
            result = await asyncio.to_thread(sync_latest_sensor_data_to_influx)
            if result.get("success"):
                logger.info(
                    "[Scheduler] Sync OK — entry_id=%s  timestamp=%s",
                    result.get("entry_id"),
                    result.get("data", {}).get("timestamp"),
                )
            else:
                logger.warning("[Scheduler] Sync reported failure: %s", result)
        except Exception as exc:
            logger.error("[Scheduler] Unexpected error during sync: %s", exc)

        await asyncio.sleep(interval)
