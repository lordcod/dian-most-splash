from typing import List
from xmlbind.root import XmlRoot
from xmlbind.models import XmlAttribute, XmlElementWrapper

from .split import Split


class Result(XmlRoot):
    lane: int = XmlAttribute('lane', required=True)
    swimtime: str = XmlAttribute('swimtime')
    status: str = XmlAttribute('status')
    backuptime1: str = XmlAttribute('backuptime1')
    backuptime2: str = XmlAttribute('backuptime2')
    backuptime3: str = XmlAttribute('backuptime3')
    splits: List[Split] = XmlElementWrapper('SPLITS', 'SPLIT')
