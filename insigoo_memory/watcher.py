"""
文件夹监控器 — 自动检测文件变更并重新扫描
"""
import os, time, threading
from pathlib import Path
from datetime import datetime


class FolderWatcher:
    """监控文件变更，触发自动重扫"""

    def __init__(self, paths: list, callback, interval: int = 30):
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.interval = interval
        self._snapshot = {}
        self._running = False

    def start(self):
        self._snapshot = self._scan()
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            time.sleep(self.interval)
            new_snapshot = self._scan()
            if new_snapshot != self._snapshot:
                changed = []
                for f in set(new_snapshot) - set(self._snapshot):
                    changed.append(f"➕ {f}")
                for f in set(self._snapshot) - set(new_snapshot):
                    changed.append(f"➖ {f}")
                for f in set(self._snapshot) & set(new_snapshot):
                    if self._snapshot[f] != new_snapshot[f]:
                        changed.append(f"✏ {f}")
                if changed:
                    print(f"\n📁 检测到 {len(changed)} 个文件变化")
                    self.callback()
                self._snapshot = new_snapshot

    def _scan(self) -> dict:
        result = {}
        for p in self.paths:
            if not p.exists():
                continue
            for root, _, files in os.walk(str(p)):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        result[fp] = os.path.getmtime(fp)
                    except:
                        pass
        return result
