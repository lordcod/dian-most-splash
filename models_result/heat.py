from typing import List
from xmlbind.root import XmlRoot
from xmlbind.models import XmlAttribute, XmlElementWrapper

import lxml.etree as ET
from .result import Result


class Heat(XmlRoot):
    heatid: int = XmlAttribute('heatid', required=True)
    results: List[Result] = XmlElementWrapper(
        'RESULTS', 'RESULT', required=True)


if __name__ == '__main__':
    xml = '''<HEAT heatid="1">
        <RESULTS>
            <RESULT lane="2" swimtime="00:00:35.40" status="DSQ"/>
        </RESULTS>
    </HEAT>'''
    element = ET.fromstring(xml)
    print(Heat._parse(element))
