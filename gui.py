import sys
import logging # logging 추가
import os # <<< os 임포트 추가
import winreg # <<< winreg 임포트 추가
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QGroupBox, QFormLayout, QHeaderView, QStatusBar, QMessageBox, 
    QSystemTrayIcon, QMenu, QAction, QStyle, QCheckBox # <<< QCheckBox 추가
)
from PyQt5.QtCore import Qt, QSize # <<< QSize 추가
from PyQt5.QtGui import QIcon # <<< 추가

# keyboard_listener 모듈 임포트 (타입 힌트용)
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from keyboard_listener import KeyboardListener 
    from config_manager import ConfigManager

# +++ resource_path 함수 추가 시작 +++
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".") # 개발 환경에서는 현재 작업 디렉토리

    return os.path.join(base_path, relative_path)
# +++ resource_path 함수 추가 끝 +++

APP_NAME_FOR_REGISTRY = "TextReplacerPAAK" # 시작 프로그램 등록 시 사용할 앱 이름

class TextReplacerSettingsWindow(QMainWindow):
    """텍스트 치환 설정 GUI 메인 윈도우 클래스"""
    # def __init__(self): # 이전 시그니처
    def __init__(self, keyboard_listener: 'KeyboardListener', config_manager: 'ConfigManager', initial_rules: Dict[str, str], start_on_boot_setting: bool): 
        super().__init__()
        self.listener = keyboard_listener # 리스너 인스턴스 저장
        self.config_manager = config_manager # ConfigManager 인스턴스 저장
        self.rules_changed_since_last_save = False # <<< 변경 감지 플래그 추가
        self.start_on_boot_setting = start_on_boot_setting # <<< 초기 설정값 저장

        self.setWindowTitle("TextReplacerPAAK")
        # self.setGeometry(100, 100, 600, 400) # 이전 코드 주석 처리
        self.resize(800, 600) # 초기 창 크기 설정 (가로 800, 세로 600)

        # --- 아이콘 설정 --- 
        icon_path = resource_path("assets/icon.ico")  # <<< resource_path 사용
        if os.path.exists(icon_path):
             self.app_icon = QIcon(icon_path)
        elif QIcon.hasThemeIcon("document-edit"): # 테마 아이콘은 개발 시에만 유용할 수 있음
            self.app_icon = QIcon.fromTheme("document-edit") # 테마 아이콘 시도
        else:
            # 표준 아이콘 사용 (예: SP_DesktopIcon)
            self.app_icon = self.style().standardIcon(QStyle.SP_DesktopIcon)
            logging.warning(f"Custom icon '{icon_path}' not found and no theme icon available. Using standard icon.")
        self.setWindowIcon(self.app_icon) # 창 아이콘 설정
        # --- 아이콘 설정 끝 ---

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_add_rule_group()
        self._create_existing_rules_group()
        self._create_management_buttons()
        self._create_status_bar() # 상태 표시줄 생성 먼저 호출
        self._create_tray_icon() # <<< 트레이 아이콘 생성

        # 초기 규칙 로드 (리스너 대신 main에서 전달받은 initial_rules 사용)
        self._load_rules_into_table(initial_rules) 
        self.rules_changed_since_last_save = False # 초기 로드 후 플래그 리셋

        self._connect_signals()
        self._update_status_bar() # 리스너 상태 표시
        self._on_rule_selection_changed() # 초기 버튼 상태 설정

        # <<< 프로그램 시작 시 현재 설정에 맞게 레지스트리 상태 동기화 >>>
        self._update_startup_registry(self.start_on_boot_setting)
        logging.info(f"Initial 'Start on Boot' registry status updated to: {self.start_on_boot_setting}")

    def _create_add_rule_group(self):
        """새 규칙 추가 섹션 생성"""
        group_box = QGroupBox("Add/Edit Rule")
        layout = QFormLayout()

        self.keyword_input = QLineEdit()
        self.replacement_input = QLineEdit()
        self.add_button = QPushButton("Add Rule")
        self.edit_button = QPushButton("Update Rule") # 이름 변경 및 초기 비활성화
        self.edit_button.setEnabled(False)

        layout.addRow(QLabel("Keyword:"), self.keyword_input)
        layout.addRow(QLabel("Replacement Text:"), self.replacement_input)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        layout.addRow(button_layout)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_existing_rules_group(self):
        """기존 규칙 목록 섹션 생성"""
        group_box = QGroupBox("Existing Rules")
        layout = QVBoxLayout()

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(2)
        self.rules_table.setHorizontalHeaderLabels(["Keyword", "Replacement Text"])
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SingleSelection)
        self.rules_table.setEditTriggers(QTableWidget.NoEditTriggers) # 직접 수정 불가

        layout.addWidget(self.rules_table)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_management_buttons(self):
        """관리 버튼 (편집, 삭제 등) 섹션 생성"""
        group_box = QGroupBox("Manage")
        layout = QHBoxLayout()

        self.delete_button = QPushButton("Delete Selected Rule")
        self.save_all_button = QPushButton("Save All Rules") # 저장 버튼
        self.close_button = QPushButton("Hide Window") # <<< 버튼 텍스트 변경

        self.delete_button.setEnabled(False) # 초기 비활성화

        layout.addWidget(self.delete_button)
        layout.addStretch()
        layout.addWidget(self.save_all_button)
        layout.addWidget(self.close_button)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_status_bar(self):
        """상태 표시줄 생성 및 부가 기능 위젯 추가"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 기본 상태 메시지 레이블 (왼쪽)
        self.status_label = QLabel("Ready")
        self.statusBar.addWidget(self.status_label)

        # 선택된 규칙 표시 레이블 (왼쪽, 상태 메시지 다음)
        self.selected_rule_label = QLabel("")
        self.statusBar.addWidget(self.selected_rule_label) 
        
        # 오른쪽 정렬될 위젯들
        # <<< Start on Boot 체크박스 생성 >>>
        self.start_on_boot_checkbox = QCheckBox("Start on Boot")
        self.start_on_boot_checkbox.setToolTip("Run TextReplacerPAAK when Windows starts")
        self.start_on_boot_checkbox.setChecked(self.start_on_boot_setting) # 초기 상태 설정
        self.start_on_boot_checkbox.stateChanged.connect(self._on_start_on_boot_changed)
        self.statusBar.addPermanentWidget(self.start_on_boot_checkbox) # <<< 오른쪽에 추가
        logging.debug("Start on Boot checkbox added to status bar.")

        # <<< 피드백 버튼 생성 >>>
        self.feedback_button = QPushButton("💬") 
        self.feedback_button.setToolTip("Send Feedback")
        self.feedback_button.setFixedSize(QSize(24, 24)) 
        self.feedback_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                font-size: 16px; /* 이모지 크기 조절 */
            }
            QPushButton:hover {
                /* 호버 효과 (선택적) */
                /* background-color: lightgray; */ 
            }
        """)
        self.feedback_button.setCursor(Qt.PointingHandCursor) 
        self.feedback_button.clicked.connect(self._open_feedback) 
        self.statusBar.addPermanentWidget(self.feedback_button) # <<< 오른쪽에 추가 (체크박스 다음)
        logging.debug("Feedback button added to status bar.")

    def _create_tray_icon(self):
        """시스템 트레이 아이콘 및 메뉴 생성"""
        self.tray_icon = QSystemTrayIcon(self.app_icon, self) # 아이콘 설정
        self.tray_icon.setToolTip("TextReplacerPAAK") # 툴큐 설정

        # 트레이 메뉴 생성
        tray_menu = QMenu()
        show_action = QAction("Settings", self)
        quit_action = QAction("Exit", self)

        show_action.triggered.connect(self.show_window) # 설정 메뉴 연결
        quit_action.triggered.connect(self.quit_app)   # 종료 메뉴 연결

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu) # 메뉴 연결
        
        # 트레이 아이콘 클릭 시 동작 연결 (예: 왼쪽 버튼 클릭)
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        
        self.tray_icon.show() # 트레이 아이콘 표시
        logging.info("System tray icon created and shown.")
        
        # 첫 실행 시 간단한 메시지 표시 (선택적)
        # self.tray_icon.showMessage("TextReplacerPAAK", "Application started.", self.app_icon, 2000)

    def _update_status_bar(self):
        """상태 표시줄을 업데이트합니다."""
        if self.listener and self.listener.is_running():
            status = "Listener Running"
        else:
            status = "Listener Stopped"
        
        selected_item = self.rules_table.currentItem()
        if selected_item:
            keyword = self.rules_table.item(selected_item.row(), 0).text()
            self.selected_rule_label.setText(f"Selected: {keyword}")
        else:
            self.selected_rule_label.setText("")
            
        # 변경 사항 여부 표시 (선택적)
        if self.rules_changed_since_last_save:
            status += " (Unsaved Changes)"
            
        self.status_label.setText(status)

    def _connect_signals(self):
        """위젯 시그널을 슬롯 메서드에 연결합니다."""
        logging.debug("Connecting GUI signals.")
        self.rules_table.itemSelectionChanged.connect(self._on_rule_selection_changed)
        self.add_button.clicked.connect(self._add_rule)
        self.edit_button.clicked.connect(self._edit_rule) # 수정 버튼 연결
        self.delete_button.clicked.connect(self._delete_rule)
        self.save_all_button.clicked.connect(self._save_all_rules) # 저장 버튼 연결
        self.close_button.clicked.connect(self.hide) # <<< Hide Window 버튼 -> 창 숨기기
        # 키워드 입력 변경 시 버튼 상태 업데이트 등 추가 가능
        # self.tray_icon.activated 시그널은 _create_tray_icon 에서 연결

    def _load_rules_into_table(self, rules: Dict[str, str]):
        """주어진 규칙 딕셔너리를 테이블 위젯에 로드합니다."""
        self.rules_table.setRowCount(0) # 기존 행 모두 삭제
        self.rules_table.setRowCount(len(rules))
        row = 0
        for keyword, replacement in rules.items():
            self.rules_table.setItem(row, 0, QTableWidgetItem(keyword))
            self.rules_table.setItem(row, 1, QTableWidgetItem(replacement))
            row += 1
        logging.info(f"Loaded {len(rules)} rules into table.")
        # self.rules_changed_since_last_save = False # 로드 후 플래그 리셋은 __init__에서

    def _on_rule_selection_changed(self):
        """테이블 선택 변경 시 호출됩니다."""
        selected_items = self.rules_table.selectedItems()
        is_selected = bool(selected_items)
        
        self.delete_button.setEnabled(is_selected)
        self.edit_button.setEnabled(is_selected) # 수정 버튼 활성화/비활성화

        if is_selected:
            selected_row = self.rules_table.currentRow()
            keyword = self.rules_table.item(selected_row, 0).text()
            replacement = self.rules_table.item(selected_row, 1).text()
            self.keyword_input.setText(keyword)
            self.replacement_input.setText(replacement)
            self.selected_rule_label.setText(f"Selected: {keyword}") # 선택된 규칙 레이블 업데이트
        else:
            self.keyword_input.clear()
            self.replacement_input.clear()
            self.selected_rule_label.setText("") # 선택 해제 시 레이블 비움
            logging.debug("Rule selection cleared.")
            
        # 상태 표시줄 업데이트 (선택된 항목 반영)
        self._update_status_bar()

    def _get_current_rules_from_table(self) -> Dict[str, str]:
        """현재 테이블 위젯의 모든 규칙을 딕셔너리로 반환합니다."""
        rules = {}
        for row in range(self.rules_table.rowCount()):
            keyword_item = self.rules_table.item(row, 0)
            replacement_item = self.rules_table.item(row, 1)
            if keyword_item and replacement_item: # 항목이 실제로 존재하는지 확인
                rules[keyword_item.text()] = replacement_item.text()
        return rules

    def _add_rule(self):
        """새 규칙을 추가합니다."""
        keyword = self.keyword_input.text().strip()
        replacement = self.replacement_input.text() # 공백 유지 가능

        if not keyword:
            QMessageBox.warning(self, "Input Error", "Keyword cannot be empty.")
            return

        # 현재 테이블에서 키워드 중복 확인
        current_rules = self._get_current_rules_from_table()
        if keyword in current_rules:
            QMessageBox.warning(self, "Duplicate Keyword", f"The keyword '{keyword}' already exists.")
            return

        # 테이블에 행 추가
        row_count = self.rules_table.rowCount()
        self.rules_table.insertRow(row_count)
        self.rules_table.setItem(row_count, 0, QTableWidgetItem(keyword))
        self.rules_table.setItem(row_count, 1, QTableWidgetItem(replacement))
        logging.info(f"Rule added to table: '{keyword}' -> '{replacement[:20]}...'")
        self.rules_changed_since_last_save = True # <<< 플래그 설정

        # 입력 필드 초기화 및 선택 해제
        self.keyword_input.clear()
        self.replacement_input.clear()
        self.rules_table.clearSelection()
        
        # 상태 업데이트 (선택적)
        # self.statusBar.showMessage(f"Rule '{keyword}' added to list. Click 'Save All' to apply.", 3000)
        self._update_status_bar() # 변경 상태 반영

    def _edit_rule(self):
        """선택된 규칙을 수정합니다."""
        selected_row = self.rules_table.currentRow()
        if selected_row < 0:
            return # 선택된 행 없음

        original_keyword = self.rules_table.item(selected_row, 0).text()
        new_keyword = self.keyword_input.text().strip()
        new_replacement = self.replacement_input.text()

        if not new_keyword:
            QMessageBox.warning(self, "Input Error", "Keyword cannot be empty.")
            return

        # 현재 테이블에서 키워드 중복 확인 (자기 자신 제외)
        current_rules = self._get_current_rules_from_table()
        if new_keyword != original_keyword and new_keyword in current_rules:
            QMessageBox.warning(self, "Duplicate Keyword", f"The keyword '{new_keyword}' already exists.")
            return
            
        # 테이블 업데이트 (변경 확인 후 플래그 설정)
        keyword_changed = (self.rules_table.item(selected_row, 0).text() != new_keyword)
        replacement_changed = (self.rules_table.item(selected_row, 1).text() != new_replacement)
        
        if keyword_changed or replacement_changed:
            self.rules_table.setItem(selected_row, 0, QTableWidgetItem(new_keyword))
            self.rules_table.setItem(selected_row, 1, QTableWidgetItem(new_replacement))
            logging.info(f"Rule updated in table: '{original_keyword}' -> '{new_keyword}' = '{new_replacement[:20]}...'")
            self.rules_changed_since_last_save = True # <<< 플래그 설정
        else:
            logging.debug("No changes detected for the selected rule.")

        # 입력 필드 초기화 및 선택 해제
        self.keyword_input.clear()
        self.replacement_input.clear()
        self.rules_table.clearSelection()
        
        # 상태 업데이트
        # self.statusBar.showMessage(f"Rule '{new_keyword}' updated in list. Click 'Save All' to apply.", 3000)
        self._update_status_bar() # 변경 상태 반영

    def _delete_rule(self):
        """선택된 규칙을 삭제합니다."""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        selected_row = selected_rows[0].row() # SingleSelection 모드이므로 첫 번째 항목 사용
        keyword = self.rules_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f"Are you sure you want to delete the rule for '{keyword}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.rules_table.removeRow(selected_row)
            logging.info(f"Rule for '{keyword}' removed from table.")
            self.rules_changed_since_last_save = True # <<< 플래그 설정
            
            # 입력 필드 초기화 및 선택 해제
            self.keyword_input.clear()
            self.replacement_input.clear()
            self.rules_table.clearSelection() # 삭제 후 선택 해제
            
            # 상태 업데이트
            # self.statusBar.showMessage(f"Rule '{keyword}' removed from list. Click 'Save All' to apply changes.", 3000)
            self._update_status_bar() # 변경 상태 반영

    def _save_all_rules(self):
        """현재 테이블의 모든 규칙을 파일에 저장하고 리스너를 업데이트합니다."""
        current_rules = self._get_current_rules_from_table()
        
        save_success = self.config_manager.save_rules(current_rules)
        
        if save_success:
            # 리스너에게도 변경된 규칙 알림
            self.listener.update_rules(current_rules)
            self.rules_changed_since_last_save = False # <<< 저장 성공 시 플래그 리셋
            self.statusBar.showMessage("All rules saved successfully!", 3000)
            logging.info("All rules saved and listener updated.")
            self._update_status_bar() # 상태 표시줄 업데이트
            return True # 저장 성공
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save rules to the file. Check logs for details.")
            self.statusBar.showMessage("Error saving rules!", 3000)
            self._update_status_bar() # 상태 표시줄 업데이트 (실패 상태 유지)
            return False # 저장 실패

    # <<< 트레이 아이콘 관련 슬롯 추가 >>>
    def _on_tray_icon_activated(self, reason):
        """트레이 아이콘 활성화 시 호출 (예: 클릭)"""
        # 더블클릭 또는 클릭 시 창 표시
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
            
    def show_window(self):
        """설정 창을 보여주고 활성화합니다."""
        if self.isHidden() or self.isMinimized():
            self.showNormal() # 최소화/숨김 상태면 보통 크기로 표시
        self.raise_() # 다른 창 위로 올림
        self.activateWindow() # 창 활성화
        logging.debug("Settings window shown from tray request.")
        
    def quit_app(self):
        """애플리케이션을 완전히 종료합니다."""
        logging.info("Quit action triggered from tray menu. Stopping listener and quitting application.")
        if self.listener:
            self.listener.stop() # 리스너 먼저 중지
        # 트레이 아이콘 숨기기 (종료 전에 깔끔하게)
        self.tray_icon.hide()
        QApplication.quit() # 애플리케이션 종료

    def closeEvent(self, event):
        """윈도우 닫기 이벤트 처리 (숨기기)""" 
        # 변경 사항 저장 여부 묻지 않고 바로 숨김
        logging.info("Close event triggered. Hiding window without save confirmation.")
        self.hide()
        event.ignore() # 실제 닫기 이벤트는 무시 (숨겼으므로)

    # <<< 피드백 버튼 슬롯 추가 >>>
    def _open_feedback(self):
        """피드백 버튼 클릭 시 호출될 슬롯 (현재는 플레이스홀더)"""
        logging.info("Feedback button clicked. (Functionality to open URL not implemented yet)")
        # 나중에 여기에 webbrowser.open('your_feedback_url') 추가
        QMessageBox.information(self, "Feedback", "Feedback functionality is not yet implemented.")

    # <<< Start on Boot 체크박스 슬롯 추가 >>>
    def _on_start_on_boot_changed(self, state):
        """'Start on Boot' 체크박스 상태 변경 시 호출됩니다."""
        is_checked = (state == Qt.Checked)
        logging.info(f"'Start on Boot' checkbox state changed to: {is_checked}")
        
        # 설정 파일 업데이트
        config = self.config_manager.load_config()
        if "settings" not in config:
            config["settings"] = {} # settings 키가 없으면 생성
        config["settings"]["start_on_boot"] = is_checked
        
        save_success = self.config_manager.save_config(config)
        
        if save_success:
            logging.info(f"'start_on_boot' setting saved as {is_checked}.")
            # <<< 실제 Windows 시작 프로그램 등록/해제 로직 호출 >>>
            if self._update_startup_registry(is_checked):
                self.statusBar.showMessage(f"Start on boot setting {'enabled' if is_checked else 'disabled'}.", 3000)
            else:
                # 레지스트리 업데이트 실패 시 사용자에게 알림 (에러는 _update_startup_registry 내부에서 로깅)
                QMessageBox.critical(self, "Registry Error", f"Failed to update 'Start on Boot' registry setting. See logs for details.")
                # 실패 시 체크박스 상태를 이전으로 되돌릴 수 있음 (선택적)
                self.start_on_boot_checkbox.blockSignals(True)
                self.start_on_boot_checkbox.setChecked(not is_checked) # 이전 상태로 복원
                self.start_on_boot_checkbox.blockSignals(False)
                is_checked = not is_checked # 내부 상태 변수도 원복
        else:
             logging.error("Failed to save 'start_on_boot' setting to config file.")
             # 오류 발생 시 사용자에게 알림 (QMessageBox 등)
             QMessageBox.critical(self, "Config Save Error", "Failed to save the 'Start on Boot' setting to the configuration file.")
             
        # 내부 상태 변수 업데이트 (필요시)
        self.start_on_boot_setting = is_checked

    def _update_startup_registry(self, enable: bool) -> bool:
        """
        Windows 시작 프로그램 레지스트리를 업데이트합니다.
        HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run 경로를 사용합니다.

        Args:
            enable (bool): True이면 시작 프로그램에 등록, False이면 제거합니다.
        
        Returns:
            bool: 작업 성공 여부.
        """
        registry_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            # 실행 파일 경로 가져오기 (PyInstaller로 빌드된 경우 포함)
            # 실행 파일이 따옴표로 묶인 경로로 레지스트리에 저장되어야 공백이 있는 경로도 정상 작동함
            executable_path = f'"{sys.executable}"'

            if enable:
                executable_path_with_arg = f'{executable_path} /tray' # <<< 인자 추가
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, APP_NAME_FOR_REGISTRY, 0, winreg.REG_SZ, executable_path_with_arg)
                logging.info(f"Application '{APP_NAME_FOR_REGISTRY}' added to startup: {executable_path_with_arg}")
            else:
                # 키가 없을 때 오류가 발생하지 않도록 예외 처리 추가
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, APP_NAME_FOR_REGISTRY)
                    logging.info(f"Application '{APP_NAME_FOR_REGISTRY}' removed from startup.")
                except FileNotFoundError:
                    logging.info(f"Application '{APP_NAME_FOR_REGISTRY}' was not found in startup. No action needed.")
                except Exception as e_delete: # 삭제 중 다른 예외
                    logging.error(f"Error removing '{APP_NAME_FOR_REGISTRY}' from startup: {e_delete}", exc_info=True)
                    # return False # 삭제 실패 시 false 반환 (선택적, 상황에 따라 다름)
            return True
        except PermissionError:
            logging.error(f"Permission denied while trying to modify startup registry for '{APP_NAME_FOR_REGISTRY}'. Ensure you have the necessary rights or run as administrator if applicable.", exc_info=True)
            QMessageBox.warning(self, "Permission Denied", "Could not modify Windows startup settings due to insufficient permissions. Please try running the application as an administrator if this issue persists.")
            return False
        except Exception as e:
            logging.error(f"Failed to update startup registry for '{APP_NAME_FOR_REGISTRY}': {e}", exc_info=True)
            return False

