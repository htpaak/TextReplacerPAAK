import threading
import time
from pynput import keyboard
import logging
# from collections import deque # deque 대신 간단한 문자열 슬라이싱 사용

class KeyboardListener:
    """전역 키보드 입력을 감지하고 키워드 매칭을 처리하는 리스너 클래스"""

    def __init__(self, rules=None):
        self.listener_thread = None
        self.listener = None
        self._stop_event = threading.Event()
        
        # 입력 버퍼 및 규칙 설정
        self.buffer = "" 
        # TODO: GUI나 파일에서 실제 규칙 로드하도록 수정 필요
        self.rules = rules if rules is not None else self._get_default_rules()
        self.max_buffer_size = self._calculate_max_buffer_size() # 가장 긴 키워드 길이 + 여유분

        # 치환 트리거 키 설정 (pynput Key 객체 사용)
        self.trigger_keys = {keyboard.Key.space, keyboard.Key.enter}

        # 키 입력 제어를 위한 Controller 인스턴스 (다음 단계에서 사용)
        # self.controller = keyboard.Controller()

        logging.info(f"KeyboardListener initialized with {len(self.rules)} rules. Max buffer size: {self.max_buffer_size}")

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
        logging.info(f"Rules updated. New rule count: {len(self.rules)}. Max buffer size: {self.max_buffer_size}")


    def _on_press(self, key):
        """키가 눌렸을 때 호출될 콜백 함수"""
        try:
            # 일반 문자 키 처리
            char = key.char
            logging.debug(f"Alphanumeric key pressed: {char}")
            self.buffer += char
            # 버퍼 크기 제한
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size:]
            logging.debug(f"Buffer: '{self.buffer}'")

        except AttributeError:
            # 특수 키 처리
            logging.debug(f"Special key pressed: {key}")
            if key in self.trigger_keys:
                logging.debug(f"Trigger key detected: {key}")
                replaced = self._check_for_replacement()
                self.buffer = "" # 트리거 입력 시 버퍼 초기화
                if replaced:
                    # TODO: 실제 치환 로직 (키 입력 시뮬레이션) 추가
                    # 현재는 트리거 키가 입력되는 것을 막지 않음
                    pass 
            elif key == keyboard.Key.backspace:
                if self.buffer:
                    self.buffer = self.buffer[:-1]
                    logging.debug(f"Backspace pressed. Buffer: '{self.buffer}'")
                else:
                    logging.debug("Backspace pressed but buffer is empty.")
            elif key == keyboard.Key.esc:
                 logging.info("ESC key pressed, stopping listener.")
                 self.stop()
                 return False # 리스너 루프 중단
            else:
                # 다른 특수키 (Shift, Ctrl, Alt, 화살표 등)는 버퍼 초기화 또는 무시
                # 여기서는 일단 버퍼를 초기화 (예: !email 입력 중 Shift 누르면 초기화)
                # 원치 않으면 이 부분을 주석처리하거나 로직 변경
                # logging.debug(f"Non-trigger special key pressed. Clearing buffer.")
                # self.buffer = ""
                pass # 다른 특수키는 일단 버퍼에 영향 주지 않음
        return True

    def _on_release(self, key):
        """키에서 손을 뗐을 때 호출될 콜백 함수"""
        # logging.debug(f"Key released: {key}") # 릴리즈 로그는 너무 많을 수 있어 주석 처리
        # ESC는 press에서 처리하므로 여기서는 특별한 로직 없음
        # if key == keyboard.Key.esc:
        #     return False
        return True # 리스너 계속 실행

    def _check_for_replacement(self):
        """현재 버퍼가 규칙 키워드로 끝나는지 확인하고, 일치 시 로그 출력"""
        if not self.buffer: # 버퍼 비어있으면 체크 안 함
            return False

        logging.debug(f"Checking buffer '{self.buffer}' for matching keyword ending.")
        
        match_found = False
        matched_keyword = None
        replacement_text = None

        # 버퍼의 끝부분이 키워드와 일치하는지 확인
        for keyword, text in self.rules.items():
            if self.buffer.endswith(keyword):
                matched_keyword = keyword
                replacement_text = text
                match_found = True
                break # 첫 번째 일치하는 규칙 사용

        if match_found:
            logging.info(f"Keyword match found! Keyword: '{matched_keyword}', Buffer: '{self.buffer}'")
            print(f"-----> ACTION: Replace '{matched_keyword}' with '{replacement_text}' (simulation) <-----")
            # 실제 치환 로직 호출 부분 (다음 단계에서 구현)
            # self._perform_replacement(matched_keyword, replacement_text)
            return True
        else:
            logging.debug("No matching keyword found for buffer ending.")
            return False

    # --- 리스너 시작/중지 및 실행 로직 (이전과 거의 동일) ---
    def _run_listener(self):
        """리스너를 실행하는 내부 메서드 (별도 스레드에서 실행됨)"""
        logging.info("Keyboard listener thread starting.")
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
                suppress=False
            )
            with self.listener as l:
                l.join()
        except Exception as e:
            logging.error(f"Error in listener thread: {e}", exc_info=True)
        finally:
            logging.info("Keyboard listener thread finished.")
            self.listener = None # 리스너 객체 확실히 정리

    def start(self):
        """키보드 리스너를 별도 스레드에서 시작"""
        if self.listener_thread is not None and self.listener_thread.is_alive():
            logging.warning("Listener is already running.")
            return

        logging.info("Starting keyboard listener...")
        self._stop_event.clear()
        self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
        self.listener_thread.start()

    def stop(self):
        """키보드 리스너를 중지"""
        if self.listener is None:
            logging.warning("Listener stop requested, but listener object does not exist (already stopped or failed to start?).")
            # 스레드가 살아있는지 확인하고 정리 시도
            if self.listener_thread and self.listener_thread.is_alive():
                 logging.info("Attempting to stop the listener thread directly (might not be clean)...")
                 # 강제 종료는 위험하므로 여기서는 시도하지 않음
                 pass
            return

        if not self._stop_event.is_set(): # 중지 요청이 이미 발생하지 않았는지 확인
             logging.info("Stopping keyboard listener...")
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
                      logging.debug("Called listener.stop()")

             except Exception as e:
                 logging.error(f"Error during listener stop: {e}", exc_info=True)
        else:
             logging.warning("Listener stop requested, but already in progress or stopped.")

        # 스레드 종료 대기 (선택 사항, 너무 길면 GUI 블록 가능)
        # if self.listener_thread and self.listener_thread.is_alive():
        #     self.listener_thread.join(timeout=0.5)
        #     if self.listener_thread.is_alive():
        #         logging.warning("Listener thread did not stop within timeout.")

        # self.listener = None # _run_listener의 finally 블록에서 처리
        logging.info("Keyboard listener stop sequence initiated.")


# 테스트용 코드
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s')
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
        print("\nCtrl+C detected, stopping listener...")
        listener.stop()
        print("Listener stopped by Ctrl+C.") 