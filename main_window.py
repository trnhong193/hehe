import uuid
import numpy as np
import os
from PIL import Image
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QGroupBox, QFormLayout, QLineEdit,
                             QLabel, QSplitter, QDoubleSpinBox, QMessageBox, QListWidget, QProgressDialog, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from calculations import calculate_emp_field # Import hàm tính toán

from map_view import MapView
from data_models import EMP, Obstacle
from report_generator import generate_report

class MainWindow(QMainWindow):
    """
    Lớp cửa sổ chính của ứng dụng.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Thiết lập các thuộc tính cơ bản cho cửa sổ
        self.setWindowTitle("Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP")
        self.setGeometry(100, 100, 1280, 720) # (x, y, width, height)
        # Biến trạng thái để biết người dùng đang muốn thêm gì
        self.current_mode = None # Có thể là "ADD_EMP" hoặc "ADD_OBSTACLE"
        
        # Danh sách lưu trữ các đối tượng
        self.emp_sources = []
        self.obstacles = []
        
        # Tạo widget trung tâm chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Tạo layout để sắp xếp các widget
         # Sử dụng layout ngang chính
        main_layout = QHBoxLayout(main_widget)

        # Sử dụng QSplitter để có thể thay đổi kích thước 2 panel
        splitter = QSplitter(Qt.Horizontal)

        # Tạo bảng điều khiển bên trái
        self.control_panel = self._create_control_panel()
        
        # Tạo bản đồ bên phải
        self.map_view = MapView()

        # Thêm 2 widget vào splitter
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.map_view)
        splitter.setSizes([350, 930]) # Kích thước ban đầu cho 2 panel

        # Thêm splitter vào layout chính
        main_layout.addWidget(splitter)
        
        # Kết nối tín hiệu từ bản đồ tới hàm xử lý
        self.map_view.bridge.mapClicked.connect(self._on_map_clicked)
        self.map_view.bridge.mapBoundsReceived.connect(self._on_map_bounds_received)
     
    def _create_control_panel(self):
        """Hàm tạo panel điều khiển bên trái."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignTop)

        # 1. Nhóm thiết lập chung
        general_group = QGroupBox("Thiết lập chung")
        general_layout = QFormLayout()
        self.altitude_input = QDoubleSpinBox()
        self.altitude_input.setRange(-1000, 10000)
        self.altitude_input.setValue(0.0)
        self.altitude_input.setSuffix(" m")
        general_layout.addRow("Độ cao xét ảnh hưởng:", self.altitude_input)
        general_group.setLayout(general_layout)

        # 2. Nhóm hành động
        actions_group = QGroupBox("Hành động")
        actions_layout = QVBoxLayout()
        self.add_emp_btn = QPushButton("Thêm nguồn EMP")
        self.add_obstacle_btn = QPushButton("Thêm vật cản")
        
        self.calc_btn = QPushButton("Tính toán và Hiển thị Vùng ảnh hưởng")
        self.export_pdf_btn = QPushButton("Xuất Báo cáo PDF")

        self.status_label = QLabel("Trạng thái: Sẵn sàng.")
        self.status_label.setWordWrap(True) # Cho phép tự xuống dòng
        
        actions_layout.addWidget(self.add_emp_btn)
        actions_layout.addWidget(self.add_obstacle_btn)
        actions_layout.addWidget(self.export_pdf_btn)
        actions_layout.addWidget(self.status_label)
        actions_group.setLayout(actions_layout)
        actions_layout.addWidget(self.calc_btn)
        # 3. Nhóm chi tiết (để nhập thông số EMP/Vật cản)
        self.details_group = QGroupBox("Chi tiết đối tượng")
        self.details_layout = QFormLayout()
        # Các ô nhập liệu sẽ được thêm vào đây sau
        self.details_group.setLayout(self.details_layout)
        self.details_group.setVisible(False) # Mặc định ẩn đi

         # --- THÊM MỚI: NHÓM DANH SÁCH ĐỐI TƯỢNG ---
        list_group = QGroupBox("Danh sách đối tượng")
        list_layout = QVBoxLayout()
        self.object_list_widget = QListWidget()
        list_layout.addWidget(self.object_list_widget)
        list_group.setLayout(list_layout)
        # --- KẾT THÚC THÊM MỚI ---


        # Thêm các nhóm vào layout chính của panel
        layout.addWidget(general_group)
        layout.addWidget(actions_group)
        layout.addWidget(self.details_group)
        layout.addWidget(list_group)

        # Kết nối tín hiệu cho các nút bấm
        self.add_emp_btn.clicked.connect(self._handle_add_emp_mode)
        self.add_obstacle_btn.clicked.connect(self._handle_add_obstacle_mode)
        self.calc_btn.clicked.connect(self._trigger_calculation)
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        return panel

    def _handle_add_emp_mode(self):
        """Kích hoạt chế độ thêm EMP."""
        self.current_mode = "ADD_EMP"
        self.status_label.setText("Trạng thái: Click lên bản đồ để chọn vị trí đặt nguồn EMP.")
        # Hiển thị form nhập chi tiết cho EMP (sẽ làm ở bước sau)
        self._populate_details_form("EMP")

    def _handle_add_obstacle_mode(self):
        """Kích hoạt chế độ thêm Vật cản."""
        self.current_mode = "ADD_OBSTACLE"
        self.status_label.setText("Trạng thái: Click lên bản đồ để chọn vị trí đặt vật cản.")
        # Hiển thị form nhập chi tiết cho Vật cản (sẽ làm ở bước sau)
        self._populate_details_form("OBSTACLE")

    def _on_map_clicked(self, lat, lon):
        if self.current_mode is None:
            return
        # Đã có self.lat_input và self.lon_input được tạo trong _populate_details_form
        self.lat_input.setText(f"{lat:.6f}")
        self.lon_input.setText(f"{lon:.6f}")
        self.status_label.setText(f"Đã chọn tọa độ: {lat:.6f}, {lon:.6f}. Vui lòng nhập các thông số còn lại.")

    def _populate_details_form(self, object_type):
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.lat_input = QLineEdit()
        self.lon_input = QLineEdit()
        self.details_layout.addRow("Vĩ độ (Lat):", self.lat_input)
        self.details_layout.addRow("Kinh độ (Lon):", self.lon_input)

        if object_type == "EMP":
            self.details_group.setTitle("Chi tiết nguồn EMP")
            self.power_input = QLineEdit("1000") # Thêm giá trị mặc định
            self.freq_input = QLineEdit("300")
            self.height_input = QLineEdit("10")
            self.details_layout.addRow("Công suất (W):", self.power_input)
            self.details_layout.addRow("Tần số (MHz):", self.freq_input)
            self.details_layout.addRow("Độ cao lắp đặt (m):", self.height_input)
        elif object_type == "OBSTACLE":
            self.details_group.setTitle("Chi tiết vật cản")
            self.length_input = QLineEdit("20")
            self.width_input = QLineEdit("10")
            self.height_input = QLineEdit("15")
            self.details_layout.addRow("Chiều dài (m):", self.length_input)
            self.details_layout.addRow("Chiều rộng (m):", self.width_input)
            self.details_layout.addRow("Chiều cao (m):", self.height_input)

        save_btn = QPushButton("Lưu đối tượng")
        cancel_btn = QPushButton("Hủy")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.details_layout.addRow(btn_layout)

        # --- KẾT NỐI NÚT LƯU VÀ HỦY ---
        save_btn.clicked.connect(self._save_object)
        cancel_btn.clicked.connect(self._reset_mode)

        self.details_group.setVisible(True)

    def _save_object(self):
        """Lấy dữ liệu từ form, tạo đối tượng, lưu trữ và vẽ lên bản đồ."""
        try:
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            obj_id = str(uuid.uuid4()) # Tạo một ID ngẫu nhiên, duy nhất

            if self.current_mode == "ADD_EMP":
                power = float(self.power_input.text())
                freq = float(self.freq_input.text())
                height = float(self.height_input.text())
                
                new_emp = EMP(id=obj_id, lat=lat, lon=lon, power=power, frequency=freq, height=height)
                self.emp_sources.append(new_emp)
                
                # Thêm vào danh sách hiển thị
                self.object_list_widget.addItem(f"EMP: {obj_id[:8]}... ({lat:.2f}, {lon:.2f})")
                # Gọi JS để vẽ
                self.map_view.run_js(f"addEmpMarker({lat}, {lon}, '{obj_id}');")

            elif self.current_mode == "ADD_OBSTACLE":
                length = float(self.length_input.text())
                width = float(self.width_input.text())
                height = float(self.height_input.text())

                new_obstacle = Obstacle(id=obj_id, lat=lat, lon=lon, length=length, width=width, height=height)
                self.obstacles.append(new_obstacle)

                # Thêm vào danh sách hiển thị
                self.object_list_widget.addItem(f"Vật cản: {obj_id[:8]}... ({lat:.2f}, {lon:.2f})")
                # Gọi JS để vẽ
                self.map_view.run_js(f"addObstacleShape({lat}, {lon}, {length}, {width}, '{obj_id}');")

            # Reset giao diện sau khi lưu thành công
            self._reset_mode()

        except ValueError:
            # Báo lỗi nếu người dùng nhập chữ vào ô số
            QMessageBox.warning(self, "Lỗi Nhập liệu", "Vui lòng nhập đúng định dạng số cho các thông số.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi không xác định", f"Đã có lỗi xảy ra: {e}")

    def _reset_mode(self):
        """Reset giao diện về trạng thái ban đầu."""
        self.current_mode = None
        self.details_group.setVisible(False)
        self.status_label.setText("Trạng thái: Sẵn sàng.")

    def _trigger_calculation(self):
        """Bắt đầu quá trình tính toán bằng cách yêu cầu JS gửi thông tin biên."""
        if not self.emp_sources:
            QMessageBox.information(self, "Thông báo", "Chưa có nguồn EMP nào để tính toán.")
            return

        # Hiển thị thanh tiến trình
        self.progress_dialog = QProgressDialog("Đang yêu cầu thông tin bản đồ...", "Hủy", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        # Yêu cầu Javascript cung cấp thông tin biên của bản đồ
        self.map_view.run_js("getMapBounds();")

    def _on_map_bounds_received(self, s, w, n, e):
        """Nhận được thông tin biên, bắt đầu tính toán thực sự."""
        self.progress_dialog.setLabelText("Đang tính toán, vui lòng chờ...")

        bounds = {'lat_min': s, 'lon_min': w, 'lat_max': n, 'lon_max': e}
        user_altitude = self.altitude_input.value()
        
        # Chạy tính toán trong một QTimer để không làm treo giao diện
        # Đây là một kỹ thuật đơn giản để xử lý tác vụ nền
        QTimer.singleShot(100, lambda: self._perform_calculation(bounds, user_altitude))

    def _perform_calculation(self, bounds, user_altitude):
        """Thực hiện tính toán và hiển thị kết quả."""
        try:
            # Gọi hàm tính toán
            grid_data = calculate_emp_field(
                self.emp_sources, self.obstacles, user_altitude, bounds, grid_size=(400, 400)
            )

            # Tạo ảnh heatmap từ dữ liệu grid
            self._create_heatmap_image(grid_data, bounds)
            
            # Yêu cầu JS hiển thị ảnh
            base_path = os.path.dirname(os.path.abspath(__file__))
            # image_path_relative = 'web/temp_overlay.png'
            # image_path_absolute = os.path.join(base_path, image_path_relative)
            image_path_for_js = "temp_overlay.png"
            # Cần đảm bảo đường dẫn dùng trong JS là tương đối
            self.map_view.run_js(
                f"updateOverlayImage('{image_path_for_js}', {bounds['lat_min']}, {bounds['lon_min']}, {bounds['lat_max']}, {bounds['lon_max']});"
            )

        except Exception as e:
            QMessageBox.critical(self, "Lỗi Tính toán", f"Đã có lỗi xảy ra: {e}")
        finally:
            self.progress_dialog.close()

    def _create_heatmap_image(self, grid_data, bounds):
        """Tạo file ảnh PNG từ dữ liệu numpy."""
        # Chuẩn hóa dữ liệu về khoảng 0-255 để tô màu
        # Dùng thang đo log để hiển thị rõ hơn các vùng chênh lệch lớn
        with np.errstate(divide='ignore'):
            grid_log = np.log10(grid_data + 1e-9) # Thêm số nhỏ để tránh log(0)
        
        # Ngưỡng màu dựa trên thang log
        # E=10 -> log10(10)=1. E=50 -> log10(50)~1.7
        log_warn = 1.0
        log_danger = 1.7
        
        # Tạo mảng màu RGBA 4 chiều
        height, width = grid_data.shape
        rgba_data = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Tô màu dựa trên ngưỡng
        safe_mask = (grid_log > 0) & (grid_log <= log_warn)
        warn_mask = (grid_log > log_warn) & (grid_log <= log_danger)
        danger_mask = (grid_log > log_danger)
        
        # Màu xanh (lá cây) cho vùng cảnh báo nhẹ (trong ngưỡng an toàn nhưng có tín hiệu)
        rgba_data[safe_mask] = [0, 255, 0, 100] # RGBA
        # Màu cam cho vùng cảnh báo
        rgba_data[warn_mask] = [255, 165, 0, 120]
        # Màu đỏ cho vùng nguy hiểm
        rgba_data[danger_mask] = [255, 0, 0, 150]
        
        # Chuyển đổi mảng numpy thành ảnh PIL và lưu
        # Cần lật ngược ảnh theo chiều dọc vì hệ tọa độ ảnh và numpy khác nhau
        img = Image.fromarray(np.flipud(rgba_data), 'RGBA')
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(base_path, 'web', 'temp_overlay.png')
        img.save(save_path, 'PNG')
    def _export_pdf(self):
        """Mở hộp thoại lưu file và tạo báo cáo PDF."""
        if not self.emp_sources:
            QMessageBox.information(self, "Không thể xuất báo cáo", "Cần có ít nhất một nguồn EMP để tạo báo cáo.")
            return

        # Mở hộp thoại để người dùng chọn nơi lưu file
        # "Báo cáo EMP.pdf" là tên file mặc định gợi ý
        default_filename = os.path.join(os.path.expanduser("~"), "BaoCao_EMP.pdf")
        filename, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo", default_filename, "PDF Files (*.pdf)")

        if not filename:
            # Người dùng đã bấm Hủy
            return

        # Chuẩn bị dữ liệu cho báo cáo
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, 'web', 'temp_overlay.png')

        report_data = {
            "emps": self.emp_sources,
            "obstacles": self.obstacles,
            "altitude": self.altitude_input.value(),
            "image_path": image_path
        }

        # Gọi hàm tạo báo cáo
        success, message = generate_report(filename, report_data)

        if success:
            QMessageBox.information(self, "Thành công", message)
        else:
            QMessageBox.critical(self, "Thất bại", message)

