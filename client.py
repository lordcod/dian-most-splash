import contextlib
import logging
import pickle
from listeners.dian import DianHandler
from parsers.dian import DianParser
from parsers.result import ResultParser
from parsers.main import FileParser
from listeners.splash import FileHandler
from os.path import join


__version__ = 'Dybfuo.Media system v0.0.3b'


class Client:
    version = __version__

    def __init__(
        self,
        lenex: str,
        dian: str,
        exchange: str
    ):
        self.exchange = exchange

        self.result_parser = ResultParser(self, lenex)
        self.file_parser = FileParser(self)
        self.dian_parser = DianParser(self, dian)

        self.file_handler = FileHandler(self, exchange)
        self.dian_handler = DianHandler(self, dian)

    def dump_files(self):
        with contextlib.suppress(Exception):
            with open(join(self.exchange, 'names.pkl'), "wb") as fp:
                pickle.dump(self.file_parser.names, fp)
            with open(join(self.exchange, 'timing.pkl'), "wb") as fp:
                pickle.dump(self.dian_parser.data, fp)

    def load_files(self):
        with contextlib.suppress(Exception):
            with open(join(self.exchange, 'names.pkl'), "rb") as fp:
                self.file_parser.names = pickle.load(fp)
            with open(join(self.exchange, 'timing.pkl'), "rb") as fp:
                self.dian_parser.data = pickle.load(fp)
                print(self.dian_parser.data)

    def observe(self):
        self.load_files()
        self.file_handler.observe()
        self.dian_handler.observe()

    def stop(self):
        self.dump_files()
        self.file_handler.stop()
        self.dian_handler.stop()


if __name__ == '__main__':
    lenex = r"C:\Users\2008d\OneDrive\Документы\tests\DainTest\lenex.lef"
    dian = r"C:\Users\2008d\OneDrive\Документы\tests\DainTest\start.Swimming"
    exchange = r"C:\Users\2008d\OneDrive\Документы\tests\DainTest"

    logging.basicConfig(level=logging.DEBUG)

    client = Client(lenex, dian, exchange)
    client.observe()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client.stop()
