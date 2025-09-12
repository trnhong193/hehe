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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import numpy as np

from map_view import MapView
from data_models import EMP, Obstacle
from calculations import calculate_emp_field
from project_manager import save_project, load_project
from report_generator import generate_report

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = None
        self.current_edit_uuid = None
        self.emp_sources = {}
        self.obstacles = {}
        self.current_project_path = None
        self.is_dirty = False
        self._save_path_pending = None
        self.current_map_state = {"center": [21.0285, 105.8542], "zoom": 13}
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
        splitter.setSizes([450, 990])
        main_layout.addWidget(splitter)
        self._connect_signals()
        self._update_window_title()

    def _create_actions(self):
        self.new_action = QAction("&Dự án mới", self)
        self.open_action = QAction("&Mở dự án...", self)
        self.save_action = QAction("&Lưu dự án", self)
        self.save_as_action = QAction("Lưu thành...", self)
        self.exit_action = QAction("Thoát", self)
        self.add_emp_action = QAction("Thêm nguồn EMP", self)
        self.add_obstacle_action = QAction("Thêm vật cản", self)
        self.calc_action = QAction("Tính toán vùng ảnh hưởng", self)
        self.report_action = QAction("Xuất báo cáo PDF", self)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&Tệp tin")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        action_menu = menu_bar.addMenu("&Hành động")
        action_menu.addAction(self.add_emp_action)
        action_menu.addAction(self.add_obstacle_action)
        action_menu.addSeparator()
        action_menu.addAction(self.calc_action)
        action_menu.addAction(self.report_action)

    def _create_tool_bar(self):
        tool_bar = QToolBar("Thanh công cụ chính")
        self.addToolBar(tool_bar)
        tool_bar.addAction(self.new_action)
        tool_bar.addAction(self.open_action)
        tool_bar.addAction(self.save_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.add_emp_action)
        tool_bar.addAction(self.add_obstacle_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.calc_action)
        tool_bar.addAction(self.report_action)

    def _create_control_panel(self):
        panel_widget = QWidget()
        panel_layout = QVBoxLayout(panel_widget)
        general_group = QGroupBox("Thiết lập chung")
        general_layout = QFormLayout()
        self.altitude_input = QDoubleSpinBox()
        self.altitude_input.setRange(-1000, 10000)
        self.altitude_input.setValue(5.0)
        self.altitude_input.setSuffix(" m")
        general_layout.addRow("Độ cao xét ảnh hưởng:", self.altitude_input)
        general_group.setLayout(general_layout)
        
        self.tab_widget = QTabWidget()
        objects_tab = QWidget()
        objects_layout = QVBoxLayout(objects_tab)
        emp_group = QGroupBox("Danh sách nguồn EMP")
        emp_layout = QVBoxLayout()
        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(3)
        self.emp_table.setHorizontalHeaderLabels(["Tên", "Vĩ độ", "Kinh độ"])
        self.emp_table.setContextMenuPolicy(Qt.CustomContextMenu)
        emp_layout.addWidget(self.emp_table)
        emp_group.setLayout(emp_layout)
        obstacle_group = QGroupBox("Danh sách vật cản")
        obstacle_layout = QVBoxLayout()
        self.obstacle_table = QTableWidget()
        self.obstacle_table.setColumnCount(3)
        self.obstacle_table.setHorizontalHeaderLabels(["Tên", "Vĩ độ", "Kinh độ"])
        self.obstacle_table.setContextMenuPolicy(Qt.CustomContextMenu)
        obstacle_layout.addWidget(self.obstacle_table)
        obstacle_group.setLayout(obstacle_layout)
        objects_layout.addWidget(emp_group)
        objects_layout.addWidget(obstacle_group)
        
        self.details_tab = QWidget()
        details_layout = QVBoxLayout(self.details_tab)
        self.details_group = QGroupBox("Chi tiết đối tượng")
        self.details_layout = QFormLayout()
        self.details_group.setLayout(self.details_layout)
        details_layout.addWidget(self.details_group)
        
        self.tab_widget.addTab(objects_tab, "Danh sách đối tượng")
        self.tab_widget.addTab(self.details_tab, "Thuộc tính")
        panel_layout.addWidget(general_group)
        panel_layout.addWidget(self.tab_widget)
        return panel_widget

    def _connect_signals(self):
        self.new_action.triggered.connect(self._new_project)
        self.open_action.triggered.connect(self._open_project)
        self.save_action.triggered.connect(self._save_project)
        self.save_as_action.triggered.connect(self._save_project_as)
        self.exit_action.triggered.connect(self.close)
        self.add_emp_action.triggered.connect(self._enter_add_emp_mode)
        self.add_obstacle_action.triggered.connect(self._enter_add_obstacle_mode)
        self.calc_action.triggered.connect(self._trigger_calculation)
        self.report_action.triggered.connect(self._export_report)
        self.map_view.bridge.mapClicked.connect(self._on_map_clicked)
        self.map_view.bridge.mapBoundsReceived.connect(self._on_map_bounds_received)
        self.map_view.bridge.mapViewReceived.connect(self._on_map_view_received)
        self.emp_table.customContextMenuRequested.connect(lambda pos: self._show_table_context_menu(self.emp_table, pos))
        self.obstacle_table.customContextMenuRequested.connect(lambda pos: self._show_table_context_menu(self.obstacle_table, pos))

    def _add_object_to_map(self, obj):
        obj_json = json.dumps(obj.__dict__)
        if isinstance(obj, EMP):
            self.map_view.run_js(f"addEmpMarker({obj_json});")
        elif isinstance(obj, Obstacle):
            self.map_view.run_js(f"addObstacleShape({obj_json});")

    def _remove_object_from_map(self, uuid):
        self.map_view.run_js(f"removeObject('{uuid}');")
    
    def _clear_map(self):
        self.map_view.run_js("clearAllObjects();")

    def _refresh_object_tables(self):
        self.emp_table.setRowCount(0)
        for uuid, emp in self.emp_sources.items():
            row = self.emp_table.rowCount()
            self.emp_table.insertRow(row)
            name_item = QTableWidgetItem(emp.name)
            name_item.setData(Qt.UserRole, uuid)
            self.emp_table.setItem(row, 0, name_item)
            self.emp_table.setItem(row, 1, QTableWidgetItem(f"{emp.lat:.6f}"))
            self.emp_table.setItem(row, 2, QTableWidgetItem(f"{emp.lon:.6f}"))
        self.obstacle_table.setRowCount(0)
        for uuid, obs in self.obstacles.items():
            row = self.obstacle_table.rowCount()
            self.obstacle_table.insertRow(row)
            name_item = QTableWidgetItem(obs.name)
            name_item.setData(Qt.UserRole, uuid)
            self.obstacle_table.setItem(row, 0, name_item)
            self.obstacle_table.setItem(row, 1, QTableWidgetItem(f"{obs.lat:.6f}"))
            self.obstacle_table.setItem(row, 2, QTableWidgetItem(f"{obs.lon:.6f}"))

    def _update_window_title(self):
        title = "Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP"
        project_name = os.path.basename(self.current_project_path) if self.current_project_path else "Dự án mới"
        dirty_marker = "*" if self.is_dirty else ""
        self.setWindowTitle(f"{project_name}{dirty_marker} - {title}")

    def _enter_add_emp_mode(self):
        self.current_mode = "ADD_EMP"
        self.statusBar().showMessage("Chế độ thêm nguồn EMP: Click lên bản đồ để chọn vị trí.")
        self._populate_details_form("EMP")
        self.tab_widget.setCurrentWidget(self.details_tab) # <-- SỬA LỖI Ở ĐÂY

    def _enter_add_obstacle_mode(self):
        self.current_mode = "ADD_OBSTACLE"
        self.statusBar().showMessage("Chế độ thêm vật cản: Click lên bản đồ để chọn vị trí.")
        self._populate_details_form("OBSTACLE")
        self.tab_widget.setCurrentWidget(self.details_tab) # <-- SỬA LỖI Ở ĐÂY

    def _on_map_clicked(self, lat, lon):
        if self.current_mode in ["ADD_EMP", "ADD_OBSTACLE"]:
            self.tab_widget.setCurrentWidget(self.details_tab)
            self.lat_input.setText(f"{lat:.6f}")
            self.lon_input.setText(f"{lon:.6f}")
            self.statusBar().showMessage(f"Đã chọn tọa độ: {lat:.6f}, {lon:.6f}. Vui lòng nhập thông tin.")
            self.name_input.setFocus()
    
    def _populate_details_form(self, object_type, data_object=None):
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
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
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Thiếu thông tin", "Tên đối tượng không được để trống.")
                return
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            uuid_to_save = self.current_edit_uuid if self.current_mode.startswith("EDIT") else str(uuid.uuid4())
            if self.current_mode in ["ADD_EMP", "EDIT_EMP"]:
                obj = EMP(name=name, lat=lat, lon=lon, power=float(self.power_input.text()), frequency=float(self.freq_input.text()), height=float(self.height_input.text()))
                obj.uuid = uuid_to_save
                self.emp_sources[obj.uuid] = obj
                self._add_object_to_map(obj)
            elif self.current_mode in ["ADD_OBSTACLE", "EDIT_OBSTACLE"]:
                obj = Obstacle(name=name, lat=lat, lon=lon, length=float(self.length_input.text()), width=float(self.width_input.text()), height=float(self.height_input.text()))
                obj.uuid = uuid_to_save
                self.obstacles[obj.uuid] = obj
                self._add_object_to_map(obj)
            self._refresh_object_tables()
            self.is_dirty = True
            self._update_window_title()
            self._cancel_details_form()
        except ValueError:
            QMessageBox.warning(self, "Lỗi Nhập liệu", "Vui lòng nhập đúng định dạng số cho các thông số.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi không xác định", f"Đã có lỗi xảy ra: {e}")

    def _cancel_details_form(self):
        self.details_group.setVisible(False)
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        self.current_mode = None
        self.current_edit_uuid = None
        self.statusBar().showMessage("Sẵn sàng.")

    def _show_table_context_menu(self, table, position):
        item = table.itemAt(position)
        if not item: return
        menu = QMenu()
        edit_action = menu.addAction("Sửa thông tin...")
        delete_action = menu.addAction("Xóa đối tượng")
        action = menu.exec_(table.mapToGlobal(position))
        if action == edit_action:
            self._enter_edit_mode(table, table.item(item.row(), 0))
        elif action == delete_action:
            self._delete_object(table, table.item(item.row(), 0))

    def _enter_edit_mode(self, table, item):
        uuid = item.data(Qt.UserRole)
        if table is self.emp_table and uuid in self.emp_sources:
            self.current_mode = "EDIT_EMP"
            self.current_edit_uuid = uuid
            self._populate_details_form("EMP", self.emp_sources[uuid])
            self.tab_widget.setCurrentWidget(self.details_tab)
        elif table is self.obstacle_table and uuid in self.obstacles:
            self.current_mode = "EDIT_OBSTACLE"
            self.current_edit_uuid = uuid
            self._populate_details_form("OBSTACLE", self.obstacles[uuid])
            self.tab_widget.setCurrentWidget(self.details_tab)

    def _delete_object(self, table, item):
        uuid = item.data(Qt.UserRole)
        name = item.text()
        reply = QMessageBox.question(self, 'Xác nhận xóa', f"Bạn có chắc chắn muốn xóa '{name}' không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if table is self.emp_table and uuid in self.emp_sources:
                del self.emp_sources[uuid]
                self._remove_object_from_map(uuid)
            elif table is self.obstacle_table and uuid in self.obstacles:
                del self.obstacles[uuid]
                self._remove_object_from_map(uuid)
            self._refresh_object_tables()
            self.is_dirty = True
            self._update_window_title()

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
        QTimer.singleShot(50, lambda: self._perform_calculation(bounds, user_altitude))

    def _perform_calculation(self, bounds, user_altitude):
        try:
            grid_data = calculate_emp_field(list(self.emp_sources.values()), list(self.obstacles.values()), user_altitude, bounds, grid_size=(200, 200))
            self._create_heatmap_image_with_contours(grid_data)
            self.map_view.run_js(f"updateOverlayImage('temp_overlay.png', {bounds['lat_min']}, {bounds['lon_min']}, {bounds['lat_max']}, {bounds['lon_max']});")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Tính toán", f"Đã có lỗi xảy ra: {e}")
        finally:
            if hasattr(self, 'progress_dialog'): self.progress_dialog.close()

    def _create_heatmap_image_with_contours(self, grid_data):
        try:
            levels = [10, 50]
            colors = ['#FFD700', '#FF4500']
            height, width = grid_data.shape
            if height == 0 or width == 0: return
            fig = plt.figure(figsize=(width / 100.0, height / 100.0), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            if np.max(grid_data) > levels[0]:
                smoothed_grid = zoom(grid_data, 3, order=1)
                ax.contourf(smoothed_grid, levels=levels, colors=colors, alpha=0.5, extend='max', origin='lower')
                ax.contour(smoothed_grid, levels=levels, colors='black', linewidths=0.7, origin='lower')
            base_path = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(base_path, 'web', 'temp_overlay.png')
            fig.savefig(save_path, transparent=True, dpi=100)
            plt.close(fig)
        except Exception as e:
            print(f"Lỗi khi tạo heatmap: {e}")

    def _export_report(self):
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'temp_overlay.png')
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng chạy 'Tính toán' trước khi xuất báo cáo.")
            return
        default_filename = f"BaoCao_EMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo PDF", default_filename, "PDF Files (*.pdf)")
        if save_path:
            report_data = {'emps': list(self.emp_sources.values()), 'obstacles': list(self.obstacles.values()), 'image_path': image_path, 'altitude': self.altitude_input.value()}
            success, message = generate_report(save_path, report_data)
            if success:
                QMessageBox.information(self, "Thành công", message)
            else:
                QMessageBox.critical(self, "Thất bại", message)

    def _on_map_view_received(self, lat, lon, zoom):
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
            self._save_path_pending = None

    def _new_project(self):
        if not self._check_dirty_and_save(): return
        self.emp_sources.clear()
        self.obstacles.clear()
        self._clear_map()
        self._refresh_object_tables()
        self.current_project_path = None
        self.is_dirty = False
        self._update_window_title()
        self.statusBar().showMessage("Đã tạo dự án mới.")

    def _open_project(self):
        if not self._check_dirty_and_save(): return
        path, _ = QFileDialog.getOpenFileName(self, "Mở dự án", "", "EMP Project Files (*.emp_proj);;All Files (*)")
        if path:
            success, data = load_project(path)
            if success:
                self._clear_map()
                self.emp_sources = data.get('emps', {})
                self.obstacles = data.get('obstacles', {})
                self._refresh_object_tables()
                for emp in self.emp_sources.values(): self._add_object_to_map(emp)
                for obs in self.obstacles.values(): self._add_object_to_map(obs)
                map_state = data.get('map_state')
                if map_state: self.map_view.run_js(f"setMapView({map_state['center'][0]}, {map_state['center'][1]}, {map_state['zoom']});")
                self.current_project_path = path
                self.is_dirty = False
                self._update_window_title()
                self.statusBar().showMessage(f"Đã mở dự án: {path}")
            else:
                QMessageBox.critical(self, "Lỗi", data)

    def _save_project(self):
        if not self.current_project_path: return self._save_project_as()
        self.statusBar().showMessage("Đang lấy trạng thái bản đồ để lưu...")
        self._save_path_pending = self.current_project_path
        self.map_view.run_js("getMapView();")
        return True

    def _save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu dự án thành", "Dự án EMP mới.emp_proj", "EMP Project Files (*.emp_proj);;All Files (*)")
        if path:
            self._save_path_pending = path
            self.map_view.run_js("getMapView();")
            return True
        return False
    
    def _check_dirty_and_save(self):
        if not self.is_dirty: return True
        reply = QMessageBox.question(self, 'Lưu thay đổi?', 'Dự án của bạn có những thay đổi chưa được lưu. Bạn có muốn lưu lại không?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
        if reply == QMessageBox.Cancel: return False
        if reply == QMessageBox.Save: return self._save_project()
        return True

    def closeEvent(self, event):
        if self._check_dirty_and_save():
            event.accept()
        else:
            event.ignore()