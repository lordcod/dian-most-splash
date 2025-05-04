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
) -> Optional[Dict[int, Tuple[Event, Event]]]:
    if old is None:
        return None

    l1, l2 = old.events, new.events
    if len(l1) != len(l2):
        return None

    ups = {}
    for i in range(len(l1)):
        v1, v2 = l1[i], l2[i]
        if v1 != v2:
            ups[i] = (v1, v2)

    return ups


def find_updated_heatnum(
    old: Event,
    new: Event
) -> Optional[int]:
    l1, l2 = old.athletes, new.athletes
    if len(l1) != len(l2):
        return None

    updated = set()
    for i in range(len(l1)):
        v1, v2 = l1[i], l2[i]
        if v1 != v2 and (v1.time != v2.time or v1.disqualification != v2.disqualification):
            updated.add(v2.heatnum)

    if len(updated) == 1:
        return updated.pop()


def check_completed(data: dict[int, list[tuple[int, int | None, str | None]]]):
    official = data.copy()

    for key, updates in data.copy().items():
        for state in enumerate(updates.copy()):
            if state[1] is None and state[2] is None:
                updates.remove(state)
        if not updates:
            data.pop(key)

    if len(data) != 1:
        _log.debug('Invalid count data')
        return False

    key = next(iter(data.keys()))
    for state in official[key]:
        if state[1] is None and state[2] is None:
            _log.debug('Athlete %s not finished, NR', state[0])
            return False
        if not state[2] and not state[3]:
            _log.debug('Athlete %s not finished, NCD', state[0])
            return False

    return True


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
        self.old_heat = [None, None, None]

    def save_event_results(self, order: int, event: Event):
        print('FOUND EVENT ORDER', order)
        event_data = self.data[order]
        if not event.athletes:
            return

        updated = defaultdict(list)
        for athl in event.athletes:
            if not (athl.heatnum
                    and athl.lanenum
                    and athl.completeddistance
                    and athl.time):
                updated[athl.heatnum].append((athl.lanenum, None, None, None))
                continue

            event_data[(athl.heatnum, athl.lanenum)] = athl
            key = (athl.heatnum, athl.lanenum, athl.completeddistance)
            event_data[key] = athl.time

            updated[athl.heatnum].append(
                (athl.lanenum, athl.completeddistance, athl.disqualification, athl.completeddistance == event.distance))

        return updated

    def save_all_results(self, meet: Meet):
        for order, event in enumerate(meet.events):
            self.save_event_results(order, event)

    def update_status_heat(self, events, status):
        index, (old, new) = next(iter(events.items()))
        heatnum = find_updated_heatnum(old, new)
        if heatnum is None:
            _log.debug('Not found heatnum')

        if heatnum == self.old_heat[0] and old == self.old_heat[1] and self.old_heat[3] == status:
            _log.debug('Status was received earlier, info heatnum')
            return
        self.old_heat = [heatnum, new, None, status]

        lenex_event = self.client.result_parser.get_lenex_event(index)
        if lenex_event is None:
            _log.debug('Not found lenex event')
            return

        for lenex_heat in lenex_event.heats:
            if lenex_heat.number == heatnum:
                break
        else:
            _log.debug('Not found lenex heat')
            return

        if lenex_heat.heatid == self.old_heat[2] and self.old_heat[3] == status:
            _log.debug('Status was received earlier, info heatid')
            return
        self.old_heat[2] = lenex_heat.heatid

        self.client.file_parser.send_status(
            lenex_event.eventid, lenex_heat.heatid, status)

    def parse(self, meet: Meet):
        events = get_updated(self.old, meet)
        self.old = meet

        if events is None:
            self.save_all_results(meet)
            return

        for order, (_, event) in events.items():
            updated = self.save_event_results(order, event)

        if len(events) != 1:
            return

        if check_completed(updated):
            self.update_status_heat(events, 'OFFICIAL')
        else:
            self.update_status_heat(events, 'ACTIVE')

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
