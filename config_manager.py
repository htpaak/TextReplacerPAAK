import json
import logging
import os

class ConfigManager:
    """애플리케이션 설정을 JSON 파일로 관리하는 클래스 (현재는 규칙만 해당)"""

    def __init__(self, config_file_path="rules.json"):
        """
        ConfigManager를 초기화합니다.

        Args:
            config_file_path (str): 설정 파일의 경로.
        """
        self.config_file_path = config_file_path
        logging.info(f"ConfigManager initialized with file: {self.config_file_path}")

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
    
    # 테스트 1: 파일 없을 때 로드 (기본 규칙 반환)
    if os.path.exists("test_rules.json"):
        os.remove("test_rules.json")
    cm_test = ConfigManager("test_rules.json")
    initial_rules = cm_test.load_rules()
    print("Initial rules (should be default):", initial_rules)
    
    # 테스트 2: 규칙 추가 및 저장
    initial_rules["!new_rule"] = "This is a new test rule."
    initial_rules["!another"] = "Another one added via test."
    save_success = cm_test.save_rules(initial_rules)
    print("Save successful:", save_success)

    # 테스트 3: 저장된 규칙 로드
    loaded_rules = cm_test.load_rules()
    print("Loaded rules (should include new ones):", loaded_rules)
    assert "!new_rule" in loaded_rules
    assert loaded_rules["!another"] == "Another one added via test."

    # 테스트 4: 잘못된 JSON 파일 로드 시도 (수동으로 파일 내용 변경 필요)
    # with open("test_rules.json", 'w') as f:
    #     f.write("this is not json")
    # error_rules = cm_test.load_rules()
    # print("Rules after loading invalid json (should be default):", error_rules)
    
    # 테스트 5: 빈 파일에서 로드
    open("empty_rules.json", 'w').close()
    cm_empty = ConfigManager("empty_rules.json")
    empty_loaded_rules = cm_empty.load_rules()
    print("Rules from empty file (should be default):", empty_loaded_rules)
    os.remove("empty_rules.json")

    if os.path.exists("test_rules.json"):
        os.remove("test_rules.json")
    print("ConfigManager test finished.") 