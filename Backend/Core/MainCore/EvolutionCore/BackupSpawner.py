"""
Vibhu-Oska AI-OS — BackupSpawner
Spawns backup models on critical failure during evolution.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("BackupSpawner")


class BackupSpawner:
    """
    Spawns backup model copies when primary fails or rewards are critically low.

    Flow:
    1. Detect critical failure (reward < threshold, NaN collapse, etc.)
    2. Copy current model weights to backup location
    3. Register backup in BackupCore pool
    4. Resume from backup if needed
    """

    def __init__(
        self,
        model_dir: Path,
        backup_dir: Path,
        max_backups: int = 3,
        reward_threshold: float = 0.1,
    ) -> None:
        self._model_dir = model_dir
        self._backup_dir = backup_dir
        self._max_backups = max_backups
        self._reward_threshold = reward_threshold
        self._spawn_count: int = 0
        self._backup_versions: list[str] = []

    async def spawn_backup(
        self,
        reason: str = "low_reward",
        checkpoint_name: str = "sovereign_gpt.pt",
    ) -> Optional[str]:
        """
        Spawn a backup copy of the current model.

        Returns: backup path if successful, None otherwise.
        """
        source = self._model_dir / checkpoint_name
        if not source.exists():
            log.error(f"Cannot spawn backup — checkpoint not found: {source}")
            return None

        # Enforce max backups
        if len(self._backup_versions) >= self._max_backups:
            oldest = self._backup_versions.pop(0)
            oldest_path = self._backup_dir / oldest
            if oldest_path.exists():
                oldest_path.unlink()
                log.info(f"Evicted oldest backup: {oldest}")

        # Create backup
        self._spawn_count += 1
        backup_name = f"backup_{self._spawn_count}_{reason}.pt"
        backup_path = self._backup_dir / backup_name

        self._backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(source, backup_path)
            self._backup_versions.append(backup_name)
            log.info(f"Spawned backup: {backup_name} (reason: {reason})")
            return str(backup_path)
        except Exception as e:
            log.error(f"Backup spawn failed: {e}")
            return None

    async def restore_backup(
        self,
        backup_name: Optional[str] = None,
        checkpoint_name: str = "sovereign_gpt.pt",
    ) -> bool:
        """
        Restore a backup to the main model directory.

        If backup_name is None, restores the most recent backup.
        """
        if not self._backup_versions:
            log.error("No backups available for restore")
            return False

        if backup_name is None:
            backup_name = self._backup_versions[-1]

        backup_path = self._backup_dir / backup_name
        if not backup_path.exists():
            log.error(f"Backup not found: {backup_name}")
            return False

        target = self._model_dir / checkpoint_name

        try:
            shutil.copy2(backup_path, target)
            log.info(f"Restored backup: {backup_name}")
            return True
        except Exception as e:
            log.error(f"Backup restore failed: {e}")
            return False

    def list_backups(self) -> list[dict[str, Any]]:
        """List all available backups."""
        backups = []
        for name in self._backup_versions:
            path = self._backup_dir / name
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                backups.append({
                    "name": name,
                    "size_mb": round(size_mb, 2),
                    "exists": True,
                })
            else:
                backups.append({
                    "name": name,
                    "size_mb": 0,
                    "exists": False,
                })
        return backups

    def get_metrics(self) -> dict[str, Any]:
        return {
            "spawn_count": self._spawn_count,
            "active_backups": len(self._backup_versions),
            "max_backups": self._max_backups,
        }
