import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt # Qt 임포트 추가
from log_setup import setup_logging
from gui import TextReplacerSettingsWindow # GUI 윈도우 임포트

setup_logging() # 항상 호출 (내부에서 조건 확인)

if __name__ == '__main__':
    # DPI 스케일링 활성화 (QApplication 생성 전 호출)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling) 
    
    app = QApplication(sys.argv)
    window = TextReplacerSettingsWindow()
    window.show()
    sys.exit(app.exec_())
