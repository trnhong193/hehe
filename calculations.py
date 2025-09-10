# emp_planning_system/calculations.py

import numpy as np
import math

# Hằng số vật lý
R_EARTH = 6371000  # Bán kính Trái Đất (mét)

def lonlat_to_xy(origin_lon, origin_lat, lon, lat):
    """
    Chuyển đổi tọa độ (lon, lat) sang (x, y) tính bằng mét,
    dựa trên một điểm gốc (origin). Dùng phép chiếu Equirectangular.
    Đây là phép tính gần đúng, hoạt động tốt cho các khu vực cục bộ.
    """
    dx = (lon - origin_lon) * math.pi / 180 * R_EARTH * math.cos(origin_lat * math.pi / 180)
    dy = (lat - origin_lat) * math.pi / 180 * R_EARTH
    return dx, dy

def check_line_box_intersection(p1, p2, box_min, box_max):
    """
    Kiểm tra xem đoạn thẳng P1-P2 có cắt hình hộp chữ nhật (AABB) không.
    Sử dụng thuật toán Slab.
    p1, p2: numpy array [x, y, z] của điểm đầu và cuối đoạn thẳng.
    box_min, box_max: numpy array [x, y, z] của góc nhỏ nhất và lớn nhất của hộp.
    """
    direction = p2 - p1
    # Tránh lỗi chia cho 0
    direction[direction == 0] = 1e-9
    
    t_near = (box_min - p1) / direction
    t_far = (box_max - p1) / direction
    
    # Đảm bảo t_near luôn nhỏ hơn t_far
    tmin = np.minimum(t_near, t_far)
    tmax = np.maximum(t_near, t_far)
    
    t0 = np.max(tmin)
    t1 = np.min(tmax)
    
    # Điều kiện để có giao cắt:
    # 1. Phải có một khoảng [t0, t1] chồng lấn (t0 < t1)
    # 2. Khoảng chồng lấn đó phải nằm trong đoạn [0, 1] (tương ứng với đoạn P1-P2)
    return t0 < t1 and t0 < 1 and t1 > 0


