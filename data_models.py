import uuid
from dataclasses import dataclass, field

@dataclass
class EMP:
    name: str
    lat: float
    lon: float
    power: float
    frequency: float
    height: float
    # Dùng UUID để định danh duy nhất, không cho người dùng sửa
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Obstacle:
    name: str
    lat: float
    lon: float
    length: float
    width: float
    height: float
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))