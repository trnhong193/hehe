# emp_planning_system/main_window.py

# ... (các import không đổi) ...
from project_manager import save_project, load_project # Import 2 hàm mới

class MainWindow(QMainWindow):
    # __init__ và _init_ui không đổi so với Phần 1
    def __init__(self, parent=None):
        # ... (code không đổi) ...
        super().__init__(parent)
        self.current_mode = None
        self.emp_sources = {}
        self.obstacles = {}
        self.current_project_path = None
        self.is_dirty = False
        self._init_ui()

    def _init_ui(self):
        # ... (code không đổi) ...
        self.map_view.bridge.mapClicked.connect(self._on_map_clicked)
        # --- Kết nối các actions ---
        self._connect_actions()

    # _create_actions, _create_menu_bar, _create_tool_bar, _create_control_panel
    # không đổi so với Phần 1

    def _connect_actions(self):
        """Kết nối tất cả các QAction với các hàm xử lý logic."""
        # Menu Tệp tin
        self.new_action.triggered.connect(self._new_project)
        self.open_action.triggered.connect(self._open_project)
        self.save_action.triggered.connect(self._save_project)
        self.save_as_action.triggered.connect(self._save_project_as)
        self.exit_action.triggered.connect(self.close) # self.close sẽ gọi closeEvent

        # Menu Hành động
        self.add_emp_action.triggered.connect(self._enter_add_emp_mode)
        self.add_obstacle_action.triggered.connect(self._enter_add_obstacle_mode)
        # (self.calc_action.triggered.connect(...) sẽ được làm ở phần sau)

    def _update_window_title(self):
        """Cập nhật tiêu đề cửa sổ để hiển thị tên file và trạng thái lưu."""
        title = "Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP"
        project_name = os.path.basename(self.current_project_path) if self.current_project_path else "Dự án mới"
        dirty_marker = "*" if self.is_dirty else ""
        self.setWindowTitle(f"{project_name}{dirty_marker} - {title}")

    # --- CHẾ ĐỘ THÊM ĐỐI TƯỢNG ---

    def _enter_add_emp_mode(self):
        self.current_mode = "ADD_EMP"
        self.statusBar().showMessage("Chế độ thêm nguồn EMP: Click lên bản đồ để chọn vị trí.")
        self._populate_details_form("EMP")
        self.control_panel.findChild(QTabWidget).setCurrentWidget(self.details_tab)

    def _enter_add_obstacle_mode(self):
        self.current_mode = "ADD_OBSTACLE"
        self.statusBar().showMessage("Chế độ thêm vật cản: Click lên bản đồ để chọn vị trí.")
        self._populate_details_form("OBSTACLE")
        self.control_panel.findChild(QTabWidget).setCurrentWidget(self.details_tab)

    def _on_map_clicked(self, lat, lon):
        if self.current_mode in ["ADD_EMP", "ADD_OBSTACLE"]:
            self.lat_input.setText(f"{lat:.6f}")
            self.lon_input.setText(f"{lon:.6f}")
            self.statusBar().showMessage(f"Đã chọn tọa độ: {lat:.6f}, {lon:.6f}. Vui lòng nhập thông tin.")
            self.name_input.setFocus()
    
    # --- FORM NHẬP LIỆU ---

    def _populate_details_form(self, object_type, data_object=None):
        """Tạo hoặc điền dữ liệu vào form chi tiết."""
        # Xóa các widget cũ trong layout
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Tạo các trường chung
        self.name_input = QLineEdit(data_object.name if data_object else "")
        self.lat_input = QLineEdit(f"{data_object.lat:.6f}" if data_object else "")
        self.lon_input = QLineEdit(f"{data_object.lon:.6f}" if data_object else "")
        self.details_layout.addRow("Tên đối tượng:", self.name_input)
        self.details_layout.addRow("Vĩ độ (Lat):", self.lat_input)
        self.details_layout.addRow("Kinh độ (Lon):", self.lon_input)

        if object_type == "EMP":
            self.details_group.setTitle("Chi tiết nguồn EMP")
            self.power_input = QLineEdit(str(data_object.power) if data_object else "1000")
            self.freq_input = QLineEdit(str(data_object.frequency) if data_object else "300")
            self.height_input = QLineEdit(str(data_object.height) if data_object else "10")
            self.details_layout.addRow("Công suất (W):", self.power_input)
            self.details_layout.addRow("Tần số (MHz):", self.freq_input)
            self.details_layout.addRow("Độ cao lắp đặt (m):", self.height_input)
        
        elif object_type == "OBSTACLE":
            self.details_group.setTitle("Chi tiết vật cản")
            self.length_input = QLineEdit(str(data_object.length) if data_object else "20")
            self.width_input = QLineEdit(str(data_object.width) if data_object else "10")
            self.height_input = QLineEdit(str(data_object.height) if data_object else "15")
            self.details_layout.addRow("Chiều dài (m):", self.length_input)
            self.details_layout.addRow("Chiều rộng (m):", self.width_input)
            self.details_layout.addRow("Chiều cao (m):", self.height_input)
        
        # Các nút Lưu và Hủy
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.details_layout.addRow(btn_layout)

        save_btn.clicked.connect(self._save_object)
        cancel_btn.clicked.connect(self._cancel_details_form)
        self.details_group.setVisible(True)

    def _save_object(self):
        """Lưu đối tượng mới hoặc cập nhật đối tượng đang sửa."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Thiếu thông tin", "Tên đối tượng không được để trống.")
                return

            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())

            if self.current_mode in ["ADD_EMP", "EDIT_EMP"]:
                new_emp = EMP(
                    name=name, lat=lat, lon=lon,
                    power=float(self.power_input.text()),
                    frequency=float(self.freq_input.text()),
                    height=float(self.height_input.text())
                )
                self.emp_sources[new_emp.uuid] = new_emp
                # TODO: Thêm/cập nhật vào bảng và bản đồ

            elif self.current_mode in ["ADD_OBSTACLE", "EDIT_OBSTACLE"]:
                new_obs = Obstacle(
                    name=name, lat=lat, lon=lon,
                    length=float(self.length_input.text()),
                    width=float(self.width_input.text()),
                    height=float(self.height_input.text())
                )
                self.obstacles[new_obs.uuid] = new_obs
                # TODO: Thêm/cập nhật vào bảng và bản đồ
            
            self.is_dirty = True
            self._update_window_title()
            self._cancel_details_form() # Dọn dẹp form sau khi lưu
            # TODO: Refresh bảng hiển thị

        except ValueError:
            QMessageBox.warning(self, "Lỗi Nhập liệu", "Vui lòng nhập đúng định dạng số cho các thông số.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi không xác định", f"Đã có lỗi xảy ra: {e}")

    def _cancel_details_form(self):
        """Dọn dẹp form và thoát khỏi chế độ Thêm/Sửa."""
        self.details_group.setVisible(False)
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.current_mode = None
        self.statusBar().showMessage("Sẵn sàng.")

    # --- LOGIC LƯU/MỞ DỰ ÁN ---

    def _new_project(self):
        if self._check_dirty_and_save():
            self.emp_sources.clear()
            self.obstacles.clear()
            self.current_project_path = None
            self.is_dirty = False
            # TODO: Xóa mọi thứ trên bảng và bản đồ
            self._update_window_title()
            self.statusBar().showMessage("Đã tạo dự án mới.")

    def _open_project(self):
        if self._check_dirty_and_save():
            path, _ = QFileDialog.getOpenFileName(self, "Mở dự án", "", "EMP Project Files (*.emp_proj);;All Files (*)")
            if path:
                success, data = load_project(path)
                if success:
                    self.emp_sources = data['emps']
                    self.obstacles = data['obstacles']
                    # TODO: Tải dữ liệu lên bảng và bản đồ
                    # TODO: Di chuyển bản đồ đến map_state
                    self.current_project_path = path
                    self.is_dirty = False
                    self._update_window_title()
                    self.statusBar().showMessage(f"Đã mở dự án: {path}")
                else:
                    QMessageBox.critical(self, "Lỗi", data)

    def _save_project(self):
        """Lưu vào file hiện tại, hoặc gọi _save_project_as nếu chưa có file."""
        if not self.current_project_path:
            return self._save_project_as()
        else:
            # TODO: Lấy map_state từ bản đồ
            map_state = {"center": [21.0285, 105.8542], "zoom": 13}
            success, message = save_project(self.current_project_path, self.emp_sources, self.obstacles, map_state)
            if success:
                self.is_dirty = False
                self._update_window_title()
                self.statusBar().showMessage(message)
            else:
                QMessageBox.critical(self, "Lỗi", message)
            return success

    def _save_project_as(self):
        """Mở hộp thoại để lưu dự án thành file mới."""
        path, _ = QFileDialog.getSaveFileName(self, "Lưu dự án thành", "Dự án EMP mới.emp_proj", "EMP Project Files (*.emp_proj);;All Files (*)")
        if path:
            self.current_project_path = path
            return self._save_project()
        return False
    
    def _check_dirty_and_save(self):
        """Kiểm tra nếu có thay đổi chưa lưu, hỏi người dùng có muốn lưu không."""
        if not self.is_dirty:
            return True # Không có gì để lưu, tiếp tục
        
        reply = QMessageBox.question(self, 'Lưu thay đổi?',
            'Dự án của bạn có những thay đổi chưa được lưu. Bạn có muốn lưu lại không?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save)

        if reply == QMessageBox.Cancel:
            return False # Người dùng hủy hành động
        if reply == QMessageBox.Save:
            return self._save_project() # Lưu và tiếp tục
        return True # Người dùng chọn Discard, tiếp tục

    def closeEvent(self, event):
        """Được gọi khi người dùng đóng cửa sổ."""
        if self._check_dirty_and_save():
            event.accept() # Chấp nhận đóng
        else:
            event.ignore() # Hủy việc đóng cửa sổ