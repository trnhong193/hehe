import os
from PyQt5.QtCore import QObject,QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
# Bridge(Object): 1 đối tượng Python có  thể giao tiếp qua QWebChannel, kế thừa từ QObject
class Bridge(QObject):
    """
    Lớp cầu nối giữa Python và JavaScript.
    Cho phép gọi hàm Python từ JavaScript và ngược lại.
    """
    # Định nghĩa một signal. Khi nhận được click từ JS, nó sẽ phát signal này
    # để các phần khác của ứng dụng (như MainWindow) có thể lắng nghe.
    # Signal này mang theo 2 tham số là float (lat, lon)
    mapClicked = pyqtSignal(float, float)
    mapBoundsReceived = pyqtSignal(float, float, float, float)
    # Dùng decorator @pyqtSlot để hàm này có thể được gọi từ Javascript
    # Kết quả (nếu có) sẽ được trả về JS. Ở đây kiểu trả về là void.
    @pyqtSlot(float, float)
    # @pyqtSlot(float, float): Decorator này "đăng ký" hàm onMapClicked với hệ thống của Qt, cho phép nó được gọi từ bên ngoài (cụ thể là từ JavaScript). Các kiểu dữ liệu float, float phải khớp với các tham số hàm nhận vào.
    def onMapClicked(self, lat, lon):
        """
        Hàm được gọi từ Javascript khi người dùng click vào bản đồ.
        """
        print(f"Click từ bản đồ! Tọa độ: Lat={lat}, Lon={lon}")
        # Phát tín hiệu mang theo tọa độ
        self.mapClicked.emit(lat, lon)

        
    @pyqtSlot(float, float, float, float)
    def onMapBoundsReceived(self, s, w, n, e):
        # Khi nhận được thông tin từ JS, phát tín hiệu cho MainWindow
        self.mapBoundsReceived.emit(s, w, n, e)
    
class MapView(QWebEngineView):
    """
    Lớp tùy chỉnh QWebEngineView để hiển thị bản đồ Leaflet.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- PHẦN THÊM MỚI ĐỂ THIẾT LẬP KÊNH GIAO TIẾP ---
        self.channel = QWebChannel()
        self.bridge = Bridge()
        # Đăng ký đối tượng bridge với tên "py_bridge" trên kênh
        # Tên "py_bridge" này phải khớp với tên trong file index.html
        self.channel.registerObject("py_bridge", self.bridge)
        # self.channel.registerObject("py_bridge", self.bridge): Đây là dòng lệnh quan trọng nhất. Nó nói với kênh giao tiếp rằng: "Hãy tạo ra một đối tượng tên là py_bridge ở phía JavaScript, và bất cứ khi nào JavaScript gọi hàm trên py_bridge, hãy thực thi hàm tương ứng trên đối tượng self.bridge của Python."
        
        # Gán kênh này cho trang web của chúng ta
        self.page().setWebChannel(self.channel)
        # --- KẾT THÚC PHẦN THÊM MỚI ---
        self.load_map()

    def load_map(self):
        """
        Tải file HTML chứa bản đồ.
        File HTML phải nằm trong thư mục web/ so với file thực thi.
        """
        # Lấy đường dẫn tuyệt đối đến file index.html
        # os.path.dirname(__file__) lấy thư mục chứa file map_view.py hiện tại.
        # os.path.join dùng để nối các phần của đường dẫn một cách an toàn.
        base_path = os.path.dirname(os.path.abspath(__file__))
        map_html_path = os.path.join(base_path, 'web', 'index.html')

        # Kiểm tra xem file có tồn tại không để dễ dàng debug
        if not os.path.exists(map_html_path):
            print(f"Lỗi: Không tìm thấy file bản đồ tại: {map_html_path}")
            return
        
        # Load file HTML bằng QUrl. Cần dùng fromLocalFile để nó
        # có thể tải các tài nguyên cục bộ khác (js, css, tiles).
        self.load(QUrl.fromLocalFile(map_html_path))

    def run_js(self, script):
        """Thực thi một đoạn mã JavaScript trên trang web."""
        self.page().runJavaScript(script)