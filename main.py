import sys
import logging # logging 임포트 추가
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt # Qt 임포트 추가
from log_setup import setup_logging
from gui import TextReplacerSettingsWindow # GUI 윈도우 임포트
from keyboard_listener import KeyboardListener # KeyboardListener 임포트
from config_manager import ConfigManager # ConfigManager 임포트

setup_logging() # 항상 호출 (내부에서 조건 확인)

CONFIG_FILE = "rules.json" # 설정 파일 경로

if __name__ == '__main__':
    # DPI 스케일링 활성화 (QApplication 생성 전 호출)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling) 
    
    app = QApplication(sys.argv)

    # ConfigManager 인스턴스 생성 및 규칙 로드
    config_manager = ConfigManager(CONFIG_FILE)
    initial_rules = config_manager.load_rules()
    logging.info(f"Loaded {len(initial_rules)} rules from {CONFIG_FILE} at startup.")

    # KeyboardListener 인스턴스 생성 시 로드된 규칙 전달
    kb_listener = KeyboardListener(rules=initial_rules)
    kb_listener.start()
    logging.info("Keyboard listener started from main with loaded rules.")

    # GUI 윈도우 생성 시 리스너 인스턴스와 ConfigManager 인스턴스, 로드된 규칙 전달
    window = TextReplacerSettingsWindow(
        keyboard_listener=kb_listener, 
        config_manager=config_manager, 
        initial_rules=initial_rules
    )
    window.show()

    # 애플리케이션 종료 시 리스너 정리 (선택적, 데몬 스레드이므로 자동 종료되지만 명시적 중지 가능)ㅂㅈㄷㄱ11!!
    # app.aboutToQuit.connect(kb_listener.stop) 

    exit_code = app.exec_()
    logging.info("Application exiting...")
    # 명시적으로 리스너를 중지하려면 여기서 호출할 수도 있습니다.
    # kb_listener.stop() # 이미 데몬 스레드라 필요 없을 수 있음
    sys.exit(exit_code)
