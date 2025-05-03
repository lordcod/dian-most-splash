from __future__ import annotations

import contextlib
import os
from pathlib import Path
import time
from typing import TYPE_CHECKING
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Lock
import logging

if TYPE_CHECKING:
    from client import Client

lock = Lock()

_log = logging.getLogger(__name__)


class DianHandler(FileSystemEventHandler):
    def __init__(self, client: Client, dian: str):
        self.client = client
        self.dian_path = Path(dian)

    def on_modified(self, event):
        if str(self.dian_path) != event.src_path:
            return
        _log.debug('Receive dian data %s', self.dian_path)
        self.client.dian_parser.up()

    def observe(self):
        self.client.dian_parser.up()

        self.observer = Observer()
        self.observer.schedule(self, self.dian_path.parent, recursive=True)
        self.observer.start()

    def stop(self):
        _log.warning('Stopped...')
        self.observer.stop()
        self.observer.join()