def calculate_emp_field(emps, obstacles, user_altitude, bounds, grid_size=(200, 200)):
    """
    Hàm tính toán chính.
    - emps: danh sách các đối tượng EMP
    - obstacles: danh sách các đối tượng Obstacle
    - user_altitude: độ cao người dùng xét (mét)
    - bounds: {'lat_max', 'lat_min', 'lon_max', 'lon_min'} của bản đồ
    - grid_size: độ phân giải của lưới tính toán (width, height)
    """
    # 1. Thiết lập lưới tính toán và hệ tọa độ XY
    origin_lon = (bounds['lon_min'] + bounds['lon_max']) / 2
    origin_lat = (bounds['lat_min'] + bounds['lat_max']) / 2
    grid_height, grid_width = grid_size
    lat_range = np.linspace(bounds['lat_min'], bounds['lat_max'], grid_size[1])
    lon_range = np.linspace(bounds['lon_min'], bounds['lon_max'], grid_size[0])
    
    # Lưới kết quả, lưu giá trị E_max tại mỗi điểm
    result_grid = np.zeros(grid_size)
    
    # Chuyển đổi tọa độ của vật cản sang XY một lần để tối ưu
    obstacles_xy = []
    for obs in obstacles:
        center_x, center_y = lonlat_to_xy(origin_lon, origin_lat, obs.lon, obs.lat)
        half_len = obs.length / 2
        half_wid = obs.width / 2
        
        # Vật cản có độ cao so với mặt đất, không phải so với mực nước biển
        # Giả sử mặt đất bằng phẳng tại z=0 trong hệ tọa độ tính toán
        box_min = np.array([center_x - half_len, center_y - half_wid, 0])
        box_max = np.array([center_x + half_len, center_y + half_wid, obs.height])
        obstacles_xy.append({'min': box_min, 'max': box_max})
    
    map_min_x, map_min_y = lonlat_to_xy(origin_lon, origin_lat, bounds['lon_min'], bounds['lat_min'])
    map_max_x, map_max_y = lonlat_to_xy(origin_lon, origin_lat, bounds['lon_max'], bounds['lat_max'])
    
    map_width_m = map_max_x - map_min_x
    map_height_m = map_max_y - map_min_y
    
    # Kích thước vật lý (mét) của một ô lưới
    cell_width_m = map_width_m / grid_width if grid_width > 0 else 0
    cell_height_m = map_height_m / grid_height if grid_height > 0 else 0
    # 2. Lặp qua từng nguồn EMP (thuật toán tối ưu)
    for emp in emps:
        emp_x, emp_y = lonlat_to_xy(origin_lon, origin_lat, emp.lon, emp.lat)
        emp_pos = np.array([emp_x, emp_y, emp.height]) # Tọa độ 3D của EMP
        if emp.power > 0:
            d_max = math.sqrt(0.3 * emp.power) * 1.1
        else:
            continue # Bỏ qua EMP không có công suất

        # B. Chuyển bán kính mét sang số ô lưới
        radius_in_cells_x = (d_max / cell_width_m) if cell_width_m > 0 else grid_width
        radius_in_cells_y = (d_max / cell_height_m) if cell_height_m > 0 else grid_height

        # C. Tìm vị trí của EMP trên lưới
        emp_i = (emp_x - map_min_x) / cell_width_m if cell_width_m > 0 else 0
        emp_j = (emp_y - map_min_y) / cell_height_m if cell_height_m > 0 else 0

        # D. Xác định vùng lưới cần duyệt (bounding box)
        i_min = max(0, int(emp_i - radius_in_cells_x))
        i_max = min(grid_width, int(emp_i + radius_in_cells_x) + 1)
        j_min = max(0, int(emp_j - radius_in_cells_y))
        j_max = min(grid_height, int(emp_j + radius_in_cells_y) + 1)

        # 3. Lặp qua các điểm trong vùng ảnh hưởng đã được tối ưu
        for j in range(j_min, j_max):
            for i in range(i_min, i_max):
                # Lấy tọa độ lon/lat từ chỉ số lưới
                lat = lat_range[j]
                lon = lon_range[i]
                
                grid_x, grid_y = lonlat_to_xy(origin_lon, origin_lat, lon, lat)
                grid_pos = np.array([grid_x, grid_y, user_altitude])
                
                # 4. Kiểm tra che khuất
                is_obstructed = False
                for obs_xy in obstacles_xy:
                    if check_line_box_intersection(emp_pos, grid_pos, obs_xy['min'], obs_xy['max']):
                        is_obstructed = True
                        break
                
                if is_obstructed:
                    e_field = 0
                else:
                    # 5. Tính cường độ điện trường
                    distance_sq = np.sum((emp_pos - grid_pos)**2)
                    if distance_sq < 1e-6: # Tránh chia cho 0 tại tâm
                        e_field = float('inf')
                    else:
                        e_field = math.sqrt(30 * emp.power / distance_sq)
        # 3. Lặp qua từng điểm trên lưới
    #     for i, lon in enumerate(lon_range):
    #         for j, lat in enumerate(lat_range):
    #             grid_x, grid_y = lonlat_to_xy(origin_lon, origin_lat, lon, lat)
    #             grid_pos = np.array([grid_x, grid_y, user_altitude]) # Tọa độ 3D của điểm xét
                
    #             # 4. Kiểm tra che khuất
    #             is_obstructed = False
    #             for obs_xy in obstacles_xy:
    #                 if check_line_box_intersection(emp_pos, grid_pos, obs_xy['min'], obs_xy['max']):
    #                     is_obstructed = True
    #                     break # Nếu bị che bởi một vật cản, không cần kiểm tra các vật cản khác
                
    #             if is_obstructed:
    #                 e_field = 0
    #             else:
    #                 # 5. Tính cường độ điện trường nếu không bị che
    #                 distance_sq = np.sum((emp_pos - grid_pos)**2)
    #                 if distance_sq == 0:
    #                     e_field = float('inf') # Cường độ vô hạn tại tâm
    #                 else:
    #                     # E = sqrt(30 * P / d^2)
    #                     e_field = math.sqrt(30 * emp.power / distance_sq)
                
    #             # 6. Cập nhật giá trị E lớn nhất vào lưới kết quả
                result_grid[j, i] = max(result_grid[j, i], e_field)

    return result_grid