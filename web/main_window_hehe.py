# emp_planning_system/main_window.py

# ... (tất cả các import đã có ở lần trước) ...
import json

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # ... (code không đổi) ...
        self._save_path_pending = None # Thêm biến tạm cho việc lưu file
        self.current_map_state = {"center": [21.0285, 105.8542], "zoom": 13}

    def _connect_signals(self):
        # ... (các kết nối cũ) ...
        # --- THÊM KẾT NỐI MỚI ---
        self.map_view.bridge.mapViewReceived.connect(self._on_map_view_received)

    # --- CÁC HÀM HELPER ĐỂ TƯƠNG TÁC VỚI BẢN ĐỒ ---

    def _add_object_to_map(self, obj):
        """Gửi lệnh cho JS để vẽ hoặc cập nhật một đối tượng trên bản đồ."""
        obj_json = json.dumps(obj.__dict__)
        if isinstance(obj, EMP):
            self.map_view.run_js(f"addEmpMarker({obj_json});")
        elif isinstance(obj, Obstacle):
            self.map_view.run_js(f"addObstacleShape({obj_json});")

    def _remove_object_from_map(self, uuid):
        """Gửi lệnh cho JS để xóa một đối tượng khỏi bản đồ."""
        self.map_view.run_js(f"removeObject('{uuid}');")
    
    def _clear_map(self):
        """Gửi lệnh cho JS để xóa sạch các đối tượng trên bản đồ."""
        self.map_view.run_js("clearAllObjects();")

    # --- CẬP NHẬT CÁC HÀM LOGIC CHÍNH ---

    def _delete_object(self, table, item):
        uuid = item.data(Qt.UserRole)
        name = item.text()
        reply = QMessageBox.question(self, 'Xác nhận xóa', f"Bạn có chắc chắn muốn xóa '{name}' không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if table is self.emp_table and uuid in self.emp_sources:
                del self.emp_sources[uuid]
                self._remove_object_from_map(uuid) # <--- HOÀN THIỆN TODO
            elif table is self.obstacle_table and uuid in self.obstacles:
                del self.obstacles[uuid]
                self._remove_object_from_map(uuid) # <--- HOÀN THIỆN TODO
            self._refresh_object_tables()
            self.is_dirty = True
            self._update_window_title()

    def _save_object(self):
        # ... (code kiểm tra dữ liệu không đổi) ...
        try:
            # ...
            uuid_to_save = self.current_edit_uuid if self.current_mode.startswith("EDIT") else str(uuid.uuid4())
            if self.current_mode in ["ADD_EMP", "EDIT_EMP"]:
                obj = EMP(...) # Tạo đối tượng
                obj.uuid = uuid_to_save
                self.emp_sources[obj.uuid] = obj
                self._add_object_to_map(obj) # <--- HOÀN THIỆN TODO
            elif self.current_mode in ["ADD_OBSTACLE", "EDIT_OBSTACLE"]:
                obj = Obstacle(...) # Tạo đối tượng
                obj.uuid = uuid_to_save
                self.obstacles[obj.uuid] = obj
                self._add_object_to_map(obj) # <--- HOÀN THIỆN TODO
            # ... (code còn lại không đổi) ...
        except Exception as e:
            # ...
    
    def _new_project(self):
        if self._check_dirty_and_save():
            self.emp_sources.clear()
            self.obstacles.clear()
            self._clear_map() # <--- HOÀN THIỆN TODO
            self._refresh_object_tables()
            # ... (code còn lại không đổi) ...

    def _open_project(self):
        if self._check_dirty_and_save():
            path, _ = QFileDialog.getOpenFileName(...)
            if path:
                success, data = load_project(path)
                if success:
                    self._clear_map() # Xóa sạch bản đồ cũ trước
                    self.emp_sources = data.get('emps', {})
                    self.obstacles = data.get('obstacles', {})
                    self._refresh_object_tables()
                    # Vẽ lại tất cả đối tượng lên bản đồ <--- HOÀN THIỆN TODO
                    for emp in self.emp_sources.values():
                        self._add_object_to_map(emp)
                    for obs in self.obstacles.values():
                        self._add_object_to_map(obs)
                    # Di chuyển bản đồ đến vị trí đã lưu <--- HOÀN THIỆN TODO
                    map_state = data.get('map_state')
                    if map_state:
                        self.map_view.run_js(f"setMapView({map_state['center'][0]}, {map_state['center'][1]}, {map_state['zoom']});")
                    # ... (code còn lại không đổi) ...

    def _on_map_view_received(self, lat, lon, zoom):
        """Slot nhận trạng thái bản đồ và thực hiện việc lưu file."""
        self.current_map_state = {"center": [lat, lon], "zoom": zoom}
        if self._save_path_pending:
            success, message = save_project(self._save_path_pending, self.emp_sources, self.obstacles, self.current_map_state)
            if success:
                self.is_dirty = False
                self.current_project_path = self._save_path_pending
                self._update_window_title()
                self.statusBar().showMessage(message)
            else:
                QMessageBox.critical(self, "Lỗi", message)
            self._save_path_pending = None # Reset biến tạm

    def _save_project(self):
        """Lưu vào file hiện tại, hoặc gọi _save_project_as nếu chưa có file."""
        if not self.current_project_path:
            return self._save_project_as()
        else:
            self.statusBar().showMessage("Đang lấy trạng thái bản đồ để lưu...")
            self._save_path_pending = self.current_project_path
            self.map_view.run_js("getMapView();") # <--- HOÀN THIỆN TODO
            return True # Giả định thành công, kết quả thực sự sẽ được xử lý ở _on_map_view_received

    def _save_project_as(self):
        """Mở hộp thoại để lưu dự án thành file mới."""
        path, _ = QFileDialog.getSaveFileName(...)
        if path:
            self.statusBar().showMessage("Đang lấy trạng thái bản đồ để lưu...")
            self._save_path_pending = path
            self.map_view.run_js("getMapView();") # <--- HOÀN THIỆN TODO
            return True
        return False