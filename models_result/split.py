from xmlbind.root import XmlRoot
from xmlbind.models import XmlAttribute


class Split(XmlRoot):
    distance: int = XmlAttribute('distance', required=True)
    swimtime: str = XmlAttribute('swimtime', required=True)
