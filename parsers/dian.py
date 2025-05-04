from collections import defaultdict
import time
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union
from dianpy.event import Event
from dianpy.meet import Meet
from dianpy.athlete import Athlete
import lxml.etree as ET
import logging

if TYPE_CHECKING:
    from client import Client


_log = logging.getLogger(__name__)


def get_updated(
    old: Meet,
    new: Meet
) -> Optional[Dict[int, Event]]:
    if old is None:
        return None

    l1, l2 = old.events, new.events
    if len(l1) != len(l2):
        return None

    ups = {}
    for i in range(len(l1)):
        v1, v2 = l1[i], l2[i]
        if v1 != v2:
            ups[i] = v2

    return ups


DianStorage = Union[Dict[Tuple[int, int, int], str],
                    Dict[Tuple[int, int], Athlete]]


class DianParser:
    data: DianStorage

    def __init__(
        self,
        client: 'Client',
        dian_path: str
    ):
        self.client = client
        self.dian_path = dian_path
        self.data = defaultdict(dict)

        self.old = None

    def save_event_results(self, order: int, event: Event):
        print('FOUND EVENT ORDER', order)
        event_data = self.data[order]
        if not event.athletes:
            return

        for athl in event.athletes:
            if not (athl.heatnum
                    and athl.lanenum
                    and athl.completeddistance
                    and athl.time):
                continue

            event_data[(athl.heatnum, athl.lanenum)] = athl
            key = (athl.heatnum, athl.lanenum, athl.completeddistance)
            event_data[key] = athl.time

    def save_all_results(self, meet: Meet):
        for order, event in enumerate(meet.events):
            self.save_event_results(order, event)

    def parse(self, meet: Meet):
        events = get_updated(self.old, meet)
        self.old = meet

        if events is None:
            self.save_all_results(meet)
            return

        print('Get updated', len(events))
        for order, event in events.items():
            self.save_event_results(order, event)

    def up(self):
        for i in range(5):
            try:
                with open(self.dian_path, 'rb') as file:
                    text_now = file.read()
            except Exception as exc:
                _log.warning('There was a % error when receiving data from dian', i,
                             exc_info=exc)
                time.sleep(0.2)
            else:
                break

        element = ET.fromstring(text_now)
        meet = Meet._parse(element)
        self.parse(meet)


if __name__ == '__main__':
    path = r"C:\Users\2008d\OneDrive\Документы\tests\DainTest\start.Swimming"
    parser = DianParser(None, path)

    while True:
        i = input()
        if i == 'p':
            print(parser.data)
        parser.up()