"""
Layout: Chúng ta dùng QSplitter để tạo ra 2 panel có thể thay đổi kích thước, một cho bảng điều khiển và một cho bản đồ.
Bảng điều khiển: Được tạo bởi hàm _create_control_panel cho gọn gàng, bao gồm các QGroupBox để nhóm các chức năng lại với nhau.
Trạng thái (self.current_mode): Biến này rất quan trọng. Nó giúp chương trình biết phải làm gì khi người dùng click lên bản đồ.
Kết nối Signal-Slot: Dòng self.map_view.bridge.mapClicked.connect(self._on_map_clicked) là trung tâm của sự tương tác. Nó kết nối tín hiệu mapClicked mà chúng ta đã tạo trong Bridge với hàm _on_map_clicked của MainWindow.
Luồng hoạt động:
Người dùng nhấn nút "Thêm nguồn EMP".
Hàm _handle_add_emp_mode được gọi. Nó đặt self.current_mode = "ADD_EMP", cập nhật dòng trạng thái và gọi _populate_details_form để hiển thị các ô nhập liệu cho EMP.
Người dùng click lên bản đồ.
Bản đồ (JS) gửi tọa độ về Bridge (Python).
Bridge phát tín hiệu mapClicked.
MainWindow bắt được tín hiệu này và gọi hàm _on_map_clicked.
Hàm này điền tọa độ lat, lon nhận được vào các ô QLineEdit tương ứng.

"""
"""
1. Thêm QListWidget: Trong _create_control_panel, chúng ta tạo một QGroupBox mới chứa self.object_list_widget để hiển thị danh sách các đối tượng đã thêm.
2. Hàm _save_object: Đây là hàm xử lý chính.
Nó được bọc trong một khối try...except ValueError để bắt lỗi khi người dùng nhập sai định dạng (ví dụ: nhập "abc" vào ô công suất). QMessageBox được dùng để hiển thị hộp thoại báo lỗi thân thiện.
uuid.uuid4(): Hàm này tạo ra một ID duy nhất toàn cục. Chúng ta chuyển nó thành chuỗi để dùng làm định danh cho đối tượng.
Tùy vào self.current_mode, nó sẽ đọc dữ liệu từ các QLineEdit tương ứng, tạo đối tượng EMP hoặc Obstacle và thêm vào danh sách (self.emp_sources hoặc self.obstacles).
self.object_list_widget.addItem(...): Thêm một dòng mới vào danh sách trên giao diện để người dùng biết họ đã tạo thành công.
self.map_view.run_js(...): Đây chính là lệnh gọi JavaScript từ Python. Chúng ta xây dựng một chuỗi JavaScript và thực thi nó. Lưu ý quan trọng: obj_id là một chuỗi nên trong câu lệnh JS, nó phải được đặt trong cặp dấu nháy đơn ('{obj_id}').

3. Hàm _reset_mode: Một hàm nhỏ để dọn dẹp giao diện (ẩn form chi tiết, đặt lại trạng thái) sau khi lưu thành công hoặc hủy bỏ.

4. Nút Hủy: Chúng ta thêm nút "Hủy" và kết nối nó với _reset_mode để người dùng có thể thoát khỏi chế độ thêm đối tượng.

"""

