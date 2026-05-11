import os
import signal
import shutil
import subprocess
import time
from typing import Optional

import requests

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings


class OllamaControlService:
    service_label = "com.ollama.ollama"

    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.process: Optional[subprocess.Popen] = None

    def status(self) -> dict:
        if settings.IS_CLOUD:
            return {
                "installed": False,
                "running": False,
                "api_running": False,
                "base_url": self.ollama_url,
                "pid": None,
                "launchd_service": None,
                "message": "Ollama no está disponible en modo cloud. Usa Gemini Cloud.",
                "can_start": False,
                "can_stop": False,
                "mode": "cloud-disabled"
            }
        binary = shutil.which("ollama")
        launchd = self._launchd_info()
        api_running = self._api_running()
        pids = self._serve_pids()
        pid = launchd.get("pid") or (pids[0] if pids else None)
        process_running = bool(pid)
        running = api_running
        mode = "launchd" if launchd.get("loaded") else "process" if process_running or self._child_running() else "unmanaged"

        return {
            "installed": bool(binary),
            "binary": binary,
            "base_url": self.ollama_url,
            "running": running,
            "api_running": api_running,
            "process_running": process_running,
            "pid": pid,
            "pids": pids,
            "mode": mode,
            "launchd_service": launchd,
            "models": self._models() if api_running else [],
            "can_start": bool(binary or launchd.get("loaded")) and not running,
            "can_stop": running,
        }

    def start(self) -> dict:
        current = self.status()
        if current["running"]:
            current["message"] = "Ollama ya está encendido."
            return current

        errors = []
        launchd = current.get("launchd_service", {})
        if launchd.get("loaded"):
            result = self._run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{self.service_label}"])
            if result.returncode != 0:
                errors.append(result.stderr.strip() or result.stdout.strip())

        if not self._wait_for_api(12):
            open_result = self._run(["open", "-a", "Ollama"], timeout=8)
            if open_result.returncode != 0:
                errors.append(open_result.stderr.strip() or open_result.stdout.strip())

        if not self._wait_for_api(12) and current.get("binary"):
            self.process = subprocess.Popen(
                [current["binary"], "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            self._wait_for_api(12)

        updated = self.status()
        updated["message"] = "Ollama encendido." if updated["running"] else "No se pudo encender Ollama."
        if errors and not updated["running"]:
            updated["errors"] = errors
        return updated

    def stop(self) -> dict:
        current = self.status()
        if not current["running"]:
            current["message"] = "Ollama ya está apagado."
            return current

        errors = []
        if current.get("launchd_service", {}).get("loaded"):
            result = self._run(["launchctl", "bootout", f"gui/{os.getuid()}/{self.service_label}"])
            if result.returncode != 0:
                errors.append(result.stderr.strip() or result.stdout.strip())

        time.sleep(1.5)
        if self._api_running() or self._serve_pids():
            for pid in self._serve_pids():
                self._terminate_pid(pid)

        if self._child_running():
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self._wait_for_shutdown(8)
        updated = self.status()
        updated["message"] = "Ollama apagado." if not updated["running"] else "No se pudo apagar Ollama completamente."
        if errors and updated["running"]:
            updated["errors"] = errors
        return updated

    def restart(self) -> dict:
        self.stop()
        return self.start()

    def _run(self, command: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except (FileNotFoundError, subprocess.TimeoutExpired) as error:
            return subprocess.CompletedProcess(command, 1, "", str(error))

    def _launchd_info(self) -> dict:
        result = self._run(["launchctl", "list"], timeout=5)
        info = {
            "label": self.service_label,
            "loaded": False,
            "pid": None,
            "last_status": None,
        }
        if result.returncode != 0:
            info["error"] = result.stderr.strip() or result.stdout.strip()
            return info

        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 3 or parts[-1] != self.service_label:
                continue
            info["loaded"] = True
            info["pid"] = int(parts[0]) if parts[0].isdigit() else None
            info["last_status"] = None if parts[1] == "-" else parts[1]
            break
        return info

    def _api_running(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/tags", timeout=2)
            return response.ok
        except requests.RequestException:
            return False

    def _models(self) -> list:
        try:
            response = requests.get(f"{self.ollama_url}/tags", timeout=3)
            response.raise_for_status()
            data = response.json()
            return [item.get("name") for item in data.get("models", []) if item.get("name")]
        except requests.RequestException:
            return []

    def _serve_pids(self) -> list[int]:
        result = self._run(["pgrep", "-x", "ollama"], timeout=5)
        if result.returncode != 0:
            return []
        pids = []
        for item in result.stdout.splitlines():
            if not item.strip().isdigit():
                continue
            pid = int(item.strip())
            if pid == os.getpid():
                continue
            details = self._run(["ps", "-p", str(pid), "-o", "args="], timeout=5)
            command = details.stdout.strip()
            if command.endswith("ollama serve") or "ollama serve" in command:
                pids.append(pid)
        return pids

    def _terminate_pid(self, pid: int):
        if pid == os.getpid():
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        except PermissionError:
            return

    def _child_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def _wait_for_api(self, seconds: int) -> bool:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self._api_running():
                return True
            time.sleep(0.5)
        return False

    def _wait_for_shutdown(self, seconds: int) -> bool:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if not self._api_running() and not self._serve_pids():
                return True
            time.sleep(0.5)
        return False


ollama_control_service = OllamaControlService()
