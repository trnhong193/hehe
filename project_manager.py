# emp_planning_system/project_manager.py

import json
from datetime import datetime
from data_models import EMP, Obstacle

def save_project(file_path, emps, obstacles, map_state):
    """
    Lưu toàn bộ dữ liệu dự án vào một file JSON.
    - emps, obstacles: Dictionaries chứa các đối tượng EMP và Vật cản.
    - map_state: Một dict chứa thông tin về bản đồ (center, zoom).
    """
    try:
        project_data = {
            "file_format_version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "map_state": map_state,
            "emps": [emp.__dict__ for emp in emps.values()],
            "obstacles": [obs.__dict__ for obs in obstacles.values()]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=4, ensure_ascii=False)
        
        return True, "Dự án đã được lưu thành công."
    except Exception as e:
        return False, f"Lỗi khi lưu dự án: {e}"

def load_project(file_path):
    """
    Tải dữ liệu dự án từ một file JSON.
    Trả về dữ liệu đã được parse hoặc báo lỗi.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # Tái tạo lại các đối tượng từ dữ liệu thô
        loaded_emps = {
            emp_data['uuid']: EMP(**{k: v for k, v in emp_data.items() if k != 'uuid'})
            for emp_data in project_data.get("emps", [])
        }
        # Gán lại uuid sau khi tạo
        for emp_data in project_data.get("emps", []):
            if emp_data['uuid'] in loaded_emps:
                loaded_emps[emp_data['uuid']].uuid = emp_data['uuid']

        loaded_obstacles = {
            obs_data['uuid']: Obstacle(**{k: v for k, v in obs_data.items() if k != 'uuid'})
            for obs_data in project_data.get("obstacles", [])
        }
        for obs_data in project_data.get("obstacles", []):
            if obs_data['uuid'] in loaded_obstacles:
                loaded_obstacles[obs_data['uuid']].uuid = obs_data['uuid']

        map_state = project_data.get("map_state", {"center": [21.0285, 105.8542], "zoom": 13})

        return True, {"emps": loaded_emps, "obstacles": loaded_obstacles, "map_state": map_state}
    except Exception as e:
        return False, f"Lỗi khi mở dự án: {e}"