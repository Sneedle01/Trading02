from core.utils import setup_logger, current_time_str

log = setup_logger("TestLogger")
log.info(f"Logger aktiv – Uhrzeit: {current_time_str()}")
