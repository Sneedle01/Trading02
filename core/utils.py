"""
Hilfsfunktionen für Logging, Zeitstempel und Fehlerbehandlung.

Diese Datei enthält zentrale Hilfsmethoden, die von anderen Modulen wiederverwendet werden können,
z. B. zur einheitlichen Protokollierung oder zur Umrechnung von Zeitformaten.
"""

import os
import logging
from datetime import datetime


def setup_logger(name: str, log_file: str = "data/logs/bot.log") -> logging.Logger:
    """
    Erstellt und konfiguriert einen Logger mit Datei- und Konsolenausgabe.

    @param name: Name des Loggers
    @param log_file: Pfad zur Log-Datei
    @return: Konfigurierter Logger
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger


def current_time_str() -> str:
    """
    Gibt den aktuellen Zeitstempel als formatierten String zurück.

    @return: Zeitstempel, z. B. '2025-05-01 15:32:12'
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def safe_float(value, fallback=0.0):
    """
    Versucht, einen Wert in float umzuwandeln. Gibt einen Fallback zurück, wenn das fehlschlägt.

    @param value: Eingabewert
    @param fallback: Rückgabewert bei Fehler
    @return: Float-Zahl oder Fallback
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return fallback
