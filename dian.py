from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from dianpy.event import Event
from dianpy.meet import Meet
from models_result.heat import Heat
from models_result.result import Result
from lenexpy.models.meet import Meet as LenexMeet
from lenexpy.models.event import Event as LenexEvent
from lenexpy import fromfile
import lxml.etree as ET
import logging
if TYPE_CHECKING:
    from files import FileParser


_log = logging.getLogger(__name__)


class ResultParser:
    NOT_FOUND = 'SEND RESULTS; NOT FOUND'
    file_parser: Optional[FileParser]

    def __init__(
        self,
        lenex_path: str,
        dian_path: str
    ):
        self.lenex = fromfile(lenex_path)
        self.dian_path = dian_path
        self.enabled = True
        self.file_parser = None

    def set_file_parser(self, file_parser: FileParser):
        self.file_parser = file_parser

    def update_lenex_meet(self, meet: LenexMeet):
        self.lenex.meet = meet

    def get_results(self, event: Event, i: int):
        results = []
        for athlete in event.athletes:
            if athlete.heatnum != i:
                continue
            if athlete.time is None:
                athlete.time = ''
            results.append(f"{athlete.lanenum};{athlete.time}")
        return results

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
        meet: Meet,
        event: LenexEvent
    ) -> Event:
        for dian_event in meet.events:
            if (dian_event.gender == event.gender
                and dian_event.stroke == event.swimstyle.stroke
                    and dian_event.distance == event.swimstyle.distance):
                return dian_event

    def get_event_response(
        self,
        meet: Meet,
        eventid: int,
        heatid: int
    ):
        ok, heat, event = self.get_heat(heatid)
        if not ok:
            _log.info('Not found lenex event %s %s', eventid, heatid)
            return self.NOT_FOUND

        dian_event = self.get_dian_event(meet, event)
        result_heat = Heat(heatid=heat.heatid, results=[])
        if not dian_event:
            _log.info('Not found dian event %s %s', eventid, heatid)
            return self.NOT_FOUND

        for athlete in dian_event.athletes:
            if athlete.heatnum != heat.number:
                continue
            result = Result(lane=athlete.lanenum)
            result_heat.results.append(result)

            if not athlete.time:
                result.status = (athlete.disqualification
                                 if athlete.disqualification
                                 else 'DNS')
                continue
            result.swimtime = athlete.time
            result.status = athlete.disqualification

        if len(result_heat.results) == 0:
            _log.info('Not found results %s %s', eventid, heatid)
            return self.NOT_FOUND

        return (
            'SEND RESULTS;START\n'
            f'{ET.tostring(result_heat.dump("HEAT")).decode()}\n'
            'SEND RESULTS;END'
        )

    def up(self, eventid: int, heatid: int):
        with open(self.dian_path, 'rb') as file:
            text_now = file.read()
        element = ET.fromstring(text_now)
        meet = Meet._parse(element)
        response = self.get_event_response(meet, eventid, heatid)
        self.file_parser.send_response(response)
