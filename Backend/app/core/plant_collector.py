import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.domain import Plant, PlantServerConnection

logger = logging.getLogger(__name__)
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
COLLECTOR_SCRIPT = REPOSITORY_ROOT / "server_data" / "collect_server_data.py"
RAW_DATA_DIRECTORY = REPOSITORY_ROOT / "server_data"
CLEANED_DATA_DIRECTORY = REPOSITORY_ROOT / "Cleaned_server_data"
DEFAULT_INGEST_URL = os.getenv(
    "COLLECTOR_INGEST_URL",
    "http://127.0.0.1:8000/api/v1/sensors/ingest",
)


def normalize_server_url(server_ip: str) -> str:
    value = server_ip.strip()
    if not value:
        raise ValueError("Enter the department server IP address or URL.")
    if "://" not in value:
        value = f"http://{value}"

    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise ValueError("The server address is invalid.") from error

    if parsed.scheme not in {"http", "https"} or not hostname or parsed.username or parsed.password:
        raise ValueError("Enter a valid HTTP or HTTPS server address.")

    netloc = parsed.netloc
    if port is None:
        host = hostname
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        netloc = f"{host}:5000"
    path = parsed.path.rstrip("/") or "/api/data"
    return urlunsplit((parsed.scheme, netloc, path, parsed.query, ""))


def create_server_connection(db: Session, plant: Plant, server_ip: str) -> PlantServerConnection:
    source_url = normalize_server_url(server_ip)
    slug = re.sub(r"[^a-z0-9]+", "_", plant.name.lower()).strip("_") or "plant"
    raw_stem = f"server_data_{slug}"
    cleaned_stem = f"cleaned_server_data_{slug}"
    configured_raw_paths = {
        str(Path(connection.raw_csv_path).resolve())
        for connection in db.query(PlantServerConnection).all()
    }
    raw_path = RAW_DATA_DIRECTORY / f"{raw_stem}.csv"
    cleaned_path = CLEANED_DATA_DIRECTORY / f"{cleaned_stem}.csv"

    if str(raw_path.resolve()) in configured_raw_paths or raw_path.exists() or cleaned_path.exists():
        suffix = re.sub(r"[^a-z0-9]+", "", plant.id.lower())[-8:]
        raw_path = RAW_DATA_DIRECTORY / f"{raw_stem}_{suffix}.csv"
        cleaned_path = CLEANED_DATA_DIRECTORY / f"{cleaned_stem}_{suffix}.csv"

    RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    CLEANED_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    raw_path.touch(exist_ok=True)
    cleaned_path.touch(exist_ok=True)
    return PlantServerConnection(
        plant_id=plant.id,
        server_ip=server_ip.strip(),
        source_url=source_url,
        raw_csv_path=str(raw_path),
        cleaned_csv_path=str(cleaned_path),
    )


class PlantCollectorManager:
    def __init__(self):
        self._processes = {}

    def is_running(self, plant_id: str) -> bool:
        process = self._processes.get(plant_id)
        return process is not None and process.poll() is None

    def start(self, connection: PlantServerConnection) -> None:
        if self.is_running(connection.plant_id):
            return

        command = [
            sys.executable,
            str(COLLECTOR_SCRIPT),
            "--url", connection.source_url,
            "--output", connection.raw_csv_path,
            "--cleaned-output", connection.cleaned_csv_path,
            "--backend-url", DEFAULT_INGEST_URL,
            "--plant-id", connection.plant_id,
        ]
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self._processes[connection.plant_id] = subprocess.Popen(
            command,
            cwd=REPOSITORY_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )

    def start_saved(self) -> None:
        db: Session = SessionLocal()
        try:
            for connection in db.query(PlantServerConnection).all():
                try:
                    self.start(connection)
                except OSError:
                    logger.exception("Could not start collector for plant %s", connection.plant_id)
        finally:
            db.close()

    def stop(self, plant_id: str) -> None:
        process = self._processes.pop(plant_id, None)
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    def stop_all(self) -> None:
        for plant_id in list(self._processes):
            self.stop(plant_id)


plant_collector_manager = PlantCollectorManager()