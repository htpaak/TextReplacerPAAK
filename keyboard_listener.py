import threading
import time
from pynput import keyboard
from pynput.keyboard import Controller # Controller 임포트
import logging
# from collections import deque # deque 대신 간단한 문자열 슬라이싱 사용

class KeyboardListener:
    """전역 키보드 입력을 감지하고 키워드 매칭 및 치환을 처리하는 리스너 클래스"""

    def __init__(self, rules=None):
        self.listener_thread = None
        self.listener = None
        self._stop_event = threading.Event()
        self.is_simulating = False # <<< 추가: 시뮬레이션 중인지 나타내는 플래그
        
        # 입력 버퍼 및 규칙 설정
        self.buffer = "" 
        # TODO: GUI나 파일에서 실제 규칙 로드하도록 수정 필요
        self.rules = rules if rules is not None else self._get_default_rules()
        self.max_buffer_size = self._calculate_max_buffer_size() # 가장 긴 키워드 길이 + 여유분

        # 치환 트리거 키 설정 (pynput Key 객체 사용)
        self.trigger_keys = {keyboard.Key.space} # 엔터키 제거하고 스페이스바만 유지

        # 키 입력 제어를 위한 Controller 인스턴스 생성
        self.controller = Controller()

        logging.info(f"[INIT] KeyboardListener initialized. Rules: {len(self.rules)}, Max buffer: {self.max_buffer_size}")

    def _get_default_rules(self):
        """테스트용 기본 규칙 반환"""
        return {
            "!email": "my.email.address@example.com",
            "!addr": "Seoul, Gangnam-gu, Teheran-ro 123",
            "!greet": "Hello there! Have a nice day.",
            "longkwtest": "This is a test for a longer keyword replacement."
        }

    def _calculate_max_buffer_size(self):
        """규칙 중 가장 긴 키워드 길이를 기준으로 버퍼 최대 크기 계산"""
        if not self.rules:
            return 10 # 규칙 없으면 기본값
        max_len = max(len(k) for k in self.rules.keys())
        return max_len + 5 # 가장 긴 키워드 + 약간의 여유

    def update_rules(self, new_rules):
        """외부에서 규칙을 업데이트하는 메서드"""
        self.rules = new_rules
        self.max_buffer_size = self._calculate_max_buffer_size()
        self.buffer = "" # 규칙 변경 시 버퍼 초기화
        logging.info(f"[UPDATE_RULES] Rules updated. Count: {len(self.rules)}, Max buffer: {self.max_buffer_size}")

    def _perform_replacement(self, keyword, replacement_text):
        """실제 키 입력 시뮬레이션을 통해 텍스트를 치환하는 메서드 (자기 입력 무시 플래그 추가)"""
        logging.debug(f"[_PERFORM_REPLACEMENT] <<< ENTER >>> Keyword='{keyword}', Replacement='{replacement_text}'")
        self.is_simulating = True
        logging.debug(f"[_PERFORM_REPLACEMENT] Set is_simulating = True")
        try:
            # logging.debug(f"[_PERFORM_REPLACEMENT] Starting backspace loop for {len(keyword)} characters.") # 이전 코드 주석 처리
            # for i in range(len(keyword)):
            #     logging.debug(f"[_PERFORM_REPLACEMENT] Simulating Backspace #{i+1} (for char '{keyword[len(keyword)-1-i]}') - Pressing...")
            #     self.controller.press(keyboard.Key.backspace)
            #     logging.debug(f"[_PERFORM_REPLACEMENT] Simulating Backspace #{i+1} - Releasing...")
            #     self.controller.release(keyboard.Key.backspace)
            #     logging.debug(f"[_PERFORM_REPLACEMENT] Simulating Backspace #{i+1} - Done.")
            #     time.sleep(1) # <<< 딜레이를 1초로 변경하여 테스트
            # logging.debug(f"[_PERFORM_REPLACEMENT] Backspace loop finished. Typing replacement text...")

            # --- 새로운 방식: Shift + 화살표로 선택 후 삭제 ---
            logging.debug(f"[_PERFORM_REPLACEMENT] Starting selection using Shift+Left Arrow for {len(keyword)} characters.")
            
            # Shift 키 누르기
            self.controller.press(keyboard.Key.shift)
            logging.debug("[_PERFORM_REPLACEMENT] Pressed Shift.")
            
            # 키워드 길이 + 1 만큼 왼쪽 화살표 누르기 (실험적 수정)
            select_count = len(keyword) + 1
            logging.debug(f"[_PERFORM_REPLACEMENT] Simulating Left Arrow {select_count} times (keyword_len + 1)...")
            for i in range(select_count):
                self.controller.press(keyboard.Key.left)
                self.controller.release(keyboard.Key.left)
                logging.debug(f"[_PERFORM_REPLACEMENT] Simulated Left Arrow #{i+1}")
                time.sleep(0.01) # 키 입력 사이에 아주 짧은 딜레이 추가 (선택적)

            # Shift 키 떼기
            self.controller.release(keyboard.Key.shift)
            logging.debug("[_PERFORM_REPLACEMENT] Released Shift.")
            
            time.sleep(0.02) # 선택 완료 후 잠시 대기

            # Delete 키 누르기
            logging.debug("[_PERFORM_REPLACEMENT] Simulating Delete key...")
            self.controller.press(keyboard.Key.delete)
            self.controller.release(keyboard.Key.delete)
            logging.debug("[_PERFORM_REPLACEMENT] Simulated Delete key.")
            
            time.sleep(0.02) # 삭제 후 잠시 대기
            # --- 선택 후 삭제 끝 ---

            logging.debug(f"[_PERFORM_REPLACEMENT] Typing replacement text...") # 기존 코드
            self.controller.type(replacement_text)
            logging.debug(f"[_PERFORM_REPLACEMENT] Finished typing replacement text.")
            logging.info(f"[_PERFORM_REPLACEMENT] Replacement successful for keyword '{keyword}'.")
        except Exception as e:
            logging.error(f"[_PERFORM_REPLACEMENT] !!! Error during replacement simulation: {e}", exc_info=True)
        finally:
            self.is_simulating = False
            logging.debug(f"[_PERFORM_REPLACEMENT] Set is_simulating = False in finally block")
        logging.debug(f"[_PERFORM_REPLACEMENT] <<< EXIT >>>")

    def _on_press(self, key):
        """키가 눌렸을 때 호출될 콜백 함수 (자기 입력 무시 로직 추가)"""
        if self.is_simulating:
            # 시뮬레이션 중인 키 종류 로깅 (Shift, Left, Delete 등 확인용)
            logging.debug(f"[_ON_PRESS] Ignoring simulated key press {key} because is_simulating is True.") 
            return True # 시뮬레이션 중인 키는 무시하고 리스너 계속 실행
        
        # <<< 로그 추가 시작 >>>
        try:
            key_char_val = key.char
        except AttributeError:
            key_char_val = 'N/A (AttributeError)' # char 속성 없음
        except Exception as e:
            key_char_val = f'N/A (Exception: {e})' # 기타 예외

        try:
            key_vk_val = key.vk
        except AttributeError:
            key_vk_val = 'N/A (AttributeError)' # vk 속성 없음
        except Exception as e:
            key_vk_val = f'N/A (Exception: {e})' # 기타 예외
        
        # key 객체 자체도 로깅 (repr 형태)
        logging.info(f"[_ON_PRESS_KEY_EVENT] RawKey={repr(key)}, Key.char='{key_char_val}', VK={key_vk_val}")
        # <<< 로그 추가 끝 >>>

        logging.debug(f"[_ON_PRESS] <<< KEY PRESS DETECTED >>> Key={key}, Current Buffer='{self.buffer}'")
        processed = False 
        return_value = True # 기본적으로 True 반환 (리스너 계속 실행)

        try:
            logging.debug(f"[_ON_PRESS] Entering TRY block (checking for char attribute)")
            char = key.char
            
            if char is not None: 
                logging.debug(f"[_ON_PRESS] Key has char='{char}'. Appending to buffer.")
                buffer_before = self.buffer
                self.buffer += char
                if len(self.buffer) > self.max_buffer_size:
                    buffer_trimmed_from = self.buffer[:-self.max_buffer_size]
                    self.buffer = self.buffer[-self.max_buffer_size:]
                    logging.debug(f"[_ON_PRESS] Buffer limit exceeded. Trimmed '{buffer_trimmed_from}'. New Buffer='{self.buffer}'")
                else:
                    logging.debug(f"[_ON_PRESS] Buffer updated: '{buffer_before}' -> '{self.buffer}'")
                processed = True
            else:
                 # char가 None인 특수 키는 여기서 처리하지 않음 (AttributeError로 감)
                 # 혹시 모를 NoneType 오류 방지용 로깅만 남김
                 logging.debug(f"[_ON_PRESS] Key has char=None. Key={key}. Possible unhandled case?")
                 # 필요하다면 여기서도 버퍼 초기화 등 처리 가능
                 processed = True # None을 처리한 것으로 간주

        except AttributeError:
            logging.debug(f"[_ON_PRESS] Entering EXCEPT AttributeError block (special key). Key={key}")
            
            if key in self.trigger_keys:
                logging.debug(f"[_ON_PRESS] ---> Trigger key detected: {key}")
                logging.debug(f"[_ON_PRESS] Calling _check_for_replacement(). Current Buffer='{self.buffer}'")
                replaced = self._check_for_replacement() # 치환 시도
                logging.debug(f"[_ON_PRESS] _check_for_replacement() returned: {replaced}")
                buffer_before = self.buffer
                self.buffer = "" # 트리거 입력 시 버퍼 초기화
                logging.debug(f"[_ON_PRESS] Buffer reset due to trigger key: '{buffer_before}' -> '{self.buffer}'")
                processed = True
            elif key == keyboard.Key.backspace:
                logging.debug(f"[_ON_PRESS] ---> Backspace key detected.")
                buffer_before = self.buffer
                if self.buffer:
                    self.buffer = self.buffer[:-1]
                    logging.debug(f"[_ON_PRESS] Backspace applied. Buffer: '{buffer_before}' -> '{self.buffer}'")
                else:
                    logging.debug(f"[_ON_PRESS] Backspace pressed but buffer was already empty.")
                processed = True
            elif key == keyboard.Key.esc:
                 logging.info(f"[_ON_PRESS] ---> ESC key detected. Stopping listener.")
                 return_value = False # 리스너 루프 중단 신호
                 processed = True # 처리됨
            # Shift, 화살표, Delete 등 _perform_replacement에서 사용할 키들은 여기서 특별히 처리할 필요 없음
            # (is_simulating 플래그로 걸러지거나, 일반 사용자 입력으로 들어와도 버퍼에 영향 없음)
            else:
                 # 기타 알려진 특수키 (Ctrl, Alt, F1 등)
                 logging.debug(f"[_ON_PRESS] ---> Ignoring known special key: {key}")
                 # 특수 키 입력 시 버퍼 초기화 여부 결정 (현재는 초기화 안 함)
                 # self.buffer = ""
                 processed = True
        
        if not processed:
            logging.warning(f"[_ON_PRESS] !!! Unhandled key press type: {key}. Clearing buffer.")
            self.buffer = "" 

        logging.debug(f"[_ON_PRESS] <<< EXITING HANDLER >>> Returning: {return_value}")
        return return_value

    def _on_release(self, key):
        """키에서 손을 뗐을 때 호출될 콜백 함수"""
        # 너무 많은 로그를 생성하므로 필요한 경우에만 주석 해제
        # logging.debug(f"[_ON_RELEASE] Key released: {key}") 
        return True # 리스너는 계속 실행

    def _check_for_replacement(self):
        """현재 버퍼가 규칙 키워드로 끝나는지 확인하고, 일치 시 실제 치환 수행 (상세 로그 추가)"""
        logging.debug(f"[_CHECK_REPLACEMENT] <<< ENTER >>> Checking buffer: '{self.buffer}'")
        if not self.buffer:
            logging.debug(f"[_CHECK_REPLACEMENT] Buffer is empty. No check needed.")
            logging.debug(f"[_CHECK_REPLACEMENT] <<< EXIT >>> Returning: False")
            return False

        matched_keyword = None
        replacement_text = None
        
        logging.debug(f"[_CHECK_REPLACEMENT] Iterating through {len(self.rules)} rules...")
        for keyword, text in self.rules.items():
            logging.debug(f"[_CHECK_REPLACEMENT]   Checking rule: Keyword='{keyword}'")
            is_match = self.buffer.endswith(keyword)
            logging.debug(f"[_CHECK_REPLACEMENT]   Does buffer ('{self.buffer}') end with keyword ('{keyword}')? -> {is_match}")
            if is_match:
                matched_keyword = keyword
                replacement_text = text
                logging.info(f"[_CHECK_REPLACEMENT] Match found! Keyword: '{matched_keyword}', Replacement: '{replacement_text}'")
                break # 첫 번째 일치하는 규칙 사용
        
        logging.debug(f"[_CHECK_REPLACEMENT] Iteration finished.")

        if matched_keyword:
            logging.debug(f"[_CHECK_REPLACEMENT] Match confirmed. Calling _perform_replacement().")
            self._perform_replacement(matched_keyword, replacement_text) # 실제 치환 함수 호출
            logging.debug(f"[_CHECK_REPLACEMENT] <<< EXIT >>> Returning: True (Match found and replacement attempted)")
            return True # 치환 성공 (시도)
        else:
            logging.debug(f"[_CHECK_REPLACEMENT] No matching keyword found for buffer ending.")
            logging.debug(f"[_CHECK_REPLACEMENT] <<< EXIT >>> Returning: False (No match)")
            return False # 치환 실패

    # --- 리스너 시작/중지 및 실행 로직 (이전과 거의 동일) ---
    def _run_listener(self):
        """리스너를 실행하는 내부 메서드 (별도 스레드에서 실행됨)"""
        logging.info("[_RUN_LISTENER] Keyboard listener thread starting.")
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
                suppress=False
            )
            with self.listener as l:
                l.join()
        except Exception as e:
            # 오류 발생 시 스레드가 조용히 종료되지 않도록 에러 로깅 강화
            logging.error(f"[_RUN_LISTENER] !!! UNEXPECTED ERROR in listener thread: {e}", exc_info=True)
        finally:
            logging.info("[_RUN_LISTENER] Keyboard listener thread finished.")
            self.listener = None # 리스너 객체 확실히 정리

    def start(self):
        """키보드 리스너를 별도 스레드에서 시작"""
        if self.listener_thread is not None and self.listener_thread.is_alive():
            logging.warning("[START] Listener is already running.")
            return

        logging.info("[START] Starting keyboard listener...")
        self._stop_event.clear()
        self.listener_thread = threading.Thread(target=self._run_listener, daemon=True, name="KeyboardListenerThread")
        self.listener_thread.start()
        logging.info("[START] Listener thread started.")

    def stop(self):
        """키보드 리스너를 중지"""
        if self.listener is None:
            logging.warning("[STOP] Listener stop requested, but listener object does not exist (already stopped or failed to start?).")
            # 스레드가 살아있는지 확인하고 정리 시도
            if self.listener_thread and self.listener_thread.is_alive():
                 logging.info("[STOP] Attempting to stop the listener thread directly (might not be clean)...")
                 # 강제 종료는 위험하므로 여기서는 시도하지 않음
                 pass
            return

        if not self._stop_event.is_set(): # 중지 요청이 이미 발생하지 않았는지 확인
             logging.info("[STOP] Stopping keyboard listener...")
             self._stop_event.set()
             try:
                 # Listener.stop()은 Listener 스레드 내에서 호출되어야 안전하게 중단됨
                 # 외부 스레드에서 호출하면 데드락 발생 가능성 있음
                 # 따라서 여기서는 직접 호출 대신, 내부 콜백(on_press/on_release)에서
                 # self._stop_event 플래그를 확인하거나, 특정 키(ESC)를 통해 중단하도록 유도
                 # 여기서는 ESC키로 중단하는 로직이 _on_press에 이미 있음.
                 # 즉시 중단을 원하면 Controller로 ESC 키를 보내는 방법도 고려 가능.
                 # keyboard.Controller().press(keyboard.Key.esc)
                 # keyboard.Controller().release(keyboard.Key.esc)
                 
                 # 또는 리스너 객체에 직접 stop 호출 (pynput 버전/환경에 따라 동작 다를 수 있음)
                  if self.listener:
                      self.listener.stop() # Listener.stop()이 join()을 해제
                      logging.debug("[STOP] Called listener.stop()")

             except Exception as e:
                 logging.error(f"[_STOP] Error during listener stop: {e}", exc_info=True)
        else:
             logging.warning("[STOP] Listener stop requested, but already in progress or stopped.")

        # 스레드 종료 대기 (선택 사항, 너무 길면 GUI 블록 가능)
        # if self.listener_thread and self.listener_thread.is_alive():
        #     self.listener_thread.join(timeout=0.5)
        #     if self.listener_thread.is_alive():
        #         logging.warning("Listener thread did not stop within timeout.")

        # self.listener = None # _run_listener의 finally 블록에서 처리
        logging.info("[STOP] Keyboard listener stop sequence initiated.")

    def is_running(self):
        """리스너 스레드가 현재 실행 중인지 확인"""
        return self.listener_thread is not None and self.listener_thread.is_alive()

# 테스트용 코드
if __name__ == '__main__':
    # 로그 포맷에 스레드 이름 추가, 레벨 DEBUG로 설정
    log_format = '%(asctime)s - %(levelname)s - [%(threadName)s] - %(filename)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format) 
    
    logging.info("Starting listener directly for testing...")
    listener = KeyboardListener()
    listener.start()
    
    try:
        # 메인 스레드가 살아 있도록 유지 (실제 앱에서는 GUI 루프)
        while True:
            if not listener.listener_thread or not listener.listener_thread.is_alive():
                logging.info("Listener thread seems to have stopped. Exiting main loop.")
                break
            time.sleep(0.5) 
    except KeyboardInterrupt:
        print("\nCtrl+C detected, requesting listener stop...")
        listener.stop()
        if listener.listener_thread and listener.listener_thread.is_alive():
             logging.debug("Waiting for listener thread to join...")
             listener.listener_thread.join(timeout=1) 
             if listener.listener_thread.is_alive():
                 logging.warning("Listener thread did not stop within timeout!")
             else:
                 logging.debug("Listener thread joined successfully.")
        print("Exiting main thread.") 