import json
import logging
import os

class ConfigManager:
    """애플리케이션 설정을 JSON 파일로 관리하는 클래스 (현재는 규칙만 해당)"""

    def __init__(self):
        """
        ConfigManager를 초기화합니다. 
        설정 파일 경로는 %LOCALAPPDATA%\TextReplacer\rules.json 으로 자동 설정됩니다.
        """
        # %LOCALAPPDATA% 경로 확인
        local_app_data = os.getenv('LOCALAPPDATA')
        if not local_app_data:
            logging.warning("LOCALAPPDATA environment variable not found. Using current directory.")
            base_dir = "." # LOCALAPPDATA 없으면 현재 디렉토리 사용
        else:
            base_dir = local_app_data
            
        # 앱 설정 폴더 경로 생성 (예: C:\Users\Username\AppData\Local\TextReplacerPAAK)
        self.app_config_dir = os.path.join(base_dir, "TextReplacerPAAK")
        
        # 설정 파일 전체 경로 설정
        self.config_file_path = os.path.join(self.app_config_dir, "rules.json")
        logging.info(f"ConfigManager initialized. Config file path set to: {self.config_file_path}")

        # 설정 폴더 생성 (존재하지 않을 경우)
        try:
            os.makedirs(self.app_config_dir, exist_ok=True)
            logging.debug(f"Ensured config directory exists: {self.app_config_dir}")
        except Exception as e:
            # 폴더 생성 실패 시 에러 로깅 (파일 저장/로드 시 문제 발생 가능)
            logging.error(f"Failed to create config directory '{self.app_config_dir}': {e}", exc_info=True)

    def get_default_rules(self):
        """기본 규칙 세트를 반환합니다."""
        # keyboard_listener의 기본 규칙과 동기화하거나, 여기서 단독으로 관리 가능
        return {
            "!email": "my.email.address@example.com",
            "!addr": "Seoul, Gangnam-gu, Teheran-ro 123",
            "!greet": "Hello there! Have a nice day.",
            "longkwtest": "This is a test for a longer keyword replacement."
        }

    def load_rules(self):
        """
        설정 파일에서 규칙을 로드합니다.
        파일이 없거나 JSON 디코딩에 실패하면 기본 규칙을 반환합니다.

        Returns:
            dict: 로드된 규칙들.
        """
        if not os.path.exists(self.config_file_path):
            logging.warning(f"Config file '{self.config_file_path}' not found. Returning default rules.")
            return self.get_default_rules()
        
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
                logging.info(f"Successfully loaded {len(rules)} rules from '{self.config_file_path}'.")
                if not isinstance(rules, dict): # 간단한 유효성 검사
                    logging.warning(f"Loaded data is not a dictionary. File: '{self.config_file_path}'. Returning default rules.")
                    return self.get_default_rules()
                return rules
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from '{self.config_file_path}'. Returning default rules.", exc_info=True)
            return self.get_default_rules()
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading rules from '{self.config_file_path}'. Returning default rules.: {e}", exc_info=True)
            return self.get_default_rules()

    def save_rules(self, rules):
        """
        주어진 규칙들을 설정 파일에 JSON 형식으로 저장합니다.

        Args:
            rules (dict): 저장할 규칙들.

        Returns:
            bool: 저장 성공 여부.
        """
        # 설정 폴더가 존재하는지 다시 한번 확인 및 생성 시도 (로드 실패 후 저장 시 대비)
        try:
            os.makedirs(self.app_config_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to ensure config directory '{self.app_config_dir}' exists before saving: {e}", exc_info=True)
            return False # 폴더 없으면 저장 불가

        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(rules, f, ensure_ascii=False, indent=4)
            logging.info(f"Successfully saved {len(rules)} rules to '{self.config_file_path}'.")
            return True
        except Exception as e:
            logging.error(f"Error saving rules to '{self.config_file_path}': {e}", exc_info=True)
            return False

if __name__ == '__main__':
    # 테스트용 코드
    logging.basicConfig(level=logging.DEBUG)
    
    # 테스트 ConfigManager 생성 (자동 경로 사용)
    cm_test = ConfigManager()
    test_file_path = cm_test.config_file_path
    print(f"Using test file path: {test_file_path}")

    # 테스트 1: 파일 없을 때 로드 (기본 규칙 반환)
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    initial_rules = cm_test.load_rules()
    print("Initial rules (should be default):", initial_rules)
    
    # 테스트 2: 규칙 추가 및 저장
    initial_rules["!new_rule"] = "This is a new test rule."
    initial_rules["!another"] = "Another one added via test."
    save_success = cm_test.save_rules(initial_rules)
    print("Save successful:", save_success)
    assert save_success
    assert os.path.exists(test_file_path)

    # 테스트 3: 저장된 규칙 로드
    loaded_rules = cm_test.load_rules()
    print("Loaded rules (should include new ones):", loaded_rules)
    assert "!new_rule" in loaded_rules
    assert loaded_rules["!another"] == "Another one added via test."

    # 테스트 4: 잘못된 JSON 파일 로드 시도 (수동으로 파일 내용 변경 필요)
    # try:
    #     with open(test_file_path, 'w') as f:
    #         f.write("this is not json")
    #     error_rules = cm_test.load_rules()
    #     print("Rules after loading invalid json (should be default):", error_rules)
    #     assert error_rules == cm_test.get_default_rules()
    # except Exception as e:
    #      print(f"Test 4 failed (manual intervention needed?): {e}")
    
    # 테스트 5: 빈 파일에서 로드 (JSONDecodeError 발생 예상)
    test_empty_file = os.path.join(cm_test.app_config_dir, "empty_rules.json")
    open(test_empty_file, 'w').close()
    cm_empty = ConfigManager()
    cm_empty.config_file_path = test_empty_file # 테스트 위해 경로 강제 변경
    empty_loaded_rules = cm_empty.load_rules()
    print("Rules from empty file (should be default):", empty_loaded_rules)
    assert empty_loaded_rules == cm_test.get_default_rules() # 빈 파일은 디코딩 에러로 기본값 반환
    os.remove(test_empty_file)

    # 테스트 종료 후 생성된 파일 삭제
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"Removed test file: {test_file_path}")
    # 앱 설정 폴더 자체는 삭제하지 않음 (다른 설정 파일이 있을 수 있으므로)
    # if os.path.exists(cm_test.app_config_dir):
    #     os.rmdir(cm_test.app_config_dir) # 폴더가 비어있어야 성공
    print("ConfigManager test finished.") 