from __future__ import annotations

import contextlib
import os
import time
from typing import TYPE_CHECKING
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Lock
import logging

if TYPE_CHECKING:
    from client import Client

send_lock = Lock()
receive_lock = Lock()

_log = logging.getLogger(__name__)
PREFIX = '\uFEFF'


class FileHandler(FileSystemEventHandler):
    observer = None

    def __init__(self, client: Client,  exchange: str):
        self.client = client
        self.exchange = exchange
        self.splash_send = os.path.join(exchange, 'splash_send.txt')
        self.splash_receive = os.path.join(exchange, 'splash_receive.txt')

    def send_response(self, response: str):
        if not response:
            return
        _log.debug('Send response %s', response)
        with send_lock:
            with open(self.splash_receive, 'wb+') as file:
                file.write(response.encode())
            time.sleep(0.5)

    def on_modified(self, event):
        if event.src_path != self.splash_send:
            return

        with contextlib.suppress(OSError), receive_lock:
            time.sleep(0.1)

            with open(self.splash_send, 'rb') as file:
                text = file.read().decode().removeprefix(PREFIX)
            if not text:
                return

            _log.debug('Receive splash data %s', text)
            try:
                response = self.client.file_parser.parse_file(text)
            except Exception as exc:
                _log.exception(
                    "An error occurred while parsing the splash file",
                    exc_info=exc)
            else:
                self.send_response(response)

            with open(self.splash_send, 'rb') as file1:
                with open(self.splash_send, 'wb+') as file2:
                    file2.write(
                        file1.read().decode().removeprefix(PREFIX+text).encode())

    def observe(self):
        self.observer = Observer()
        self.observer.schedule(self, self.exchange, recursive=True)
        self.observer.start()

    def stop(self):
        _log.warning('Stopped...')
        self.observer.stop()
        self.observer.join()
