import win32api
import win32con
import time
from typing import Tuple


class InputController:
    @staticmethod
    def click(x: int, y: int, button: str = 'left', delay: float = 0.1):
        win32api.SetCursorPos((x, y))
        time.sleep(delay)
        
        if button == 'left':
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        elif button == 'right':
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
    
    @staticmethod
    def move_to(x: int, y: int, delay: float = 0.1):
        win32api.SetCursorPos((x, y))
        time.sleep(delay)
    
    @staticmethod
    def press_key(key_code: int, delay: float = 0.1):
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(delay)
    
    @staticmethod
    def press_key_by_name(key_name: str, delay: float = 0.1):
        key_map = {
            'f1': win32con.VK_F1,
            'f2': win32con.VK_F2,
            'f3': win32con.VK_F3,
            'f4': win32con.VK_F4,
            'f5': win32con.VK_F5,
            '1': ord('1'),
            '2': ord('2'),
            '3': ord('3'),
            '4': ord('4'),
            'enter': win32con.VK_RETURN,
            'esc': win32con.VK_ESCAPE,
            'space': win32con.VK_SPACE,
        }
        
        key_code = key_map.get(key_name.lower())
        if key_code:
            InputController.press_key(key_code, delay)
    
    @staticmethod
    def type_text(text: str, delay: float = 0.05):
        for char in text:
            vk_code = win32api.VkKeyScan(char)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(delay)
