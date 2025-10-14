import pyautogui
import time

print("鼠标坐标获取工具")
print("=" * 50)
print("5秒后开始显示坐标，按Ctrl+C停止")
print("移动鼠标到需要的位置并记录坐标")
print("=" * 50)

time.sleep(5)

try:
    while True:
        x, y = pyautogui.position()
        print(f"\r坐标: ({x}, {y})    ", end="", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n已停止")
