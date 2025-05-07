import sys
import logging # logging 임포트 추가
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon # QIcon 임포트 추가
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
    app.setWindowIcon(QIcon('assets/icon.ico')) # 애플리케이션 아이콘 설정
    # 마지막 창이 닫혀도 앱이 종료되지 않도록 설정
    app.setQuitOnLastWindowClosed(False) 

    # <<< 시작 시 트레이 모드로 실행할지 결정 >>>
    start_in_tray_mode = "/tray" in sys.argv
    logging.info(f"Command line arguments: {sys.argv}")
    logging.info(f"Start in tray mode evaluated to: {start_in_tray_mode}")

    # ConfigManager 인스턴스 생성 및 전체 설정 로드
    config_manager = ConfigManager()
    config = config_manager.load_config()
    initial_rules = config.get("rules", {}) # rules 키가 없으면 빈 딕셔너리
    initial_settings = config.get("settings", {}) # settings 키가 없으면 빈 딕셔너리
    start_on_boot_setting = initial_settings.get("start_on_boot", False) # start_on_boot 없으면 False
    
    logging.info(f"Using config file: {config_manager.config_file_path}")
    logging.info(f"Loaded {len(initial_rules)} rules and settings (Start on boot: {start_on_boot_setting}) at startup.")
    
    # TODO: 로드된 start_on_boot_setting 값에 따라 실제 시작 프로그램 등록/해제 로직 수행
    # (예: update_startup_registry(start_on_boot_setting))

    # KeyboardListener 인스턴스 생성 시 로드된 규칙 전달
    kb_listener = KeyboardListener(rules=initial_rules)
    kb_listener.start()
    logging.info("Keyboard listener started from main with loaded rules.")

    # GUI 윈도우 생성 (시작 시 숨겨진 상태 -> 활성화됨)
    window = TextReplacerSettingsWindow(
        keyboard_listener=kb_listener, 
        config_manager=config_manager, 
        initial_rules=initial_rules,
        start_on_boot_setting=start_on_boot_setting # <<< 시작 설정값 전달
    )
    # window.show() # <<< 시작 시 창을 보여주도록 변경 -> 조건부 호출로 변경

    # <<< 트레이 모드 시작 여부에 따라 창 표시 결정 >>>
    if not start_in_tray_mode:
        window.show()
        logging.info("Main window shown normally because start_in_tray_mode is False.")
    else:
        logging.info("Starting in tray mode (window.show() not called). Tray icon should be visible from gui.py.")

    # 애플리케이션 이벤트 루프 시작
    exit_code = app.exec_()
    logging.info("Application event loop finished.") # 종료 로그 메시지 변경
    
    # 애플리케이션 종료 전 리스너 명시적 중지 (quit_app에서 이미 호출하지만 안전하게 한번 더)
    if kb_listener and kb_listener.is_running():
        logging.info("Stopping keyboard listener before exiting...")
        kb_listener.stop()
        
    sys.exit(exit_code)