if __name__ == '__main__':
    # 이 파일 단독 실행 시 GUI 테스트용
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # <<< 트레이 앱을 위해 추가
    
    # 테스트를 위한 Mock 객체 또는 실제 객체 생성 필요
    class MockListener: rules = {"!t1": "test1", "!t2": "test2"}; is_running=lambda:True; update_rules=lambda x: print("Mock update:", x); stop=lambda: print("Mock listener stopped")
    class MockConfigManager: save_rules=lambda x: print("Mock save:", x); load_rules=lambda: {}
    window = TextReplacerSettingsWindow(MockListener(), MockConfigManager(), {"!t1": "test1", "!t2": "test2"}, False)
    # window.show() # <<< 시작 시 창 표시 안 함
    
    sys.exit(app.exec_())

import os # 아이콘 경로 확인용
from PyQt5.QtWidgets import QStyle # 표준 아이콘용

if __name__ == '__main__':
    # 이 파일 단독 실행 시 GUI 테스트용
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # <<< 트레이 앱을 위해 추가
    
    # 테스트를 위한 Mock 객체 또는 실제 객체 생성 필요
    class MockListener: rules = {"!t1": "test1", "!t2": "test2"}; is_running=lambda:True; update_rules=lambda x: print("Mock update:", x); stop=lambda: print("Mock listener stopped")
    class MockConfigManager: save_rules=lambda x: print("Mock save:", x); load_rules=lambda: {}
    window = TextReplacerSettingsWindow(MockListener(), MockConfigManager(), {"!t1": "test1", "!t2": "test2"}, False)
    # window.show() # <<< 시작 시 창 표시 안 함
    
    sys.exit(app.exec_()) 