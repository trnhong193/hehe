# emp_planning_system/main_window.py

import os
from datetime import datetime
import uuid
import json

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QGroupBox, QFormLayout, QLineEdit,
                             QLabel, QSplitter, QDoubleSpinBox, QMessageBox,
                             QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem,
                             QAction, QToolBar, QStatusBar, QMenu, QProgressDialog)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QIcon

# --- Các import cần thiết cho heatmap mới ---
import matplotlib
matplotlib.use('Agg') # Chuyển backend để không cần GUI của matplotlib
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import numpy as np
# -------------------------------------------

from map_view import MapView
from data_models import EMP, Obstacle
from calculations import calculate_emp_field
from project_manager import save_project, load_project
from report_generator import generate_report

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = None
        self.emp_sources = {}
        self.obstacles = {}
        self.current_project_path = None
        self.is_dirty = False
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP")
        self.setGeometry(100, 100, 1440, 800)
        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self.setStatusBar(QStatusBar(self))
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        splitter = QSplitter(Qt.Horizontal)
        self.control_panel = self._create_control_panel()
        self.map_view = MapView()
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.map_view)
        splitter.setSizes([400, 1040])
        main_layout.addWidget(splitter)
        self._connect_signals()
        self._update_window_title()

    # _create_actions, _create_menu_bar, _create_tool_bar không đổi

    def _create_control_panel(self):
        # ... (code không đổi so với Phần 2, chỉ thêm context menu) ...
        panel_widget = QWidget()
        # ... (tạo general_group, tab_widget, objects_tab, details_tab) ...
        # --- Bổ sung Context Menu cho Bảng ---
        self.emp_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.emp_table.customContextMenuRequested.connect(lambda pos: self._show_table_context_menu(self.emp_table, pos))
        self.obstacle_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.obstacle_table.customContextMenuRequested.connect(lambda pos: self._show_table_context_menu(self.obstacle_table, pos))
        # ------------------------------------
        return panel_widget

    def _connect_signals(self):
        """Kết nối tất cả các tín hiệu (actions và widgets)."""
        # Actions
        self.new_action.triggered.connect(self._new_project)
        self.open_action.triggered.connect(self._open_project)
        self.save_action.triggered.connect(self._save_project)
        self.save_as_action.triggered.connect(self._save_project_as)
        self.exit_action.triggered.connect(self.close)
        self.add_emp_action.triggered.connect(self._enter_add_emp_mode)
        self.add_obstacle_action.triggered.connect(self._enter_add_obstacle_mode)
        self.calc_action.triggered.connect(self._trigger_calculation)

        # Map signals
        self.map_view.bridge.mapClicked.connect(self._on_map_clicked)
        self.map_view.bridge.mapBoundsReceived.connect(self._on_map_bounds_received)

    # --- LOGIC QUẢN LÝ DỰ ÁN (Lưu, Mở, Mới) ---
    # (Các hàm này đã hoàn thiện ở Phần 2, không cần thay đổi)

    # --- LOGIC QUẢN LÝ ĐỐI TƯỢNG (Thêm, Sửa, Xóa) ---

    def _enter_edit_mode(self, table, item):
        """Vào chế độ chỉnh sửa cho đối tượng được chọn."""
        uuid = item.data(Qt.UserRole)
        if table is self.emp_table and uuid in self.emp_sources:
            self.current_mode = "EDIT_EMP"
            self.current_edit_uuid = uuid
            self._populate_details_form("EMP", self.emp_sources[uuid])
        elif table is self.obstacle_table and uuid in self.obstacles:
            self.current_mode = "EDIT_OBSTACLE"
            self.current_edit_uuid = uuid
            self._populate_details_form("OBSTACLE", self.obstacles[uuid])
        self.control_panel.findChild(QTabWidget).setCurrentWidget(self.details_tab)

    def _delete_object(self, table, item):
        """Xóa đối tượng được chọn."""
        uuid = item.data(Qt.UserRole)
        name = item.text()
        
        reply = QMessageBox.question(self, 'Xác nhận xóa',
            f"Bạn có chắc chắn muốn xóa đối tượng '{name}' không?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if table is self.emp_table and uuid in self.emp_sources:
                del self.emp_sources[uuid]
                # TODO: Xóa marker trên bản đồ
            elif table is self.obstacle_table and uuid in self.obstacles:
                del self.obstacles[uuid]
                # TODO: Xóa hình trên bản đồ
            
            self._refresh_object_tables()
            self.is_dirty = True
            self._update_window_title()

    def _save_object(self):
        # ... (code kiểm tra tên, lat, lon không đổi) ...
        # --- Cập nhật logic để xử lý Sửa và Thêm ---
        uuid_to_save = self.current_edit_uuid if self.current_mode in ["EDIT_EMP", "EDIT_OBSTACLE"] else str(uuid.uuid4())

        if self.current_mode in ["ADD_EMP", "EDIT_EMP"]:
            obj = EMP(...)
            obj.uuid = uuid_to_save
            self.emp_sources[obj.uuid] = obj
            # TODO: Vẽ/Cập nhật marker trên bản đồ

        elif self.current_mode in ["ADD_OBSTACLE", "EDIT_OBSTACLE"]:
            obj = Obstacle(...)
            obj.uuid = uuid_to_save
            self.obstacles[obj.uuid] = obj
            # TODO: Vẽ/Cập nhật hình trên bản đồ
            
        self._refresh_object_tables()
        self.is_dirty = True
        self._update_window_title()
        self._cancel_details_form()
    
    # --- CẬP NHẬT GIAO DIỆN ---

    def _refresh_object_tables(self):
        """Cập nhật lại toàn bộ dữ liệu trên cả hai bảng."""
        # Bảng EMP
        self.emp_table.setRowCount(0)
        for uuid, emp in self.emp_sources.items():
            row_position = self.emp_table.rowCount()
            self.emp_table.insertRow(row_position)
            
            name_item = QTableWidgetItem(emp.name)
            name_item.setData(Qt.UserRole, uuid) # Gắn UUID ẩn vào item
            
            self.emp_table.setItem(row_position, 0, name_item)
            self.emp_table.setItem(row_position, 1, QTableWidgetItem(f"{emp.lat:.6f}"))
            self.emp_table.setItem(row_position, 2, QTableWidgetItem(f"{emp.lon:.6f}"))

        # Bảng Vật cản
        self.obstacle_table.setRowCount(0)
        for uuid, obs in self.obstacles.items():
            row_position = self.obstacle_table.rowCount()
            self.obstacle_table.insertRow(row_position)

            name_item = QTableWidgetItem(obs.name)
            name_item.setData(Qt.UserRole, uuid)

            self.obstacle_table.setItem(row_position, 0, name_item)
            self.obstacle_table.setItem(row_position, 1, QTableWidgetItem(f"{obs.lat:.6f}"))
            self.obstacle_table.setItem(row_position, 2, QTableWidgetItem(f"{obs.lon:.6f}"))
    
    def _show_table_context_menu(self, table, position):
        """Hiển thị menu chuột phải cho bảng."""
        item = table.itemAt(position)
        if not item:
            return

        menu = QMenu()
        edit_action = menu.addAction("Sửa thông tin...")
        delete_action = menu.addAction("Xóa đối tượng")
        # zoom_action = menu.addAction("Phóng to tới đối tượng")
        
        action = menu.exec_(table.mapToGlobal(position))
        
        if action == edit_action:
            self._enter_edit_mode(table, table.item(item.row(), 0))
        elif action == delete_action:
            self._delete_object(table, table.item(item.row(), 0))
    
    # --- LOGIC TÍNH TOÁN VÀ HIỂN THỊ HEATMAP ---

    def _trigger_calculation(self):
        if not self.emp_sources:
            QMessageBox.information(self, "Thông báo", "Chưa có nguồn EMP nào để tính toán.")
            return
        self.progress_dialog = QProgressDialog("Đang yêu cầu thông tin bản đồ...", "Hủy", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        self.map_view.run_js("getMapBounds();")

    def _on_map_bounds_received(self, s, w, n, e):
        self.progress_dialog.setLabelText("Đang tính toán, vui lòng chờ...")
        bounds = {'lat_min': s, 'lon_min': w, 'lat_max': n, 'lon_max': e}
        user_altitude = self.altitude_input.value()
        QTimer.singleShot(100, lambda: self._perform_calculation(bounds, user_altitude))

    def _perform_calculation(self, bounds, user_altitude):
        try:
            grid_data = calculate_emp_field(
                list(self.emp_sources.values()), 
                list(self.obstacles.values()), 
                user_altitude, bounds, grid_size=(200, 200)
            )
            self._create_heatmap_image_with_contours(grid_data)
            image_path_for_js = 'temp_overlay.png'
            self.map_view.run_js(
                f"updateOverlayImage('{image_path_for_js}', {bounds['lat_min']}, {bounds['lon_min']}, {bounds['lat_max']}, {bounds['lon_max']});"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Tính toán", f"Đã có lỗi xảy ra: {e}")
        finally:
            self.progress_dialog.close()

    def _create_heatmap_image_with_contours(self, grid_data):
        """Tạo file ảnh PNG với các đường viền (contour) bằng Matplotlib."""
        try:
            levels = [10, 50]  # Ngưỡng Cảnh báo và Nguy hiểm
            colors = ['#FFD700', '#FF4500'] # Màu Vàng và Đỏ Cam
            height, width = grid_data.shape
            if height == 0 or width == 0: return

            fig = plt.figure(figsize=(width / 100.0, height / 100.0), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')

            # Chỉ vẽ nếu có giá trị lớn hơn 0
            if np.max(grid_data) > 0:
                # Dùng zoom để làm mịn dữ liệu
                smoothed_grid = zoom(grid_data, 3)
                # Vẽ vùng tô màu
                ax.contourf(smoothed_grid, levels=levels, colors=colors, alpha=0.5, extend='max', origin='lower')
                # Vẽ đường viền
                ax.contour(smoothed_grid, levels=levels, colors='black', linewidths=0.7, origin='lower')

            base_path = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(base_path, 'web', 'temp_overlay.png')
            fig.savefig(save_path, transparent=True, dpi=100)
            plt.close(fig)
        except Exception as e:
            print(f"Lỗi khi tạo heatmap: {e}")


    # ... (Các hàm còn lại như _cancel_details_form, _on_map_clicked, etc. đã hoàn thiện) ...