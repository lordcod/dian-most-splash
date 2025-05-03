from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Dict
import lxml.etree as ET
from lenexpy.models_st.heat import Heat
from lenexpy.models.meet import Meet


if TYPE_CHECKING:
    from client import Client


class FileParser:
    names: Dict[int, Heat]

    def __init__(self, client: Client):
        self.client = client
        self.names = {}
        self.meet = None

    def send_status(self, event_id: int, heat_id: int, status: str):
        self.client.file_handler.send_response(
            f"STATUS;EVENTID={event_id};HEATID={heat_id};{status}")

    def ask_names(self, event_id: int, heat_id: int):
        self.client.file_handler.send_response(
            f"ASK NAMES;EVENTID={event_id};HEATID={heat_id}")

    def parse_send_names(self, text: str):
        element = ET.fromstring(text)
        heat = Heat._parse(element)
        self.names[heat.heatid] = heat

    def parse_download_event(self, text: str):
        element = ET.fromstring(text)
        self.meet = Meet._parse(element)
        self.client.result_parser.update_lenex_meet(self.meet)
        return 'DOWNLOAD EVENT;OK'

    def parse_file(self, text: str):
        module = None
        module_receive = None
        responses = []
        for func in text.splitlines():
            name, *args = func.split(';')

            if module is not None and (len(args) == 0 or args[0] != 'END'):
                module_receive += func+'\n'
                continue

            name, *args = func.split(';')

            if name == 'SEND NAMES':
                if args[0] == 'START':
                    module = name
                    module_receive = ''
                if args[0] == 'END':
                    responses.append(self.parse_send_names(module_receive))
                    module = None
                    module_receive = None

            if name == 'DOWNLOAD EVENT':
                if args[0] == 'START':
                    module = name
                    module_receive = ''
                if args[0] == 'END':
                    responses.append(self.parse_download_event(module_receive))
                    module = None
                    module_receive = None

            if name == 'VERSION':
                responses.append(f'{name};{self.client.version}')

            if name == 'ASK RESULTS':
                eventid, heatid = args[0].removeprefix(
                    'EVENTID='), args[1].removeprefix('HEATID=')
                args = [int(eventid), int(heatid)]

                thread = threading.Thread(
                    target=self.client.result_parser.up,
                    args=args
                )
                thread.start()

        return '\n'.join(filter(lambda i: i, responses))
