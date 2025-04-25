import contextlib
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Lock
import logging

from files import FileParser

lock = Lock()

_log = logging.getLogger(__name__)


class FileHandler(FileSystemEventHandler):
    observer = None

    def __init__(self, parser: FileParser,  exchange: str):
        self.parser = parser
        self.exchange = exchange
        self.splash_send = os.path.join(exchange, 'splash_send.txt')
        self.splash_receive = os.path.join(exchange, 'splash_receive.txt')

    def send_response(self, response: str):
        if not response:
            return
        _log.debug('Send response %s', response)
        with lock:
            with open(self.splash_receive, 'wb+') as file:
                file.write(response.encode())
            time.sleep(0.5)

    def on_modified(self, event):
        if event.src_path != self.splash_send:
            return

        time.sleep(1)

        with contextlib.suppress(OSError):
            with open(self.splash_send, 'rb') as file:
                text = file.read().decode().removeprefix('\uFEFF')

            _log.debug('Receive data %s', text)
            response = self.parser.parse_file(text)
            self.send_response(response)

            with open(self.splash_send, 'w+') as file:
                file.write('')

    def observe(self):
        self.observer = Observer()
        self.observer.schedule(self, self.exchange, recursive=True)
        self.observer.start()

    def stop(self):
        _log.warning('Stopped...')
        self.observer.stop()
        self.observer.join()


if __name__ == "__main__":
    from dian import ResultParser
    # lenex = input('>')
    # dian = input('>')
    # exchange = input('>')
    lenex = 'global.lef'
    dian = 'cpb.Swimming'
    exchange = 'Exchange'

    result_parser = ResultParser(lenex, dian)
    file_parser = FileParser()

    result_parser.set_file_parser(file_parser)
    file_parser.set_result_parser(result_parser)

    event_handler = FileHandler(file_parser, exchange)
    file_parser.set_send_response(event_handler.send_response)

    event_handler.observe()
