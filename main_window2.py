# emp_planning_system/data_models.py

import uuid
from dataclasses import dataclass, field

@dataclass
class EMP:
    """Lớp lưu trữ thông tin cho một nguồn phát EMP."""
    name: str
    lat: float
    lon: float
    power: float
    frequency: float
    height: float
    # UUID (Universally Unique Identifier) là một định danh duy nhất do máy tự tạo.
    # Nó giúp chương trình phân biệt chính xác các đối tượng ngay cả khi chúng trùng tên.
    # Nó không cần được cung cấp khi khởi tạo (init=False) và không hiển thị khi print (repr=False).
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()), init=False, repr=False)

@dataclass
class Obstacle:
    """Lớp lưu trữ thông tin cho một vật cản."""
    name: str
    lat: float
    lon: float
    length: float
    width: float
    height: float
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()), init=False, repr=False)
```**Giải thích:**
*   `id` đã được thay bằng `name` để người dùng có thể đặt tên tùy ý.
*   `uuid` được thêm vào để làm định danh nội bộ. `field(default_factory=...)` đảm bảo mỗi khi một đối tượng mới được tạo, nó sẽ tự động có một UUID duy nhất.

---

#### **Bước 1.2: Đại tu `main_window.py`**

Đây là thay đổi lớn nhất. Chúng ta sẽ xây dựng lại giao diện theo hướng chuyên nghiệp hơn. Hãy **thay thế toàn bộ** nội dung file `main_window.py` của bạn bằng mã nguồn bên dưới.

**Lưu ý:** Mã nguồn này sẽ tạo ra giao diện mới nhưng các nút bấm sẽ chưa có đầy đủ chức năng. Chúng ta sẽ lập trình logic cho chúng ở Phần 2.

```python
# emp_planning_system/main_window.py

import os
from datetime import datetime
import uuid
import json 

# --- THAY ĐỔI LỚN VỀ CÁC THƯ VIỆN QT ĐƯỢC IMPORT ---
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QGroupBox, QFormLayout, QLineEdit,
                             QLabel, QSplitter, QDoubleSpinBox, QMessageBox,
                             QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem,
                             QAction, QToolBar, QStatusBar)
from PyQt5.QtCore import Qt, QTimer

from map_view import MapView
from data_models import EMP, Obstacle
from calculations import calculate_emp_field
# (Chúng ta sẽ tạo file report_generator sau, tạm thời có thể comment dòng import nếu cần)
# from report_generator import generate_report

