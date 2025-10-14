import win32gui
import win32con
import win32api
import time
from typing import Optional, Tuple


class WindowController:
    def __init__(self, window_title: str):
        self.window_title = window_title
        self.hwnd: Optional[int] = None
    
    def find_window(self) -> bool:
        self.hwnd = win32gui.FindWindow(None, self.window_title)
        if self.hwnd:
            return True
        return False
    
    def is_window_active(self) -> bool:
        if not self.hwnd:
            return False
        return win32gui.IsWindow(self.hwnd) and win32gui.IsWindowVisible(self.hwnd)
    
    def activate_window(self) -> bool:
        if not self.hwnd:
            if not self.find_window():
                return False
        
        try:
            if win32gui.IsIconic(self.hwnd):
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.2)
            return True
        except Exception as e:
            print(f"Error activating window: {e}")
            return False
    
    def get_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        if not self.hwnd:
            return None
        try:
            return win32gui.GetWindowRect(self.hwnd)
        except Exception:
            return None
    
    def get_client_rect(self) -> Optional[Tuple[int, int, int, int]]:
        if not self.hwnd:
            return None
        try:
            rect = win32gui.GetClientRect(self.hwnd)
            point = win32gui.ClientToScreen(self.hwnd, (rect[0], rect[1]))
            return (point[0], point[1], point[0] + rect[2], point[1] + rect[3])
        except Exception:
            return None
