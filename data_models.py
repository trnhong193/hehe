# emp_planning_system/data_models.py

from dataclasses import dataclass

@dataclass
class EMP:
    """Lớp lưu trữ thông tin cho một nguồn phát EMP."""
    id: str  # Một định danh duy nhất, ví dụ dùng uuid
    lat: float
    lon: float
    power: float      # Công suất (W)
    frequency: float  # Tần số (MHz)
    height: float     # Độ cao lắp đặt so với mặt đất (m)

@dataclass
class Obstacle:
    """Lớp lưu trữ thông tin cho một vật cản."""
    id: str
    lat: float
    lon: float
    length: float  # Chiều dài (m)
    width: float   # Chiều rộng (m)
    height: float  # Chiều cao (m)