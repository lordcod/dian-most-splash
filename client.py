import logging
from listeners.dian import DianHandler
from parsers.dian import DianParser
from parsers.result import ResultParser
from parsers.main import FileParser
from listeners.splash import FileHandler


__version__ = 'Dybfuo.Media system v0.0.1'


class Client:
    version = __version__

    def __init__(
        self,
        lenex: str,
        dian: str,
        exchange: str
    ):
        self.result_parser = ResultParser(self, lenex)
        self.file_parser = FileParser(self)
        self.dian_parser = DianParser(self, dian)

        self.file_handler = FileHandler(self, exchange)
        self.dian_handler = DianHandler(self, dian)

    def observe(self):
        self.file_handler.observe()
        self.dian_handler.observe()

    def stop(self):
        self.file_handler.stop()
        self.dian_handler.stop()


if __name__ == '__main__':
    lenex = r"C:\Users\2008d\OneDrive\Документы\tests\DainTest\lenex.lxf"
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
