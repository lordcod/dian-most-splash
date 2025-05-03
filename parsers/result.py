from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Tuple, Union

from dianpy.athlete import Athlete as DianAthlete
from xml_result.heat import Heat
from xml_result.result import Result
from lenexpy.models.meet import Meet as LenexMeet
from lenexpy.models.event import Event as LenexEvent
from lenexpy import fromfile
import lxml.etree as ET
import logging

from xml_result.split import Split

if TYPE_CHECKING:
    from client import Client


_log = logging.getLogger(__name__)
DianResponse = Union[Dict[Tuple[int, int, int], str],
                     Dict[Tuple[int, int], DianAthlete]]


class ResultParser:
    NOT_FOUND = 'SEND RESULTS; NOT FOUND'

    def __init__(
        self,
        client: Client,
        lenex_path: str
    ):
        self.client = client
        self.lenex = fromfile(lenex_path)

    def update_lenex_meet(self, meet: LenexMeet):
        self.lenex.meet = meet

    def get_heat(
        self,
        heatid: int
    ):
        for session in self.lenex.meet.sessions:
            for event in session.events:
                for heat in event.heats or []:
                    if heat.heatid == heatid:
                        return True, heat, event

        return False, None, None

    def get_dian_event(
        self,
        event: LenexEvent
    ) -> DianResponse:
        i = 0
        for s in self.lenex.meet.sessions:
            for e in s.events:
                if e.eventid == event.eventid:
                    print('FOUND', i)
                    return self.client.dian_parser.data[i]
                if e.swimstyle and e.swimstyle.distance:
                    i += 1

    def parse_dian_results(
        self,
        heat_number: int,
        event: LenexEvent,
        dian_data: DianResponse
    ):
        data = defaultdict(dict)
        for receive, time in dian_data.items():
            if len(receive) != 3:
                continue

            heatnum, lanenum, completed_distance = receive
            if heatnum != heat_number:
                continue
            athlete = dian_data[(heatnum, lanenum)]

            if lanenum not in data:
                result = data[lanenum] = Result(
                    lane=lanenum,
                    status=athlete.disqualification,
                    splits=[]
                )
            else:
                result = data[lanenum]

            if completed_distance == event.swimstyle.distance:
                result.swimtime = time
            else:
                split = Split(distance=completed_distance, swimtime=time)
                result.splits.append(split)
        return data.values()

    def get_event_response(
        self,
        eventid: int,
        heatid: int
    ):
        ok, heat, event = self.get_heat(heatid)
        if not ok:
            _log.info('Not found lenex event %s %s', eventid, heatid)
            return self.NOT_FOUND
        result_heat = Heat(heatid=heat.heatid,
                           results=[])

        dian_data = self.get_dian_event(event)
        if not dian_data:
            _log.info('Not found dian event %s %s', eventid, heatid)
            return self.NOT_FOUND

        results = self.parse_dian_results(heat.number,
                                          event,
                                          dian_data)
        result_heat.results.extend(results)

        if len(result_heat.results) == 0:
            _log.info('Not found results %s %s', eventid, heatid)
            return self.NOT_FOUND

        return (
            'SEND RESULTS;START\n'
            f'{ET.tostring(result_heat.dump("HEAT")).decode()}\n'
            'SEND RESULTS;END'
        )

    def up(self, eventid: int, heatid: int):
        response = self.get_event_response(eventid, heatid)
        self.client.file_handler.send_response(response)
