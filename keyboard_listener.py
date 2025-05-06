import threading
import time
from pynput import keyboard
import logging

class KeyboardListener:
    """전역 키보드 입력을 감지하는 리스너 클래스"""

    def __init__(self):
        self.listener_thread = None
        self.listener = None
        self._stop_event = threading.Event()
        logging.info("KeyboardListener initialized.")

    def _on_press(self, key):
        """키가 눌렸을 때 호출될 콜백 함수"""
        try:
            # 일반 문자인 경우
            logging.debug(f"Alphanumeric key pressed: {key.char}")
            # TODO: 입력된 키를 버퍼에 저장하는 로직 추가
        except AttributeError:
            # 특수 키인 경우 (Shift, Ctrl, Alt, F1 등)
            logging.debug(f"Special key pressed: {key}")
            # TODO: 특수 키 처리 로직 (필요한 경우)
            pass

    def _on_release(self, key):
        """키에서 손을 뗐을 때 호출될 콜백 함수"""
        logging.debug(f"Key released: {key}")
        # 필요하다면 키 릴리즈 이벤트 처리
        # 예: ESC 키를 누르면 리스너 종료
        if key == keyboard.Key.esc:
            logging.info("ESC key pressed, stopping listener.")
            self.stop()
            return False # 리스너 루프 중단
        return True # 리스너 계속 실행

    def _run_listener(self):
        """리스너를 실행하는 내부 메서드 (별도 스레드에서 실행됨)"""
        logging.info("Keyboard listener thread starting.")
        # Listener 인스턴스 생성. non-blocking 방식으로 실행됩니다.
        # suppress=True 로 설정하면 이벤트가 다른 곳으로 전달되지 않도록 막을 수 있지만,
        # 여기서는 다른 프로그램 입력을 방해하지 않도록 False (기본값) 또는 명시적으로 설정합니다.
        self.listener = keyboard.Listener(
            on_press=self._on_press, 
            on_release=self._on_release,
            suppress=False # 다른 애플리케이션으로 키 이벤트 전달 허용
        )
        # 리스너 시작 (join()을 호출하면 이 스레드가 여기서 블록됨)
        # 리스너가 자체 스레드에서 실행되므로 join()으로 대기합니다.
        with self.listener as l:
            l.join()
        logging.info("Keyboard listener thread finished.")

    def start(self):
        """키보드 리스너를 별도 스레드에서 시작"""
        if self.listener_thread is not None and self.listener_thread.is_alive():
            logging.warning("Listener is already running.")
            return

        logging.info("Starting keyboard listener...")
        self._stop_event.clear() # 중지 플래그 리셋
        # 데몬 스레드로 설정하면 메인 스레드 종료 시 함께 종료됨
        self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
        self.listener_thread.start()

    def stop(self):
        """키보드 리스너를 중지"""
        if self.listener is None:
            logging.warning("Listener was not started.")
            return
        
        if self.listener_thread is None or not self.listener_thread.is_alive():
             logging.warning("Listener thread is not running or already stopped.")
             return

        logging.info("Stopping keyboard listener...")
        self._stop_event.set() # 중지 신호 설정 (필요 시 콜백 내부에서 확인)

        # pynput 리스너에게 직접 중지 요청
        # keyboard.Listener.stop() 은 내부적으로 예외를 발생시켜 join()을 해제합니다.
        # Listener 스레드 내에서 호출되어야 할 수도 있습니다. 
        # 또는 간단하게는 keyboard.Controller를 사용하여 특정 키(예: Esc)를 보내는 방식도 고려 가능
        # 여기서는 _on_release 에서 ESC 키 감지 시 리턴 False로 중단합니다.
        if self.listener:
             self.listener.stop()

        # 스레드가 완전히 종료될 때까지 잠시 대기 (선택 사항, 너무 길면 GUI 블록 가능성)
        # self.listener_thread.join(timeout=1) 

        self.listener = None # 리스너 객체 정리
        # self.listener_thread = None # 스레드 객체는 재사용 불가
        logging.info("Keyboard listener stopped.")

# 테스트용 코드: 이 파일을 직접 실행하면 리스너 시작
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    listener = KeyboardListener()
    listener.start()
    
    # 메인 스레드가 종료되지 않도록 유지 (테스트 목적)
    # 실제 앱에서는 GUI 이벤트 루프가 이 역할을 함
    try:
        while listener.listener_thread.is_alive():
             time.sleep(0.1) # CPU 사용량 줄이기
    except KeyboardInterrupt:
        print("\nCtrl+C detected, stopping listener...")
        listener.stop()
        print("Listener stopped by Ctrl+C.") 