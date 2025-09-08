import sys
import os
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

# Hàm chính để chạy ứng dụng
def main():
    """
    Hàm khởi tạo và chạy ứng dụng PyQt.
    """
    # Mỗi ứng dụng PyQt cần một đối tượng QApplication.
    # sys.argv là các tham số dòng lệnh truyền vào (nếu có).
    app = QApplication(sys.argv)

    # Tạo một instance của cửa sổ chính mà chúng ta sẽ định nghĩa trong file main_window.py
    main_win = MainWindow()

    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222" 

    # Hiển thị cửa sổ
    main_win.show()

    # Bắt đầu vòng lặp sự kiện của ứng dụng.
    # Chương trình sẽ ở đây cho đến khi người dùng đóng cửa sổ.
    # sys.exit() đảm bảo chương trình thoát một cách sạch sẽ.
    sys.exit(app.exec_())

# Dòng này đảm bảo hàm main() chỉ được gọi khi file này được chạy trực tiếp
# (chứ không phải khi được import bởi một file khác).
if __name__ == '__main__':
    main()