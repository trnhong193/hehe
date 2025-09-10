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
    
    tmin = np.minimum(t_near, t_far)
    tmax = np.maximum(t_near, t_far)
    
    t0 = np.max(tmin)
    t1 = np.min(tmax)
    
    return t0 < t1 and t0 < 1 and t1 > 0


def calculate_emp_field(emps, obstacles, user_altitude, bounds, grid_size=(200, 200)):
    """
    Hàm tính toán chính (phiên bản tối ưu).
    """
    # 1. Thiết lập lưới tính toán và hệ tọa độ XY
    origin_lon = (bounds['lon_min'] + bounds['lon_max']) / 2
    origin_lat = (bounds['lat_min'] + bounds['lat_max']) / 2
    
    grid_height, grid_width = grid_size
    lat_range = np.linspace(bounds['lat_min'], bounds['lat_max'], grid_height)
    lon_range = np.linspace(bounds['lon_min'], bounds['lon_max'], grid_width)
    
    # Lưới kết quả, lưu giá trị E_max tại mỗi điểm
    result_grid = np.zeros(grid_size)
    
    # Chuyển đổi tọa độ của vật cản sang XY một lần để tối ưu
    obstacles_xy = []
    for obs in obstacles:
        center_x, center_y = lonlat_to_xy(origin_lon, origin_lat, obs.lon, obs.lat)
        half_len = obs.length / 2
        half_wid = obs.width / 2
        box_min = np.array([center_x - half_len, center_y - half_wid, 0])
        box_max = np.array([center_x + half_len, center_y + half_wid, obs.height])
        obstacles_xy.append({'min': box_min, 'max': box_max})

    # --- GIẢI THÍCH CHO CÂU HỎI 2: TÍNH LINH HOẠT CỦA GRID SIZE ---
    # Mặc dù grid_size là cố định (200, 200), nhưng kích thước vật lý của nó thay đổi
    # theo khu vực bản đồ (bounds). Khi zoom gần, mỗi ô lưới đại diện cho 1m x 1m,
    # cho kết quả chi tiết. Khi zoom xa, mỗi ô lưới có thể đại diện cho 50m x 50m,
    # cho cái nhìn tổng quan. Điều này giúp hiệu năng ổn định mà vẫn linh hoạt.
    map_min_x, map_min_y = lonlat_to_xy(origin_lon, origin_lat, bounds['lon_min'], bounds['lat_min'])
    map_max_x, map_max_y = lonlat_to_xy(origin_lon, origin_lat, bounds['lon_max'], bounds['lat_max'])
    
    map_width_m = map_max_x - map_min_x
    map_height_m = map_max_y - map_min_y
    
    # Kích thước vật lý (mét) của một ô lưới
    cell_width_m = map_width_m / grid_width if grid_width > 0 else 0
    cell_height_m = map_height_m / grid_height if grid_height > 0 else 0

    # 2. Lặp qua từng nguồn EMP
    for emp in emps:
        emp_x, emp_y = lonlat_to_xy(origin_lon, origin_lat, emp.lon, emp.lat)
        emp_pos = np.array([emp_x, emp_y, emp.height]) # Tọa độ 3D của EMP

        # --- TỐI ƯU HÓA HIỆU NĂNG (GIẢI QUYẾT CÂU HỎI 1) ---
        # Thay vì duyệt toàn bộ 200x200 ô, ta chỉ duyệt các ô nằm trong
        # một bán kính ảnh hưởng hợp lý xung quanh EMP.
        
        # A. Tính bán kính ảnh hưởng tối đa (d_max)
        # Tìm khoảng cách mà tại đó E lần đầu giảm xuống dưới ngưỡng cảnh báo (10 V/m)
        # 10 = sqrt(30 * P / d^2) => d_max = sqrt(0.3 * P)
        # Thêm 1 hệ số an toàn nhỏ để không bỏ sót
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
                
                # 6. Cập nhật giá trị E lớn nhất vào lưới kết quả
                # --- GIẢI THÍCH CHO CÂU HỎI 3: TẠI SAO DÙNG MAX() ---
                # Cường độ điện trường là đại lượng vector, có cả hướng và pha.
                # Việc cộng tổng các độ lớn (|E1| + |E2|) là sai về mặt vật lý vì
                # nó bỏ qua hiện tượng giao thoa (sóng có thể cộng hưởng hoặc triệt tiêu).
                # Tính toán vector tổng hợp thì quá phức tạp cho ứng dụng này.
                # Do đó, lấy max(|E|) là một phương pháp gần đúng an toàn,
                # nó thể hiện mức độ nguy hiểm theo "trường hợp xấu nhất" tại một điểm,
                # đảm bảo cảnh báo không bao giờ bị đánh giá thấp hơn mối nguy lớn nhất.
                result_grid[j, i] = max(result_grid[j, i], e_field)

    return result_grid