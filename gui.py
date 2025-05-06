import sys
import logging # logging 추가
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QGroupBox, QFormLayout, QHeaderView, QStatusBar, QMessageBox # QMessageBox 추가
)
from PyQt5.QtCore import Qt

# keyboard_listener 모듈 임포트 (타입 힌트용)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from keyboard_listener import KeyboardListener 

class TextReplacerSettingsWindow(QMainWindow):
    """텍스트 치환 설정 GUI 메인 윈도우 클래스"""
    # def __init__(self): # 이전 시그니처
    def __init__(self, keyboard_listener: 'KeyboardListener'): # 리스너 인자 추가
        super().__init__()
        self.listener = keyboard_listener # 리스너 인스턴스 저장
        self.setWindowTitle("Text Replacer Settings")
        # self.setGeometry(100, 100, 600, 400) # 이전 코드 주석 처리
        self.resize(800, 600) # 초기 창 크기 설정 (가로 800, 세로 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_add_rule_group()
        self._create_existing_rules_group()
        self._create_management_buttons()
        self._create_status_bar()

        self._connect_signals()
        self._load_rules_from_listener() # 초기 규칙 로드
        self._update_status_bar() # 초기 상태 업데이트

    def _create_add_rule_group(self):
        """새 규칙 추가 섹션 생성"""
        group_box = QGroupBox("Add New Rule")
        layout = QFormLayout()

        self.keyword_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.add_button = QPushButton("Add Rule")

        layout.addRow("Keyword:", self.keyword_input)
        layout.addRow("Replace:", self.replace_input)
        layout.addWidget(self.add_button) # Add button below inputs

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_existing_rules_group(self):
        """기존 규칙 목록 섹션 생성"""
        group_box = QGroupBox("Existing Rules")
        layout = QVBoxLayout()

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(2)
        self.rules_table.setHorizontalHeaderLabels(["Keyword", "Replace Text"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectRows) # 행 전체 선택
        self.rules_table.setSelectionMode(QTableWidget.SingleSelection) # 단일 행 선택
        self.rules_table.setEditTriggers(QTableWidget.NoEditTriggers) # 직접 수정 금지
        # self._add_sample_rules() # 샘플 데이터 추가 대신 리스너에서 로드

        layout.addWidget(self.rules_table)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _load_rules_from_listener(self):
        """KeyboardListener에서 규칙을 가져와 테이블 위젯에 로드"""
        logging.debug("Loading rules into GUI table.")
        self.rules_table.setRowCount(0) # 테이블 초기화
        if self.listener and self.listener.rules:
            rules = self.listener.rules
            self.rules_table.setRowCount(len(rules))
            for row, (keyword, replace_text) in enumerate(rules.items()):
                self.rules_table.setItem(row, 0, QTableWidgetItem(keyword))
                self.rules_table.setItem(row, 1, QTableWidgetItem(replace_text))
            logging.info(f"Loaded {len(rules)} rules into table.")
        else:
            logging.warning("Listener or rules not available to load.")

    def _create_management_buttons(self):
        """관리 버튼 (편집, 삭제 등) 섹션 생성"""
        self.selected_rule_label = QLabel("Selected Rule: None")
        self.main_layout.addWidget(self.selected_rule_label) # Show selected rule above buttons

        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.save_all_button = QPushButton("Save All")
        self.close_button = QPushButton("Close")

        # 초기에는 비활성화 (규칙 선택 시 활성화되도록 추후 구현)
        self.edit_button.setEnabled(False) 
        self.delete_button.setEnabled(False)

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch() # 버튼 사이 공간
        button_layout.addWidget(self.save_all_button)
        button_layout.addWidget(self.close_button)
        
        self.main_layout.addLayout(button_layout)

    def _create_status_bar(self):
        """상태 표시줄 생성"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        # 초기 상태는 _update_status_bar 에서 설정

    def _update_status_bar(self):
        """리스너 상태에 따라 상태 표시줄 업데이트"""
        if self.listener and self.listener.is_running():
            self.statusBar.showMessage("Status: Listener Running")
        else:
            self.statusBar.showMessage("Status: Listener Stopped")

    def _connect_signals(self):
        """GUI 위젯의 시그널을 슬롯 메서드에 연결"""
        logging.debug("Connecting GUI signals.")
        self.close_button.clicked.connect(self.close) # Close 버튼 -> 창 닫기
        self.save_all_button.clicked.connect(self._save_all_rules) # Save All 버튼 -> _save_all_rules 호출
        # TODO: Add, Edit, Delete 버튼 및 테이블 선택 시그널 연결

    def _save_all_rules(self):
        """'Save All' 버튼 클릭 시 호출될 슬롯 (현재는 플레이스홀더)"""
        # TODO: 현재 테이블 내용을 파일이나 다른 저장소에 저장하는 로직 구현
        # TODO: 저장 후 리스너의 규칙 업데이트 (self.listener.update_rules)
        logging.info("'Save All' button clicked. (Save functionality not implemented yet)")
        # 간단한 확인 메시지 표시
        QMessageBox.information(self, "Save Rules", "Save functionality is not yet implemented.")

    # ... (closeEvent 등 필요한 메서드 추가 가능) ...

if __name__ == '__main__':
    # 이 파일 단독 실행 시 GUI 테스트용
    app = QApplication(sys.argv)
    window = TextReplacerSettingsWindow()
    window.show()
    sys.exit(app.exec_()) 