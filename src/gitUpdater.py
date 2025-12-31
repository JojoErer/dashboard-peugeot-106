# git_updater.py
import subprocess
import threading
import socket
from pathlib import Path
import shutil

class GitUpdater:
    def __init__(self, repo_path, version_getter, status_callback=None):
        self.repo_path = Path(repo_path)
        self.version_getter = version_getter
        self.status_callback = status_callback
        self._updating = False

    # -----------------------------
    # Utilities
    # -----------------------------
    def _set_status(self, message):
        print(f"[GIT] {message}")
        if self.status_callback:
            self.status_callback(message)

    def _has_internet(self, timeout=3):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            return False

    def _git_available(self):
        return shutil.which("git") is not None

    def _get_git_commit(self):
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() or "unknown"
        except Exception:
            return "unknown"

    # -----------------------------
    # Public API (called by main.py)
    # -----------------------------
    def handle_update_request(self):
        if self._updating:
            self._set_status("Update already in progress")
            return

        if not self.repo_path.exists():
            self._set_status("Repository not found")
            return

        if not self._git_available():
            self._set_status("Git is not installed")
            return

        if not self._has_internet():
            self._set_status("No internet connection")
            return

        self._updating = True
        threading.Thread(target=self._run_git_pull, daemon=True).start()

    # -----------------------------
    # Worker
    # -----------------------------
    def _run_git_pull(self):
        old_version = self.version_getter()
        old_commit = self._get_git_commit()

        self._set_status(f"Updating from v{old_version} ({old_commit})")

        try:
            result = subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode != 0:
                self._set_status(f"Update failed:\n{result.stderr.strip()}")
                return

            new_commit = self._get_git_commit()
            new_version = self.version_getter()

            self._set_status(
                "Update successful\n"
                f"Version: {old_version} → {new_version}\n"
                f"Commit: {old_commit} → {new_commit}\n"
                "Restart recommended"
            )

        except Exception as e:
            self._set_status(f"Update error: {e}")

        finally:
            self._updating = False
