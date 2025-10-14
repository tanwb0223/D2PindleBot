"""
颜色校准工具
用于确定暗金装备等物品的准确颜色范围
"""
import cv2
import numpy as np
from PIL import ImageGrab
import time

def mouse_callback(event, x, y, flags, param):
    """鼠标回调，点击获取颜色"""
    if event == cv2.EVENT_LBUTTONDOWN:
        img = param['img']
        if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
            bgr = img[y, x]
            print(f"\n坐标: ({x}, {y})")
            print(f"BGR颜色: {bgr}")
            print(f"建议下限: {np.maximum(bgr - 30, 0)}")
            print(f"建议上限: {np.minimum(bgr + 30, 255)}")

def main():
    print("=" * 60)
    print("暗黑2物品颜色校准工具")
    print("=" * 60)
    print("\n使用方法:")
    print("1. 启动游戏，让物品掉落在地上")
    print("2. 3秒后会截取屏幕")
    print("3. 在弹出的窗口中点击物品名称文字")
    print("4. 控制台会显示该位置的BGR颜色值")
    print("5. 按 ESC 退出")
    print("=" * 60)
    
    # 设置截取区域
    scan_area = (200, 100, 800, 600)  # (x1, y1, x2, y2)
    
    print(f"\n扫描区域: {scan_area}")
    print("\n3秒后开始截图...")
    time.sleep(3)
    
    # 截取屏幕
    print("正在截取屏幕...")
    screenshot = ImageGrab.grab(bbox=scan_area)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 创建窗口
    window_name = 'Color Calibration - Click on item text'
    cv2.namedWindow(window_name)
    
    # 设置鼠标回调
    param = {'img': img}
    cv2.setMouseCallback(window_name, mouse_callback, param)
    
    print("\n截图完成！请在窗口中点击物品文字获取颜色")
    print("按 ESC 键退出\n")
    print("常见物品类型:")
    print("  - 暗金装备: 深棕色/金色文字")
    print("  - 绿色装备: 亮绿色文字")
    print("  - 符文: 橙色/橙红色文字")
    print("  - 稀有装备: 亮黄色文字")
    
    # 显示图像
    while True:
        cv2.imshow(window_name, img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
    
    cv2.destroyAllWindows()
    print("\n校准完成！")


if __name__ == '__main__':
    main()