"""
1.Nút "Tính toán": Thêm một nút mới vào giao diện để người dùng chủ động ra lệnh tính toán.
2.Luồng bất đồng bộ: Việc tính toán có thể mất vài giây. Nếu làm trực tiếp, giao diện sẽ bị "treo". Luồng xử lý mới sẽ là:
_trigger_calculation: Bấm nút -> Python yêu cầu JS cung cấp biên bản đồ (getMapBounds).
_on_map_bounds_received: JS gửi biên về -> Python nhận được và gọi _perform_calculation thông qua một QTimer.singleShot. Việc này giúp giao diện có thời gian "thở" và cập nhật thanh tiến trình.
_perform_calculation: Thực hiện việc tính toán nặng, tạo ảnh, rồi yêu cầu JS hiển thị ảnh đó.
3._create_heatmap_image:
Hàm này nhận mảng kết quả từ calculate_emp_field.
Nó dùng numpy để lọc ra các vùng nguy hiểm, cảnh báo, an toàn dựa trên ngưỡng.
Nó tạo ra một mảng 4 chiều (R, G, B, Alpha - độ trong suốt). Các vùng không có tín hiệu sẽ có Alpha=0 (hoàn toàn trong suốt).
Cuối cùng, nó dùng thư viện Pillow (Image.fromarray) để chuyển mảng numpy này thành file ảnh temp_overlay.png và lưu vào thư mục web/.
"""

"""
Thêm nút: Chúng ta thêm QPushButton("Xuất báo cáo PDF") vào nhóm "Hành động".
Kết nối _export_pdf: Nút mới được kết nối với hàm _export_pdf.
Hàm _export_pdf:
Kiểm tra xem đã có dữ liệu để báo cáo chưa.
Sử dụng QFileDialog.getSaveFileName để mở một cửa sổ "Lưu file" chuẩn của hệ điều hành. Điều này cho phép người dùng chọn vị trí và tên file PDF.
Nếu người dùng chọn một file (không bấm Hủy), hàm sẽ thu thập tất cả dữ liệu cần thiết (danh sách EMP, vật cản, độ cao, đường dẫn ảnh heatmap) vào một dictionary report_data.
Nó gọi hàm generate_report từ module report_generator và truyền tên file cùng dữ liệu vào.
Cuối cùng, nó hiển thị một thông báo thành công hoặc thất bại cho người dùng.

"""
