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
        # Chuyển đổi các đối tượng dataclass thành dictionary để có thể lưu dưới dạng JSON
        emps_data = []
        for emp in emps.values():
            emp_dict = emp.__dict__
            emp_dict['uuid'] = emp.uuid # Đảm bảo uuid được thêm vào dict
            emps_data.append(emp_dict)

        obstacles_data = []
        for obs in obstacles.values():
            obs_dict = obs.__dict__
            obs_dict['uuid'] = obs.uuid # Đảm bảo uuid được thêm vào dict
            obstacles_data.append(obs_dict)
            
        project_data = {
            "file_format_version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "map_state": map_state,
            "emps": emps_data,
            "obstacles": obstacles_data
        }

        # Ghi dữ liệu vào file
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

        # Tái tạo lại các đối tượng EMP từ dữ liệu thô trong file JSON
        loaded_emps = {}
        for emp_data in project_data.get("emps", []):
            # Lấy uuid ra khỏi dict trước khi khởi tạo đối tượng
            # vì uuid của chúng ta được thiết lập là init=False
            uuid = emp_data.pop('uuid', None)
            if uuid:
                new_emp = EMP(**emp_data)
                new_emp.uuid = uuid  # Gán lại uuid sau khi đối tượng đã được tạo
                loaded_emps[uuid] = new_emp

        # Tái tạo lại các đối tượng Obstacle
        loaded_obstacles = {}
        for obs_data in project_data.get("obstacles", []):
            uuid = obs_data.pop('uuid', None)
            if uuid:
                new_obs = Obstacle(**obs_data)
                new_obs.uuid = uuid
                loaded_obstacles[uuid] = new_obs
        
        # Lấy trạng thái bản đồ, có giá trị mặc định nếu không tìm thấy
        map_state = project_data.get("map_state", {"center": [21.0285, 105.8542], "zoom": 13})

        return True, {"emps": loaded_emps, "obstacles": loaded_obstacles, "map_state": map_state}
    except Exception as e:
        return False, f"Lỗi khi mở dự án: {e}"