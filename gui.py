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
        self._on_rule_selected() # 초기 버튼 상태 설정

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
            # 키워드 순으로 정렬해서 보여주기 (선택 사항)
            sorted_keywords = sorted(rules.keys())
            for row, keyword in enumerate(sorted_keywords):
                replace_text = rules[keyword]
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
        self.rules_table.itemSelectionChanged.connect(self._on_rule_selected)
        self.add_button.clicked.connect(self._add_rule)
        self.delete_button.clicked.connect(self._delete_rule)

    def _on_rule_selected(self):
        """테이블에서 규칙(행) 선택 시 호출될 슬롯"""
        selected_items = self.rules_table.selectedItems()
        if len(selected_items) > 0: # 항목이 선택되었는지 확인 (보통 2개: 키워드, 내용)
            selected_row = self.rules_table.currentRow()
            keyword_item = self.rules_table.item(selected_row, 0)
            if keyword_item: # 선택된 행의 아이템이 유효한지 확인
                keyword = keyword_item.text()
                self.selected_rule_label.setText(f"Selected Rule: {keyword}")
                self.edit_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                logging.debug(f"Rule selected: Row {selected_row}, Keyword '{keyword}'")
            else: # 행은 선택했지만 아이템이 없는 경우 (이론상 발생 어려움)
                 self.selected_rule_label.setText("Selected Rule: Invalid selection")
                 self.edit_button.setEnabled(False)
                 self.delete_button.setEnabled(False)
        else: # 아무것도 선택되지 않은 경우
            self.selected_rule_label.setText("Selected Rule: None")
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            logging.debug("Rule selection cleared.")
            
    def _add_rule(self):
        """'Add Rule' 버튼 클릭 시 호출될 슬롯"""
        keyword = self.keyword_input.text().strip()
        replace_text = self.replace_input.text().strip() # 앞뒤 공백 제거

        # 유효성 검사
        if not keyword or not replace_text:
            QMessageBox.warning(self, "Add Rule Error", "Keyword and Replace Text cannot be empty.")
            return
        
        if keyword in self.listener.rules:
             QMessageBox.warning(self, "Add Rule Error", f"Keyword '{keyword}' already exists.")
             return
             
        # 리스너 규칙 업데이트
        self.listener.rules[keyword] = replace_text
        # TODO: 리스너의 max_buffer_size 업데이트 필요 시 self.listener._calculate_max_buffer_size() 호출 또는 update_rules 사용
        # 임시방편: 버퍼 크기 강제 업데이트
        self.listener.max_buffer_size = self.listener._calculate_max_buffer_size()
        logging.info(f"Rule added to listener: '{keyword}' -> '{replace_text}'. New max buffer size: {self.listener.max_buffer_size}")

        # 테이블 업데이트
        # 테이블 업데이트 전에 정렬된 리스트를 다시 로드하여 일관성 유지
        self._load_rules_from_listener() 
        # row_count = self.rules_table.rowCount()
        # self.rules_table.insertRow(row_count)
        # self.rules_table.setItem(row_count, 0, QTableWidgetItem(keyword))
        # self.rules_table.setItem(row_count, 1, QTableWidgetItem(replace_text))
        # logging.info(f"Rule added to GUI table: Row {row_count}")

        # 입력 필드 초기화
        self.keyword_input.clear()
        self.replace_input.clear()

    def _delete_rule(self):
        """'Delete' 버튼 클릭 시 호출될 슬롯"""
        selected_row = self.rules_table.currentRow()
        if selected_row < 0: # 선택된 행이 없는 경우
            logging.warning("Delete button clicked but no row selected.")
            return

        keyword_item = self.rules_table.item(selected_row, 0)
        if not keyword_item:
             logging.error(f"Cannot get keyword from selected row {selected_row}.")
             return
        keyword = keyword_item.text()

        # 삭제 확인
        reply = QMessageBox.question(self, 'Delete Rule', 
                                     f"Are you sure you want to delete the rule for '{keyword}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            logging.info(f"Deleting rule for keyword: '{keyword}'")
            # 리스너 규칙 업데이트
            rule_deleted_from_listener = False
            if keyword in self.listener.rules:
                del self.listener.rules[keyword]
                # TODO: 리스너의 max_buffer_size 업데이트 필요 시
                self.listener.max_buffer_size = self.listener._calculate_max_buffer_size()
                logging.info(f"Rule deleted from listener. New max buffer size: {self.listener.max_buffer_size}")
                rule_deleted_from_listener = True
            else:
                logging.warning(f"Keyword '{keyword}' not found in listener rules during delete.")

            # 테이블 업데이트
            self.rules_table.removeRow(selected_row)
            logging.info(f"Row {selected_row} removed from GUI table.")

            # 선택 상태 초기화 (중요: 행 삭제 후 선택 상태가 이상해질 수 있음)
            self.rules_table.clearSelection() 
            self._on_rule_selected() # 버튼 상태 등 업데이트

    def _save_all_rules(self):
        """'Save All' 버튼 클릭 시 호출될 슬롯 (현재는 플레이스홀더)"""
        # TODO: 현재 리스너의 규칙(self.listener.rules)을 파일에 저장
        logging.info("'Save All' button clicked. (Save functionality not implemented yet)")
        QMessageBox.information(self, "Save Rules", "Save functionality is not yet implemented.")

    # ... (closeEvent 등 필요한 메서드 추가 가능) ...

if __name__ == '__main__':
    # 이 파일 단독 실행 시 GUI 테스트용
    app = QApplication(sys.argv)
    window = TextReplacerSettingsWindow()
    window.show()
    sys.exit(app.exec_()) 