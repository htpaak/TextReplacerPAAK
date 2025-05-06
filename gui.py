import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QGroupBox, QFormLayout, QHeaderView, QStatusBar
)
from PyQt5.QtCore import Qt

class TextReplacerSettingsWindow(QMainWindow):
    """텍스트 치환 설정 GUI 메인 윈도우 클래스"""
    def __init__(self):
        super().__init__()
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

        # TODO: Connect signals and slots

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
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 컬럼 너비 자동 조절
        # TODO: Add sample data or load from storage
        
        # 임시 데이터 추가
        self._add_sample_rules()

        layout.addWidget(self.rules_table)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _add_sample_rules(self):
        """테이블에 임시 규칙 데이터 추가 (테스트용)"""
        sample_rules = [
            ("!email", "my.email.address@example.com"),
            ("!addr", "Seoul, Gangnam-gu...") ,
            ("!greet", "Hello there!")
        ]
        self.rules_table.setRowCount(len(sample_rules))
        for row, (keyword, replace_text) in enumerate(sample_rules):
            self.rules_table.setItem(row, 0, QTableWidgetItem(keyword))
            self.rules_table.setItem(row, 1, QTableWidgetItem(replace_text))


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
        self.statusBar.showMessage("Status: Listener Idle") # 초기 상태


if __name__ == '__main__':
    # 이 파일 단독 실행 시 GUI 테스트용
    app = QApplication(sys.argv)
    window = TextReplacerSettingsWindow()
    window.show()
    sys.exit(app.exec_()) 