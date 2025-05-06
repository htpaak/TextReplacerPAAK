import sys
import logging # logging 임포트 추가
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt # Qt 임포트 추가
from log_setup import setup_logging
from gui import TextReplacerSettingsWindow # GUI 윈도우 임포트
from keyboard_listener import KeyboardListener # KeyboardListener 임포트
from config_manager import ConfigManager # ConfigManager 임포트

setup_logging() # 로그 설정 먼저 호출

# CONFIG_FILE = "rules.json" # 설정 파일 경로 -> ConfigManager 내부에서 결정하므로 제거

if __name__ == '__main__':
    # DPI 스케일링 활성화 (QApplication 생성 전 호출)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling) 
    
    app = QApplication(sys.argv)
    # 마지막 창이 닫혀도 앱이 종료되지 않도록 설정
    app.setQuitOnLastWindowClosed(False) 

    # ConfigManager 인스턴스 생성 및 규칙 로드 (인자 없이 호출)
    config_manager = ConfigManager()
    initial_rules = config_manager.load_rules()
    # 경로 로깅 추가 (config_manager에서 결정된 경로 확인용)
    logging.info(f"Using config file: {config_manager.config_file_path}")
    logging.info(f"Loaded {len(initial_rules)} rules at startup.") # 경로 정보는 위 로그에 포함

    # KeyboardListener 인스턴스 생성 시 로드된 규칙 전달
    kb_listener = KeyboardListener(rules=initial_rules)
    kb_listener.start()
    logging.info("Keyboard listener started from main with loaded rules.")

    # GUI 윈도우 생성 (시작 시 숨겨진 상태)
    window = TextReplacerSettingsWindow(
        keyboard_listener=kb_listener, 
        config_manager=config_manager, 
        initial_rules=initial_rules
    )
    window.show() # <<< 시작 시 창을 보여주도록 변경

    # 애플리케이션 이벤트 루프 시작
    exit_code = app.exec_()
    logging.info("Application event loop finished.") # 종료 로그 메시지 변경
    
    # 애플리케이션 종료 전 리스너 명시적 중지 (quit_app에서 이미 호출하지만 안전하게 한번 더)
    if kb_listener and kb_listener.is_running():
        logging.info("Stopping keyboard listener before exiting...")
        kb_listener.stop()
        
    sys.exit(exit_code)