# --- CẤU TRÚC LỚP MAINWINDOW HOÀN TOÀN MỚI ---
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Các thuộc tính quản lý trạng thái ---
        self.current_mode = None  # ADD_EMP, ADD_OBSTACLE, EDIT_EMP, EDIT_OBSTACLE
        
        # Dùng dictionary thay cho list để truy cập, sửa, xóa nhanh hơn qua UUID
        self.emp_sources = {}     
        self.obstacles = {}       
        
        self.current_project_path = None # Đường dẫn file dự án đang mở
        self.is_dirty = False # Biến cờ để kiểm tra xem dự án đã có thay đổi chưa lưu

        # Bắt đầu xây dựng giao diện
        self._init_ui()

    def _init_ui(self):
        """Hàm khởi tạo toàn bộ giao diện người dùng."""
        self.setWindowTitle("Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP")
        self.setGeometry(100, 100, 1440, 800) # Tăng kích thước cửa sổ một chút

        # --- 1. TẠO CÁC THÀNH PHẦN CHÍNH: MENU, TOOLBAR, STATUSBAR ---
        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self.setStatusBar(QStatusBar(self)) # Thêm thanh trạng thái

        # --- 2. TẠO BỐ CỤC CHÍNH (3 KHỐI) ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        splitter = QSplitter(Qt.Horizontal)
        
        # KHỐI TRÁI: PANEL ĐIỀU KHIỂN
        self.control_panel = self._create_control_panel()
        
        # KHỐI PHẢI: BẢN ĐỒ
        self.map_view = MapView()

        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.map_view)
        splitter.setSizes([400, 1040]) # Điều chỉnh kích thước ban đầu

        main_layout.addWidget(splitter)
        
        # Kết nối các tín hiệu ban đầu
        self.map_view.bridge.mapClicked.connect(self._on_map_clicked)
        # (Các kết nối khác sẽ được thêm ở Phần 2)

    def _create_actions(self):
        """Tạo các hành động (QAction) sẽ được dùng trong menu và toolbar."""
        # Lưu ý: Để có icon, bạn cần tạo thư mục 'icons' và đặt các file ảnh vào đó
        # Ví dụ: self.new_action = QAction(QIcon('icons/new.png'), "&Dự án mới", self)
        # Ở đây, chúng ta tạm thời dùng phiên bản không có icon để đảm bảo code chạy được ngay.
        self.new_action = QAction("&Dự án mới", self)
        self.open_action = QAction("&Mở dự án...", self)
        self.save_action = QAction("&Lưu dự án", self)
        self.save_as_action = QAction("Lưu thành...", self)
        self.exit_action = QAction("Thoát", self)
        
        self.add_emp_action = QAction("Thêm nguồn EMP", self)
        self.add_obstacle_action = QAction("Thêm vật cản", self)
        self.calc_action = QAction("Tính toán vùng ảnh hưởng", self)

    def _create_menu_bar(self):
        """Tạo thanh menu ở trên cùng cửa sổ."""
        menu_bar = self.menuBar()
        # Menu Tệp tin
        file_menu = menu_bar.addMenu("&Tệp tin")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Menu Hành động
        action_menu = menu_bar.addMenu("&Hành động")
        action_menu.addAction(self.add_emp_action)
        action_menu.addAction(self.add_obstacle_action)
        action_menu.addSeparator()
        action_menu.addAction(self.calc_action)

    def _create_tool_bar(self):
        """Tạo thanh công cụ với các icon truy cập nhanh."""
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

    def _create_control_panel(self):
        """Tạo panel điều khiển bên trái với cấu trúc Tab."""
        panel_widget = QWidget()
        panel_layout = QVBoxLayout(panel_widget)

        # Hộp Thiết lập chung
        general_group = QGroupBox("Thiết lập chung")
        general_layout = QFormLayout()
        self.altitude_input = QDoubleSpinBox()
        self.altitude_input.setRange(-1000, 10000)
        self.altitude_input.setValue(5.0)
        self.altitude_input.setSuffix(" m")
        general_layout.addRow("Độ cao xét ảnh hưởng:", self.altitude_input)
        general_group.setLayout(general_layout)

        # Cấu trúc Tab
        tab_widget = QTabWidget()
        
        # -- TAB 1: DANH SÁCH ĐỐI TƯỢNG --
        objects_tab = QWidget()
        objects_layout = QVBoxLayout(objects_tab)
        
        # Bảng EMP
        emp_group = QGroupBox("Danh sách nguồn EMP")
        emp_layout = QVBoxLayout()
        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(3)
        self.emp_table.setHorizontalHeaderLabels(["Tên", "Vĩ độ", "Kinh độ"])
        emp_layout.addWidget(self.emp_table)
        emp_group.setLayout(emp_layout)
        
        # Bảng Vật cản
        obstacle_group = QGroupBox("Danh sách vật cản")
        obstacle_layout = QVBoxLayout()
        self.obstacle_table = QTableWidget()
        self.obstacle_table.setColumnCount(3)
        self.obstacle_table.setHorizontalHeaderLabels(["Tên", "Vĩ độ", "Kinh độ"])
        obstacle_layout.addWidget(self.obstacle_table)
        obstacle_group.setLayout(obstacle_layout)

        objects_layout.addWidget(emp_group)
        objects_layout.addWidget(obstacle_group)

        # -- TAB 2: THUỘC TÍNH / THÊM MỚI --
        self.details_tab = QWidget()
        details_layout = QVBoxLayout(self.details_tab)
        
        self.details_group = QGroupBox("Chi tiết đối tượng")
        self.details_layout = QFormLayout()
        self.details_group.setLayout(self.details_layout)
        details_layout.addWidget(self.details_group)
        # Form chi tiết sẽ được tạo động, ban đầu chỉ là một group trống
        
        tab_widget.addTab(objects_tab, "Danh sách đối tượng")
        tab_widget.addTab(self.details_tab, "Thuộc tính")

        panel_layout.addWidget(general_group)
        panel_layout.addWidget(tab_widget)
        
        return panel_widget

    def _on_map_clicked(self, lat, lon):
        """Hàm được gọi khi nhận được tín hiệu click từ bản đồ."""
        # Logic đầy đủ sẽ được hoàn thiện ở Phần 2.
        # Tạm thời chỉ in ra để kiểm tra.
        print(f"Bản đồ được click tại {lat}, {lon}. Chế độ hiện tại: {self.current_mode}")
        if self.current_mode in ["ADD_EMP", "ADD_OBSTACLE"]:
            # Tự động chuyển qua tab "Thuộc tính" và điền tọa độ
            self.control_panel.findChild(QTabWidget).setCurrentWidget(self.details_tab)
            self.lat_input.setText(f"{lat:.6f}")
            self.lon_input.setText(f"{lon:.6f}")
            self.statusBar().showMessage(f"Đã chọn tọa độ: {lat:.6f}, {lon:.6f}. Vui lòng nhập thông tin.")
            self.name_input.setFocus() # Chuyển con trỏ vào ô nhập Tên

    # --- CÁC HÀM LOGIC SẼ ĐƯỢC HOÀN THIỆN Ở BƯỚC TIẾP THEO ---
    # Các hàm trống này là cần thiết để chương trình có thể chạy mà không báo lỗi.
    def _populate_details_form(self, object_type, data=None):
        pass

    def _save_object(self):
        pass
    
    def _new_project(self):
        pass

    def _open_project(self):
        pass

    def _save_project(self):
        pass

    def closeEvent(self, event):
        # Hàm này sẽ được gọi khi người dùng đóng cửa sổ
        # Chúng ta sẽ thêm logic hỏi lưu file ở đây
        pass