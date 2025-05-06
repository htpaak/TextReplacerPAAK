import json
import logging
import os

class ConfigManager:
    """애플리케이션 설정을 JSON 파일로 관리하는 클래스 (규칙 및 일반 설정 포함)"""

    def __init__(self):
        """
        ConfigManager를 초기화합니다. 
        설정 파일 경로는 %LOCALAPPDATA%\TextReplacerPAAK\rules.json 으로 자동 설정됩니다.
        """
        local_app_data = os.getenv('LOCALAPPDATA')
        if not local_app_data:
            logging.warning("LOCALAPPDATA environment variable not found. Using current directory.")
            base_dir = "." 
        else:
            base_dir = local_app_data
            
        self.app_config_dir = os.path.join(base_dir, "TextReplacerPAAK")
        self.config_file_path = os.path.join(self.app_config_dir, "rules.json")
        logging.info(f"ConfigManager initialized. Config file path set to: {self.config_file_path}")

        try:
            os.makedirs(self.app_config_dir, exist_ok=True)
            logging.debug(f"Ensured config directory exists: {self.app_config_dir}")
        except Exception as e:
            logging.error(f"Failed to create config directory '{self.app_config_dir}': {e}", exc_info=True)

    def get_default_config(self):
        """기본 설정 (규칙 및 세팅)을 포함하는 딕셔너리를 반환합니다."""
        return {
            "rules": {
                "!email": "my.email.address@example.com",
                "!addr": "Seoul, Gangnam-gu, Teheran-ro 123",
                "!greet": "Hello there! Have a nice day.",
                "longkwtest": "This is a test for a longer keyword replacement."
            },
            "settings": {
                "start_on_boot": False # 기본값: 시작 시 실행 안 함
                # 나중에 다른 설정 추가 가능
            }
        }

    def load_config(self):
        """
        설정 파일에서 전체 설정을 로드합니다.
        파일이 없거나 JSON 디코딩/형식 오류 시 기본 설정을 반환합니다.

        Returns:
            dict: 로드된 전체 설정 (rules와 settings 포함).
        """
        if not os.path.exists(self.config_file_path):
            logging.warning(f"Config file '{self.config_file_path}' not found. Returning default config.")
            return self.get_default_config()
        
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logging.info(f"Successfully loaded config from '{self.config_file_path}'.")
            
            # 기본 구조 확인 및 병합 (기존 파일에 settings 등이 없을 경우 대비)
            default_config = self.get_default_config()
            if "rules" not in config or not isinstance(config.get("rules"), dict):
                logging.warning("'rules' key missing or not a dict in config file. Using default rules.")
                config["rules"] = default_config["rules"]
            if "settings" not in config or not isinstance(config.get("settings"), dict):
                logging.warning("'settings' key missing or not a dict in config file. Using default settings.")
                config["settings"] = default_config["settings"]
            else:
                # settings 내부에 누락된 기본 키가 있는지 확인하고 추가
                for key, value in default_config["settings"].items():
                    if key not in config["settings"]:
                        logging.warning(f"Setting key '{key}' missing in config file. Adding default value: {value}")
                        config["settings"][key] = value
                        
            return config
            
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from '{self.config_file_path}'. Returning default config.", exc_info=True)
            return self.get_default_config()
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading config from '{self.config_file_path}'. Returning default config.: {e}", exc_info=True)
            return self.get_default_config()

    def save_config(self, config):
        """
        주어진 전체 설정을 설정 파일에 JSON 형식으로 저장합니다.

        Args:
            config (dict): 저장할 전체 설정 (rules와 settings 포함).

        Returns:
            bool: 저장 성공 여부.
        """
        try:
            os.makedirs(self.app_config_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to ensure config directory '{self.app_config_dir}' exists before saving: {e}", exc_info=True)
            return False

        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            logging.info(f"Successfully saved config to '{self.config_file_path}'.")
            return True
        except Exception as e:
            logging.error(f"Error saving config to '{self.config_file_path}': {e}", exc_info=True)
            return False

    def save_rules(self, rules_data: dict):
        """
        주어진 규칙 데이터를 설정 파일에 저장합니다.
        기존 설정(settings)은 유지됩니다.

        Args:
            rules_data (dict): 저장할 규칙 데이터.

        Returns:
            bool: 저장 성공 여부.
        """
        current_config = self.load_config() # 기존 전체 설정 로드
        current_config["rules"] = rules_data # rules 부분만 업데이트
        return self.save_config(current_config) # 전체 설정 저장

if __name__ == '__main__':
    # 테스트용 코드
    logging.basicConfig(level=logging.DEBUG)
    
    cm_test = ConfigManager()
    test_file_path = cm_test.config_file_path
    print(f"Using test file path: {test_file_path}")

    # 테스트 1: 파일 없을 때 로드 (기본 설정 반환)
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    initial_config = cm_test.load_config()
    print("Initial config (should be default):")
    print(json.dumps(initial_config, indent=4))
    assert "rules" in initial_config
    assert "settings" in initial_config
    assert initial_config["settings"]["start_on_boot"] == False
    
    # 테스트 2: 설정 및 규칙 변경 후 저장
    initial_config["rules"]["!new_rule"] = "New rule for test."
    initial_config["settings"]["start_on_boot"] = True
    initial_config["settings"]["new_setting"] = 123 # 새 설정 추가 테스트
    save_success = cm_test.save_config(initial_config)
    print("\nSave successful:", save_success)
    assert save_success
    assert os.path.exists(test_file_path)

    # 테스트 3: 저장된 설정 로드
    loaded_config = cm_test.load_config()
    print("\nLoaded config (should include changes):")
    print(json.dumps(loaded_config, indent=4))
    assert "!new_rule" in loaded_config["rules"]
    assert loaded_config["settings"]["start_on_boot"] == True
    assert loaded_config["settings"]["new_setting"] == 123 
    
    # 테스트 4: 일부 키가 누락된 파일 로드 시 기본값 병합 테스트
    corrupted_config = {"rules": {"!only_rule": "abc"}} # settings 누락
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(corrupted_config, f, indent=4)
    loaded_corrupted = cm_test.load_config()
    print("\nLoaded from corrupted (settings missing):")
    print(json.dumps(loaded_corrupted, indent=4))
    assert "settings" in loaded_corrupted
    assert loaded_corrupted["settings"]["start_on_boot"] == False # 기본값 복원 확인
    assert loaded_corrupted["rules"]["!only_rule"] == "abc" # 기존 규칙 유지 확인
    
    corrupted_config_2 = {"rules": {"!r1": "v1"}, "settings": {"another_setting": True}} # start_on_boot 누락
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(corrupted_config_2, f, indent=4)
    loaded_corrupted_2 = cm_test.load_config()
    print("\nLoaded from corrupted (start_on_boot missing):")
    print(json.dumps(loaded_corrupted_2, indent=4))
    assert loaded_corrupted_2["settings"]["start_on_boot"] == False # 기본값 복원 확인
    assert loaded_corrupted_2["settings"]["another_setting"] == True # 기존 설정 유지 확인

    # 테스트 종료 후 생성된 파일 삭제
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"\nRemoved test file: {test_file_path}")
    
    print("\nConfigManager test finished.") 